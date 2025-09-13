#!/usr/bin/env python3
"""
🚀 Integrated Trading Bot with Real-Time Training
Trading bot that continuously trains on live data while trading
"""

import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

from src.trading_bot import TradingBot
from src.realtime_training_engine import RealTimeTrainingEngine
from src.sp500_manager import SP500Manager
from src.hybrid_ai_engine import HybridAIEngine
from src.storage_optimizer import StorageOptimizer
from utils.logger import trading_logger
from config import config

class IntegratedTradingBot:
    """Integrated trading bot with real-time training"""
    
    def __init__(self):
        self.name = "Integrated Trading Bot with Real-Time Training"
        self.description = "Trading bot that continuously trains on live data"
        
        # Core components
        self.sp500_manager = SP500Manager()
        self.ai_engine = HybridAIEngine()
        self.trading_bot = None
        self.realtime_training = None
        self.storage_optimizer = None
        
        # Trading configuration
        self.active_symbols = []
        self.trading_active = False
        self.training_active = False
        
        # Performance tracking
        self.performance_metrics = {
            'trades_executed': 0,
            'successful_trades': 0,
            'total_profit': 0.0,
            'models_updated': 0,
            'training_cycles': 0,
            'start_time': datetime.now()
        }
        
        # Initialize components
        self._initialize_components()
        
        trading_logger.info("Integrated trading bot initialized")
    
    def _initialize_components(self):
        """Initialize all components"""
        try:
        # Initialize trading bot (without ai_engine parameter)
        self.trading_bot = TradingBot()
        
        # Initialize real-time training
        self.realtime_training = RealTimeTrainingEngine(trading_bot=self)
        
        # Initialize storage optimizer
        self.storage_optimizer = StorageOptimizer()
            
            # Get active symbols
            self._update_active_symbols()
            
            trading_logger.info("Components initialized successfully")
            
        except Exception as e:
            trading_logger.error(f"Component initialization failed: {e}")
            raise
    
    def _update_active_symbols(self):
        """Update active trading symbols"""
        try:
            if config.USE_SP500_MODE:
                # Get top S&P 500 performers
                top_performers = self.sp500_manager.get_top_performers(config.SP500_TOP_PERFORMERS)
                self.active_symbols = list(top_performers)
            else:
                # Use configured symbols
                self.active_symbols = config.SYMBOLS.copy()
            
            trading_logger.info(f"Active symbols updated: {len(self.active_symbols)} symbols")
            
        except Exception as e:
            trading_logger.error(f"Failed to update active symbols: {e}")
    
    def start_integrated_trading(self):
        """Start integrated trading with real-time training"""
        print("🚀 Starting Integrated Trading Bot with Real-Time Training")
        print("=" * 70)
        print(f"Started at: {datetime.now()}")
        print()
        
        try:
            # Step 1: Start real-time training
            print("🔄 Starting real-time training engine...")
            self.realtime_training.start_realtime_training()
            self.training_active = True
            print("   ✅ Real-time training started")
            
            # Step 2: Start trading bot
            print("📈 Starting trading operations...")
            self.trading_bot.start_trading()
            self.trading_active = True
            print("   ✅ Trading operations started")
            
        # Step 3: Start monitoring thread
        print("📊 Starting performance monitoring...")
        monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        monitoring_thread.start()
        print("   ✅ Performance monitoring started")
        
        # Step 4: Start storage optimization
        print("💾 Starting storage optimization...")
        storage_thread = threading.Thread(target=self._storage_optimization_worker, daemon=True)
        storage_thread.start()
        print("   ✅ Storage optimization started")
            
            print()
            print("🎯 Integrated system is now running!")
            print("   📈 Trading: Active")
            print("   🔄 Training: Active")
            print("   📊 Monitoring: Active")
            print()
            print("Press Ctrl+C to stop")
            
            # Keep main thread alive
            try:
                while self.trading_active or self.training_active:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping integrated system...")
                self.stop_integrated_trading()
            
        except Exception as e:
            print(f"❌ Failed to start integrated trading: {e}")
            trading_logger.error(f"Integrated trading startup failed: {e}")
            self.stop_integrated_trading()
    
    def stop_integrated_trading(self):
        """Stop integrated trading system"""
        print("🛑 Stopping integrated trading system...")
        
        try:
            # Stop trading
            if self.trading_active:
                self.trading_active = False
                print("   ✅ Trading stopped")
            
            # Stop training
            if self.training_active:
                self.realtime_training.stop_realtime_training()
                self.training_active = False
                print("   ✅ Real-time training stopped")
            
            # Run final storage optimization
            if self.storage_optimizer:
                print("   💾 Running final storage optimization...")
                self.storage_optimizer.optimize_storage()
                print("   ✅ Storage optimization completed")
            
            # Save final performance report
            self._save_performance_report()
            
            print("✅ Integrated system stopped successfully")
            
        except Exception as e:
            print(f"❌ Error stopping integrated system: {e}")
            trading_logger.error(f"Integrated system shutdown error: {e}")
    
    def _monitoring_worker(self):
        """Performance monitoring worker thread"""
        trading_logger.info("Performance monitoring worker started")
        
        while self.trading_active or self.training_active:
            try:
                # Update performance metrics
                self._update_performance_metrics()
                
                # Log performance summary every hour
                if datetime.now().minute == 0:  # Every hour
                    self._log_performance_summary()
                
                # Run storage optimization every 6 hours
                if datetime.now().hour % 6 == 0 and datetime.now().minute == 0:
                    self._run_storage_optimization()
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                trading_logger.error(f"Performance monitoring error: {e}")
                time.sleep(300)
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Get training status
            training_status = self.realtime_training.get_training_status()
            
            # Update metrics
            self.performance_metrics['models_updated'] = training_status.get('training_stats', {}).get('total_trainings', 0)
            self.performance_metrics['training_cycles'] = training_status.get('training_stats', {}).get('successful_trainings', 0)
            
        except Exception as e:
            trading_logger.error(f"Failed to update performance metrics: {e}")
    
    def _log_performance_summary(self):
        """Log performance summary"""
        try:
            uptime = datetime.now() - self.performance_metrics['start_time']
            
            summary = {
                'uptime_hours': uptime.total_seconds() / 3600,
                'active_symbols': len(self.active_symbols),
                'models_updated': self.performance_metrics['models_updated'],
                'training_cycles': self.performance_metrics['training_cycles'],
                'trading_active': self.trading_active,
                'training_active': self.training_active
            }
            
            trading_logger.info("Performance summary", **summary)
            
        except Exception as e:
            trading_logger.error(f"Failed to log performance summary: {e}")
    
    def _storage_optimization_worker(self):
        """Storage optimization worker thread"""
        trading_logger.info("Storage optimization worker started")
        
        while self.trading_active or self.training_active:
            try:
                # Run storage optimization every 6 hours
                time.sleep(6 * 3600)  # 6 hours
                
                if self.trading_active or self.training_active:
                    self._run_storage_optimization()
                
            except Exception as e:
                trading_logger.error(f"Storage optimization worker error: {e}")
                time.sleep(3600)  # Wait 1 hour before retry
    
    def _run_storage_optimization(self):
        """Run storage optimization"""
        try:
            trading_logger.info("Running scheduled storage optimization...")
            
            # Analyze storage usage
            analysis = self.storage_optimizer.analyze_storage_usage()
            total_size_gb = analysis.get('total_size_gb', 0)
            
            # Check if optimization is needed
            if total_size_gb > self.storage_optimizer.max_storage_gb * 0.8:  # 80% threshold
                trading_logger.info(f"Storage usage high ({total_size_gb:.2f} GB), running optimization...")
                
                # Run optimization
                results = self.storage_optimizer.optimize_storage()
                
                trading_logger.info("Storage optimization completed", 
                                   space_saved_gb=results['total_space_saved_gb'])
            else:
                trading_logger.info(f"Storage usage normal ({total_size_gb:.2f} GB), no optimization needed")
                
        except Exception as e:
            trading_logger.error(f"Storage optimization failed: {e}")
    
    def _save_performance_report(self):
        """Save final performance report"""
        try:
            uptime = datetime.now() - self.performance_metrics['start_time']
            
            report = {
                'session_info': {
                    'start_time': self.performance_metrics['start_time'].isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'uptime_hours': uptime.total_seconds() / 3600
                },
                'performance_metrics': self.performance_metrics,
                'active_symbols': self.active_symbols,
                'training_status': self.realtime_training.get_training_status() if self.realtime_training else None,
                'ai_engine_status': self.ai_engine.get_performance_summary()
            }
            
            # Save to file
            import json
            report_file = f"logs/integrated_trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            trading_logger.info(f"Performance report saved: {report_file}")
            
        except Exception as e:
            trading_logger.error(f"Failed to save performance report: {e}")
    
    def get_integrated_status(self) -> Dict[str, Any]:
        """Get comprehensive integrated system status"""
        try:
            training_status = self.realtime_training.get_training_status() if self.realtime_training else {}
            ai_status = self.ai_engine.get_performance_summary()
            sp500_status = self.sp500_manager.get_status_report()
            
            uptime = datetime.now() - self.performance_metrics['start_time']
            
            return {
                'system_name': self.name,
                'description': self.description,
                'status': {
                    'trading_active': self.trading_active,
                    'training_active': self.training_active,
                    'uptime_hours': uptime.total_seconds() / 3600
                },
                'active_symbols': {
                    'count': len(self.active_symbols),
                    'symbols': self.active_symbols[:10]  # Show first 10
                },
                'performance_metrics': self.performance_metrics,
                'training_status': training_status,
                'ai_engine_status': ai_status,
                'sp500_status': sp500_status,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            trading_logger.error(f"Failed to get integrated status: {e}")
            return {}
    
    def force_model_update(self, symbol: str):
        """Force immediate model update for a symbol"""
        try:
            if self.realtime_training:
                self.realtime_training.force_training_update(symbol)
                trading_logger.info(f"Forced model update for {symbol}")
            else:
                trading_logger.warning("Real-time training not available")
        except Exception as e:
            trading_logger.error(f"Failed to force model update for {symbol}: {e}")
    
    def get_live_prediction(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get live prediction for a symbol"""
        try:
            if self.realtime_training:
                return self.realtime_training.get_live_predictions(symbol)
            else:
                # Fallback to standard prediction
                return self.ai_engine.predict(symbol, None)
        except Exception as e:
            trading_logger.error(f"Failed to get live prediction for {symbol}: {e}")
            return None

def main():
    """Main function"""
    print("🚀 Integrated Trading Bot with Real-Time Training")
    print("=" * 70)
    
    # Validate configuration
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Create and start integrated bot
    try:
        integrated_bot = IntegratedTradingBot()
        integrated_bot.start_integrated_trading()
    except Exception as e:
        print(f"❌ Failed to start integrated bot: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
