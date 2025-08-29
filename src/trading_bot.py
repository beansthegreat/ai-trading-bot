import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import pytz

from config import config
from utils.logger import trading_logger
from utils.alpaca_client import alpaca_client
from utils.risk_management import risk_manager
from strategies.adaptive_strategy import StrategyIntelligence

class TradingBot:
    """Main trading bot class with timezone-aware scheduling"""
    
    def __init__(self):
        self.strategy = StrategyIntelligence()
        self.is_running = False
        self.last_run = None
        self.trades_today = 0
        
        # Timezone setup
        self.nyse_tz = pytz.timezone('America/New_York')
        self.netherlands_tz = pytz.timezone('Europe/Amsterdam')
        
        trading_logger.info("Trading bot initialized", strategy=self.strategy.name)
    
    def start(self):
        """Start the trading bot with automatic NYSE timezone scheduling"""
        try:
            # Validate configuration
            config.validate()
            
            # Test connection
            self._test_connection()
            
            # Schedule trading jobs with timezone awareness
            self._schedule_jobs_timezone_aware()
            
            self.is_running = True
            trading_logger.success("Trading bot started successfully with timezone-aware scheduling")
            
            # Show next trading session info
            self._show_next_trading_session()
            
            # Keep the bot running
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            trading_logger.info("Trading bot stopped by user")
            self.stop()
        except Exception as e:
            trading_logger.error(f"Trading bot error: {e}")
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        trading_logger.info("Trading bot stopped")
    
    def _test_connection(self):
        """Test Alpaca connection"""
        try:
            account = alpaca_client.get_account()
            trading_logger.success(
                "Alpaca connection successful",
                account_id=account['id'],
                status=account['status'],
                cash=f"${account['cash']:.2f}",
                portfolio_value=f"${account['portfolio_value']:.2f}"
            )
        except Exception as e:
            trading_logger.error(f"Failed to connect to Alpaca: {e}")
            raise
    
    def _get_nyse_times_in_netherlands(self):
        """Get NYSE opening and closing times in Netherlands timezone"""
        now = datetime.now(self.netherlands_tz)
        
        # Create naive datetime objects for NYSE times
        nyse_open_et = datetime(now.year, now.month, now.day, 9, 30, 0)
        nyse_close_et = datetime(now.year, now.month, now.day, 16, 0, 0)
        
        # Localize to NYSE timezone
        nyse_open_et = self.nyse_tz.localize(nyse_open_et)
        nyse_close_et = self.nyse_tz.localize(nyse_close_et)
        
        # Convert to Netherlands time
        nyse_open_nl = nyse_open_et.astimezone(self.netherlands_tz)
        nyse_close_nl = nyse_close_et.astimezone(self.netherlands_tz)
        
        return nyse_open_nl, nyse_close_nl
    
    def _schedule_jobs_timezone_aware(self):
        """Schedule trading jobs with timezone awareness"""
        # Clear existing schedules
        schedule.clear()
        
        # Get NYSE times in Netherlands timezone
        nyse_open_nl, nyse_close_nl = self._get_nyse_times_in_netherlands()
        
        # Format times for scheduling
        open_time = nyse_open_nl.strftime("%H:%M")
        close_time = nyse_close_nl.strftime("%H:%M")
        
        trading_logger.info(
            "Scheduling timezone-aware trading",
            nyse_open_et="09:30",
            nyse_close_et="16:00",
            nyse_open_nl=open_time,
            nyse_close_nl=close_time,
            netherlands_tz=self.netherlands_tz.zone
        )
        
        # Schedule daily reset at NYSE open (Netherlands time)
        schedule.every().monday.at(open_time).do(self._reset_daily_tracking)
        schedule.every().tuesday.at(open_time).do(self._reset_daily_tracking)
        schedule.every().wednesday.at(open_time).do(self._reset_daily_tracking)
        schedule.every().thursday.at(open_time).do(self._reset_daily_tracking)
        schedule.every().friday.at(open_time).do(self._reset_daily_tracking)
        
                # CONSERVATIVE: Schedule trading cycles every 2 minutes during market hours (API rate limit safe)
        schedule.every(config.TRADING_CYCLE_MINUTES).minutes.do(self.run_trading_cycle)
        
        # Schedule end of day cleanup at NYSE close (Netherlands time)
        schedule.every().monday.at(close_time).do(self._end_of_day_cleanup)
        schedule.every().tuesday.at(close_time).do(self._end_of_day_cleanup)
        schedule.every().wednesday.at(close_time).do(self._end_of_day_cleanup)
        schedule.every().thursday.at(close_time).do(self._end_of_day_cleanup)
        schedule.every().friday.at(close_time).do(self._end_of_day_cleanup)
        
        trading_logger.info("Timezone-aware trading jobs scheduled")
    
    def _show_next_trading_session(self):
        """Show information about the next trading session"""
        now = datetime.now(self.netherlands_tz)
        nyse_open_nl, nyse_close_nl = self._get_nyse_times_in_netherlands()
        
        # Find next trading day
        next_trading_day = now
        while next_trading_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
            next_trading_day += timedelta(days=1)
        
        next_open = next_trading_day.replace(
            hour=nyse_open_nl.hour, 
            minute=nyse_open_nl.minute, 
            second=0, 
            microsecond=0
        )
        
        if now.weekday() < 5:  # Weekday
            if now.time() < nyse_open_nl.time():
                # Market opens today
                time_until_open = next_open - now
                trading_logger.info(
                    "Next trading session",
                    date=next_open.strftime("%Y-%m-%d"),
                    opens_at=f"09:30 (New York time) / {nyse_open_nl.strftime('%H:%M')} (Netherlands time)",
                    time_until_open=f"{time_until_open.seconds // 3600}h {(time_until_open.seconds % 3600) // 60}m"
                )
            elif now.time() < nyse_close_nl.time():
                # Market is open now
                time_until_close = nyse_close_nl - now
                trading_logger.info(
                    "Market is currently open",
                    closes_at=f"16:00 (New York time) / {nyse_close_nl.strftime('%H:%M')} (Netherlands time)",
                    time_until_close=f"{time_until_close.seconds // 3600}h {(time_until_close.seconds % 3600) // 60}m"
                )
            else:
                # Market closed for today
                next_open += timedelta(days=1)
                while next_open.weekday() >= 5:
                    next_open += timedelta(days=1)
                time_until_next = next_open - now
                trading_logger.info(
                    "Market closed for today",
                    next_session=f"{next_open.strftime('%Y-%m-%d')} at {nyse_open_nl.strftime('%H:%M')} (Netherlands time)",
                    time_until_next=f"{time_until_next.days}d {time_until_next.seconds // 3600}h"
                )
        else:
            # Weekend
            time_until_next = next_open - now
            trading_logger.info(
                "Weekend - no trading",
                next_session=f"{next_open.strftime('%Y-%m-%d')} at {nyse_open_nl.strftime('%H:%M')} (Netherlands time)",
                time_until_next=f"{time_until_next.days}d {time_until_next.seconds // 3600}h"
            )
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        try:
            # Check if market is open
            if not alpaca_client.is_market_open():
                trading_logger.info("Market is closed, skipping trading cycle")
                return
            
            # Get current time in both timezones for logging
            now_nl = datetime.now(self.netherlands_tz)
            now_nyse = datetime.now(self.nyse_tz)
            
            trading_logger.debug(
                "Running trading cycle",
                netherlands_time=now_nl.strftime("%H:%M:%S"),
                nyse_time=now_nyse.strftime("%H:%M:%S")
            )
            
            # Get account information
            account = alpaca_client.get_account()
            
            # Check risk management
            risk_check = risk_manager.can_trade(account)
            if not risk_check['can_trade']:
                trading_logger.warning("Trading blocked by risk management", failed_checks=risk_check['failed_checks'])
                return
            
            # Check for emergency stop
            if risk_manager.should_emergency_stop(account['portfolio_value']):
                trading_logger.error("Emergency stop triggered - closing all positions")
                alpaca_client.close_all_positions()
                return
            
            # Analyze each symbol
            for symbol in config.SYMBOLS:
                self._analyze_symbol(symbol, account)
            
            self.last_run = datetime.now()
            self.trades_today += 1
            
        except Exception as e:
            trading_logger.error(f"Error in trading cycle: {e}")
    
    def _analyze_symbol(self, symbol: str, account: Dict[str, Any]):
        """Analyze a single symbol and execute trades if needed"""
        try:
            # Get historical data
            df = alpaca_client.get_historical_data(symbol, timeframe='1D', limit=100)
            if df.empty:
                trading_logger.warning(f"No data available for {symbol}")
                return
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Get current position
            position = alpaca_client.get_position(symbol)
            
            # Analyze with strategy
            analysis = self.strategy.analyze(df)
            
            trading_logger.debug(
                f"Analysis for {symbol}",
                signal=analysis['signal'],
                strength=analysis['strength'],
                reason=analysis['reason']
            )
            
            # Execute trades based on analysis with wash sale prevention
            if analysis['signal'] == 'buy' and not position:
                # Check wash sale restriction before buying
                if not risk_manager.check_wash_sale_restriction(symbol, 'buy'):
                    self._execute_buy(symbol, df, analysis, account)
                else:
                    trading_logger.warning(f"Skipping buy for {symbol} due to wash sale restriction")
            elif analysis['signal'] == 'sell' and position:
                self._execute_sell(symbol, position, analysis)
            
            # Check stop loss and take profit
            if position:
                current_price = df['close'].iloc[-1]
                if risk_manager.should_stop_loss(position, current_price):
                    self._execute_sell(symbol, position, {'signal': 'stop_loss', 'reason': 'Stop loss triggered'})
                elif risk_manager.should_take_profit(position, current_price):
                    self._execute_sell(symbol, position, {'signal': 'take_profit', 'reason': 'Take profit triggered'})
            
        except Exception as e:
            trading_logger.error(f"Error analyzing {symbol}: {e}")
    
    def _execute_buy(self, symbol: str, df: pd.DataFrame, analysis: Dict[str, Any], account: Dict[str, Any]):
        """Execute a buy order with intelligent position sizing"""
        try:
            current_price = df['close'].iloc[-1]
            available_cash = account['cash']
            
            # Calculate intelligent position size with volatility adjustment
            volatility = analysis.get('volatility', None)
            position_info = risk_manager.calculate_position_size(
                symbol, current_price, available_cash, analysis['strength'], volatility
            )
            
            # Validate trade
            validation = risk_manager.validate_trade(
                symbol, 'buy', position_info['amount'], current_price, account, position_info['type']
            )
            
            if not validation['valid']:
                trading_logger.warning(f"Buy validation failed for {symbol}", errors=validation['errors'])
                return
            
            # Place order based on intelligent position type
            if position_info['type'] == 'dollar_amount':
                order = alpaca_client.place_dollar_amount_order(symbol, 'buy', position_info['amount'])
                trading_logger.info(f"Intelligent buy order placed for {symbol}", 
                                  dollar_amount=position_info['amount'],
                                  estimated_shares=position_info['shares'],
                                  reason=position_info['reason'])
            else:
                order = alpaca_client.place_market_order(symbol, 'buy', position_info['amount'])
                trading_logger.info(f"Intelligent buy order placed for {symbol}", 
                                  shares=position_info['amount'],
                                  dollar_value=position_info['dollar_value'],
                                  reason=position_info['reason'])
            
            # Record trade for cooldown system
            self.strategy.record_trade(symbol)
            
            # Log the trade with the correct amount
            if position_info['type'] == 'dollar_amount':
                trading_logger.trade(
                    action='BUY',
                    symbol=symbol,
                    dollar_amount=position_info['amount'],
                    price=current_price,
                    order_id=order['id'],
                    strength=analysis['strength']
                )
            else:
                trading_logger.trade(
                    action='BUY',
                    symbol=symbol,
                    quantity=position_info['amount'],
                    price=current_price,
                    order_id=order['id'],
                    strength=analysis['strength']
                )
            
        except Exception as e:
            trading_logger.error(f"Error executing buy for {symbol}: {e}")
    
    def _execute_sell(self, symbol: str, position: Dict[str, Any], analysis: Dict[str, Any]):
        """Execute a sell order with fractional shares support and wash sale tracking"""
        try:
            quantity = abs(float(position['quantity']))
            
            # Place order
            order = alpaca_client.place_market_order(symbol, 'sell', quantity)
            
            # Record trade for cooldown system
            self.strategy.record_trade(symbol)
            
            # Record potential wash sale if selling at a loss
            unrealized_pl = float(position.get('unrealized_pl', 0))
            if unrealized_pl < 0:  # Selling at a loss
                risk_manager.record_wash_sale(symbol, 'sell', abs(unrealized_pl))
            
            trading_logger.trade(
                action='SELL',
                symbol=symbol,
                quantity=quantity,
                order_id=order['id'],
                signal=analysis['signal'],
                reason=analysis['reason']
            )
            
        except Exception as e:
            trading_logger.error(f"Error executing sell for {symbol}: {e}")
    
    def _reset_daily_tracking(self):
        """Reset daily tracking at market open"""
        risk_manager.reset_daily_tracking()
        self.trades_today = 0
        trading_logger.info("Daily tracking reset at NYSE open")
    
    def _end_of_day_cleanup(self):
        """End of day cleanup"""
        try:
            # Close all positions if configured
            positions = alpaca_client.get_positions()
            if positions:
                trading_logger.info(f"Closing {len(positions)} positions at end of day")
                alpaca_client.close_all_positions()
            
            # Log daily summary
            risk_summary = risk_manager.get_risk_summary()
            trading_logger.info(
                "End of day summary",
                trades_today=self.trades_today,
                daily_loss=risk_summary['daily_loss'],
                max_drawdown=risk_summary['max_drawdown']
            )
            
        except Exception as e:
            trading_logger.error(f"Error in end of day cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        now_nl = datetime.now(self.netherlands_tz)
        now_nyse = datetime.now(self.nyse_tz)
        
        return {
            'is_running': self.is_running,
            'last_run': self.last_run,
            'trades_today': self.trades_today,
            'strategy': self.strategy.name,
            'symbols': config.SYMBOLS,
            'risk_summary': risk_manager.get_risk_summary(),
            'timezone_info': {
                'netherlands_time': now_nl.strftime("%Y-%m-%d %H:%M:%S"),
                'nyse_time': now_nyse.strftime("%Y-%m-%d %H:%M:%S"),
                'netherlands_tz': self.netherlands_tz.zone,
                'nyse_tz': self.nyse_tz.zone
            }
        }

# Global bot instance
trading_bot = TradingBot()

if __name__ == "__main__":
    trading_bot.start()
