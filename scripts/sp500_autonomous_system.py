#!/usr/bin/env python3
"""
🤖 S&P 500 Autonomous System
Fully automated S&P 500 management with no user interaction required
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import time
import schedule
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from src.sp500_manager import SP500Manager
from src.hybrid_ai_engine import HybridAIEngine
from utils.logger import trading_logger
from config import config

class SP500AutonomousSystem:
    """Fully autonomous S&P 500 management system"""
    
    def __init__(self):
        self.sp500_manager = SP500Manager()
        self.ai_engine = HybridAIEngine()
        
        # Autonomous configuration
        self.auto_data_collection = True
        self.auto_training = True
        self.auto_cleanup = True
        self.auto_trading = True
        
        # Schedule configuration
        self.data_collection_interval = 6  # hours
        self.training_interval = 24  # hours
        self.cleanup_interval = 24  # hours
        self.constituent_check_interval = 6  # hours
        
        # Performance tracking
        self.system_status = {
            'last_data_collection': None,
            'last_training': None,
            'last_cleanup': None,
            'last_constituent_update': None,
            'total_stocks_processed': 0,
            'total_models_trained': 0,
            'system_uptime': datetime.now()
        }
        
    def start_autonomous_system(self):
        """Start the fully autonomous S&P 500 system"""
        print("🤖 S&P 500 Autonomous System Starting...")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        print()
        
        # Initial system setup
        self._initial_setup()
        
        # Schedule autonomous tasks
        self._setup_schedule()
        
        print("✅ Autonomous system initialized successfully!")
        print("🔄 Running scheduled tasks...")
        print("Press Ctrl+C to stop")
        print()
        
        # Keep system running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Autonomous system stopped by user")
            self._shutdown_system()
    
    def _initial_setup(self):
        """Initial system setup"""
        print("🔧 Performing initial setup...")
        
        # Step 1: Update S&P 500 constituents
        print("   📊 Updating S&P 500 constituents...")
        try:
            update_result = self.sp500_manager.run_full_update()
            print(f"   ✅ Updated {update_result['update_result']['total_stocks']} stocks")
            self.system_status['last_constituent_update'] = datetime.now()
        except Exception as e:
            print(f"   ❌ Constituent update failed: {e}")
        
        # Step 2: Initial data collection
        if self.auto_data_collection:
            print("   📥 Starting initial data collection...")
            try:
                self._autonomous_data_collection()
            except Exception as e:
                print(f"   ❌ Initial data collection failed: {e}")
        
        # Step 3: Initial training
        if self.auto_training:
            print("   🤖 Starting initial model training...")
            try:
                self._autonomous_training()
            except Exception as e:
                print(f"   ❌ Initial training failed: {e}")
        
        print("   ✅ Initial setup completed")
        print()
    
    def _setup_schedule(self):
        """Setup autonomous schedule"""
        # Data collection every 6 hours
        schedule.every(self.data_collection_interval).hours.do(self._autonomous_data_collection)
        
        # Training every 24 hours
        schedule.every(self.training_interval).hours.do(self._autonomous_training)
        
        # Cleanup every 24 hours
        schedule.every(self.cleanup_interval).hours.do(self._autonomous_cleanup)
        
        # Constituent updates every 6 hours
        schedule.every(self.constituent_check_interval).hours.do(self._autonomous_constituent_update)
        
        # Daily system health check
        schedule.every().day.at("02:00").do(self._daily_health_check)
        
        # Weekly full system update
        schedule.every().monday.at("01:00").do(self._weekly_full_update)
        
        print("📅 Scheduled tasks:")
        print(f"   📥 Data collection: every {self.data_collection_interval} hours")
        print(f"   🤖 Model training: every {self.training_interval} hours")
        print(f"   🗑️ Data cleanup: every {self.cleanup_interval} hours")
        print(f"   📊 Constituent updates: every {self.constituent_check_interval} hours")
        print(f"   🏥 Health check: daily at 02:00")
        print(f"   🔄 Full update: weekly on Monday at 01:00")
        print()
    
    def _autonomous_data_collection(self):
        """Autonomous data collection"""
        print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Starting autonomous data collection...")
        
        try:
            # Update constituents first
            update_result = self.sp500_manager.update_sp500_constituents()
            new_stocks = update_result['new_stocks']
            
            if new_stocks:
                print(f"   📈 Found {len(new_stocks)} new stocks to collect data for")
                self._collect_data_for_stocks(new_stocks)
            else:
                print("   ✅ No new stocks need data collection")
            
            self.system_status['last_data_collection'] = datetime.now()
            print(f"   ✅ Data collection completed")
            
        except Exception as e:
            print(f"   ❌ Data collection failed: {e}")
            trading_logger.error(f"Autonomous data collection failed: {e}")
    
    def _collect_data_for_stocks(self, symbols: list):
        """Collect data for specific stocks"""
        try:
            import yfinance as yf
            
            success_count = 0
            for symbol in symbols:
                try:
                    # Collect 3 years of daily data
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=1095)
                    
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(
                        start=start_date,
                        end=end_date,
                        interval='1d',
                        auto_adjust=True
                    )
                    
                    if not data.empty:
                        # Save data
                        data_dir = "data/sp500/historical"
                        os.makedirs(data_dir, exist_ok=True)
                        
                        data = data.reset_index()
                        data.columns = [col.lower() for col in data.columns]
                        data['symbol'] = symbol
                        data['timeframe'] = '1d'
                        
                        filename = f"{data_dir}/{symbol}_1d_data.csv"
                        data.to_csv(filename, index=False)
                        
                        success_count += 1
                        self.system_status['total_stocks_processed'] += 1
                        
                except Exception as e:
                    trading_logger.warning(f"Failed to collect data for {symbol}: {e}")
            
            print(f"   📊 Collected data for {success_count}/{len(symbols)} stocks")
            
        except Exception as e:
            trading_logger.error(f"Data collection for stocks failed: {e}")
    
    def _autonomous_training(self):
        """Autonomous model training"""
        print(f"🤖 [{datetime.now().strftime('%H:%M:%S')}] Starting autonomous training...")
        
        try:
            # Get training candidates
            training_candidates = self.sp500_manager.get_training_candidates()
            
            if training_candidates:
                print(f"   📊 Found {len(training_candidates)} stocks needing training")
                
                # Train in batches
                batch_size = 10
                trained_count = 0
                
                for i in range(0, len(training_candidates), batch_size):
                    batch = training_candidates[i:i + batch_size]
                    print(f"   🔄 Training batch {i//batch_size + 1}: {len(batch)} stocks")
                    
                    for symbol in batch:
                        try:
                            # Load data and train
                            data = self._load_stock_data(symbol)
                            if data is not None and len(data) > 100:
                                results = self.ai_engine.train_models(symbol, data)
                                if results:
                                    trained_count += 1
                                    self.system_status['total_models_trained'] += 1
                        except Exception as e:
                            trading_logger.warning(f"Training failed for {symbol}: {e}")
                
                print(f"   ✅ Trained {trained_count}/{len(training_candidates)} models")
            else:
                print("   ✅ No stocks need training")
            
            self.system_status['last_training'] = datetime.now()
            print(f"   ✅ Training completed")
            
        except Exception as e:
            print(f"   ❌ Training failed: {e}")
            trading_logger.error(f"Autonomous training failed: {e}")
    
    def _load_stock_data(self, symbol: str):
        """Load stock data for training"""
        try:
            filename = f"data/sp500/historical/{symbol}_1d_data.csv"
            if os.path.exists(filename):
                data = pd.read_csv(filename)
                
                # Convert timestamp
                if 'date' in data.columns:
                    data['date'] = pd.to_datetime(data['date'])
                    data = data.set_index('date')
                elif 'datetime' in data.columns:
                    data['datetime'] = pd.to_datetime(data['datetime'])
                    data = data.set_index('datetime')
                
                return data
            return None
        except Exception as e:
            trading_logger.error(f"Failed to load data for {symbol}: {e}")
            return None
    
    def _autonomous_cleanup(self):
        """Autonomous data cleanup"""
        print(f"🗑️ [{datetime.now().strftime('%H:%M:%S')}] Starting autonomous cleanup...")
        
        try:
            # Clean up delisted stock data
            self.sp500_manager.cleanup_delisted_data()
            
            self.system_status['last_cleanup'] = datetime.now()
            print(f"   ✅ Cleanup completed")
            
        except Exception as e:
            print(f"   ❌ Cleanup failed: {e}")
            trading_logger.error(f"Autonomous cleanup failed: {e}")
    
    def _autonomous_constituent_update(self):
        """Autonomous constituent updates"""
        print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Checking S&P 500 constituents...")
        
        try:
            update_result = self.sp500_manager.update_sp500_constituents()
            
            if update_result['new_count'] > 0 or update_result['removed_count'] > 0:
                print(f"   📈 Changes detected: {update_result['new_count']} new, {update_result['removed_count']} removed")
            else:
                print("   ✅ No changes detected")
            
            self.system_status['last_constituent_update'] = datetime.now()
            
        except Exception as e:
            print(f"   ❌ Constituent update failed: {e}")
            trading_logger.error(f"Autonomous constituent update failed: {e}")
    
    def _daily_health_check(self):
        """Daily system health check"""
        print(f"🏥 [{datetime.now().strftime('%H:%M:%S')}] Running daily health check...")
        
        try:
            # Check system status
            status = self.get_system_status()
            
            # Log health metrics
            trading_logger.info("Daily health check", **status)
            
            print(f"   📊 System Status:")
            print(f"      Total stocks processed: {status['total_stocks_processed']}")
            print(f"      Total models trained: {status['total_models_trained']}")
            print(f"      S&P 500 stocks: {status['sp500_stocks_count']}")
            print(f"      System uptime: {status['system_uptime_hours']:.1f} hours")
            
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            trading_logger.error(f"Daily health check failed: {e}")
    
    def _weekly_full_update(self):
        """Weekly full system update"""
        print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Running weekly full update...")
        
        try:
            # Full S&P 500 update
            update_result = self.sp500_manager.run_full_update()
            
            # Recalculate performance rankings
            self.sp500_manager._calculate_performance_ranking()
            
            print(f"   ✅ Weekly update completed: {update_result['update_result']['total_stocks']} stocks")
            
        except Exception as e:
            print(f"   ❌ Weekly update failed: {e}")
            trading_logger.error(f"Weekly full update failed: {e}")
    
    def _shutdown_system(self):
        """Graceful system shutdown"""
        print("\n🛑 Shutting down autonomous system...")
        
        try:
            # Save final status
            final_status = self.get_system_status()
            trading_logger.info("System shutdown", **final_status)
            
            print("✅ System shutdown completed")
            
        except Exception as e:
            print(f"❌ Shutdown error: {e}")
    
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            sp500_status = self.sp500_manager.get_status_report()
            ai_status = self.ai_engine.get_performance_summary()
            
            uptime = datetime.now() - self.system_status['system_uptime']
            
            return {
                'system_name': 'S&P 500 Autonomous System',
                'status': 'running',
                'uptime_hours': uptime.total_seconds() / 3600,
                'total_stocks_processed': self.system_status['total_stocks_processed'],
                'total_models_trained': self.system_status['total_models_trained'],
                'sp500_stocks_count': sp500_status['current_stocks_count'],
                'ai_engine_status': ai_status['engine_name'],
                'gpu_available': ai_status['hardware_status']['gpu_available'],
                'npu_available': ai_status['hardware_status']['npu_available'],
                'last_data_collection': self.system_status['last_data_collection'],
                'last_training': self.system_status['last_training'],
                'last_cleanup': self.system_status['last_cleanup'],
                'last_constituent_update': self.system_status['last_constituent_update'],
                'scheduled_tasks': len(schedule.jobs),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            trading_logger.error(f"Failed to get system status: {e}")
            return {}

def main():
    """Main function"""
    print("🤖 S&P 500 Autonomous System")
    print("=" * 60)
    
    # Create and start autonomous system
    autonomous_system = SP500AutonomousSystem()
    autonomous_system.start_autonomous_system()

if __name__ == "__main__":
    main()
