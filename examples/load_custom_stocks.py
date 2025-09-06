#!/usr/bin/env python3
"""
📊 Custom Stock Data Loading Script
Load historical data for specific stocks
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.historical_trainer import HistoricalTrainer
from utils.logger import trading_logger

def load_custom_stocks():
    """Load data for custom stock symbols"""
    print("📊 Custom Stock Data Loading")
    print("=" * 40)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define your custom stocks here
    custom_symbols = [
        'AAPL',   # Apple
        'MSFT',   # Microsoft
        'GOOGL',  # Google
        'TSLA',   # Tesla
        'AMZN',   # Amazon
        'NVDA',   # NVIDIA
        'AMD',    # Advanced Micro Devices
        'META',   # Meta (Facebook)
        'NFLX',   # Netflix
        'CRM',    # Salesforce
        'ADBE',   # Adobe
        'PYPL',   # PayPal
        # Add more stocks as needed
    ]
    
    print(f"📈 Loading data for {len(custom_symbols)} stocks:")
    for symbol in custom_symbols:
        print(f"   • {symbol}")
    print()
    
    try:
        # Initialize trainer
        trainer = HistoricalTrainer()
        
        # Collect data for custom symbols
        comprehensive_data = trainer.collect_comprehensive_data(custom_symbols)
        
        # Display results
        print("\n📊 Data Loading Results:")
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
        
        print(f"\n🎯 Summary:")
        print(f"   📈 Symbols loaded: {len(comprehensive_data)}")
        print(f"   📅 Total timeframes: {total_timeframes}")
        print(f"   📊 Total data points: {total_data_points:,}")
        print(f"   💾 Data saved in: {trainer.data_dir}")
        
        if comprehensive_data:
            print(f"\n✅ Data loading completed successfully!")
            print(f"Next steps:")
            print(f"   🤖 Train models: python scripts/train_historical_models.py")
            print(f"   📊 View dashboard: python scripts/training_dashboard.py")
        else:
            print(f"\n⚠️ No data was loaded.")
            print(f"Please check your internet connection and symbol names.")
        
    except Exception as e:
        print(f"\n❌ Data loading failed: {e}")
        trading_logger.error(f"Custom stock data loading failed: {e}")

if __name__ == "__main__":
    load_custom_stocks()
