import pandas as pd
import yfinance as yf
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.logger import trading_logger
from utils.performance_analytics import performance_analytics
from strategies.momentum_strategy import MomentumStrategy
from config import config

class Backtester:
    """Backtesting framework for trading strategies"""
    
    def __init__(self):
        self.strategy = MomentumStrategy()
        self.results = []
        self.portfolio_value = 10000  # Starting portfolio value
        self.cash = 10000
        self.positions = {}
        self.trades = []
        
    def run_backtest(self, symbols: List[str], start_date: str, end_date: str = None) -> Dict[str, Any]:
        """Run backtest on historical data"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        trading_logger.info(f"Starting backtest", 
                           symbols=symbols,
                           start_date=start_date,
                           end_date=end_date)
        
        # Reset state
        self.results = []
        self.portfolio_value = 10000
        self.cash = 10000
        self.positions = {}
        self.trades = []
        
        # Get historical data for all symbols
        data = self._get_historical_data(symbols, start_date, end_date)
        
        if not data:
            trading_logger.error("No historical data available for backtest")
            return {}
        
        # Run simulation
        self._run_simulation(data)
        
        # Calculate results
        results = self._calculate_results()
        
        trading_logger.info(f"Backtest completed", 
                           total_trades=len(self.trades),
                           final_portfolio_value=self.portfolio_value,
                           total_return=results['total_return'])
        
        return results
    
    def _get_historical_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """Get historical minute data for symbols"""
        data = {}
        
        for symbol in symbols:
            try:
                # Get 1-minute data for the past 7 days (yfinance limit for free tier)
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, interval='1m')
                
                if not df.empty:
                    # Clean and prepare data
                    df = df.reset_index()
                    df['symbol'] = symbol
                    df = df.rename(columns={
                        'Datetime': 'timestamp',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })
                    
                    # Ensure we have required columns
                    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'symbol']
                    if all(col in df.columns for col in required_columns):
                        data[symbol] = df
                        trading_logger.info(f"Loaded {len(df)} data points for {symbol}")
                    else:
                        trading_logger.warning(f"Missing required columns for {symbol}")
                else:
                    trading_logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                trading_logger.error(f"Error loading data for {symbol}: {e}")
        
        return data
    
    def _run_simulation(self, data: Dict[str, pd.DataFrame]):
        """Run the trading simulation"""
        # Combine all data and sort by timestamp
        all_data = []
        for symbol, df in data.items():
            all_data.extend(df.to_dict('records'))
        
        all_data.sort(key=lambda x: x['timestamp'])
        
        # Process each minute
        for i, row in enumerate(all_data):
            symbol = row['symbol']
            timestamp = row['timestamp']
            
            # Update current price
            if symbol not in self.positions:
                self.positions[symbol] = 0
            
            # Get historical data for analysis (last 100 points)
            symbol_data = data[symbol]
            start_idx = max(0, i - 100)
            historical_df = symbol_data.iloc[start_idx:i+1].copy()
            
            if len(historical_df) < 20:  # Need minimum data for analysis
                continue
            
            # Analyze with strategy
            analysis = self.strategy.analyze(historical_df)
            
            # Execute trades based on signals
            if analysis['signal'] == 'buy' and self.positions[symbol] == 0:
                self._execute_buy(symbol, row, analysis, timestamp)
            elif analysis['signal'] == 'sell' and self.positions[symbol] > 0:
                self._execute_sell(symbol, row, analysis, timestamp)
            
            # Update portfolio value
            self._update_portfolio_value(row, timestamp)
    
    def _execute_buy(self, symbol: str, row: Dict[str, Any], analysis: Dict[str, Any], timestamp: datetime):
        """Execute a buy order in backtest"""
        price = row['close']
        
        # Calculate position size (simplified for backtest)
        position_value = min(1000, self.cash * 0.1)  # 10% of cash, max $1000
        shares = position_value / price
        
        if shares > 0 and self.cash >= position_value:
            self.positions[symbol] = shares
            self.cash -= position_value
            
            trade = {
                'timestamp': timestamp,
                'symbol': symbol,
                'action': 'buy',
                'quantity': shares,
                'price': price,
                'value': position_value,
                'signal_strength': analysis.get('strength', 0),
                'confirmation_passed': analysis.get('confirmation_passed', False)
            }
            
            self.trades.append(trade)
            
            # Record trade for analytics
            performance_analytics.record_trade(trade)
            
            trading_logger.debug(f"Backtest BUY: {symbol} {shares:.4f} @ ${price:.2f}")
    
    def _execute_sell(self, symbol: str, row: Dict[str, Any], analysis: Dict[str, Any], timestamp: datetime):
        """Execute a sell order in backtest"""
        price = row['close']
        shares = self.positions[symbol]
        
        if shares > 0:
            position_value = shares * price
            self.positions[symbol] = 0
            self.cash += position_value
            
            # Calculate P&L
            buy_trade = next((t for t in self.trades if t['symbol'] == symbol and t['action'] == 'buy'), None)
            pnl = 0
            if buy_trade:
                pnl = (price - buy_trade['price']) * shares
            
            trade = {
                'timestamp': timestamp,
                'symbol': symbol,
                'action': 'sell',
                'quantity': shares,
                'price': price,
                'value': position_value,
                'pnl': pnl,
                'signal_strength': analysis.get('strength', 0),
                'confirmation_passed': analysis.get('confirmation_passed', False)
            }
            
            self.trades.append(trade)
            
            # Record trade for analytics
            performance_analytics.record_trade(trade)
            
            trading_logger.debug(f"Backtest SELL: {symbol} {shares:.4f} @ ${price:.2f} P&L: ${pnl:.2f}")
    
    def _update_portfolio_value(self, row: Dict[str, Any], timestamp: datetime):
        """Update portfolio value"""
        symbol = row['symbol']
        price = row['close']
        
        # Calculate current portfolio value
        positions_value = sum(
            self.positions[s] * price if s == symbol else 0
            for s in self.positions
        )
        
        self.portfolio_value = self.cash + positions_value
        
        # Record portfolio value
        self.results.append({
            'timestamp': timestamp,
            'portfolio_value': self.portfolio_value,
            'cash': self.cash,
            'positions_value': positions_value
        })
    
    def _calculate_results(self) -> Dict[str, Any]:
        """Calculate backtest results"""
        if not self.results:
            return {}
        
        initial_value = 10000
        final_value = self.results[-1]['portfolio_value']
        total_return = (final_value - initial_value) / initial_value
        
        # Calculate metrics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in self.trades if t.get('pnl', 0) < 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate profit factor
        total_wins = sum(t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) > 0)
        total_losses = abs(sum(t.get('pnl', 0) for t in self.trades if t.get('pnl', 0) < 0))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'trades': self.trades,
            'portfolio_history': self.results
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.results:
            return 0
        
        peak = self.results[0]['portfolio_value']
        max_dd = 0
        
        for result in self.results:
            value = result['portfolio_value']
            if value > peak:
                peak = value
            else:
                dd = (peak - value) / peak
                max_dd = max(max_dd, dd)
        
        return max_dd
    
    def generate_backtest_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive backtest report"""
        if not results:
            return "No backtest results available"
        
        report = []
        report.append("🔬 BACKTEST RESULTS")
        report.append("=" * 50)
        report.append("")
        
        # Performance Summary
        report.append("📊 PERFORMANCE SUMMARY:")
        report.append(f"   Initial Value: ${results['initial_value']:,.2f}")
        report.append(f"   Final Value: ${results['final_value']:,.2f}")
        report.append(f"   Total Return: {results['total_return']:.2%}")
        report.append(f"   Max Drawdown: {results['max_drawdown']:.2%}")
        report.append("")
        
        # Trading Statistics
        report.append("📈 TRADING STATISTICS:")
        report.append(f"   Total Trades: {results['total_trades']}")
        report.append(f"   Winning Trades: {results['winning_trades']}")
        report.append(f"   Losing Trades: {results['losing_trades']}")
        report.append(f"   Win Rate: {results['win_rate']:.1%}")
        report.append(f"   Profit Factor: {results['profit_factor']:.2f}")
        report.append("")
        
        # Recent Trades
        report.append("🔄 RECENT TRADES:")
        for trade in results['trades'][-5:]:  # Last 5 trades
            action = trade['action'].upper()
            symbol = trade['symbol']
            quantity = trade['quantity']
            price = trade['price']
            pnl = trade.get('pnl', 0)
            
            report.append(f"   {action} {quantity:.4f} {symbol} @ ${price:.2f} P&L: ${pnl:.2f}")
        
        return "\n".join(report)

# Global instance
backtester = Backtester()
