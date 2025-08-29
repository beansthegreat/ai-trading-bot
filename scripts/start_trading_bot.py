#!/usr/bin/env python3
"""
Startup script for the timezone-aware trading bot
Automatically starts trading based on NYSE opening times relative to Netherlands timezone
"""

import sys
import os
from datetime import datetime
import pytz

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_bot import TradingBot
from utils.logger import trading_logger

def main():
    """Main startup function"""
    print("🚀 Starting Timezone-Aware Trading Bot")
    print("=" * 50)
    
    # Show timezone information
    netherlands_tz = pytz.timezone('Europe/Amsterdam')
    nyse_tz = pytz.timezone('America/New_York')
    
    now_nl = datetime.now(netherlands_tz)
    now_nyse = datetime.now(nyse_tz)
    
    print(f"🌍 Timezone Information:")
    print(f"   Netherlands: {now_nl.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   NYSE:        {now_nyse.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    print(f"📅 NYSE Trading Hours (Netherlands Time):")
    print(f"   Open:  15:30 (Netherlands) / 09:30 (NYSE ET)")
    print(f"   Close: 22:00 (Netherlands) / 16:00 (NYSE ET)")
    print()
    
    # Create and start the trading bot
    try:
        bot = TradingBot()
        
        print("✅ Trading bot created successfully")
        print("🔄 Starting automated trading...")
        print()
        print("📊 The bot will:")
        print("   • Automatically start trading at NYSE open (15:30 Netherlands time)")
        print("   • Run trading cycles every 5 minutes during market hours")
        print("   • Apply momentum strategy with technical indicators")
        print("   • Implement comprehensive risk management")
        print("   • Stop trading at NYSE close (22:00 Netherlands time)")
        print()
        print("🛑 Press Ctrl+C to stop the bot")
        print("=" * 50)
        
        # Start the bot
        bot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Trading bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting trading bot: {e}")
        trading_logger.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
