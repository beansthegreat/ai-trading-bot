#!/usr/bin/env python3
"""
🧠 Advanced AI Trading Engine
Enhanced with more sophisticated models and features
"""

import pandas as pd
import numpy as np
import joblib
import mlflow
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Advanced ML libraries
try:
    import xgboost as xgb
    from xgboost import XGBClassifier, XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    from lightgbm import LGBMClassifier, LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier, CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.decomposition import PCA

from utils.logger import trading_logger
from utils.indicators import TechnicalIndicators
from config import config

class AdvancedAIEngine:
    """Advanced AI Trading Engine with sophisticated models"""
    
    def __init__(self):
        self.name = "Advanced AI Trading Engine"
        self.description = "Sophisticated AI with ensemble learning and feature engineering"
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.feature_names = []
        
        # GPU configuration
        self.use_gpu = self._check_gpu_availability()
        self.gpu_params = self._get_gpu_params()
        
        # Advanced features
        self.use_feature_selection = True
        self.use_pca = False
        self.use_ensemble_voting = True
        self.cross_validation_folds = 5
        
        # Performance tracking
        self.model_performance = {}
        self.feature_importance = {}
        self.last_training_time = None
        self.training_data_size = 0
        
        # Initialize MLflow
        self._setup_mlflow()
        
        trading_logger.info("Advanced AI Engine initialized", 
                           gpu_available=self.use_gpu,
                           feature_selection=self.use_feature_selection,
                           ensemble_voting=self.use_ensemble_voting)
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            if XGBOOST_AVAILABLE:
                test_data = np.random.random((100, 10))
                test_labels = np.random.randint(0, 3, 100)
                
                model = XGBClassifier(
                    n_estimators=10,
                    tree_method='gpu_hist',
                    gpu_id=0,
                    random_state=42
                )
                model.fit(test_data, test_labels)
                return True
        except Exception as e:
            trading_logger.warning(f"GPU acceleration not available: {e}")
        
        return False
    
    def _get_gpu_params(self) -> Dict[str, Any]:
        """Get GPU-optimized parameters"""
        if self.use_gpu:
            return {
                'xgboost': {
                    'tree_method': 'gpu_hist',
                    'gpu_id': 0,
                    'predictor': 'gpu_predictor'
                },
                'lightgbm': {
                    'device': 'gpu',
                    'gpu_platform_id': 0,
                    'gpu_device_id': 0
                },
                'catboost': {
                    'task_type': 'GPU',
                    'devices': '0'
                }
            }
        else:
            return {
                'xgboost': {
                    'tree_method': 'hist',
                    'predictor': 'cpu_predictor'
                },
                'lightgbm': {
                    'device': 'cpu'
                },
                'catboost': {
                    'task_type': 'CPU'
                }
            }
    
    def _setup_mlflow(self):
        """Setup MLflow for model tracking"""
        try:
            mlflow.set_tracking_uri("file:./mlruns")
            mlflow.set_experiment("advanced_trading_ai")
            trading_logger.info("Advanced MLflow tracking initialized")
        except Exception as e:
            trading_logger.warning(f"MLflow setup failed: {e}")
    
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced features for AI models"""
        if len(df) < 100:
            return pd.DataFrame()
        
        # Calculate all technical indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Create advanced AI features
        advanced_features = self._create_advanced_features(df_with_indicators)
        
        # Combine all features
        all_features = pd.concat([df_with_indicators, advanced_features], axis=1)
        
        # Store feature names
        self.feature_names = [col for col in all_features.columns 
                             if col not in ['open', 'high', 'low', 'close', 'volume', 'symbol', 'timeframe']]
        
        return all_features
    
    def _create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced AI-specific features"""
        features = pd.DataFrame(index=df.index)
        
        # Advanced price features
        features['price_acceleration'] = df['close'].pct_change().diff()
        features['price_jerk'] = features['price_acceleration'].diff()
        features['price_momentum_ratio'] = df['close'].pct_change(5) / df['close'].pct_change(1)
        
        # Advanced volume features
        features['volume_price_trend'] = (df['volume'] * df['close']).pct_change()
        features['volume_force'] = df['volume'] * abs(df['close'].pct_change())
        features['volume_surge'] = df['volume'] / df['volume'].rolling(50).mean()
        
        # Advanced volatility features
        features['realized_volatility'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
        features['volatility_of_volatility'] = features['realized_volatility'].rolling(10).std()
        features['volatility_regime_change'] = features['realized_volatility'].diff()
        
        # Advanced trend features
        features['trend_strength_ratio'] = abs(df['ema_short'] - df['ema_long']) / df['close']
        features['trend_acceleration'] = features['trend_strength_ratio'].diff()
        features['trend_reversal_probability'] = self._calculate_trend_reversal_probability(df)
        
        # Advanced momentum features
        features['rsi_divergence'] = self._calculate_rsi_divergence(df)
        features['macd_divergence'] = self._calculate_macd_divergence(df)
        features['momentum_consensus'] = self._calculate_momentum_consensus(df)
        
        # Advanced support/resistance features
        features['support_strength'] = self._calculate_support_strength(df)
        features['resistance_strength'] = self._calculate_resistance_strength(df)
        features['breakout_probability'] = self._calculate_breakout_probability(df)
        
        # Advanced market microstructure features
        features['bid_ask_spread_estimate'] = (df['high'] - df['low']) / df['close']
        features['price_efficiency'] = self._calculate_price_efficiency(df)
        features['market_impact'] = self._calculate_market_impact(df)
        
        # Advanced time-based features
        features['intraday_pattern'] = self._calculate_intraday_pattern(df)
        features['weekly_pattern'] = self._calculate_weekly_pattern(df)
        features['monthly_pattern'] = self._calculate_monthly_pattern(df)
        
        # Advanced regime features
        features['market_regime_advanced'] = self._calculate_advanced_market_regime(df)
        features['volatility_regime_advanced'] = self._calculate_advanced_volatility_regime(df)
        features['liquidity_regime'] = self._calculate_liquidity_regime(df)
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
    
    def _calculate_trend_reversal_probability(self, df: pd.DataFrame) -> pd.Series:
        """Calculate probability of trend reversal"""
        # Simple implementation - can be enhanced
        rsi = df.get('rsi', pd.Series(50, index=df.index))
        macd_hist = df.get('macd_histogram', pd.Series(0, index=df.index))
        
        # Higher probability when RSI is extreme and MACD shows divergence
        reversal_prob = pd.Series(0.5, index=df.index)
        
        # Oversold/overbought conditions
        reversal_prob.loc[rsi < 20] += 0.2
        reversal_prob.loc[rsi > 80] += 0.2
        
        # MACD divergence
        reversal_prob.loc[macd_hist < 0] += 0.1
        
        return reversal_prob.clip(0, 1)
    
    def _calculate_rsi_divergence(self, df: pd.DataFrame) -> pd.Series:
        """Calculate RSI divergence"""
        rsi = df.get('rsi', pd.Series(50, index=df.index))
        price = df['close']
        
        # Simple divergence detection
        rsi_ma = rsi.rolling(14).mean()
        price_ma = price.rolling(14).mean()
        
        divergence = pd.Series(0, index=df.index)
        
        # Bullish divergence: price lower, RSI higher
        divergence.loc[(price < price_ma) & (rsi > rsi_ma)] = 1
        
        # Bearish divergence: price higher, RSI lower
        divergence.loc[(price > price_ma) & (rsi < rsi_ma)] = -1
        
        return divergence
    
    def _calculate_macd_divergence(self, df: pd.DataFrame) -> pd.Series:
        """Calculate MACD divergence"""
        macd = df.get('macd', pd.Series(0, index=df.index))
        price = df['close']
        
        # Simple divergence detection
        macd_ma = macd.rolling(12).mean()
        price_ma = price.rolling(12).mean()
        
        divergence = pd.Series(0, index=df.index)
        
        # Bullish divergence
        divergence.loc[(price < price_ma) & (macd > macd_ma)] = 1
        
        # Bearish divergence
        divergence.loc[(price > price_ma) & (macd < macd_ma)] = -1
        
        return divergence
    
    def _calculate_momentum_consensus(self, df: pd.DataFrame) -> pd.Series:
        """Calculate momentum consensus across multiple indicators"""
        rsi = df.get('rsi', pd.Series(50, index=df.index))
        macd = df.get('macd', pd.Series(0, index=df.index))
        stoch = df.get('stoch_k', pd.Series(50, index=df.index))
        
        consensus = pd.Series(0, index=df.index)
        
        # Count bullish signals
        bullish_count = 0
        bullish_count += (rsi < 30).astype(int)
        bullish_count += (macd > 0).astype(int)
        bullish_count += (stoch < 20).astype(int)
        
        # Count bearish signals
        bearish_count = 0
        bearish_count += (rsi > 70).astype(int)
        bearish_count += (macd < 0).astype(int)
        bearish_count += (stoch > 80).astype(int)
        
        consensus = bullish_count - bearish_count
        return consensus / 3  # Normalize to [-1, 1]
    
    def _calculate_support_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate support level strength"""
        low = df['low']
        close = df['close']
        
        # Find recent support levels
        support_levels = low.rolling(20).min()
        
        # Calculate distance to support
        distance_to_support = (close - support_levels) / close
        
        # Strength based on proximity and volume
        volume_ratio = df['volume'] / df['volume'].rolling(20).mean()
        support_strength = 1 / (1 + distance_to_support) * volume_ratio
        
        return support_strength.fillna(0)
    
    def _calculate_resistance_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate resistance level strength"""
        high = df['high']
        close = df['close']
        
        # Find recent resistance levels
        resistance_levels = high.rolling(20).max()
        
        # Calculate distance to resistance
        distance_to_resistance = (resistance_levels - close) / close
        
        # Strength based on proximity and volume
        volume_ratio = df['volume'] / df['volume'].rolling(20).mean()
        resistance_strength = 1 / (1 + distance_to_resistance) * volume_ratio
        
        return resistance_strength.fillna(0)
    
    def _calculate_breakout_probability(self, df: pd.DataFrame) -> pd.Series:
        """Calculate probability of breakout"""
        bb_upper = df.get('bb_upper', df['close'] * 1.02)
        bb_lower = df.get('bb_lower', df['close'] * 0.98)
        close = df['close']
        
        # Distance from bands
        upper_distance = (bb_upper - close) / close
        lower_distance = (close - bb_lower) / close
        
        # Volume confirmation
        volume_surge = df['volume'] / df['volume'].rolling(20).mean()
        
        # Breakout probability
        breakout_prob = pd.Series(0.5, index=df.index)
        
        # Near upper band with volume
        breakout_prob.loc[(upper_distance < 0.01) & (volume_surge > 1.5)] += 0.3
        
        # Near lower band with volume
        breakout_prob.loc[(lower_distance < 0.01) & (volume_surge > 1.5)] += 0.3
        
        return breakout_prob.clip(0, 1)
    
    def _calculate_price_efficiency(self, df: pd.DataFrame) -> pd.Series:
        """Calculate price efficiency (how random vs trending)"""
        returns = df['close'].pct_change()
        
        # Variance ratio test (simplified)
        var_1 = returns.rolling(5).var()
        var_5 = returns.rolling(25).var()
        
        efficiency = var_1 / var_5
        return efficiency.fillna(1)
    
    def _calculate_market_impact(self, df: pd.DataFrame) -> pd.Series:
        """Calculate estimated market impact"""
        volume = df['volume']
        price = df['close']
        
        # Simple market impact model
        impact = (volume / volume.rolling(20).mean()) * (price / price.rolling(20).mean())
        return impact.fillna(1)
    
    def _calculate_intraday_pattern(self, df: pd.DataFrame) -> pd.Series:
        """Calculate intraday trading pattern"""
        hour = pd.to_datetime(df.index).hour
        
        # Morning momentum (9-11 AM)
        morning_pattern = ((hour >= 9) & (hour <= 11)).astype(int)
        
        # Lunch lull (11-2 PM)
        lunch_pattern = ((hour >= 11) & (hour <= 14)).astype(int)
        
        # Afternoon activity (2-4 PM)
        afternoon_pattern = ((hour >= 14) & (hour <= 16)).astype(int)
        
        return morning_pattern + afternoon_pattern - lunch_pattern
    
    def _calculate_weekly_pattern(self, df: pd.DataFrame) -> pd.Series:
        """Calculate weekly trading pattern"""
        day_of_week = pd.to_datetime(df.index).dayofweek
        
        # Monday blues, Friday optimism
        pattern = pd.Series(0, index=df.index)
        pattern.loc[day_of_week == 0] = -0.2  # Monday
        pattern.loc[day_of_week == 4] = 0.2   # Friday
        
        return pattern
    
    def _calculate_monthly_pattern(self, df: pd.DataFrame) -> pd.Series:
        """Calculate monthly trading pattern"""
        day_of_month = pd.to_datetime(df.index).day
        
        # Month-end effects
        pattern = pd.Series(0, index=df.index)
        pattern.loc[day_of_month >= 25] = 0.1  # Month-end
        
        return pattern
    
    def _calculate_advanced_market_regime(self, df: pd.DataFrame) -> pd.Series:
        """Calculate advanced market regime classification"""
        adx = df.get('adx', pd.Series(25, index=df.index))
        volatility = df['close'].pct_change().rolling(20).std()
        volume_ratio = df['volume'] / df['volume'].rolling(20).mean()
        
        regime = pd.Series(0, index=df.index)  # Normal
        
        # Strong trend
        regime.loc[(adx > 30) & (volatility > 0.02)] = 1
        
        # High volatility
        regime.loc[(volatility > 0.03) & (volume_ratio > 1.5)] = 2
        
        # Low volatility
        regime.loc[(volatility < 0.015) & (adx < 20)] = 3
        
        return regime
    
    def _calculate_advanced_volatility_regime(self, df: pd.DataFrame) -> pd.Series:
        """Calculate advanced volatility regime"""
        volatility = df['close'].pct_change().rolling(20).std()
        vol_of_vol = volatility.rolling(10).std()
        
        regime = pd.Series(1, index=df.index)  # Medium
        
        # Low volatility
        regime.loc[volatility < 0.015] = 0
        
        # High volatility
        regime.loc[volatility > 0.03] = 2
        
        # Volatility clustering
        regime.loc[vol_of_vol > 0.01] = 3
        
        return regime
    
    def _calculate_liquidity_regime(self, df: pd.DataFrame) -> pd.Series:
        """Calculate liquidity regime"""
        volume = df['volume']
        price = df['close']
        
        # Average trade size
        avg_trade_size = (volume * price).rolling(20).mean()
        
        # Liquidity regime
        regime = pd.Series(1, index=df.index)  # Normal
        
        # High liquidity
        regime.loc[avg_trade_size > avg_trade_size.quantile(0.8)] = 2
        
        # Low liquidity
        regime.loc[avg_trade_size < avg_trade_size.quantile(0.2)] = 0
        
        return regime
    
    def create_advanced_labels(self, df: pd.DataFrame, lookahead: int = 5) -> pd.Series:
        """Create advanced labels for supervised learning"""
        # Calculate future returns
        future_returns = df['close'].shift(-lookahead) / df['close'] - 1
        
        # Create labels: 0=hold, 1=buy, 2=sell
        labels = pd.Series(0, index=df.index)  # Default to hold
        
        # Buy signal: future return > 1%
        labels.loc[future_returns > 0.01] = 1
        
        # Sell signal: future return < -1%
        labels.loc[future_returns < -0.01] = 2
        
        return labels
    
    def train_advanced_models(self, df: pd.DataFrame, symbol: str = "UNKNOWN"):
        """Train advanced AI models with sophisticated techniques"""
        if len(df) < 200:
            trading_logger.warning(f"Insufficient data for advanced training: {len(df)} samples")
            return
        
        # Create features and labels
        features_df = self.create_advanced_features(df)
        labels = self.create_advanced_labels(df)
        
        # Remove rows with NaN values
        valid_mask = ~(features_df.isna().any(axis=1) | labels.isna())
        features_df = features_df[valid_mask]
        labels = labels[valid_mask]
        
        if len(features_df) < 100:
            trading_logger.warning(f"Not enough valid data for advanced training: {len(features_df)} samples")
            return
        
        # Prepare training data
        X = features_df[self.feature_names].values
        y = labels.values
        
        # Handle infinity and extreme values
        X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
        y = np.nan_to_num(y, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Feature scaling
        scaler = RobustScaler()  # More robust to outliers
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[symbol] = scaler
        
        # Feature selection
        if self.use_feature_selection:
            feature_selector = SelectKBest(score_func=f_classif, k=min(50, len(self.feature_names)))
            X_train_selected = feature_selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = feature_selector.transform(X_test_scaled)
            
            self.feature_selectors[symbol] = feature_selector
            selected_features = feature_selector.get_support()
            self.feature_importance[symbol] = dict(zip(self.feature_names, selected_features))
        else:
            X_train_selected = X_train_scaled
            X_test_selected = X_test_scaled
        
        # Train advanced models
        self._train_advanced_xgboost(X_train_selected, X_test_selected, y_train, y_test, symbol)
        self._train_advanced_lightgbm(X_train_selected, X_test_selected, y_train, y_test, symbol)
        self._train_advanced_catboost(X_train_selected, X_test_selected, y_train, y_test, symbol)
        self._train_neural_network(X_train_selected, X_test_selected, y_train, y_test, symbol)
        self._train_ensemble_model(X_train_selected, X_test_selected, y_train, y_test, symbol)
        
        # Log training results
        self.training_data_size = len(X_train)
        self.last_training_time = datetime.now()
        
        trading_logger.success(f"Advanced AI models trained for {symbol}", 
                              data_size=len(X_train),
                              feature_count=len(self.feature_names),
                              gpu_used=self.use_gpu)
    
    def _train_advanced_xgboost(self, X_train, X_test, y_train, y_test, symbol):
        """Train advanced XGBoost model"""
        if not XGBOOST_AVAILABLE:
            return
        
        try:
            # Advanced parameters
            params = {
                'n_estimators': 200,
                'max_depth': 8,
                'learning_rate': 0.05,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'random_state': 42,
                **self.gpu_params['xgboost']
            }
            
            model = XGBClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_advanced_xgboost"] = model
            self.model_performance[f"{symbol}_advanced_xgboost"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"Advanced XGBoost trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}",
                               gpu_used=self.use_gpu)
            
        except Exception as e:
            trading_logger.error(f"Advanced XGBoost training failed for {symbol}: {e}")
    
    def _train_advanced_lightgbm(self, X_train, X_test, y_train, y_test, symbol):
        """Train advanced LightGBM model"""
        if not LIGHTGBM_AVAILABLE:
            return
        
        try:
            # Advanced parameters
            params = {
                'n_estimators': 200,
                'max_depth': 8,
                'learning_rate': 0.05,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'random_state': 42,
                **self.gpu_params['lightgbm']
            }
            
            model = LGBMClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_advanced_lightgbm"] = model
            self.model_performance[f"{symbol}_advanced_lightgbm"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"Advanced LightGBM trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}",
                               gpu_used=self.use_gpu)
            
        except Exception as e:
            trading_logger.error(f"Advanced LightGBM training failed for {symbol}: {e}")
    
    def _train_advanced_catboost(self, X_train, X_test, y_train, y_test, symbol):
        """Train advanced CatBoost model"""
        if not CATBOOST_AVAILABLE:
            return
        
        try:
            # Advanced parameters
            params = {
                'iterations': 200,
                'depth': 8,
                'learning_rate': 0.05,
                'random_state': 42,
                'verbose': False,
                **self.gpu_params['catboost']
            }
            
            model = CatBoostClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_advanced_catboost"] = model
            self.model_performance[f"{symbol}_advanced_catboost"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"Advanced CatBoost trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}",
                               gpu_used=self.use_gpu)
            
        except Exception as e:
            trading_logger.error(f"Advanced CatBoost training failed for {symbol}: {e}")
    
    def _train_neural_network(self, X_train, X_test, y_train, y_test, symbol):
        """Train neural network model"""
        try:
            # Neural network parameters
            params = {
                'hidden_layer_sizes': (100, 50, 25),
                'activation': 'relu',
                'solver': 'adam',
                'alpha': 0.001,
                'learning_rate': 'adaptive',
                'max_iter': 500,
                'random_state': 42
            }
            
            model = MLPClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_neural_network"] = model
            self.model_performance[f"{symbol}_neural_network"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"Neural Network trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}")
            
        except Exception as e:
            trading_logger.error(f"Neural Network training failed for {symbol}: {e}")
    
    def _train_ensemble_model(self, X_train, X_test, y_train, y_test, symbol):
        """Train ensemble voting model"""
        try:
            # Create base models
            base_models = []
            
            if XGBOOST_AVAILABLE:
                xgb_model = XGBClassifier(n_estimators=100, random_state=42, **self.gpu_params['xgboost'])
                base_models.append(('xgb', xgb_model))
            
            if LIGHTGBM_AVAILABLE:
                lgb_model = LGBMClassifier(n_estimators=100, random_state=42, **self.gpu_params['lightgbm'])
                base_models.append(('lgb', lgb_model))
            
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            base_models.append(('rf', rf_model))
            
            # Create voting ensemble
            ensemble = VotingClassifier(estimators=base_models, voting='soft')
            ensemble.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = ensemble.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_ensemble"] = ensemble
            self.model_performance[f"{symbol}_ensemble"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"Ensemble model trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}")
            
        except Exception as e:
            trading_logger.error(f"Ensemble training failed for {symbol}: {e}")
    
    def predict_advanced(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """Make advanced predictions using all trained models"""
        if not self.models or symbol not in self.scalers:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No trained models'}
        
        # Create features
        features_df = self.create_advanced_features(df)
        if len(features_df) == 0:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Get latest features
        latest_features = features_df[self.feature_names].iloc[-1].values.reshape(1, -1)
        
        # Scale features
        scaler = self.scalers[symbol]
        latest_features_scaled = scaler.transform(latest_features)
        
        # Apply feature selection if used
        if symbol in self.feature_selectors:
            feature_selector = self.feature_selectors[symbol]
            latest_features_selected = feature_selector.transform(latest_features_scaled)
        else:
            latest_features_selected = latest_features_scaled
        
        # Make predictions with all models
        predictions = {}
        confidences = {}
        
        for model_name, model in self.models.items():
            if symbol in model_name:
                try:
                    pred = model.predict(latest_features_selected)[0]
                    proba = model.predict_proba(latest_features_selected)[0]
                    confidence = np.max(proba)
                    
                    predictions[model_name] = pred
                    confidences[model_name] = confidence
                    
                except Exception as e:
                    trading_logger.error(f"Advanced prediction failed for {model_name}: {e}")
        
        if not predictions:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No valid predictions'}
        
        # Advanced ensemble prediction
        ensemble_prediction = self._advanced_ensemble_predict(predictions, confidences)
        
        return ensemble_prediction
    
    def _advanced_ensemble_predict(self, predictions: Dict[str, int], confidences: Dict[str, float]) -> Dict[str, Any]:
        """Advanced ensemble prediction with weighted voting"""
        # Weight models by their confidence and performance
        weighted_predictions = {}
        
        for model_name, pred in predictions.items():
            confidence = confidences[model_name]
            
            # Get model performance weight
            performance_weight = 1.0
            if model_name in self.model_performance:
                perf = self.model_performance[model_name]
                performance_weight = perf.get('accuracy', 0.5)
            
            # Combined weight
            total_weight = confidence * performance_weight
            
            if pred not in weighted_predictions:
                weighted_predictions[pred] = 0
            weighted_predictions[pred] += total_weight
        
        # Get the most confident prediction
        if weighted_predictions:
            final_prediction = max(weighted_predictions.items(), key=lambda x: x[1])
            avg_confidence = np.mean(list(confidences.values()))
            
            # Convert prediction to signal
            signal_map = {0: 'neutral', 1: 'buy', 2: 'sell'}
            signal = signal_map.get(final_prediction[0], 'neutral')
            
            return {
                'signal': signal,
                'confidence': avg_confidence,
                'prediction': final_prediction[0],
                'model_predictions': predictions,
                'model_confidences': confidences,
                'weighted_score': final_prediction[1],
                'reason': f"Advanced AI ensemble: {signal} (confidence: {avg_confidence:.3f})"
            }
        
        return {'signal': 'neutral', 'confidence': 0, 'reason': 'No valid ensemble prediction'}
    
    def save_advanced_models(self, symbol: str):
        """Save advanced trained models to disk"""
        try:
            import os
            os.makedirs('advanced_models', exist_ok=True)
            
            # Save models
            for model_name, model in self.models.items():
                if symbol in model_name:
                    model_path = f"advanced_models/{model_name}.joblib"
                    joblib.dump(model, model_path)
            
            # Save scalers and selectors
            if symbol in self.scalers:
                scaler_path = f"advanced_models/{symbol}_scaler.joblib"
                joblib.dump(self.scalers[symbol], scaler_path)
            
            if symbol in self.feature_selectors:
                selector_path = f"advanced_models/{symbol}_selector.joblib"
                joblib.dump(self.feature_selectors[symbol], selector_path)
            
            trading_logger.success(f"Advanced models saved for {symbol}")
            
        except Exception as e:
            trading_logger.error(f"Failed to save advanced models for {symbol}: {e}")
    
    def load_advanced_models(self, symbol: str):
        """Load advanced trained models from disk"""
        try:
            import os
            # Load models
            model_files = [f for f in os.listdir('advanced_models') if f.startswith(symbol) and f.endswith('.joblib')]
            
            for model_file in model_files:
                model_name = model_file.replace('.joblib', '')
                model_path = f"advanced_models/{model_file}"
                model = joblib.load(model_path)
                self.models[model_name] = model
            
            # Load scaler
            scaler_path = f"advanced_models/{symbol}_scaler.joblib"
            if os.path.exists(scaler_path):
                self.scalers[symbol] = joblib.load(scaler_path)
            
            # Load selector
            selector_path = f"advanced_models/{symbol}_selector.joblib"
            if os.path.exists(selector_path):
                self.feature_selectors[symbol] = joblib.load(selector_path)
            
            trading_logger.success(f"Advanced models loaded for {symbol}")
            
        except Exception as e:
            trading_logger.error(f"Failed to load advanced models for {symbol}: {e}")
    
    def get_advanced_performance_summary(self) -> Dict[str, Any]:
        """Get advanced performance summary"""
        return {
            'total_models': len(self.models),
            'gpu_available': self.use_gpu,
            'feature_selection': self.use_feature_selection,
            'ensemble_voting': self.use_ensemble_voting,
            'last_training': self.last_training_time,
            'training_data_size': self.training_data_size,
            'model_performance': self.model_performance,
            'feature_importance': self.feature_importance
        }
