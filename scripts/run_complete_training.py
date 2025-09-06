#!/usr/bin/env python3
"""
🚀 Complete Historical Training Pipeline
Run the entire historical training process from data collection to model deployment
"""

import sys
import os
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.historical_trainer import HistoricalTrainer
from config import config
from utils.logger import trading_logger

def run_complete_training_pipeline():
    """Run the complete historical training pipeline"""
    print("🚀 Complete Historical Training Pipeline")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    try:
        # Step 1: Initialize trainer
        print("🔧 Step 1: Initializing Historical Trainer")
        print("-" * 40)
        trainer = HistoricalTrainer()
        symbols = config.SYMBOLS
        
        print(f"✅ Trainer initialized")
        print(f"📊 Symbols: {', '.join(symbols)}")
        print(f"📅 Timeframes: {', '.join(trainer.timeframes)}")
        print(f"📈 Historical years: {trainer.historical_years}")
        print()
        
        # Step 2: Collect historical data
        print("📊 Step 2: Collecting Historical Data")
        print("-" * 40)
        data_start = time.time()
        
        comprehensive_data = trainer.collect_comprehensive_data(symbols)
        
        data_time = time.time() - data_start
        print(f"✅ Data collection completed in {data_time:.1f} seconds")
        print(f"📈 Symbols with data: {len(comprehensive_data)}")
        
        total_timeframes = sum(len(data) for data in comprehensive_data.values())
        total_data_points = sum(
            sum(len(timeframe_data) for timeframe_data in symbol_data.values())
            for symbol_data in comprehensive_data.values()
        )
        
        print(f"📅 Total timeframes: {total_timeframes}")
        print(f"📊 Total data points: {total_data_points:,}")
        print()
        
        # Step 3: Train AI models
        print("🤖 Step 3: Training AI Models")
        print("-" * 40)
        training_start = time.time()
        
        results = trainer.train_models_with_historical_data(symbols, use_advanced=True)
        
        training_time = time.time() - training_start
        print(f"✅ Model training completed in {training_time:.1f} seconds")
        
        # Count successful trainings
        successful = sum(1 for r in results.values() if r.get('training_completed', False))
        failed = len(results) - successful
        
        print(f"✅ Successful trainings: {successful}")
        print(f"❌ Failed trainings: {failed}")
        print()
        
        # Step 4: Generate training report
        print("📊 Step 4: Generating Training Report")
        print("-" * 40)
        
        # Display detailed results
        for symbol, result in results.items():
            if result.get('training_completed', False):
                data_points = result.get('data_points', 0)
                timeframes = result.get('timeframes_available', [])
                
                print(f"✅ {symbol}:")
                print(f"   📊 Data points: {data_points:,}")
                print(f"   📅 Timeframes: {', '.join(timeframes)}")
                
                # Show model performance
                standard_perf = result.get('standard_performance', {})
                if standard_perf and 'model_performance' in standard_perf:
                    model_count = standard_perf.get('total_models', 0)
                    gpu_used = standard_perf.get('gpu_available', False)
                    print(f"   🤖 Standard models: {model_count} (GPU: {gpu_used})")
                
                advanced_perf = result.get('advanced_performance', {})
                if advanced_perf and 'model_performance' in advanced_perf:
                    advanced_count = advanced_perf.get('total_models', 0)
                    feature_selection = advanced_perf.get('feature_selection', False)
                    print(f"   🧠 Advanced models: {advanced_count} (Feature selection: {feature_selection})")
                
                print()
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ {symbol}: {error}")
        
        # Step 5: Final summary
        total_time = time.time() - start_time
        
        print("🎯 Training Pipeline Summary")
        print("=" * 40)
        print(f"⏱️ Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"📊 Data collection: {data_time:.1f} seconds")
        print(f"🤖 Model training: {training_time:.1f} seconds")
        print(f"📈 Symbols processed: {len(results)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success rate: {(successful/len(results)*100):.1f}%")
        print()
        
        # Step 6: Next steps
        print("🚀 Next Steps")
        print("-" * 40)
        if successful > 0:
            print("✅ Your AI models are ready for trading!")
            print()
            print("🎯 Available commands:")
            print("   📊 View training dashboard: python scripts/training_dashboard.py")
            print("   🤖 Start trading bot: python main.py")
            print("   📈 Monitor live trading: python scripts/live_monitor.py")
            print("   🔄 Retrain models: python scripts/run_complete_training.py")
            print()
            print("📁 Important directories:")
            print(f"   📊 Historical data: {trainer.data_dir}")
            print(f"   🤖 Trained models: {trainer.models_dir}")
            print(f"   🗂️ Training cache: {trainer.cache_dir}")
        else:
            print("⚠️ No models were trained successfully")
            print("🔍 Check the error messages above for troubleshooting")
            print("🔄 Try running the pipeline again after fixing issues")
        
        print()
        print("🎉 Complete training pipeline finished!")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Training pipeline failed: {e}")
        trading_logger.error(f"Complete training pipeline failed: {e}")
        return None

def main():
    """Main function"""
    results = run_complete_training_pipeline()
    
    if results:
        # Exit with success code
        sys.exit(0)
    else:
        # Exit with error code
        sys.exit(1)

if __name__ == "__main__":
    main()
