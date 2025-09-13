#!/usr/bin/env python3
"""
📊 S&P 500 Monitoring System
Monitors S&P 500 changes and manages the trading bot accordingly
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

class SP500Monitor:
    """Monitors S&P 500 changes and manages trading operations"""
    
    def __init__(self):
        self.sp500_manager = SP500Manager()
        self.ai_engine = HybridAIEngine()
        
        # Monitoring configuration
        self.check_interval_hours = 6  # Check every 6 hours
        self.auto_retrain = True
        self.auto_cleanup = True
        self.auto_data_collection = True
        
        # Performance tracking
        self.monitoring_history = []
        self.performance_metrics = {}
        
    def start_monitoring(self):
        """Start continuous S&P 500 monitoring"""
        trading_logger.info("Starting S&P 500 monitoring system...")
        
        print("📊 S&P 500 Monitoring System Started")
        print("=" * 50)
        print(f"Check interval: {self.check_interval_hours} hours")
        print(f"Auto retrain: {self.auto_retrain}")
        print(f"Auto cleanup: {self.auto_cleanup}")
        print(f"Auto data collection: {self.auto_data_collection}")
        print()
        
        # Schedule monitoring tasks
        schedule.every(self.check_interval_hours).hours.do(self._monitoring_cycle)
        schedule.every().day.at("09:00").do(self._daily_update)
        schedule.every().monday.at("08:00").do(self._weekly_retrain)
        
        # Initial check
        self._monitoring_cycle()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            trading_logger.info("S&P 500 monitoring stopped by user")
    
    def _monitoring_cycle(self):
        """Main monitoring cycle"""
        trading_logger.info("Running S&P 500 monitoring cycle...")
        
        start_time = time.time()
        
        try:
            # Step 1: Update S&P 500 constituents
            print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Checking S&P 500 constituents...")
            update_result = self.sp500_manager.update_sp500_constituents()
            
            # Step 2: Handle changes
            if update_result['new_count'] > 0 or update_result['removed_count'] > 0:
                print(f"   📈 Changes detected: {update_result['new_count']} new, {update_result['removed_count']} removed")
                self._handle_constituent_changes(update_result)
            else:
                print("   ✅ No changes detected")
            
            # Step 3: Check training needs
            training_candidates = self.sp500_manager.get_training_candidates()
            if training_candidates:
                print(f"   🤖 {len(training_candidates)} stocks need training")
                if self.auto_retrain:
                    self._auto_retrain_models(training_candidates)
            
            # Step 4: Performance monitoring
            self._monitor_performance()
            
            # Step 5: Log monitoring cycle
            cycle_time = time.time() - start_time
            self._log_monitoring_cycle(update_result, cycle_time)
            
            print(f"   ✅ Monitoring cycle completed in {cycle_time:.1f}s")
            
        except Exception as e:
            trading_logger.error(f"Monitoring cycle failed: {e}")
            print(f"   ❌ Monitoring cycle failed: {e}")
    
    def _handle_constituent_changes(self, update_result: Dict[str, Any]):
        """Handle S&P 500 constituent changes"""
        try:
            # Handle new stocks
            if update_result['new_count'] > 0:
                print(f"   📊 Processing {update_result['new_count']} new stocks...")
                self._process_new_stocks(update_result['new_stocks'])
            
            # Handle removed stocks
            if update_result['removed_count'] > 0:
                print(f"   🗑️ Processing {update_result['removed_count']} removed stocks...")
                self._process_removed_stocks(update_result['removed_stocks'])
            
        except Exception as e:
            trading_logger.error(f"Failed to handle constituent changes: {e}")
    
    def _process_new_stocks(self, new_stocks: List[str]):
        """Process newly added S&P 500 stocks"""
        try:
            if self.auto_data_collection:
                # Collect data for new stocks
                print(f"      📥 Collecting data for new stocks...")
                # This would integrate with the data collector
                
            if self.auto_retrain:
                # Train models for new stocks
                print(f"      🤖 Training models for new stocks...")
                # This would integrate with the training system
                
        except Exception as e:
            trading_logger.error(f"Failed to process new stocks: {e}")
    
    def _process_removed_stocks(self, removed_stocks: List[str]):
        """Process removed S&P 500 stocks"""
        try:
            if self.auto_cleanup:
                # Clean up data for removed stocks
                print(f"      🗑️ Cleaning up data for removed stocks...")
                self.sp500_manager.cleanup_delisted_data()
                
        except Exception as e:
            trading_logger.error(f"Failed to process removed stocks: {e}")
    
    def _auto_retrain_models(self, training_candidates: List[str]):
        """Automatically retrain models"""
        try:
            # Limit concurrent training
            max_concurrent = 10
            candidates = training_candidates[:max_concurrent]
            
            print(f"      🤖 Auto-retraining {len(candidates)} models...")
            
            # This would integrate with the training system
            # For now, just log the candidates
            trading_logger.info(f"Auto-retraining candidates: {candidates}")
            
        except Exception as e:
            trading_logger.error(f"Auto-retrain failed: {e}")
    
    def _monitor_performance(self):
        """Monitor trading performance"""
        try:
            # Get performance metrics
            performance_ranking = self.sp500_manager.get_performance_ranking()
            
            # Update performance metrics
            self.performance_metrics = {
                'total_stocks': len(performance_ranking),
                'top_performers': list(performance_ranking.keys())[:10],
                'last_updated': datetime.now().isoformat()
            }
            
            # Log performance summary
            if len(performance_ranking) > 0:
                top_5 = list(performance_ranking.keys())[:5]
                print(f"   📈 Top performers: {', '.join(top_5)}")
            
        except Exception as e:
            trading_logger.error(f"Performance monitoring failed: {e}")
    
    def _daily_update(self):
        """Daily update routine"""
        trading_logger.info("Running daily S&P 500 update...")
        
        print(f"🌅 [{datetime.now().strftime('%H:%M:%S')}] Daily update...")
        
        try:
            # Full update cycle
            update_result = self.sp500_manager.run_full_update()
            
            # Performance ranking update
            self.sp500_manager._calculate_performance_ranking()
            
            print(f"   ✅ Daily update completed: {update_result['update_result']['total_stocks']} stocks")
            
        except Exception as e:
            trading_logger.error(f"Daily update failed: {e}")
            print(f"   ❌ Daily update failed: {e}")
    
    def _weekly_retrain(self):
        """Weekly retraining routine"""
        trading_logger.info("Running weekly S&P 500 retraining...")
        
        print(f"📅 [{datetime.now().strftime('%H:%M:%S')}] Weekly retraining...")
        
        try:
            # Get all training candidates
            training_candidates = self.sp500_manager.get_training_candidates()
            
            if training_candidates:
                print(f"   🤖 Retraining {len(training_candidates)} models...")
                # This would integrate with the training system
            else:
                print("   ✅ No models need retraining")
            
        except Exception as e:
            trading_logger.error(f"Weekly retrain failed: {e}")
            print(f"   ❌ Weekly retrain failed: {e}")
    
    def _log_monitoring_cycle(self, update_result: Dict[str, Any], cycle_time: float):
        """Log monitoring cycle results"""
        try:
            cycle_log = {
                'timestamp': datetime.now().isoformat(),
                'cycle_time': cycle_time,
                'total_stocks': update_result['total_stocks'],
                'new_stocks': update_result['new_count'],
                'removed_stocks': update_result['removed_count'],
                'performance_metrics': self.performance_metrics
            }
            
            self.monitoring_history.append(cycle_log)
            
            # Keep only last 100 cycles
            self.monitoring_history = self.monitoring_history[-100:]
            
        except Exception as e:
            trading_logger.error(f"Failed to log monitoring cycle: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status report"""
        try:
            return {
                'monitor_name': 'S&P 500 Monitor',
                'check_interval_hours': self.check_interval_hours,
                'auto_retrain': self.auto_retrain,
                'auto_cleanup': self.auto_cleanup,
                'auto_data_collection': self.auto_data_collection,
                'sp500_status': self.sp500_manager.get_status_report(),
                'ai_engine_status': self.ai_engine.get_performance_summary(),
                'performance_metrics': self.performance_metrics,
                'monitoring_history_count': len(self.monitoring_history),
                'last_cycle': self.monitoring_history[-1] if self.monitoring_history else None
            }
        except Exception as e:
            trading_logger.error(f"Failed to get monitoring status: {e}")
            return {}

