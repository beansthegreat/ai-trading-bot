#!/usr/bin/env python3
"""
📈 Historical Training System
Comprehensive historical data training with charts, volumes, and pricing
"""

import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import mlflow
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import os
import warnings
warnings.filterwarnings('ignore')

from utils.logger import trading_logger
from utils.indicators import TechnicalIndicators
from src.ai_engine import AIEngine
from src.advanced_ai_engine import AdvancedAIEngine
from config import config

class HistoricalTrainer:
    """Enhanced historical training system with comprehensive data collection"""
    
    def __init__(self):
        self.name = "Historical Training System"
        self.description = "Comprehensive historical data training with charts, volumes, and pricing"
        
        # Data storage
        self.data_dir = "historical_training_data"
        self.models_dir = "trained_models"
        self.cache_dir = "training_cache"
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Training configuration
        self.timeframes = ['1m', '5m', '15m', '1h', '1d']
        self.historical_years = 3  # 3 years of historical data
        self.min_data_points = 1000  # Minimum data points for training
        
        # Feature engineering
        self.chart_patterns = True
        self.volume_analysis = True
        self.price_action = True
        self.market_regime = True
        
        # AI engines
        self.ai_engine = AIEngine()
        self.advanced_ai_engine = AdvancedAIEngine()
        
        # Performance tracking
        self.training_results = {}
        self.feature_importance = {}
        
        trading_logger.info("Historical Training System initialized",
                           timeframes=self.timeframes,
                           historical_years=self.historical_years,
                           min_data_points=self.min_data_points)
    
    def collect_comprehensive_data(self, symbols: List[str]) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Collect comprehensive historical data for multiple timeframes"""
        print(f"📊 Collecting comprehensive historical data for {len(symbols)} symbols...")
        
        comprehensive_data = {}
        
        for symbol in symbols:
            print(f"\n📈 Processing {symbol}...")
            symbol_data = {}
            
            for timeframe in self.timeframes:
                try:
                    print(f"   📅 Downloading {timeframe} data...")
                    
                    # Calculate period based on timeframe
                    period = self._get_period_for_timeframe(timeframe)
                    
                    # Download data
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period, interval=timeframe)
                    
                    if len(data) > 0:
                        # Clean and enhance data
                        data = self._clean_and_enhance_data(data, symbol, timeframe)
                        
                        # Add technical indicators
                        data = self._add_technical_indicators(data)
                        
                        # Add chart patterns
                        if self.chart_patterns:
                            data = self._add_chart_patterns(data)
                        
                        # Add volume analysis
                        if self.volume_analysis:
                            data = self._add_volume_analysis(data)
                        
                        # Add price action features
                        if self.price_action:
                            data = self._add_price_action_features(data)
                        
                        # Add market regime classification
                        if self.market_regime:
                            data = self._add_market_regime(data)
                        
                        symbol_data[timeframe] = data
                        
                        # Save individual timeframe data
                        file_path = os.path.join(self.data_dir, f"{symbol}_{timeframe}_data.csv")
                        data.to_csv(file_path)
                        
                        print(f"   ✅ {timeframe}: {len(data)} data points")
                    else:
                        print(f"   ❌ {timeframe}: No data available")
                        
                except Exception as e:
                    print(f"   ❌ {timeframe}: Error - {e}")
                    continue
            
            if symbol_data:
                comprehensive_data[symbol] = symbol_data
                print(f"✅ {symbol}: {len(symbol_data)} timeframes collected")
            else:
                print(f"❌ {symbol}: No data collected")
        
        # Save comprehensive data cache
        self._save_comprehensive_cache(comprehensive_data)
        
        print(f"\n🎯 Comprehensive data collection complete!")
        print(f"   Symbols: {len(comprehensive_data)}")
        print(f"   Total timeframes: {sum(len(data) for data in comprehensive_data.values())}")
        
        return comprehensive_data
    
    def _get_period_for_timeframe(self, timeframe: str) -> str:
        """Get appropriate period for timeframe"""
        period_map = {
            '1m': '7d',    # 1 week for 1-minute data
            '5m': '60d',   # 2 months for 5-minute data
            '15m': '1y',   # 1 year for 15-minute data
            '1h': '2y',    # 2 years for hourly data
            '1d': '5y'     # 5 years for daily data
        }
        return period_map.get(timeframe, '1y')
    
    def _clean_and_enhance_data(self, df: pd.DataFrame, symbol: str, timeframe: str) -> pd.DataFrame:
        """Clean and enhance raw data"""
        # Reset index
        df = df.reset_index()
        
        # Rename columns
        df = df.rename(columns={
            'Datetime': 'timestamp',
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Add metadata
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        
        # Set timestamp as index
        df = df.set_index('timestamp')
        
        # Remove any NaN values
        df = df.dropna()
        
        # Add basic price features
        df['price_change'] = df['close'].pct_change()
        df['price_range'] = (df['high'] - df['low']) / df['close']
        df['body_size'] = abs(df['close'] - df['open']) / df['close']
        df['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
        df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add comprehensive technical indicators"""
        try:
            # Use existing TechnicalIndicators class
            df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
            
            # Add additional indicators
            df_with_indicators = self._add_additional_indicators(df_with_indicators)
            
            return df_with_indicators
        except Exception as e:
            trading_logger.warning(f"Error adding technical indicators: {e}")
            return df
    
    def _add_additional_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add additional technical indicators"""
        # Williams %R
        df['williams_r'] = ((df['high'].rolling(14).max() - df['close']) / 
                           (df['high'].rolling(14).max() - df['low'].rolling(14).min())) * -100
        
        # Commodity Channel Index (CCI)
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['sma_tp'] = df['typical_price'].rolling(20).mean()
        df['mad'] = df['typical_price'].rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())))
        df['cci'] = (df['typical_price'] - df['sma_tp']) / (0.015 * df['mad'])
        
        # Money Flow Index (MFI)
        df['typical_price_mfi'] = (df['high'] + df['low'] + df['close']) / 3
        df['raw_money_flow'] = df['typical_price_mfi'] * df['volume']
        
        positive_flow = df['raw_money_flow'].where(df['typical_price_mfi'] > df['typical_price_mfi'].shift(1), 0)
        negative_flow = df['raw_money_flow'].where(df['typical_price_mfi'] < df['typical_price_mfi'].shift(1), 0)
        
        df['positive_money_flow'] = positive_flow.rolling(14).sum()
        df['negative_money_flow'] = negative_flow.rolling(14).sum()
        df['mfi'] = 100 - (100 / (1 + df['positive_money_flow'] / df['negative_money_flow']))
        
        # On-Balance Volume (OBV)
        df['obv'] = (df['volume'] * np.where(df['close'] > df['close'].shift(1), 1, 
                                           np.where(df['close'] < df['close'].shift(1), -1, 0))).cumsum()
        
        # Volume Weighted Average Price (VWAP)
        df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        
        # Price Rate of Change (ROC)
        df['roc'] = df['close'].pct_change(periods=10) * 100
        
        # Momentum
        df['momentum'] = df['close'] - df['close'].shift(10)
        
        return df
    
    def _add_chart_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add chart pattern recognition features"""
        # Head and Shoulders pattern
        df['head_shoulders'] = self._detect_head_shoulders(df)
        
        # Double Top/Bottom
        df['double_top'] = self._detect_double_top(df)
        df['double_bottom'] = self._detect_double_bottom(df)
        
        # Triangle patterns
        df['ascending_triangle'] = self._detect_ascending_triangle(df)
        df['descending_triangle'] = self._detect_descending_triangle(df)
        df['symmetrical_triangle'] = self._detect_symmetrical_triangle(df)
        
        # Flag and Pennant
        df['bull_flag'] = self._detect_bull_flag(df)
        df['bear_flag'] = self._detect_bear_flag(df)
        
        # Support and Resistance levels
        df['support_level'] = self._calculate_support_level(df)
        df['resistance_level'] = self._calculate_resistance_level(df)
        df['support_distance'] = (df['close'] - df['support_level']) / df['close']
        df['resistance_distance'] = (df['resistance_level'] - df['close']) / df['close']
        
        return df
    
    def _detect_head_shoulders(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Head and Shoulders pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Find local maxima
            left_shoulder = df['high'].iloc[i-window:i].max()
            head = df['high'].iloc[i-window//2:i+window//2].max()
            right_shoulder = df['high'].iloc[i:i+window].max()
            
            # Check if head is higher than shoulders
            if head > left_shoulder and head > right_shoulder:
                # Check if shoulders are roughly equal
                if abs(left_shoulder - right_shoulder) / left_shoulder < 0.05:
                    pattern.iloc[i] = 1  # Head and Shoulders detected
        
        return pattern
    
    def _detect_double_top(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Double Top pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Find two peaks
            peak1 = df['high'].iloc[i-window:i].max()
            peak2 = df['high'].iloc[i:i+window].max()
            
            # Check if peaks are roughly equal
            if abs(peak1 - peak2) / peak1 < 0.03:
                pattern.iloc[i] = 1  # Double Top detected
        
        return pattern
    
    def _detect_double_bottom(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Double Bottom pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Find two troughs
            trough1 = df['low'].iloc[i-window:i].min()
            trough2 = df['low'].iloc[i:i+window].min()
            
            # Check if troughs are roughly equal
            if abs(trough1 - trough2) / trough1 < 0.03:
                pattern.iloc[i] = 1  # Double Bottom detected
        
        return pattern
    
    def _detect_ascending_triangle(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Ascending Triangle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for horizontal resistance and ascending support
            resistance = df['high'].iloc[i-window:i+window].max()
            support_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            # Resistance should be relatively flat, support should be ascending
            if support_trend > 0 and abs(resistance - df['high'].iloc[i-window:i].mean()) / resistance < 0.02:
                pattern.iloc[i] = 1  # Ascending Triangle detected
        
        return pattern
    
    def _detect_descending_triangle(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Descending Triangle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for horizontal support and descending resistance
            support = df['low'].iloc[i-window:i+window].min()
            resistance_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            
            # Support should be relatively flat, resistance should be descending
            if resistance_trend < 0 and abs(support - df['low'].iloc[i-window:i].mean()) / support < 0.02:
                pattern.iloc[i] = 1  # Descending Triangle detected
        
        return pattern
    
    def _detect_symmetrical_triangle(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Symmetrical Triangle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for converging trend lines
            high_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            low_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            # Both trend lines should be converging
            if high_trend < 0 and low_trend > 0:
                pattern.iloc[i] = 1  # Symmetrical Triangle detected
        
        return pattern
    
    def _detect_bull_flag(self, df: pd.DataFrame, window: int = 15) -> pd.Series:
        """Detect Bull Flag pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for strong upward move followed by consolidation
            initial_move = (df['close'].iloc[i-window] - df['close'].iloc[i-window*2]) / df['close'].iloc[i-window*2]
            consolidation_range = (df['high'].iloc[i-window:i+window].max() - df['low'].iloc[i-window:i+window].min()) / df['close'].iloc[i]
            
            if initial_move > 0.05 and consolidation_range < 0.03:
                pattern.iloc[i] = 1  # Bull Flag detected
        
        return pattern
    
    def _detect_bear_flag(self, df: pd.DataFrame, window: int = 15) -> pd.Series:
        """Detect Bear Flag pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for strong downward move followed by consolidation
            initial_move = (df['close'].iloc[i-window] - df['close'].iloc[i-window*2]) / df['close'].iloc[i-window*2]
            consolidation_range = (df['high'].iloc[i-window:i+window].max() - df['low'].iloc[i-window:i+window].min()) / df['close'].iloc[i]
            
            if initial_move < -0.05 and consolidation_range < 0.03:
                pattern.iloc[i] = 1  # Bear Flag detected
        
        return pattern
    
    def _calculate_support_level(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate dynamic support level"""
        return df['low'].rolling(window).min()
    
    def _calculate_resistance_level(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate dynamic resistance level"""
        return df['high'].rolling(window).max()
    
    def _add_volume_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add comprehensive volume analysis features"""
        # Volume moving averages
        df['volume_sma_5'] = df['volume'].rolling(5).mean()
        df['volume_sma_20'] = df['volume'].rolling(20).mean()
        df['volume_sma_50'] = df['volume'].rolling(50).mean()
        
        # Volume ratios
        df['volume_ratio_5'] = df['volume'] / df['volume_sma_5']
        df['volume_ratio_20'] = df['volume'] / df['volume_sma_20']
        df['volume_ratio_50'] = df['volume'] / df['volume_sma_50']
        
        # Volume spikes
        df['volume_spike'] = (df['volume'] > df['volume_sma_20'] * 2).astype(int)
        df['volume_drought'] = (df['volume'] < df['volume_sma_20'] * 0.5).astype(int)
        
        # Volume trend
        df['volume_trend'] = df['volume'].rolling(10).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        
        # Price-Volume relationship
        df['price_volume_trend'] = df['price_change'] * df['volume_ratio_20']
        df['volume_price_correlation'] = df['price_change'].rolling(20).corr(df['volume_ratio_20'])
        
        # Volume profile features
        df['volume_at_price'] = df['volume'] * df['body_size']
        df['volume_weighted_price'] = (df['volume'] * df['close']).rolling(20).sum() / df['volume'].rolling(20).sum()
        
        return df
    
    def _add_price_action_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price action and candlestick pattern features"""
        # Candlestick patterns
        df['doji'] = (abs(df['close'] - df['open']) / df['close'] < 0.001).astype(int)
        df['hammer'] = ((df['lower_shadow'] > 2 * df['body_size']) & 
                       (df['upper_shadow'] < df['body_size'])).astype(int)
        df['shooting_star'] = ((df['upper_shadow'] > 2 * df['body_size']) & 
                             (df['lower_shadow'] < df['body_size'])).astype(int)
        
        # Engulfing patterns
        df['bullish_engulfing'] = ((df['close'] > df['open']) & 
                                  (df['close'].shift(1) < df['open'].shift(1)) &
                                  (df['open'] < df['close'].shift(1)) &
                                  (df['close'] > df['open'].shift(1))).astype(int)
        
        df['bearish_engulfing'] = ((df['close'] < df['open']) & 
                                  (df['close'].shift(1) > df['open'].shift(1)) &
                                  (df['open'] > df['close'].shift(1)) &
                                  (df['close'] < df['open'].shift(1))).astype(int)
        
        # Gap analysis
        df['gap_up'] = (df['open'] > df['close'].shift(1) * 1.01).astype(int)
        df['gap_down'] = (df['open'] < df['close'].shift(1) * 0.99).astype(int)
        
        # Price momentum
        df['price_momentum_1'] = df['close'].pct_change(1)
        df['price_momentum_3'] = df['close'].pct_change(3)
        df['price_momentum_5'] = df['close'].pct_change(5)
        df['price_momentum_10'] = df['close'].pct_change(10)
        
        # Volatility features
        df['volatility_5'] = df['price_change'].rolling(5).std()
        df['volatility_20'] = df['price_change'].rolling(20).std()
        df['volatility_ratio'] = df['volatility_5'] / df['volatility_20']
        
        # Trend strength
        df['trend_strength'] = abs(df['ema_short'] - df['ema_long']) / df['ema_long']
        df['trend_direction'] = np.where(df['ema_short'] > df['ema_long'], 1, -1)
        
        return df
    
    def _add_market_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market regime classification"""
        # Calculate regime indicators
        volatility = df['price_change'].rolling(20).std()
        trend_strength = abs(df['ema_short'] - df['ema_long']) / df['ema_long']
        volume_ratio = df['volume'] / df['volume_sma_20']
        
        # Classify market regimes
        df['market_regime'] = 0  # Default: Normal
        
        # Trending market
        df.loc[(trend_strength > 0.02) & (volatility > 0.01), 'market_regime'] = 1
        
        # Volatile market
        df.loc[(volatility > 0.03) & (volume_ratio > 1.5), 'market_regime'] = 2
        
        # Low volatility market
        df.loc[(volatility < 0.01) & (trend_strength < 0.01), 'market_regime'] = 3
        
        # High volume breakout
        df.loc[(volume_ratio > 2.0) & (volatility > 0.02), 'market_regime'] = 4
        
        return df
    
    def _save_comprehensive_cache(self, data: Dict[str, Dict[str, pd.DataFrame]]):
        """Save comprehensive data cache"""
        cache_path = os.path.join(self.cache_dir, "comprehensive_data.pkl")
        import pickle
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"💾 Comprehensive data cache saved to {cache_path}")
    
    def load_comprehensive_cache(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Load comprehensive data cache"""
        cache_path = os.path.join(self.cache_dir, "comprehensive_data.pkl")
        if os.path.exists(cache_path):
            import pickle
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            print(f"📂 Loaded comprehensive data cache: {len(data)} symbols")
            return data
        else:
            print("📂 No comprehensive data cache found")
            return {}
    
    def train_models_with_historical_data(self, symbols: List[str], 
                                        use_advanced: bool = True) -> Dict[str, Any]:
        """Train models using comprehensive historical data"""
        print(f"🤖 Training models with historical data for {len(symbols)} symbols...")
        
        # Load or collect data
        comprehensive_data = self.load_comprehensive_cache()
        if not comprehensive_data:
            comprehensive_data = self.collect_comprehensive_data(symbols)
        
        training_results = {}
        
        for symbol in symbols:
            if symbol not in comprehensive_data:
                print(f"⚠️ No data available for {symbol}")
                continue
            
            print(f"\n🎯 Training models for {symbol}...")
            
            # Use daily data for training (most reliable)
            if '1d' in comprehensive_data[symbol]:
                training_data = comprehensive_data[symbol]['1d']
            else:
                # Use the longest timeframe available
                longest_timeframe = max(comprehensive_data[symbol].keys(), 
                                      key=lambda x: len(comprehensive_data[symbol][x]))
                training_data = comprehensive_data[symbol][longest_timeframe]
            
            if len(training_data) < self.min_data_points:
                print(f"⚠️ Insufficient data for {symbol}: {len(training_data)} < {self.min_data_points}")
                continue
            
            try:
                # Train with standard AI engine
                print(f"   🔧 Training standard AI models...")
                self.ai_engine.train_models(training_data, symbol)
                self.ai_engine.save_models(symbol)
                
                # Train with advanced AI engine
                if use_advanced:
                    print(f"   🚀 Training advanced AI models...")
                    self.advanced_ai_engine.train_advanced_models(training_data, symbol)
                    self.advanced_ai_engine.save_advanced_models(symbol)
                
                # Get performance summary
                standard_perf = self.ai_engine.get_performance_summary()
                advanced_perf = self.advanced_ai_engine.get_advanced_performance_summary() if use_advanced else {}
                
                training_results[symbol] = {
                    'data_points': len(training_data),
                    'timeframes_available': list(comprehensive_data[symbol].keys()),
                    'standard_performance': standard_perf,
                    'advanced_performance': advanced_perf,
                    'training_completed': True
                }
                
                print(f"   ✅ {symbol}: Training completed successfully")
                
            except Exception as e:
                print(f"   ❌ {symbol}: Training failed - {e}")
                training_results[symbol] = {
                    'training_completed': False,
                    'error': str(e)
                }
        
        # Save training results
        self.training_results = training_results
        self._save_training_results(training_results)
        
        print(f"\n🎯 Historical training complete!")
        print(f"   Symbols trained: {sum(1 for r in training_results.values() if r.get('training_completed', False))}")
        print(f"   Total symbols: {len(training_results)}")
        
        return training_results
    
    def _save_training_results(self, results: Dict[str, Any]):
        """Save training results"""
        results_path = os.path.join(self.cache_dir, "training_results.pkl")
        import pickle
        with open(results_path, 'wb') as f:
            pickle.dump(results, f)
        print(f"💾 Training results saved to {results_path}")
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary"""
        return {
            'system_info': {
                'name': self.name,
                'description': self.description,
                'timeframes': self.timeframes,
                'historical_years': self.historical_years,
                'min_data_points': self.min_data_points
            },
            'training_results': self.training_results,
            'data_directory': self.data_dir,
            'models_directory': self.models_dir,
            'cache_directory': self.cache_dir
        }

def run_comprehensive_training():
    """Main function to run comprehensive historical training"""
    print("🚀 Comprehensive Historical Training System")
    print("=" * 60)
    
    # Initialize trainer
    trainer = HistoricalTrainer()
    
    # Symbols to train
    symbols = config.SYMBOLS  # Use symbols from config
    
    # Run comprehensive training
    results = trainer.train_models_with_historical_data(symbols, use_advanced=True)
    
    # Display summary
    summary = trainer.get_training_summary()
    print(f"\n📊 Training Summary:")
    print(f"   System: {summary['system_info']['name']}")
    print(f"   Symbols processed: {len(results)}")
    print(f"   Successful trainings: {sum(1 for r in results.values() if r.get('training_completed', False))}")
    print(f"   Data directory: {summary['data_directory']}")
    print(f"   Models directory: {summary['models_directory']}")
    
    print(f"\n✅ Comprehensive historical training complete!")
    print(f"Your AI models now have extensive historical data to learn from!")

if __name__ == "__main__":
    run_comprehensive_training()
