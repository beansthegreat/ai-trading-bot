#!/usr/bin/env python3
"""
📊 S&P 500 Data Collection Script
Collects historical data for all S&P 500 stocks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

from src.sp500_manager import SP500Manager
from utils.logger import trading_logger
from config import config

class SP500DataCollector:
    """Collects historical data for S&P 500 stocks"""
    
    def __init__(self):
        self.sp500_manager = SP500Manager()
        self.data_dir = "data/sp500/historical"
        self.timeframes = ['1d', '1h', '5m', '1m']
        self.lookback_days = 1095  # 3 years
        
    def collect_all_sp500_data(self):
        """Collect data for all S&P 500 stocks"""
        trading_logger.info("Starting S&P 500 data collection...")
        
        # Update S&P 500 constituents
        update_result = self.sp500_manager.run_full_update()
        current_stocks = self.sp500_manager.current_stocks
        
        print(f"📈 Collecting data for {len(current_stocks)} S&P 500 stocks")
        print(f"📅 Timeframes: {', '.join(self.timeframes)}")
        print(f"📊 Lookback period: {self.lookback_days} days")
        print()
        
        # Collect data for each stock
        success_count = 0
        error_count = 0
        
        for i, symbol in enumerate(current_stocks, 1):
            print(f"[{i:3d}/{len(current_stocks)}] Collecting {symbol}...", end=" ")
            
            try:
                success = self._collect_stock_data(symbol)
                if success:
                    success_count += 1
                    print("✅")
                else:
                    error_count += 1
                    print("❌")
            except Exception as e:
                error_count += 1
                print(f"❌ Error: {e}")
                trading_logger.error(f"Failed to collect data for {symbol}: {e}")
            
            # Rate limiting
            time.sleep(0.1)
        
        print()
        print(f"📊 Collection Summary:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        print(f"   📈 Total: {len(current_stocks)}")
        
        trading_logger.info("S&P 500 data collection completed", 
                           successful=success_count,
                           failed=error_count,
                           total=len(current_stocks))
    
    def _collect_stock_data(self, symbol: str) -> bool:
        """Collect data for a single stock"""
        try:
            # Check if data already exists and is recent
            data_file = f"{self.data_dir}/{symbol}_1d_data.csv"
            if os.path.exists(data_file):
                # Check file age
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(data_file))
                if file_age.days < 1:  # Data is less than 1 day old
                    return True
            
            # Collect data for each timeframe
            all_data = {}
            
            for timeframe in self.timeframes:
                data = self._fetch_stock_data(symbol, timeframe)
                if data is not None and len(data) > 0:
                    all_data[timeframe] = data
            
            # Save data
            if all_data:
                self._save_stock_data(symbol, all_data)
                return True
            else:
                return False
                
        except Exception as e:
            trading_logger.error(f"Error collecting data for {symbol}: {e}")
            return False
    
    def _fetch_stock_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch stock data from data source"""
        try:
            # Use yfinance for data collection
            import yfinance as yf
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.lookback_days)
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=timeframe,
                auto_adjust=True,
                prepost=True
            )
            
            if data.empty:
                return None
            
            # Clean and format data
            data = data.reset_index()
            data.columns = [col.lower() for col in data.columns]
            
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in data.columns:
                    return None
            
            # Add symbol and timeframe
            data['symbol'] = symbol
            data['timeframe'] = timeframe
            
            # Remove rows with missing data
            data = data.dropna(subset=required_columns)
            
            return data
            
        except Exception as e:
            trading_logger.warning(f"Failed to fetch {symbol} {timeframe} data: {e}")
            return None
    
    def _save_stock_data(self, symbol: str, all_data: Dict[str, pd.DataFrame]):
        """Save stock data to files"""
        try:
            for timeframe, data in all_data.items():
                filename = f"{self.data_dir}/{symbol}_{timeframe}_data.csv"
                data.to_csv(filename, index=False)
            
            trading_logger.info(f"Saved data for {symbol}", 
                               timeframes=list(all_data.keys()),
                               total_rows=sum(len(df) for df in all_data.values()))
            
        except Exception as e:
            trading_logger.error(f"Failed to save data for {symbol}: {e}")
    
    def collect_new_stocks_data(self):
        """Collect data only for new S&P 500 stocks"""
        trading_logger.info("Collecting data for new S&P 500 stocks...")
        
        # Update constituents to get new stocks
        update_result = self.sp500_manager.update_sp500_constituents()
        new_stocks = self.sp500_manager.new_stocks
        
        if not new_stocks:
            print("✅ No new stocks to collect data for")
            return
        
        print(f"📈 Collecting data for {len(new_stocks)} new stocks: {', '.join(new_stocks)}")
        print()
        
        success_count = 0
        for symbol in new_stocks:
            print(f"Collecting {symbol}...", end=" ")
            try:
                success = self._collect_stock_data(symbol)
                if success:
                    success_count += 1
                    print("✅")
                else:
                    print("❌")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n📊 New stocks collection: {success_count}/{len(new_stocks)} successful")
    
    def cleanup_delisted_data(self):
        """Clean up data for delisted stocks"""
        trading_logger.info("Cleaning up delisted stock data...")
        
        # Get removed stocks
        removed_stocks = self.sp500_manager.removed_stocks
        
        if not removed_stocks:
            print("✅ No delisted stocks to clean up")
            return
        
        print(f"🗑️ Cleaning up data for {len(removed_stocks)} delisted stocks: {', '.join(removed_stocks)}")
        
        cleaned_count = 0
        for symbol in removed_stocks:
            for timeframe in self.timeframes:
                filename = f"{self.data_dir}/{symbol}_{timeframe}_data.csv"
                if os.path.exists(filename):
                    os.remove(filename)
                    cleaned_count += 1
        
        print(f"📊 Cleaned up {cleaned_count} data files")
        trading_logger.info("Delisted data cleanup completed", 
                           removed_stocks=len(removed_stocks),
                           cleaned_files=cleaned_count)

def main():
    """Main function"""
    print("📊 S&P 500 Data Collection System")
    print("=" * 50)
    
    collector = SP500DataCollector()
    
    while True:
        print("\nSelect operation:")
        print("1. Collect data for all S&P 500 stocks")
        print("2. Collect data for new stocks only")
        print("3. Clean up delisted stock data")
        print("4. Update S&P 500 constituents")
        print("5. Show status report")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            collector.collect_all_sp500_data()
        elif choice == '2':
            collector.collect_new_stocks_data()
        elif choice == '3':
            collector.cleanup_delisted_data()
        elif choice == '4':
            result = collector.sp500_manager.run_full_update()
            print(f"✅ Updated {result['update_result']['total_stocks']} stocks")
            print(f"   New: {result['update_result']['new_count']}")
            print(f"   Removed: {result['update_result']['removed_count']}")
        elif choice == '5':
            report = collector.sp500_manager.get_status_report()
            print(f"\n📊 S&P 500 Status Report:")
            print(f"   Current stocks: {report['current_stocks_count']}")
            print(f"   New stocks: {report['new_stocks_count']}")
            print(f"   Removed stocks: {report['removed_stocks_count']}")
            print(f"   Training candidates: {report['training_candidates_count']}")
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