def main():
    """Main function"""
    print("📊 S&P 500 Monitoring System")
    print("=" * 50)
    
    monitor = SP500Monitor()
    
    while True:
        print("\nSelect operation:")
        print("1. Start continuous monitoring")
        print("2. Run single monitoring cycle")
        print("3. Show monitoring status")
        print("4. Configure monitoring settings")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            monitor.start_monitoring()
        elif choice == '2':
            monitor._monitoring_cycle()
        elif choice == '3':
            status = monitor.get_monitoring_status()
            print(f"\n📊 Monitoring Status:")
            print(f"   Check interval: {status['check_interval_hours']} hours")
            print(f"   Auto retrain: {status['auto_retrain']}")
            print(f"   Auto cleanup: {status['auto_cleanup']}")
            print(f"   S&P 500 stocks: {status['sp500_status']['current_stocks_count']}")
            print(f"   AI Engine: {status['ai_engine_status']['engine_name']}")
            print(f"   Monitoring cycles: {status['monitoring_history_count']}")
        elif choice == '4':
            print("\n⚙️ Monitoring Configuration:")
            print(f"   Current check interval: {monitor.check_interval_hours} hours")
            new_interval = input("   New check interval (hours): ").strip()
            if new_interval.isdigit():
                monitor.check_interval_hours = int(new_interval)
                print(f"   ✅ Check interval updated to {monitor.check_interval_hours} hours")
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
