#!/usr/bin/env python3
"""
Buy Signal Scanner
Shows all current buy signals across all stocks
"""

import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from strategies.adaptive_strategy import StrategyIntelligence
from utils.alpaca_client import alpaca_client
import yfinance as yf
import pandas as pd

class BuySignalScanner:
    """Scanner for buy signals across all stocks"""
    
    def __init__(self):
        self.strategy = StrategyIntelligence()
        self.signals = []
        
    def scan_all_signals(self):
        """Scan all symbols for buy signals"""
        print("🔍 Scanning for Buy Signals...")
        print("=" * 60)
        
        all_signals = []
        
        for symbol in config.SYMBOLS:
            try:
                print(f"📊 Analyzing {symbol}...")
                
                # Get market data
                df = yf.download(symbol, period='1d', interval='1m')
                df.columns = df.columns.get_level_values(0)
                df.columns = df.columns.str.lower()
                df['symbol'] = symbol
                
                # Analyze with adaptive strategy
                result = self.strategy.analyze(df)
                
                # Store signal information
                signal_info = {
                    'symbol': symbol,
                    'signal': result['signal'],
                    'strength': result['strength'],
                    'reason': result['reason'],
                    'strategy_used': result.get('strategy_used', 'unknown'),
                    'market_regime': result.get('market_regime', 'unknown'),
                    'regime_confidence': result.get('regime_confidence', 0),
                    'rsi': result.get('market_metrics', {}).get('rsi', 0),
                    'adx': result.get('market_metrics', {}).get('adx', 0),
                    'volatility': result.get('market_metrics', {}).get('volatility', 0),
                    'confirmation_passed': result.get('confirmation_passed', False),
                    'cooldown_active': result.get('cooldown_active', False),
                    'current_price': df['close'].iloc[-1] if len(df) > 0 else 0
                }
                
                all_signals.append(signal_info)
                
                # Show immediate results
                if result['signal'] == 'buy':
                    print(f"   🟢 BUY SIGNAL: {symbol}")
                    print(f"      Strength: {result['strength']:.4f}")
                    print(f"      Strategy: {result.get('strategy_used', 'unknown')}")
                    print(f"      Regime: {result.get('market_regime', 'unknown')}")
                    print(f"      RSI: {result.get('market_metrics', {}).get('rsi', 0):.1f}")
                    print(f"      Price: ${signal_info['current_price']:.2f}")
                elif result['signal'] == 'sell':
                    print(f"   🔴 SELL SIGNAL: {symbol}")
                else:
                    print(f"   ⚪ NEUTRAL: {symbol}")
                
            except Exception as e:
                print(f"   ❌ Error analyzing {symbol}: {e}")
                all_signals.append({
                    'symbol': symbol,
                    'signal': 'error',
                    'strength': 0,
                    'reason': f"Error: {e}",
                    'current_price': 0
                })
        
        self.signals = all_signals
        return all_signals
    
    def display_buy_signals(self):
        """Display all buy signals in a formatted table"""
        buy_signals = [s for s in self.signals if s['signal'] == 'buy']
        
        if not buy_signals:
            print("\n❌ No buy signals found at this time")
            print("   The bot is waiting for better market conditions")
            return
        
        print(f"\n🟢 BUY SIGNALS FOUND: {len(buy_signals)}")
        print("=" * 80)
        print(f"{'Symbol':<8} {'Signal':<8} {'Strength':<10} {'Strategy':<20} {'Regime':<12} {'RSI':<6} {'Price':<8} {'Reason'}")
        print("-" * 80)
        
        # Sort by signal strength (strongest first)
        buy_signals.sort(key=lambda x: abs(x['strength']), reverse=True)
        
        for signal in buy_signals:
            print(f"{signal['symbol']:<8} "
                  f"{'BUY':<8} "
                  f"{signal['strength']:<10.4f} "
                  f"{signal['strategy_used']:<20} "
                  f"{signal['market_regime']:<12} "
                  f"{signal['rsi']:<6.1f} "
                  f"${signal['current_price']:<7.2f} "
                  f"{signal['reason'][:50]}...")
    
    def display_market_summary(self):
        """Display market summary"""
        print(f"\n📊 MARKET SUMMARY")
        print("=" * 60)
        
        # Count signals
        buy_count = len([s for s in self.signals if s['signal'] == 'buy'])
        sell_count = len([s for s in self.signals if s['signal'] == 'sell'])
        neutral_count = len([s for s in self.signals if s['signal'] == 'neutral'])
        
        print(f"Buy Signals: {buy_count}")
        print(f"Sell Signals: {sell_count}")
        print(f"Neutral: {neutral_count}")
        print(f"Total Analyzed: {len(self.signals)}")
        
        # Show market regimes
        regimes = {}
        for signal in self.signals:
            regime = signal.get('market_regime', 'unknown')
            regimes[regime] = regimes.get(regime, 0) + 1
        
        print(f"\nMarket Regimes:")
        for regime, count in regimes.items():
            print(f"  {regime}: {count} stocks")
    
    def display_strategy_performance(self):
        """Display strategy performance summary"""
        print(f"\n📈 STRATEGY PERFORMANCE")
        print("=" * 60)
        
        summary = self.strategy.get_strategy_summary()
        
        print(f"Current Strategy: {summary['current_strategy']}")
        print(f"Market Regime: {summary['market_regime']}")
        print(f"Available Strategies: {', '.join(summary['available_strategies'])}")
        
        if summary['strategy_performance']:
            print(f"\nStrategy Performance:")
            for strategy, perf in summary['strategy_performance'].items():
                print(f"  {strategy}:")
                print(f"    Trades: {perf['trades']}")
                print(f"    Win Rate: {perf['win_rate']:.2%}")
                print(f"    Profit Factor: {perf['profit_factor']:.2f}")
    
    def get_position_info(self):
        """Get current position information"""
        try:
            positions = alpaca_client.get_positions()
            account = alpaca_client.get_account()
            
            print(f"\n💰 POSITION SUMMARY")
            print("=" * 60)
            print(f"Cash: ${account['cash']:.2f}")
            print(f"Portfolio Value: ${account['portfolio_value']:.2f}")
            print(f"Open Positions: {len(positions)}")
            
            if positions:
                print(f"\nCurrent Positions:")
                for pos in positions:
                    print(f"  {pos['symbol']}: {pos['quantity']:.6f} shares @ ${pos['average_price']:.2f}")
                    print(f"    Value: ${pos['market_value']:.2f} | P&L: ${pos['unrealized_pl']:.2f}")
            
        except Exception as e:
            print(f"❌ Error getting position info: {e}")
    
    def run_full_scan(self):
        """Run a complete scan and display results"""
        print("🚀 Starting Buy Signal Scanner...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Scan all signals
        self.scan_all_signals()
        
        # Display results
        self.display_buy_signals()
        self.display_market_summary()
        self.display_strategy_performance()
        self.get_position_info()
        
        print(f"\n✅ Scan completed at {datetime.now().strftime('%H:%M:%S')}")

def main():
    """Main function"""
    # Load environment variables
    load_dotenv()
    
    # Create scanner and run
    scanner = BuySignalScanner()
    scanner.run_full_scan()

if __name__ == "__main__":
    main()
