#!/usr/bin/env python3
"""
📊 Training Dashboard
Monitor and analyze historical training results
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.historical_trainer import HistoricalTrainer
from config import config

def display_training_dashboard():
    """Display comprehensive training dashboard"""
    print("📊 Historical Training Dashboard")
    print("=" * 50)
    print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize trainer
        trainer = HistoricalTrainer()
        
        # Load training results
        import pickle
        results_path = os.path.join(trainer.cache_dir, "training_results.pkl")
        
        if os.path.exists(results_path):
            with open(results_path, 'rb') as f:
                training_results = pickle.load(f)
        else:
            print("⚠️ No training results found. Run training first.")
            return
        
        # Display system information
        print("🔧 System Information:")
        print("-" * 30)
        summary = trainer.get_training_summary()
        system_info = summary['system_info']
        print(f"   Name: {system_info['name']}")
        print(f"   Timeframes: {', '.join(system_info['timeframes'])}")
        print(f"   Historical Years: {system_info['historical_years']}")
        print(f"   Min Data Points: {system_info['min_data_points']:,}")
        print()
        
        # Display training results
        print("📊 Training Results:")
        print("-" * 30)
        
        successful = 0
        failed = 0
        total_data_points = 0
        
        for symbol, result in training_results.items():
            if result.get('training_completed', False):
                successful += 1
                data_points = result.get('data_points', 0)
                total_data_points += data_points
                timeframes = result.get('timeframes_available', [])
                
                print(f"✅ {symbol}:")
                print(f"   📊 Data Points: {data_points:,}")
                print(f"   📅 Timeframes: {', '.join(timeframes)}")
                
                # Display performance metrics
                standard_perf = result.get('standard_performance', {})
                if standard_perf:
                    print(f"   🤖 Standard Models: {standard_perf.get('total_models', 0)}")
                    print(f"   🚀 GPU Available: {standard_perf.get('gpu_available', False)}")
                
                advanced_perf = result.get('advanced_performance', {})
                if advanced_perf:
                    print(f"   🧠 Advanced Models: {advanced_perf.get('total_models', 0)}")
                    print(f"   🔍 Feature Selection: {advanced_perf.get('feature_selection', False)}")
                
                print()
            else:
                failed += 1
                error = result.get('error', 'Unknown error')
                print(f"❌ {symbol}: {error}")
        
        # Display summary statistics
        print("📈 Summary Statistics:")
        print("-" * 30)
        print(f"   ✅ Successful Trainings: {successful}")
        print(f"   ❌ Failed Trainings: {failed}")
        print(f"   📊 Total Symbols: {len(training_results)}")
        print(f"   📈 Total Data Points: {total_data_points:,}")
        print(f"   📅 Success Rate: {(successful/len(training_results)*100):.1f}%")
        print()
        
        # Display directory information
        print("📁 Directory Information:")
        print("-" * 30)
        print(f"   📊 Data Directory: {summary['data_directory']}")
        print(f"   🤖 Models Directory: {summary['models_directory']}")
        print(f"   🗂️ Cache Directory: {summary['cache_directory']}")
        print()
        
        # Check for available models
        print("🤖 Available Models:")
        print("-" * 30)
        
        models_dir = summary['models_directory']
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
            if model_files:
                print(f"   📁 Found {len(model_files)} model files:")
                for model_file in sorted(model_files):
                    file_path = os.path.join(models_dir, model_file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    print(f"      📄 {model_file} ({file_size:.1f} MB)")
            else:
                print("   ⚠️ No model files found")
        else:
            print("   ⚠️ Models directory does not exist")
        
        print()
        
        # Display next steps
        print("🚀 Next Steps:")
        print("-" * 30)
        if successful > 0:
            print("   ✅ Your AI models are ready for trading!")
            print("   🎯 Start the trading bot: python main.py")
            print("   📊 Monitor performance: python scripts/live_monitor.py")
            print("   🔄 Retrain models: python scripts/train_historical_models.py")
        else:
            print("   ⚠️ No models were trained successfully")
            print("   🔄 Run training: python scripts/train_historical_models.py")
            print("   📊 Collect data: python scripts/collect_historical_data.py")
        
        print()
        print("🎉 Dashboard complete!")
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

if __name__ == "__main__":
    display_training_dashboard()
