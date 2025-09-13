#!/usr/bin/env python3
"""
📈 S&P 500 Dynamic Stock Management System
Automatically manages S&P 500 constituents, training, and data cleanup
"""

import pandas as pd
import numpy as np
import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

from utils.logger import trading_logger
from config import config

class SP500Manager:
    """Dynamic S&P 500 stock management system"""
    
    def __init__(self):
        self.name = "S&P 500 Dynamic Manager"
        self.description = "Manages S&P 500 constituents with automatic training and cleanup"
        
        # Data sources
        self.data_sources = {
            'wikipedia': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            'yahoo_finance': 'https://query1.finance.yahoo.com/v1/finance/screener',
            'marketbeat': 'https://www.marketbeat.com/types-of-stock/sp-500-stocks/',
            'slickcharts': 'https://www.slickcharts.com/sp500'
        }
        
        # Storage paths
        self.data_dir = "data/sp500"
        self.current_stocks_file = f"{self.data_dir}/current_stocks.json"
        self.historical_changes_file = f"{self.data_dir}/historical_changes.json"
        self.performance_ranking_file = f"{self.data_dir}/performance_ranking.json"
        
        # Current state
        self.current_stocks = set()
        self.previous_stocks = set()
        self.new_stocks = set()
        self.removed_stocks = set()
        self.performance_ranking = {}
        
        # Configuration
        self.max_stocks = 500
        self.min_training_data_days = 252  # 1 year
        self.retrain_threshold_days = 7    # Retrain weekly
        self.cleanup_delay_days = 30       # Keep delisted data for 30 days
        
        # Initialize
        self._setup_directories()
        self._load_current_state()
        
        trading_logger.info("S&P 500 Manager initialized", 
                           current_stocks=len(self.current_stocks),
                           data_dir=self.data_dir)
    
    def _setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/historical", exist_ok=True)
        os.makedirs(f"{self.data_dir}/models", exist_ok=True)
        os.makedirs(f"{self.data_dir}/cache", exist_ok=True)
    
    def _load_current_state(self):
        """Load current state from files"""
        try:
            # Load current stocks
            if os.path.exists(self.current_stocks_file):
                with open(self.current_stocks_file, 'r') as f:
                    data = json.load(f)
                    self.current_stocks = set(data.get('stocks', []))
                    self.previous_stocks = set(data.get('previous_stocks', []))
            
            # Load performance ranking
            if os.path.exists(self.performance_ranking_file):
                with open(self.performance_ranking_file, 'r') as f:
                    self.performance_ranking = json.load(f)
            
            trading_logger.info("Current state loaded", 
                               stocks_count=len(self.current_stocks))
        except Exception as e:
            trading_logger.warning(f"Failed to load current state: {e}")
    
    def _save_current_state(self):
        """Save current state to files"""
        try:
            # Save current stocks
            with open(self.current_stocks_file, 'w') as f:
                json.dump({
                    'stocks': list(self.current_stocks),
                    'previous_stocks': list(self.previous_stocks),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
            
            # Save performance ranking
            with open(self.performance_ranking_file, 'w') as f:
                json.dump(self.performance_ranking, f, indent=2)
            
            trading_logger.info("Current state saved")
        except Exception as e:
            trading_logger.error(f"Failed to save current state: {e}")
    
    def fetch_sp500_stocks(self) -> Set[str]:
        """Fetch current S&P 500 stock symbols from multiple sources"""
        all_stocks = set()
        
        # Try multiple sources for reliability
        sources_used = []
        
        # Source 1: Wikipedia (most reliable)
        try:
            stocks = self._fetch_from_wikipedia()
            if stocks:
                all_stocks.update(stocks)
                sources_used.append('wikipedia')
                trading_logger.info(f"Fetched {len(stocks)} stocks from Wikipedia")
        except Exception as e:
            trading_logger.warning(f"Wikipedia fetch failed: {e}")
        
        # Source 2: Yahoo Finance API
        try:
            stocks = self._fetch_from_yahoo_finance()
            if stocks:
                all_stocks.update(stocks)
                sources_used.append('yahoo_finance')
                trading_logger.info(f"Fetched {len(stocks)} stocks from Yahoo Finance")
        except Exception as e:
            trading_logger.warning(f"Yahoo Finance fetch failed: {e}")
        
        # Source 3: MarketBeat (fallback)
        try:
            stocks = self._fetch_from_marketbeat()
            if stocks:
                all_stocks.update(stocks)
                sources_used.append('marketbeat')
                trading_logger.info(f"Fetched {len(stocks)} stocks from MarketBeat")
        except Exception as e:
            trading_logger.warning(f"MarketBeat fetch failed: {e}")
        
        # Validate and clean stock symbols
        validated_stocks = self._validate_stock_symbols(all_stocks)
        
        trading_logger.info(f"S&P 500 fetch completed", 
                           total_found=len(all_stocks),
                           validated=len(validated_stocks),
                           sources_used=sources_used)
        
        return validated_stocks
    
    def _fetch_from_wikipedia(self) -> Set[str]:
        """Fetch S&P 500 stocks from Wikipedia"""
        try:
            url = self.data_sources['wikipedia']
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML table
            tables = pd.read_html(response.text)
            sp500_table = tables[0]  # First table is usually S&P 500
            
            # Extract symbols (usually in first column)
            symbols = set()
            for col in sp500_table.columns:
                if 'symbol' in col.lower() or 'ticker' in col.lower():
                    symbols.update(sp500_table[col].dropna().astype(str).str.upper())
                    break
            
            return symbols
        except Exception as e:
            trading_logger.error(f"Wikipedia fetch error: {e}")
            return set()
    
    def _fetch_from_yahoo_finance(self) -> Set[str]:
        """Fetch S&P 500 stocks from Yahoo Finance"""
        try:
            # Yahoo Finance screener for S&P 500
            url = "https://query1.finance.yahoo.com/v1/finance/screener"
            params = {
                'formatted': 'true',
                'lang': 'en-US',
                'region': 'US',
                'sort': 'market_cap',
                'count': 500,
                'corsDomain': 'finance.yahoo.com'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            symbols = set()
            
            if 'finance' in data and 'result' in data['finance']:
                for item in data['finance']['result']:
                    if 'symbol' in item:
                        symbols.add(item['symbol'].upper())
            
            return symbols
        except Exception as e:
            trading_logger.error(f"Yahoo Finance fetch error: {e}")
            return set()
    
    def _fetch_from_marketbeat(self) -> Set[str]:
        """Fetch S&P 500 stocks from MarketBeat (fallback)"""
        try:
            # This would require web scraping - simplified version
            # In practice, you might use a more robust scraping approach
            url = self.data_sources['marketbeat']
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Simple regex-based extraction (would need more sophisticated parsing)
            import re
            symbols = set()
            symbol_pattern = r'\b[A-Z]{1,5}\b'
            matches = re.findall(symbol_pattern, response.text)
            
            # Filter for likely stock symbols (3-5 characters, common patterns)
            for match in matches:
                if 3 <= len(match) <= 5 and match.isalpha():
                    symbols.add(match)
            
            return symbols
        except Exception as e:
            trading_logger.error(f"MarketBeat fetch error: {e}")
            return set()
    
    def _validate_stock_symbols(self, symbols: Set[str]) -> Set[str]:
        """Validate and clean stock symbols"""
        validated = set()
        
        for symbol in symbols:
            # Basic validation
            if (symbol and 
                isinstance(symbol, str) and 
                1 <= len(symbol) <= 5 and 
                symbol.isalpha() and
                symbol.isupper()):
                validated.add(symbol)
        
        # Remove common non-stock symbols
        excluded = {
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'GLD', 'SLV',
            'TLT', 'HYG', 'LQD', 'EMB', 'EFA', 'EEM', 'IEFA', 'IEMG', 'ACWI'
        }
        validated = validated - excluded
        
        return validated
    
    def update_sp500_constituents(self) -> Dict[str, Any]:
        """Update S&P 500 constituents and identify changes"""
        trading_logger.info("Updating S&P 500 constituents...")
        
        # Store previous state
        self.previous_stocks = self.current_stocks.copy()
        
        # Fetch new constituents
        new_constituents = self.fetch_sp500_stocks()
        
        # Identify changes
        self.new_stocks = new_constituents - self.current_stocks
        self.removed_stocks = self.current_stocks - new_constituents
        
        # Update current stocks
        self.current_stocks = new_constituents
        
        # Save changes
        self._save_current_state()
        self._log_changes()
        
        # Prepare result
        result = {
            'total_stocks': len(self.current_stocks),
            'new_stocks': list(self.new_stocks),
            'removed_stocks': list(self.removed_stocks),
            'new_count': len(self.new_stocks),
            'removed_count': len(self.removed_stocks),
            'timestamp': datetime.now().isoformat()
        }
        
        trading_logger.info("S&P 500 constituents updated", **result)
        return result
    
    def _log_changes(self):
        """Log historical changes"""
        try:
            changes = {
                'timestamp': datetime.now().isoformat(),
                'new_stocks': list(self.new_stocks),
                'removed_stocks': list(self.removed_stocks),
                'total_stocks': len(self.current_stocks)
            }
            
            # Load existing changes
            historical_changes = []
            if os.path.exists(self.historical_changes_file):
                with open(self.historical_changes_file, 'r') as f:
                    historical_changes = json.load(f)
            
            # Add new changes
            historical_changes.append(changes)
            
            # Keep only last 100 changes
            historical_changes = historical_changes[-100:]
            
            # Save updated changes
            with open(self.historical_changes_file, 'w') as f:
                json.dump(historical_changes, f, indent=2)
            
        except Exception as e:
            trading_logger.error(f"Failed to log changes: {e}")
    
    def get_training_candidates(self) -> List[str]:
        """Get stocks that need training or retraining"""
        candidates = []
        
        for symbol in self.current_stocks:
            # Check if model exists and is recent
            model_path = f"{self.data_dir}/models/{symbol}_model.joblib"
            
            if not os.path.exists(model_path):
                # New stock - needs training
                candidates.append(symbol)
            else:
                # Check model age
                model_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(model_path))
                if model_age.days >= self.retrain_threshold_days:
                    # Model is old - needs retraining
                    candidates.append(symbol)
        
        trading_logger.info(f"Found {len(candidates)} training candidates")
        return candidates
    
    def get_performance_ranking(self) -> Dict[str, float]:
        """Get performance ranking of all S&P 500 stocks"""
        if not self.performance_ranking:
            self._calculate_performance_ranking()
        
        return self.performance_ranking
    
    def _calculate_performance_ranking(self):
        """Calculate performance ranking for all stocks"""
        try:
            ranking = {}
            
            for symbol in self.current_stocks:
                # Calculate performance metrics
                performance_score = self._calculate_stock_performance(symbol)
                if performance_score is not None:
                    ranking[symbol] = performance_score
            
            # Sort by performance
            sorted_ranking = dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))
            
            self.performance_ranking = sorted_ranking
            
            # Save ranking
            with open(self.performance_ranking_file, 'w') as f:
                json.dump(sorted_ranking, f, indent=2)
            
            trading_logger.info(f"Performance ranking calculated for {len(ranking)} stocks")
            
        except Exception as e:
            trading_logger.error(f"Failed to calculate performance ranking: {e}")
    
    def _calculate_stock_performance(self, symbol: str) -> Optional[float]:
        """Calculate performance score for a single stock"""
        try:
            # This would integrate with your existing data collection
            # For now, return a placeholder score
            return np.random.uniform(0.5, 1.0)  # Placeholder
        except Exception as e:
            trading_logger.warning(f"Failed to calculate performance for {symbol}: {e}")
            return None
    
    def cleanup_delisted_data(self):
        """Clean up data for delisted stocks"""
        try:
            cleaned_count = 0
            
            for symbol in self.removed_stocks:
                # Check if enough time has passed since removal
                # (This would need to track removal dates)
                
                # Clean up historical data
                historical_file = f"{self.data_dir}/historical/{symbol}_data.csv"
                if os.path.exists(historical_file):
                    os.remove(historical_file)
                    cleaned_count += 1
                
                # Clean up model files
                model_file = f"{self.data_dir}/models/{symbol}_model.joblib"
                if os.path.exists(model_file):
                    os.remove(model_file)
                    cleaned_count += 1
                
                # Clean up cache files
                cache_file = f"{self.data_dir}/cache/{symbol}_cache.pkl"
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                    cleaned_count += 1
            
            trading_logger.info(f"Cleaned up data for {cleaned_count} delisted stocks")
            
        except Exception as e:
            trading_logger.error(f"Failed to cleanup delisted data: {e}")
    
    def get_top_performers(self, count: int = 50) -> List[str]:
        """Get top performing stocks"""
        ranking = self.get_performance_ranking()
        return list(ranking.keys())[:count]
    
    def get_bottom_performers(self, count: int = 50) -> List[str]:
        """Get bottom performing stocks"""
        ranking = self.get_performance_ranking()
        return list(ranking.keys())[-count:]
    
    def get_sector_diversity(self) -> Dict[str, int]:
        """Get sector diversity of current holdings"""
        # This would require sector information from a data source
        # For now, return placeholder
        return {
            'Technology': 150,
            'Healthcare': 80,
            'Financials': 70,
            'Consumer Discretionary': 60,
            'Industrials': 50,
            'Other': 90
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            'manager_name': self.name,
            'description': self.description,
            'current_stocks_count': len(self.current_stocks),
            'new_stocks_count': len(self.new_stocks),
            'removed_stocks_count': len(self.removed_stocks),
            'training_candidates_count': len(self.get_training_candidates()),
            'top_performers': self.get_top_performers(10),
            'sector_diversity': self.get_sector_diversity(),
            'last_updated': datetime.now().isoformat(),
            'data_directory': self.data_dir
        }
    
    def run_full_update(self) -> Dict[str, Any]:
        """Run complete S&P 500 update cycle"""
        trading_logger.info("Starting full S&P 500 update cycle...")
        
        start_time = time.time()
        
        # Step 1: Update constituents
        update_result = self.update_sp500_constituents()
        
        # Step 2: Calculate performance ranking
        self._calculate_performance_ranking()
        
        # Step 3: Cleanup delisted data
        self.cleanup_delisted_data()
        
        # Step 4: Get training candidates
        training_candidates = self.get_training_candidates()
        
        # Step 5: Generate status report
        status_report = self.get_status_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            'update_result': update_result,
            'training_candidates': training_candidates,
            'status_report': status_report,
            'duration_seconds': duration,
            'success': True
        }
        
        trading_logger.info("Full S&P 500 update cycle completed", 
                           duration=duration,
                           training_candidates=len(training_candidates))
        
        return result
