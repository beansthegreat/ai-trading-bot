#!/usr/bin/env python3
"""
📊 Data Enhancement Utility
Downloads and injects historical market data to improve AI training
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import pickle
from utils.logger import trading_logger

class DataEnhancer:
    """Enhances AI training with historical market data"""
    
    def __init__(self):
        self.data_dir = "historical_data"
        self.cache_file = "data_cache.pkl"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def download_historical_data(self, symbols: List[str], years: int = 2) -> Dict[str, pd.DataFrame]:
        """Download historical data for multiple symbols"""
        print(f"📥 Downloading {years} years of historical data for {len(symbols)} symbols...")
        
        historical_data = {}
        start_date = datetime.now() - timedelta(days=365 * years)
        
        for symbol in symbols:
            try:
                print(f"   Downloading {symbol}...")
                
                # Download data
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, interval="1m")
                
                if len(data) > 0:
                    # Clean and prepare data
                    data = self._prepare_data(data, symbol)
                    historical_data[symbol] = data
                    
                    # Save individual file
                    file_path = os.path.join(self.data_dir, f"{symbol}_historical.csv")
                    data.to_csv(file_path)
                    
                    print(f"   ✅ {symbol}: {len(data)} data points")
                else:
                    print(f"   ❌ {symbol}: No data available")
                    
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")
                continue
        
        # Save combined cache
        self._save_cache(historical_data)
        
        print(f"📊 Downloaded {len(historical_data)} symbols successfully")
        return historical_data
    
    def _prepare_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Prepare downloaded data for AI training"""
        # Reset index to get datetime as column
        df = df.reset_index()
        
        # Rename columns to match our format
        df = df.rename(columns={
            'Datetime': 'timestamp',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Add symbol column
        df['symbol'] = symbol
        
        # Set timestamp as index
        df = df.set_index('timestamp')
        
        # Remove any NaN values
        df = df.dropna()
        
        return df
    
    def _save_cache(self, data: Dict[str, pd.DataFrame]):
        """Save data cache to disk"""
        cache_path = os.path.join(self.data_dir, self.cache_file)
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"💾 Data cache saved to {cache_path}")
    
    def load_cache(self) -> Dict[str, pd.DataFrame]:
        """Load data cache from disk"""
        cache_path = os.path.join(self.data_dir, self.cache_file)
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            print(f"📂 Loaded {len(data)} symbols from cache")
            return data
        else:
            print("📂 No cache found")
            return {}
    
    def get_enhanced_training_data(self, symbol: str, min_data_points: int = 1000) -> pd.DataFrame:
        """Get enhanced training data for a specific symbol"""
        cache = self.load_cache()
        
        if symbol in cache:
            data = cache[symbol]
            if len(data) >= min_data_points:
                print(f"📊 Using {len(data)} historical data points for {symbol}")
                return data
            else:
                print(f"⚠️ Insufficient historical data for {symbol}: {len(data)} < {min_data_points}")
        else:
            print(f"⚠️ No historical data found for {symbol}")
        
        return pd.DataFrame()  # Return empty if no data
    
    def inject_data_into_ai(self, ai_engine, symbols: List[str]):
        """Inject historical data into AI engine for training"""
        print("🤖 Injecting historical data into AI engine...")
        
        for symbol in symbols:
            historical_data = self.get_enhanced_training_data(symbol)
            
            if len(historical_data) > 0:
                print(f"   Training AI with {len(historical_data)} data points for {symbol}")
                
                try:
                    # Train AI with historical data
                    ai_engine.train_models(historical_data, symbol)
                    
                    # Save the enhanced models
                    ai_engine.save_models(symbol)
                    
                    print(f"   ✅ AI trained successfully for {symbol}")
                    
                except Exception as e:
                    print(f"   ❌ AI training failed for {symbol}: {e}")
            else:
                print(f"   ⚠️ Skipping {symbol} - no historical data")
        
        print("🎯 Historical data injection complete!")

def enhance_ai_with_historical_data():
    """Main function to enhance AI with historical data"""
    print("🚀 AI Data Enhancement Process")
    print("=" * 50)
    
    # Initialize enhancer
    enhancer = DataEnhancer()
    
    # Symbols to enhance
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'AMD']
    
    # Download historical data (2 years)
    print("\n📥 Step 1: Downloading Historical Data")
    historical_data = enhancer.download_historical_data(symbols, years=2)
    
    # Inject into AI engine
    print("\n🤖 Step 2: Injecting Data into AI Engine")
    from src.ai_engine import AIEngine
    ai_engine = AIEngine()
    enhancer.inject_data_into_ai(ai_engine, symbols)
    
    print("\n✅ AI Enhancement Complete!")
    print("Your AI now has real historical data to learn from!")

if __name__ == "__main__":
    enhance_ai_with_historical_data()
