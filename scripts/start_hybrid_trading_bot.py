#!/usr/bin/env python3
"""
🚀 Hybrid Trading Bot Launcher
Start the trading bot with GPU + NPU acceleration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from src.hybrid_ai_engine import HybridAIEngine
from src.trading_bot import TradingBot
from utils.logger import trading_logger
from config import config

def main():
    """Start the hybrid trading bot"""
    print("🚀 Starting Hybrid AI Trading Bot")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Validate configuration
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Initialize hybrid AI engine
    print("🤖 Initializing Hybrid AI Engine...")
    try:
        ai_engine = HybridAIEngine()
        
        # Display hardware status
        performance_summary = ai_engine.get_performance_summary()
        print(f"AI Engine: {performance_summary['engine_name']}")
        print(f"GPU Available: {performance_summary['hardware_status']['gpu_available']}")
        print(f"NPU Available: {performance_summary['hardware_status']['npu_available']}")
        print(f"Hybrid Mode: {performance_summary['hardware_status']['hybrid_mode']}")
        print()
        
        if not performance_summary['hardware_status']['gpu_available'] and not performance_summary['hardware_status']['npu_available']:
            print("⚠️ Warning: No GPU or NPU acceleration available. Running in CPU-only mode.")
            print()
        
    except Exception as e:
        print(f"❌ Failed to initialize AI engine: {e}")
        trading_logger.error(f"AI engine initialization failed: {e}")
        return 1
    
    # Initialize trading bot with hybrid AI engine
    print("📈 Initializing Trading Bot...")
    try:
        trading_bot = TradingBot(ai_engine=ai_engine)
        print("✅ Trading bot initialized successfully")
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize trading bot: {e}")
        trading_logger.error(f"Trading bot initialization failed: {e}")
        return 1
    
    # Start trading
    print("🎯 Starting trading operations...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        trading_bot.start_trading()
    except KeyboardInterrupt:
        print("\n🛑 Trading stopped by user")
        trading_logger.info("Trading stopped by user")
    except Exception as e:
        print(f"\n❌ Trading error: {e}")
        trading_logger.error(f"Trading error: {e}")
        return 1
    
    print("✅ Trading bot stopped successfully")
    return 0

if __name__ == "__main__":
    exit(main())
