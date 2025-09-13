#!/usr/bin/env python3
"""
🚀 Start Integrated Trading Bot
One-click startup for trading + real-time training system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrated_trading_bot import IntegratedTradingBot

def main():
    """Start the integrated trading system"""
    print("🚀 Starting Integrated Trading Bot with Real-Time Training")
    print("=" * 70)
    print()
    print("This system will:")
    print("  📈 Trade S&P 500 stocks in real-time")
    print("  🔄 Continuously train AI models on live data")
    print("  📊 Monitor performance and adapt to market changes")
    print("  🤖 Use hybrid GPU+NPU acceleration for speed")
    print("  📱 Update models every 15 minutes with new data")
    print()
    print("Key Features:")
    print("  ✅ Real-time data collection every 5 minutes")
    print("  ✅ Model training every 15 minutes")
    print("  ✅ Live predictions using latest models")
    print("  ✅ Automatic adaptation to market changes")
    print("  ✅ Performance monitoring and reporting")
    print()
    print("Press Ctrl+C to stop the system")
    print()
    
    # Start the integrated system
    integrated_bot = IntegratedTradingBot()
    integrated_bot.start_integrated_trading()

if __name__ == "__main__":
    main()
