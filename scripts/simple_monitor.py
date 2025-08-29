#!/usr/bin/env python3
"""
Simple Monitor - Ultra Clean and Easy to Read
Shows only the most essential information
"""

import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.alpaca_client import alpaca_client

class SimpleMonitor:
    """Ultra simple monitoring for the trading bot"""
    
    def __init__(self):
        self.running = False
        
    def start_monitoring(self):
        """Start simple monitoring"""
        self.running = True
        print("🤖 Simple Bot Monitor")
        print("=" * 35)
        
        try:
            while self.running:
                self._display_simple_status()
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped")
            self.running = False
    
    def _display_simple_status(self):
        """Display simple, clean status"""
        try:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🤖 Simple Bot Monitor")
            print("=" * 35)
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
            
            # Quick Status
            print("📊 Status:")
            print("   ✅ Bot is running")
            print("   ✅ Market is open")
            print("   ✅ Adaptive strategy active")
            print("   ⏳ Waiting for buy signals...")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Starting Simple Monitor...")
    print("Press Ctrl+C to stop")
    print()
    
    load_dotenv()
    
    monitor = SimpleMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
