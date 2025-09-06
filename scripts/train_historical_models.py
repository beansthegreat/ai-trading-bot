#!/usr/bin/env python3
"""
🚀 Historical Model Training Script
Train AI models with comprehensive historical data
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.historical_trainer import HistoricalTrainer
from config import config
from utils.logger import trading_logger

def main():
    """Main training function"""
    print("🚀 Historical AI Model Training")
    print("=" * 50)
    print(f"📅 Training started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize trainer
        trainer = HistoricalTrainer()
        
        # Get symbols from config
        symbols = config.SYMBOLS
        print(f"📊 Training symbols: {', '.join(symbols)}")
        print(f"📈 Timeframes: {', '.join(trainer.timeframes)}")
        print(f"📅 Historical period: {trainer.historical_years} years")
        print()
        
        # Run comprehensive training
        results = trainer.train_models_with_historical_data(symbols, use_advanced=True)
        
        # Display results
        print("\n📊 Training Results Summary:")
        print("-" * 40)
        
        successful = 0
        failed = 0
        
        for symbol, result in results.items():
            if result.get('training_completed', False):
                successful += 1
                data_points = result.get('data_points', 0)
                timeframes = result.get('timeframes_available', [])
                print(f"✅ {symbol}: {data_points} data points, {len(timeframes)} timeframes")
            else:
                failed += 1
                error = result.get('error', 'Unknown error')
                print(f"❌ {symbol}: Failed - {error}")
        
        print(f"\n🎯 Training Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Total: {len(results)}")
        
        if successful > 0:
            print(f"\n🎉 Training completed successfully!")
            print(f"Your AI models are now trained with comprehensive historical data.")
            print(f"Models saved in: {trainer.models_dir}")
            print(f"Data saved in: {trainer.data_dir}")
        else:
            print(f"\n⚠️ No models were trained successfully.")
            print(f"Please check the error messages above.")
        
    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")
        trading_logger.error(f"Historical training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
