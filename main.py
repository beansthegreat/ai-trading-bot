#!/usr/bin/env python3
"""
🚀 Python Trading Bot - Main Entry Point
Ultra-Intelligent Micro-Movement Trading System
"""

import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the trading bot"""
    print("🚀 Python Trading Bot - Ultra-Intelligent Micro-Movement System")
    print("=" * 60)
    print()
    print("🎯 Features:")
    print("   ✅ Micro-movement detection (0.001% sensitivity)")
    print("   ✅ Adaptive volatility thresholds")
    print("   ✅ API rate limiting (150/200 req/min)")
    print("   ✅ Dollar amount trading")
    print("   ✅ Wash sale prevention")
    print("   ✅ Timezone-aware scheduling")
    print("   ✅ Ultra-fast response (every 2 minutes)")
    print()
    
    # Import and start the trading bot
    from src.trading_bot import TradingBot
    
    try:
        # Create and start the bot
        bot = TradingBot()
        bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Start the bot
    main()
