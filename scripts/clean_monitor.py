#!/usr/bin/env python3
"""
Clean Live Monitor - Simple and Easy to Read
Shows only the most important information
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

class CleanMonitor:
    """Clean and simple monitoring for the trading bot"""
    
    def __init__(self):
        self.running = False
        self.last_log_position = 0
        
    def start_monitoring(self):
        """Start clean monitoring"""
        self.running = True
        print("🤖 Trading Bot Monitor")
        print("=" * 40)
        
        # Start log monitoring in a separate thread
        log_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        log_thread.start()
        
        try:
            while self.running:
                self._display_clean_status()
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped")
            self.running = False
    
    def _display_clean_status(self):
        """Display clean, simple status"""
        try:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🤖 Trading Bot Monitor")
            print("=" * 40)
            print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            # Account Info
            account = alpaca_client.get_account()
            print("💰 Account:")
            print(f"   Cash: ${account['cash']:.2f}")
            print(f"   Total: ${account['portfolio_value']:.2f}")
            print()
            
            # Market Status
            market_open = alpaca_client.is_market_open()
            print("🏛️  Market:")
            print(f"   {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
            print()
            
            # Positions
            positions = alpaca_client.get_positions()
            print("📈 Positions:")
            if positions:
                for pos in positions:
                    pnl_color = "🟢" if pos['unrealized_pl'] >= 0 else "🔴"
                    print(f"   {pos['symbol']}: {pos['quantity']:.2f} shares")
                    print(f"      {pnl_color} P&L: ${pos['unrealized_pl']:.2f}")
            else:
                print("   No positions")
            print()
            
            # Recent Trades
            try:
                orders = alpaca_client.get_orders(status='filled', limit=3)
                print("📋 Recent Trades:")
                if orders:
                    for order in orders:
                        time_str = order['created_at'].strftime('%H:%M') if hasattr(order['created_at'], 'strftime') else 'N/A'
                        side_emoji = "🟢" if order['side'] == 'buy' else "🔴"
                        print(f"   {time_str} {side_emoji} {order['side'].upper()} {order.get('quantity', 0):.2f} {order['symbol']}")
                else:
                    print("   No recent trades")
            except:
                print("   No recent trades")
            print()
            
            # Bot Status
            print("🤖 Bot:")
            print("   🟢 RUNNING")
            print("   Strategy: Adaptive Intelligence")
            print(f"   Checking: {len(config.SYMBOLS)} stocks")
            print()
            
            # Buy Signals
            self._show_buy_signals()
            
            print("📊 Live Updates:")
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _show_buy_signals(self):
        """Show current buy signals"""
        try:
            from strategies.adaptive_strategy import StrategyIntelligence
            import yfinance as yf
            
            print("🔍 Buy Signals:")
            
            # Suppress yfinance output
            import warnings
            warnings.filterwarnings('ignore')
            
            strategy = StrategyIntelligence()
            buy_count = 0
            
            # Quick check of first 3 stocks
            for symbol in config.SYMBOLS[:3]:
                try:
                    # Suppress yfinance download output
                    import io
                    import sys
                    old_stdout = sys.stdout
                    sys.stdout = io.StringIO()
                    
                    df = yf.download(symbol, period='1d', interval='1m', progress=False)
                    
                    # Restore stdout
                    sys.stdout = old_stdout
                    
                    df.columns = df.columns.get_level_values(0)
                    df.columns = df.columns.str.lower()
                    df['symbol'] = symbol
                    
                    result = strategy.analyze(df)
                    
                    if result['signal'] == 'buy':
                        buy_count += 1
                        price = df['close'].iloc[-1] if len(df) > 0 else 0
                        print(f"   🟢 {symbol}: ${price:.2f}")
                        
                except:
                    continue
            
            if buy_count == 0:
                print("   ⚪ None found")
            print()
                
        except Exception as e:
            print("   ❌ Error checking signals")
            print()
    
    def _monitor_logs(self):
        """Monitor log file for new entries"""
        log_file = config.LOG_FILE
        
        while self.running:
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        current_position = len(lines)
                        
                        if current_position > self.last_log_position:
                            new_lines = lines[self.last_log_position:]
                            for line in new_lines:
                                formatted = self._format_log_line(line.strip())
                                if formatted:
                                    print(formatted)
                            
                            self.last_log_position = current_position
                
                time.sleep(2)
                
            except Exception:
                time.sleep(5)
    
    def _format_log_line(self, line):
        """Format log line simply"""
        if not line or line.startswith('{'):
            return None
            
        try:
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) >= 3:
                    timestamp = parts[0].strip()
                    level = parts[1].strip()
                    message = parts[2].strip()
                    
                    # Only show important messages
                    if 'BUY' in message or 'SELL' in message:
                        return f"💰 {timestamp} | {message}"
                    elif 'ERROR' in level:
                        return f"🔴 {timestamp} | {message}"
                    elif 'SUCCESS' in level:
                        return f"🟢 {timestamp} | {message}"
                    # Skip most other messages to keep it clean
            
            return None
            
        except Exception:
            return None

def main():
    """Main function"""
    print("🚀 Starting Clean Monitor...")
    print("Press Ctrl+C to stop")
    print()
    
    load_dotenv()
    
    monitor = CleanMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
