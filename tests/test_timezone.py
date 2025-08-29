#!/usr/bin/env python3
"""
Test script to verify timezone-aware scheduling for Netherlands timezone
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_bot import TradingBot

def test_timezone_scheduling():
    """Test timezone-aware scheduling"""
    print("🌍 Testing Timezone-Aware Scheduling")
    print("=" * 50)
    
    # Create bot instance
    bot = TradingBot()
    
    # Get NYSE times in Netherlands timezone
    nyse_open_nl, nyse_close_nl = bot._get_nyse_times_in_netherlands()
    
    print(f"📅 NYSE Trading Hours (Netherlands Time):")
    print(f"   Open:  {nyse_open_nl.strftime('%H:%M')} (Netherlands)")
    print(f"   Close: {nyse_close_nl.strftime('%H:%M')} (Netherlands)")
    print(f"   Open:  09:30 (NYSE ET)")
    print(f"   Close: 16:00 (NYSE ET)")
    print()
    
    # Show current times
    now_nl = datetime.now(bot.netherlands_tz)
    now_nyse = datetime.now(bot.nyse_tz)
    
    print(f"🕐 Current Times:")
    print(f"   Netherlands: {now_nl.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   NYSE:        {now_nyse.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    # Test next trading session info
    print("📊 Next Trading Session Info:")
    bot._show_next_trading_session()
    print()
    
    # Test status with timezone info
    print("📈 Bot Status with Timezone Info:")
    status = bot.get_status()
    print(f"   Running: {status['is_running']}")
    print(f"   Strategy: {status['strategy']}")
    print(f"   Symbols: {', '.join(status['symbols'])}")
    print(f"   Netherlands Time: {status['timezone_info']['netherlands_time']}")
    print(f"   NYSE Time: {status['timezone_info']['nyse_time']}")
    print()
    
    # Test scheduling
    print("⏰ Testing Schedule Creation:")
    bot._schedule_jobs_timezone_aware()
    print("   ✅ Timezone-aware schedules created")
    print()
    
    print("🎉 Timezone test completed successfully!")

if __name__ == "__main__":
    test_timezone_scheduling()
