#!/usr/bin/env python3
"""
🤖 AI Trading Engine - GPU-Accelerated Machine Learning
Ultra-Intelligent Trading System with RTX 5070 Optimization
"""

import pandas as pd
import numpy as np
import joblib
import mlflow
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# GPU-optimized ML libraries
try:
    import xgboost as xgb
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost not available - falling back to CPU")

try:
    import lightgbm as lgb
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️ LightGBM not available - falling back to CPU")

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from utils.logger import trading_logger
from utils.indicators import TechnicalIndicators
from config import config

class AIEngine:
    """GPU-Accelerated AI Trading Engine"""
    
    def __init__(self):
        self.name = "GPU-Accelerated AI Trading Engine"
        self.description = "Ultra-intelligent trading with RTX 5070 optimization"
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        
        # GPU configuration
        self.use_gpu = self._check_gpu_availability()
        self.gpu_params = self._get_gpu_params()
        
        # Performance tracking
        self.model_performance = {}
        self.last_training_time = None
        self.training_data_size = 0
        
        # Initialize MLflow for model tracking
        self._setup_mlflow()
        
        trading_logger.info("AI Engine initialized", 
                           gpu_available=self.use_gpu,
                           gpu_params=self.gpu_params)
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            # Check XGBoost GPU support
            if XGBOOST_AVAILABLE:
                # Test GPU availability
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
                }
            }
    
    def _setup_mlflow(self):
        """Setup MLflow for model tracking"""
        try:
            mlflow.set_tracking_uri("file:./mlruns")
            mlflow.set_experiment("trading_ai_models")
            trading_logger.info("MLflow tracking initialized")
        except Exception as e:
            trading_logger.warning(f"MLflow setup failed: {e}")
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create enhanced features for AI models"""
        if len(df) < 50:
            return pd.DataFrame()
        
        # Calculate all technical indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Create AI-specific features
        ai_features = self._create_ai_features(df_with_indicators)
        
        # Combine all features
        all_features = pd.concat([df_with_indicators, ai_features], axis=1)
        
        # Store feature names for model training
        self.feature_names = [col for col in all_features.columns 
                             if col not in ['open', 'high', 'low', 'close', 'volume', 'symbol', 'timeframe']]
        
        return all_features
    
    def _create_ai_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create AI-specific features"""
        features = pd.DataFrame(index=df.index)
        
        # Price momentum features (micro-movements)
        features['price_momentum_1m'] = df['close'].pct_change(1)
        features['price_momentum_5m'] = df['close'].pct_change(5)
        features['price_momentum_15m'] = df['close'].pct_change(15)
        features['price_momentum_30m'] = df['close'].pct_change(30)
        
        # Volume momentum features
        features['volume_momentum_1m'] = df['volume'].pct_change(1)
        features['volume_momentum_5m'] = df['volume'].pct_change(5)
        features['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Volatility features
        features['volatility_1m'] = df['close'].pct_change().rolling(1).std()
        features['volatility_5m'] = df['close'].pct_change().rolling(5).std()
        features['volatility_15m'] = df['close'].pct_change().rolling(15).std()
        
        # Trend strength features
        features['trend_strength'] = abs(df['ema_short'] - df['ema_long']) / df['ema_long']
        features['trend_direction'] = np.where(df['ema_short'] > df['ema_long'], 1, -1)
        
        # RSI momentum features
        features['rsi_momentum'] = df['rsi'].diff()
        features['rsi_acceleration'] = df['rsi'].diff().diff()
        
        # MACD features
        features['macd_momentum'] = df['macd'].diff()
        features['macd_crossover'] = np.where(df['macd'] > df['macd_signal'], 1, -1)
        
        # Bollinger Band features
        features['bb_squeeze'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        features['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Support/Resistance features
        features['support_level'] = df['low'].rolling(20).min()
        features['resistance_level'] = df['high'].rolling(20).max()
        features['support_distance'] = (df['close'] - features['support_level']) / df['close']
        features['resistance_distance'] = (features['resistance_level'] - df['close']) / df['close']
        
        # Market regime features
        features['market_regime'] = self._calculate_market_regime(df)
        features['volatility_regime'] = self._calculate_volatility_regime(df)
        
        # Time-based features
        features['hour_of_day'] = pd.to_datetime(df.index).hour
        features['day_of_week'] = pd.to_datetime(df.index).dayofweek
        features['is_market_open'] = ((features['hour_of_day'] >= 9) & 
                                    (features['hour_of_day'] < 16)).astype(int)
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
    
    def _calculate_market_regime(self, df: pd.DataFrame) -> pd.Series:
        """Calculate market regime (trending, choppy, volatile, stable)"""
        # Use ADX for trend strength
        adx = df.get('adx', pd.Series(25, index=df.index))
        
        # Use volatility for regime classification
        volatility = df['close'].pct_change().rolling(20).std()
        
        regime = pd.Series('stable', index=df.index)
        
        # Trending market
        regime.loc[(adx > 25) & (volatility > 0.02)] = 'trending'
        
        # Volatile market
        regime.loc[(adx < 20) & (volatility > 0.03)] = 'volatile'
        
        # Choppy market
        regime.loc[(adx < 20) & (volatility < 0.02)] = 'choppy'
        
        # Convert to numeric
        regime_map = {'stable': 0, 'choppy': 1, 'volatile': 2, 'trending': 3}
        return regime.map(regime_map)
    
    def _calculate_volatility_regime(self, df: pd.DataFrame) -> pd.Series:
        """Calculate volatility regime"""
        volatility = df['close'].pct_change().rolling(20).std()
        
        regime = pd.Series(1, index=df.index)  # Medium volatility
        
        # Low volatility
        regime.loc[volatility < 0.015] = 0
        
        # High volatility
        regime.loc[volatility > 0.03] = 2
        
        return regime
    
    def create_labels(self, df: pd.DataFrame, lookahead: int = 5) -> pd.Series:
        """Create labels for supervised learning"""
        # Calculate future returns
        future_returns = df['close'].shift(-lookahead) / df['close'] - 1
        
        # Create labels: 0=hold, 1=buy, 2=sell
        labels = pd.Series(0, index=df.index)  # Default to hold
        
        # Buy signal: future return > 1%
        labels.loc[future_returns > 0.01] = 1
        
        # Sell signal: future return < -1%
        labels.loc[future_returns < -0.01] = 2
        
        return labels
    
    def train_models(self, df: pd.DataFrame, symbol: str = "UNKNOWN"):
        """Train all AI models with GPU acceleration"""
        if len(df) < 100:
            trading_logger.warning(f"Insufficient data for training: {len(df)} samples")
            return
        
        # Create features and labels
        features_df = self.create_features(df)
        labels = self.create_labels(df)
        
        # Remove rows with NaN values
        valid_mask = ~(features_df.isna().any(axis=1) | labels.isna())
        features_df = features_df[valid_mask]
        labels = labels[valid_mask]
        
        if len(features_df) < 50:
            trading_logger.warning(f"Not enough valid data for training: {len(features_df)} samples")
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
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[symbol] = scaler
        
        # Train models with GPU acceleration
        self._train_xgboost_model(X_train_scaled, X_test_scaled, y_train, y_test, symbol)
        self._train_lightgbm_model(X_train_scaled, X_test_scaled, y_train, y_test, symbol)
        self._train_random_forest_model(X_train_scaled, X_test_scaled, y_train, y_test, symbol)
        
        # Log training results
        self.training_data_size = len(X_train)
        self.last_training_time = datetime.now()
        
        trading_logger.success(f"AI models trained for {symbol}", 
                              data_size=len(X_train),
                              feature_count=len(self.feature_names),
                              gpu_used=self.use_gpu)
    
    def _train_xgboost_model(self, X_train, X_test, y_train, y_test, symbol):
        """Train XGBoost model with GPU acceleration"""
        if not XGBOOST_AVAILABLE:
            return
        
        try:
            # GPU-optimized parameters
            params = {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                **self.gpu_params['xgboost']
            }
            
            model = XGBClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_xgboost"] = model
            self.model_performance[f"{symbol}_xgboost"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"XGBoost model trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}",
                               gpu_used=self.use_gpu)
            
        except Exception as e:
            trading_logger.error(f"XGBoost training failed for {symbol}: {e}")
    
    def _train_lightgbm_model(self, X_train, X_test, y_train, y_test, symbol):
        """Train LightGBM model with GPU acceleration"""
        if not LIGHTGBM_AVAILABLE:
            return
        
        try:
            # GPU-optimized parameters (reduced to prevent overfitting)
            params = {
                'n_estimators': 50,  # Reduced from 100
                'max_depth': 4,      # Reduced from 6
                'learning_rate': 0.05,  # Reduced from 0.1
                'subsample': 0.9,    # Increased from 0.8
                'colsample_bytree': 0.9,  # Increased from 0.8
                'min_child_samples': 20,  # Added to prevent overfitting
                'reg_alpha': 0.1,    # Added L1 regularization
                'reg_lambda': 0.1,   # Added L2 regularization
                'random_state': 42,
                'verbosity': -1,     # Reduce verbosity
                **self.gpu_params['lightgbm']
            }
            
            model = LGBMClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_lightgbm"] = model
            self.model_performance[f"{symbol}_lightgbm"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"LightGBM model trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}",
                               gpu_used=self.use_gpu)
            
        except Exception as e:
            trading_logger.error(f"LightGBM training failed for {symbol}: {e}")
    
    def _train_random_forest_model(self, X_train, X_test, y_train, y_test, symbol):
        """Train Random Forest model (CPU fallback)"""
        try:
            params = {
                'n_estimators': 100,
                'max_depth': 8,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42,
                'n_jobs': -1  # Use all CPU cores
            }
            
            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.models[f"{symbol}_random_forest"] = model
            self.model_performance[f"{symbol}_random_forest"] = {
                'accuracy': accuracy,
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            trading_logger.info(f"Random Forest model trained for {symbol}", 
                               accuracy=f"{accuracy:.3f}")
            
        except Exception as e:
            trading_logger.error(f"Random Forest training failed for {symbol}: {e}")
    
    def predict(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """Make predictions using all trained models"""
        if not self.models or symbol not in self.scalers:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No trained models'}
        
        # Create features
        features_df = self.create_features(df)
        if len(features_df) == 0:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Get latest features
        latest_features = features_df[self.feature_names].iloc[-1].values.reshape(1, -1)
        
        # Scale features
        scaler = self.scalers[symbol]
        latest_features_scaled = scaler.transform(latest_features)
        
        # Make predictions with all models
        predictions = {}
        confidences = {}
        
        for model_name, model in self.models.items():
            if symbol in model_name:
                try:
                    pred = model.predict(latest_features_scaled)[0]
                    proba = model.predict_proba(latest_features_scaled)[0]
                    confidence = np.max(proba)
                    
                    predictions[model_name] = pred
                    confidences[model_name] = confidence
                    
                except Exception as e:
                    trading_logger.error(f"Prediction failed for {model_name}: {e}")
        
        if not predictions:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No valid predictions'}
        
        # Ensemble prediction
        ensemble_prediction = self._ensemble_predict(predictions, confidences)
        
        return ensemble_prediction
    
    def _ensemble_predict(self, predictions: Dict[str, int], confidences: Dict[str, float]) -> Dict[str, Any]:
        """Combine predictions from multiple models"""
        # Weight models by their confidence
        weighted_predictions = {}
        
        for model_name, pred in predictions.items():
            confidence = confidences[model_name]
            if pred not in weighted_predictions:
                weighted_predictions[pred] = 0
            weighted_predictions[pred] += confidence
        
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
                'reason': f"AI ensemble prediction: {signal} (confidence: {avg_confidence:.3f})"
            }
        
        return {'signal': 'neutral', 'confidence': 0, 'reason': 'No valid ensemble prediction'}
    
    def save_models(self, symbol: str):
        """Save trained models to disk"""
        try:
            import os
            os.makedirs('models', exist_ok=True)
            
            # Save models
            for model_name, model in self.models.items():
                if symbol in model_name:
                    model_path = f"models/{model_name}.joblib"
                    joblib.dump(model, model_path)
            
            # Save scalers
            if symbol in self.scalers:
                scaler_path = f"models/{symbol}_scaler.joblib"
                joblib.dump(self.scalers[symbol], scaler_path)
            
            trading_logger.success(f"Models saved for {symbol}")
            
        except Exception as e:
            trading_logger.error(f"Failed to save models for {symbol}: {e}")
    
    def load_models(self, symbol: str):
        """Load trained models from disk"""
        try:
            import os
            # Load models
            model_files = [f for f in os.listdir('models') if f.startswith(symbol) and f.endswith('.joblib')]
            
            for model_file in model_files:
                model_name = model_file.replace('.joblib', '')
                model_path = f"models/{model_file}"
                model = joblib.load(model_path)
                self.models[model_name] = model
            
            # Load scaler
            scaler_path = f"models/{symbol}_scaler.joblib"
            if os.path.exists(scaler_path):
                self.scalers[symbol] = joblib.load(scaler_path)
            
            trading_logger.success(f"Models loaded for {symbol}")
            
        except Exception as e:
            trading_logger.error(f"Failed to load models for {symbol}: {e}")
    
    def generate_explanation(self, signal: str, symbol: str, market_data: Dict[str, Any], 
                           technical_indicators: Dict[str, Any], confidence: float) -> str:
        """Generate AI-powered natural language explanation for trading decision"""
        try:
            # Extract key metrics
            rsi = technical_indicators.get('rsi', 50)
            price = market_data.get('current_price', 0)
            volume = market_data.get('volume', 0)
            market_regime = market_data.get('regime', 'unknown')
            
            # Create context for AI explanation
            context = {
                'signal': signal.upper(),
                'symbol': symbol,
                'rsi': round(rsi, 1),
                'price': round(price, 2),
                'volume': volume,
                'market_regime': market_regime,
                'confidence': round(confidence, 2)
            }
            
            # Generate simple, easy-to-understand explanations
            if signal.upper() == 'BUY':
                if rsi < 30:
                    explanation = f"🤖 BUYING {symbol} because it's super cheap right now! RSI is {rsi:.1f} (like a 70% off sale). Price: ${price:.2f}. We're {confidence*100:.0f}% sure this is a good deal. Market is {market_regime}."
                elif rsi < 50:
                    explanation = f"🤖 BUYING {symbol} because it's at a good price! RSI is {rsi:.1f} (not too expensive, not too cheap). Price: ${price:.2f}. We're {confidence*100:.0f}% confident. Market is {market_regime}."
                else:
                    explanation = f"🤖 BUYING {symbol} because it's going up fast! RSI is {rsi:.1f} (like catching a wave). Price: ${price:.2f}. We're {confidence*100:.0f}% sure it'll keep going up. Market is {market_regime}."
                    
            elif signal.upper() == 'SELL':
                if rsi > 70:
                    explanation = f"🤖 SELLING {symbol} because it's way too expensive! RSI is {rsi:.1f} (like paying $100 for something worth $30). Price: ${price:.2f}. We're {confidence*100:.0f}% sure it'll drop soon. Market is {market_regime}."
                else:
                    explanation = f"🤖 SELLING {symbol} because it's starting to go down! RSI is {rsi:.1f}. Price: ${price:.2f}. We're {confidence*100:.0f}% sure it's time to take our money and run. Market is {market_regime}."
                    
            else:  # NEUTRAL/HOLD
                if rsi > 70:
                    explanation = f"🤖 WAITING on {symbol} because it's too expensive! RSI is {rsi:.1f} (like waiting for Black Friday sales). Price: ${price:.2f}. We're only {confidence*100:.0f}% sure. Market is {market_regime}."
                elif rsi < 30:
                    explanation = f"🤖 WAITING on {symbol} because even though it's cheap (RSI {rsi:.1f}), we need more proof it won't keep going down. Price: ${price:.2f}. We're only {confidence*100:.0f}% sure. Market is {market_regime}."
                else:
                    explanation = f"🤖 WAITING on {symbol} because nothing exciting is happening! RSI is {rsi:.1f} (like waiting for a good movie to start). Price: ${price:.2f}. We're only {confidence*100:.0f}% sure. Market is {market_regime}."
            
            # Add AI signature
            explanation += f" [AI Analysis: {self.name}]"
            
            return explanation
            
        except Exception as e:
            trading_logger.error(f"Failed to generate AI explanation: {e}")
            return f"🤖 AI Decision: {signal.upper()} {symbol} - AI analysis in progress..."
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of all models"""
        return {
            'total_models': len(self.models),
            'gpu_available': self.use_gpu,
            'last_training': self.last_training_time,
            'training_data_size': self.training_data_size,
            'model_performance': self.model_performance
        }
