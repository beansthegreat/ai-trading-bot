#!/usr/bin/env python3
"""
🚀 S&P 500 Trading Bot Launcher
Start the trading bot with S&P 500 dynamic stock management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from src.sp500_manager import SP500Manager
from src.hybrid_ai_engine import HybridAIEngine
from src.trading_bot import TradingBot
from utils.logger import trading_logger
from config import config

class SP500TradingBot:
    """S&P 500 enabled trading bot"""
    
    def __init__(self):
        self.sp500_manager = SP500Manager()
        self.ai_engine = HybridAIEngine()
        self.trading_bot = None
        
        # S&P 500 configuration
        self.use_sp500_mode = config.USE_SP500_MODE
        self.top_performers_count = config.SP500_TOP_PERFORMERS
        
    def initialize(self):
        """Initialize the S&P 500 trading bot"""
        print("🚀 Initializing S&P 500 Trading Bot")
        print("=" * 50)
        
        # Step 1: Initialize S&P 500 manager
        print("📊 Initializing S&P 500 Manager...")
        try:
            # Update S&P 500 constituents
            update_result = self.sp500_manager.run_full_update()
            print(f"   ✅ S&P 500 updated: {update_result['update_result']['total_stocks']} stocks")
            print(f"   📈 New stocks: {update_result['update_result']['new_count']}")
            print(f"   🗑️ Removed stocks: {update_result['update_result']['removed_count']}")
        except Exception as e:
            print(f"   ❌ S&P 500 initialization failed: {e}")
            return False
        
        # Step 2: Initialize AI engine
        print("\n🤖 Initializing Hybrid AI Engine...")
        try:
            ai_status = self.ai_engine.get_performance_summary()
            print(f"   ✅ AI Engine: {ai_status['engine_name']}")
            print(f"   🖥️ GPU Available: {ai_status['hardware_status']['gpu_available']}")
            print(f"   🧠 NPU Available: {ai_status['hardware_status']['npu_available']}")
            print(f"   🔄 Hybrid Mode: {ai_status['hardware_status']['hybrid_mode']}")
        except Exception as e:
            print(f"   ❌ AI Engine initialization failed: {e}")
            return False
        
        # Step 3: Get trading symbols
        print("\n📈 Setting up trading symbols...")
        try:
            if self.use_sp500_mode:
                # Get top performing S&P 500 stocks
                top_performers = self.sp500_manager.get_top_performers(self.top_performers_count)
                trading_symbols = list(top_performers)
                print(f"   ✅ Using top {len(trading_symbols)} S&P 500 performers")
                print(f"   📊 Top 10: {', '.join(trading_symbols[:10])}")
            else:
                # Use configured symbols
                trading_symbols = config.SYMBOLS
                print(f"   ✅ Using configured symbols: {', '.join(trading_symbols)}")
        except Exception as e:
            print(f"   ❌ Symbol setup failed: {e}")
            return False
        
        # Step 4: Initialize trading bot
        print("\n🎯 Initializing Trading Bot...")
        try:
            self.trading_bot = TradingBot(ai_engine=self.ai_engine)
            print(f"   ✅ Trading bot initialized")
        except Exception as e:
            print(f"   ❌ Trading bot initialization failed: {e}")
            return False
        
        print("\n✅ S&P 500 Trading Bot initialized successfully!")
        return True
    
    def start_trading(self):
        """Start trading operations"""
        if not self.trading_bot:
            print("❌ Trading bot not initialized. Please run initialize() first.")
            return
        
        print("\n🎯 Starting S&P 500 Trading Operations")
        print("=" * 50)
        print("Press Ctrl+C to stop")
        print()
        
        try:
            # Start trading
            self.trading_bot.start_trading()
        except KeyboardInterrupt:
            print("\n🛑 Trading stopped by user")
            trading_logger.info("S&P 500 trading stopped by user")
        except Exception as e:
            print(f"\n❌ Trading error: {e}")
            trading_logger.error(f"S&P 500 trading error: {e}")
    
    def get_status(self):
        """Get comprehensive status report"""
        try:
            sp500_status = self.sp500_manager.get_status_report()
            ai_status = self.ai_engine.get_performance_summary()
            
            return {
                'bot_name': 'S&P 500 Trading Bot',
                'sp500_mode': self.use_sp500_mode,
                'top_performers_count': self.top_performers_count,
                'sp500_status': sp500_status,
                'ai_engine_status': ai_status,
                'trading_bot_initialized': self.trading_bot is not None,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            trading_logger.error(f"Failed to get status: {e}")
            return {}

def main():
    """Main function"""
    print("🚀 S&P 500 Trading Bot")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Validate configuration
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Initialize bot
    bot = SP500TradingBot()
    
    if not bot.initialize():
        print("❌ Failed to initialize S&P 500 trading bot")
        return 1
    
    # Show status
    status = bot.get_status()
    print(f"\n📊 Bot Status:")
    print(f"   S&P 500 Mode: {status['sp500_mode']}")
    print(f"   Top Performers: {status['top_performers_count']}")
    print(f"   S&P 500 Stocks: {status['sp500_status']['current_stocks_count']}")
    print(f"   AI Engine: {status['ai_engine_status']['engine_name']}")
    print(f"   GPU Available: {status['ai_engine_status']['hardware_status']['gpu_available']}")
    print(f"   NPU Available: {status['ai_engine_status']['hardware_status']['npu_available']}")
    print()
    
    # Start trading
    bot.start_trading()
    
    print("✅ S&P 500 trading bot stopped successfully")
    return 0

if __name__ == "__main__":
    exit(main())
