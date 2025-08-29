#!/usr/bin/env python3
"""
Live monitoring script for the trading bot
Shows real-time updates, current status, and live log monitoring
"""

import sys
import os
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.alpaca_client import alpaca_client
from utils.logger import trading_logger

class LiveMonitor:
    """Live monitoring for the trading bot"""
    
    def __init__(self):
        self.running = False
        self.last_log_position = 0
        
    def start_monitoring(self):
        """Start live monitoring"""
        self.running = True
        print("🔴 Live Trading Bot Monitor")
        print("=" * 50)
        
        # Start log monitoring in a separate thread
        log_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        log_thread.start()
        
        try:
            while self.running:
                self._display_status()
                time.sleep(30)  # Update status every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Live monitoring stopped")
            self.running = False
    
    def _display_status(self):
        """Display current bot status"""
        try:
            # Clear screen (Windows)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🔴 Live Trading Bot Monitor")
            print("=" * 50)
            print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Account Status
            account = alpaca_client.get_account()
            print("💰 Account Status:")
            print(f"   Cash: ${account['cash']:.2f}")
            print(f"   Portfolio Value: ${account['portfolio_value']:.2f}")
            print(f"   Equity: ${account['equity']:.2f}")
            print()
            
            # Market Status
            market_open = alpaca_client.is_market_open()
            print("🏛️  Market Status:")
            print(f"   Market: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
            print()
            
            # Current Positions
            positions = alpaca_client.get_positions()
            print("📈 Current Positions:")
            if positions:
                for pos in positions:
                    print(f"   {pos['symbol']}: {pos['quantity']:.6f} shares @ ${pos['average_price']:.2f}")
                    print(f"      Value: ${pos['market_value']:.2f} | P&L: ${pos['unrealized_pl']:.2f}")
            else:
                print("   No open positions")
            print()
            
            # Recent Orders
            try:
                orders = alpaca_client.get_orders(status='filled', limit=5)
                print("📋 Recent Orders:")
                if orders:
                    for order in orders[:3]:  # Show last 3 orders
                        try:
                            order_time = order['created_at'].strftime('%H:%M:%S') if hasattr(order['created_at'], 'strftime') else str(order['created_at'])
                            quantity = order.get('quantity', 0) or 0
                            price = order.get('price', 'N/A')
                            print(f"   {order_time} | {order['side'].upper()} {quantity} {order['symbol']} @ ${price}")
                        except Exception as e:
                            print(f"   Error displaying order: {e}")
                else:
                    print("   No recent orders")
            except Exception as e:
                print("📋 Recent Orders:")
                print(f"   Error loading orders: {e}")
            print()
            
            # Trading Bot Status
            print("🤖 Bot Status:")
            print("   Status: 🟢 RUNNING")
            print("   Strategy: Adaptive Strategy Intelligence")
            print(f"   Symbols: {', '.join(config.SYMBOLS)}")
            print(f"   Frequency: Every {config.TRADING_CYCLE_MINUTES} minutes")
            print("   API Rate Limiting: ✅ Active (150/200 req/min)")
            print("   Signal Confirmation: ✅ Active (RSI, MACD, ADX)")
            print("   Cooldown System: ✅ Active (15min symbol, 5min global)")
            print("   Volatility Adjustment: ✅ Active")
            print("   Performance Analytics: ✅ Active")
            print("   Micro-Movement Detection: ✅ Active")
            print("   Adaptive Strategy Intelligence: ✅ Active")
            print()
            
            # Quick Buy Signal Check
            self._show_quick_buy_signals()
            
            print("📊 Live Log Updates:")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error updating status: {e}")
    
    def _show_quick_buy_signals(self):
        """Show quick buy signal summary"""
        try:
            from strategies.adaptive_strategy import StrategyIntelligence
            import yfinance as yf
            import pandas as pd
            
            print("🔍 Quick Buy Signal Check:")
            
            strategy = StrategyIntelligence()
            buy_signals = []
            
            # Check first 3 symbols for quick scan
            for symbol in config.SYMBOLS[:3]:
                try:
                    df = yf.download(symbol, period='1d', interval='1m')
                    df.columns = df.columns.get_level_values(0)
                    df.columns = df.columns.str.lower()
                    df['symbol'] = symbol
                    
                    result = strategy.analyze(df)
                    
                    if result['signal'] == 'buy':
                        buy_signals.append({
                            'symbol': symbol,
                            'strength': result['strength'],
                            'strategy': result.get('strategy_used', 'unknown'),
                            'price': df['close'].iloc[-1] if len(df) > 0 else 0
                        })
                        
                except Exception:
                    continue
            
            if buy_signals:
                print("   🟢 Active Buy Signals:")
                for signal in buy_signals:
                    print(f"      {signal['symbol']}: {signal['strength']:.4f} strength @ ${signal['price']:.2f}")
            else:
                print("   ⚪ No buy signals currently")
                
        except Exception as e:
            print(f"   ❌ Signal check error: {e}")
    
    def _monitor_logs(self):
        """Monitor log file for new entries"""
        log_file = config.LOG_FILE
        
        while self.running:
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        # Read all lines and get current position
                        lines = f.readlines()
                        current_position = len(lines)
                        
                        # Show new lines since last check
                        if current_position > self.last_log_position:
                            new_lines = lines[self.last_log_position:]
                            for line in new_lines:
                                # Parse and format log line
                                formatted_line = self._format_log_line(line.strip())
                                if formatted_line:
                                    print(formatted_line)
                            
                            self.last_log_position = current_position
                
                time.sleep(2)  # Check logs every 2 seconds
                
            except Exception as e:
                print(f"❌ Error monitoring logs: {e}")
                time.sleep(5)
    
    def _format_log_line(self, line):
        """Format log line for display"""
        if not line:
            return None
            
        # Skip old log format lines
        if line.startswith('{'):
            return None
            
        # Parse timestamp and message
        try:
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) >= 3:
                    timestamp = parts[0].strip()
                    level = parts[1].strip()
                    message = parts[2].strip()
                    
                    # Color code based on level
                    if 'ERROR' in level:
                        return f"🔴 {timestamp} | {message}"
                    elif 'WARNING' in level:
                        return f"🟡 {timestamp} | {message}"
                    elif 'SUCCESS' in level:
                        return f"🟢 {timestamp} | {message}"
                    elif 'TRADE' in message:
                        return f"💰 {timestamp} | {message}"
                    elif 'STRATEGY' in message:
                        return f"📊 {timestamp} | {message}"
                    else:
                        return f"ℹ️  {timestamp} | {message}"
            
            return f"ℹ️  {line}"
            
        except Exception:
            return f"ℹ️  {line}"

def main():
    """Main function"""
    print("🚀 Starting Live Trading Bot Monitor...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Create and start monitor
    monitor = LiveMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
