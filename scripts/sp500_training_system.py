#!/usr/bin/env python3
"""
🤖 S&P 500 Training System
Trains AI models for all S&P 500 stocks using hybrid acceleration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from src.sp500_manager import SP500Manager
from src.hybrid_ai_engine import HybridAIEngine
from utils.logger import trading_logger
from config import config

class SP500TrainingSystem:
    """Trains AI models for S&P 500 stocks"""
    
    def __init__(self):
        self.sp500_manager = SP500Manager()
        self.ai_engine = HybridAIEngine()
        self.data_dir = "data/sp500/historical"
        self.models_dir = "data/sp500/models"
        
        # Training configuration
        self.min_data_points = 1000  # Minimum data points for training
        self.max_training_stocks = 50  # Limit concurrent training
        self.training_batch_size = 10  # Train in batches
        
        # Performance tracking
        self.training_results = {}
        self.performance_metrics = {}
        
    def train_all_sp500_models(self):
        """Train models for all S&P 500 stocks"""
        trading_logger.info("Starting S&P 500 model training...")
        
        # Get training candidates
        training_candidates = self.sp500_manager.get_training_candidates()
        
        if not training_candidates:
            print("✅ No stocks need training")
            return
        
        print(f"🤖 Training models for {len(training_candidates)} S&P 500 stocks")
        print(f"📊 Using hybrid GPU+NPU acceleration")
        print()
        
        # Train in batches
        success_count = 0
        error_count = 0
        
        for i in range(0, len(training_candidates), self.training_batch_size):
            batch = training_candidates[i:i + self.training_batch_size]
            print(f"📦 Training batch {i//self.training_batch_size + 1}: {len(batch)} stocks")
            
            batch_results = self._train_batch(batch)
            
            for symbol, result in batch_results.items():
                if result['success']:
                    success_count += 1
                    print(f"   ✅ {symbol}: {result['model_type']} - Accuracy: {result['accuracy']:.3f}")
                else:
                    error_count += 1
                    print(f"   ❌ {symbol}: {result['error']}")
            
            print()
        
        print(f"📊 Training Summary:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        print(f"   📈 Total: {len(training_candidates)}")
        
        # Save training results
        self._save_training_results()
        
        trading_logger.info("S&P 500 model training completed", 
                           successful=success_count,
                           failed=error_count,
                           total=len(training_candidates))
    
    def _train_batch(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Train models for a batch of symbols"""
        results = {}
        
        for symbol in symbols:
            try:
                result = self._train_single_stock(symbol)
                results[symbol] = result
            except Exception as e:
                results[symbol] = {
                    'success': False,
                    'error': str(e)
                }
                trading_logger.error(f"Training failed for {symbol}: {e}")
        
        return results
    
    def _train_single_stock(self, symbol: str) -> Dict[str, Any]:
        """Train model for a single stock"""
        try:
            # Load stock data
            data = self._load_stock_data(symbol)
            if data is None or len(data) < self.min_data_points:
                return {
                    'success': False,
                    'error': f'Insufficient data: {len(data) if data is not None else 0} points'
                }
            
            # Train model
            start_time = time.time()
            training_results = self.ai_engine.train_models(symbol, data)
            training_time = time.time() - start_time
            
            if not training_results:
                return {
                    'success': False,
                    'error': 'No models trained'
                }
            
            # Get best model
            best_model = self._get_best_model(training_results)
            
            # Save model
            self._save_model(symbol, best_model)
            
            return {
                'success': True,
                'model_type': best_model['model_type'],
                'accuracy': best_model['accuracy'],
                'training_time': training_time,
                'models_trained': len(training_results),
                'hardware_used': best_model['hardware']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load stock data for training"""
        try:
            # Try different timeframes, prefer daily data
            timeframes = ['1d', '1h', '5m']
            
            for timeframe in timeframes:
                filename = f"{self.data_dir}/{symbol}_{timeframe}_data.csv"
                if os.path.exists(filename):
                    data = pd.read_csv(filename)
                    
                    # Convert timestamp
                    if 'date' in data.columns:
                        data['date'] = pd.to_datetime(data['date'])
                        data = data.set_index('date')
                    elif 'datetime' in data.columns:
                        data['datetime'] = pd.to_datetime(data['datetime'])
                        data = data.set_index('datetime')
                    
                    # Ensure required columns
                    required_columns = ['open', 'high', 'low', 'close', 'volume']
                    if all(col in data.columns for col in required_columns):
                        return data
            
            return None
            
        except Exception as e:
            trading_logger.error(f"Failed to load data for {symbol}: {e}")
            return None
    
    def _get_best_model(self, training_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get the best performing model from training results"""
        best_model = None
        best_accuracy = 0
        
        for model_name, result in training_results.items():
            if result['accuracy'] > best_accuracy:
                best_accuracy = result['accuracy']
                best_model = result
        
        return best_model
    
    def _save_model(self, symbol: str, model_info: Dict[str, Any]):
        """Save trained model"""
        try:
            # Save model info
            model_file = f"{self.models_dir}/{symbol}_model_info.json"
            import json
            
            with open(model_file, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            # Save actual model (this would depend on the model type)
            # For now, we'll save the model info
            
        except Exception as e:
            trading_logger.error(f"Failed to save model for {symbol}: {e}")
    
    def _save_training_results(self):
        """Save training results"""
        try:
            results_file = f"{self.models_dir}/training_results.json"
            import json
            
            with open(results_file, 'w') as f:
                json.dump(self.training_results, f, indent=2)
            
        except Exception as e:
            trading_logger.error(f"Failed to save training results: {e}")
    
    def train_new_stocks_only(self):
        """Train models only for new S&P 500 stocks"""
        trading_logger.info("Training models for new S&P 500 stocks...")
        
        # Get new stocks
        new_stocks = self.sp500_manager.new_stocks
        
        if not new_stocks:
            print("✅ No new stocks to train")
            return
        
        print(f"🤖 Training models for {len(new_stocks)} new stocks: {', '.join(new_stocks)}")
        print()
        
        success_count = 0
        for symbol in new_stocks:
            print(f"Training {symbol}...", end=" ")
            try:
                result = self._train_single_stock(symbol)
                if result['success']:
                    success_count += 1
                    print(f"✅ {result['model_type']} - {result['accuracy']:.3f}")
                else:
                    print(f"❌ {result['error']}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n📊 New stocks training: {success_count}/{len(new_stocks)} successful")
    
    def retrain_old_models(self):
        """Retrain models that are older than threshold"""
        trading_logger.info("Retraining old models...")
        
        # Get training candidates (includes old models)
        training_candidates = self.sp500_manager.get_training_candidates()
        
        if not training_candidates:
            print("✅ No old models need retraining")
            return
        
        print(f"🔄 Retraining {len(training_candidates)} old models")
        print()
        
        # Train all candidates
        self.train_all_sp500_models()
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get training status report"""
        try:
            # Count trained models
            trained_models = 0
            if os.path.exists(self.models_dir):
                trained_models = len([f for f in os.listdir(self.models_dir) if f.endswith('_model_info.json')])
            
            # Get training candidates
            training_candidates = self.sp500_manager.get_training_candidates()
            
            # Get performance summary
            performance_summary = self.ai_engine.get_performance_summary()
            
            return {
                'total_sp500_stocks': len(self.sp500_manager.current_stocks),
                'trained_models': trained_models,
                'training_candidates': len(training_candidates),
                'new_stocks': len(self.sp500_manager.new_stocks),
                'ai_engine_status': performance_summary,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            trading_logger.error(f"Failed to get training status: {e}")
            return {}

def main():
    """Main function"""
    print("🤖 S&P 500 AI Training System")
    print("=" * 50)
    
    trainer = SP500TrainingSystem()
    
    while True:
        print("\nSelect operation:")
        print("1. Train models for all S&P 500 stocks")
        print("2. Train models for new stocks only")
        print("3. Retrain old models")
        print("4. Show training status")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            trainer.train_all_sp500_models()
        elif choice == '2':
            trainer.train_new_stocks_only()
        elif choice == '3':
            trainer.retrain_old_models()
        elif choice == '4':
            status = trainer.get_training_status()
            print(f"\n📊 Training Status:")
            print(f"   Total S&P 500 stocks: {status['total_sp500_stocks']}")
            print(f"   Trained models: {status['trained_models']}")
            print(f"   Training candidates: {status['training_candidates']}")
            print(f"   New stocks: {status['new_stocks']}")
            print(f"   AI Engine: {status['ai_engine_status']['engine_name']}")
            print(f"   GPU Available: {status['ai_engine_status']['hardware_status']['gpu_available']}")
            print(f"   NPU Available: {status['ai_engine_status']['hardware_status']['npu_available']}")
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
