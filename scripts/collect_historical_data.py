#!/usr/bin/env python3
"""
📊 Historical Data Collection Script
Collect comprehensive historical data for training
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
    """Main data collection function"""
    print("📊 Historical Data Collection")
    print("=" * 40)
    print(f"📅 Collection started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize trainer
        trainer = HistoricalTrainer()
        
        # Get symbols from config
        symbols = config.SYMBOLS
        print(f"📈 Collecting data for: {', '.join(symbols)}")
        print(f"📊 Timeframes: {', '.join(trainer.timeframes)}")
        print(f"📅 Historical period: {trainer.historical_years} years")
        print()
        
        # Collect comprehensive data
        comprehensive_data = trainer.collect_comprehensive_data(symbols)
        
        # Display results
        print("\n📊 Data Collection Results:")
        print("-" * 40)
        
        total_timeframes = 0
        total_data_points = 0
        
        for symbol, timeframes in comprehensive_data.items():
            print(f"\n📈 {symbol}:")
            symbol_data_points = 0
            
            for timeframe, data in timeframes.items():
                data_points = len(data)
                symbol_data_points += data_points
                total_data_points += data_points
                total_timeframes += 1
                print(f"   📅 {timeframe}: {data_points:,} data points")
            
            print(f"   📊 Total: {symbol_data_points:,} data points")
        
        print(f"\n🎯 Collection Summary:")
        print(f"   📈 Symbols: {len(comprehensive_data)}")
        print(f"   📅 Timeframes: {total_timeframes}")
        print(f"   📊 Total data points: {total_data_points:,}")
        print(f"   💾 Data saved in: {trainer.data_dir}")
        print(f"   🗂️ Cache saved in: {trainer.cache_dir}")
        
        if comprehensive_data:
            print(f"\n✅ Data collection completed successfully!")
            print(f"You can now run training with: python scripts/train_historical_models.py")
        else:
            print(f"\n⚠️ No data was collected.")
            print(f"Please check your internet connection and symbol configurations.")
        
    except Exception as e:
        print(f"\n❌ Data collection failed with error: {e}")
        trading_logger.error(f"Historical data collection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
