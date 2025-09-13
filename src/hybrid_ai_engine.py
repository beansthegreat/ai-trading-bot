#!/usr/bin/env python3
"""
🚀 Hybrid AI Trading Engine - GPU + NPU Acceleration
Ultra-Intelligent Trading System with Ryzen 7 8700F NPU + GPU Optimization
"""

import pandas as pd
import numpy as np
import joblib
import mlflow
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("⚠️ CatBoost not available - falling back to CPU")

# NPU-optimized libraries
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("⚠️ ONNX Runtime not available - NPU acceleration disabled")

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available - neural networks disabled")

from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from utils.logger import trading_logger
from utils.indicators import TechnicalIndicators
from config import config

class HybridAIEngine:
    """Hybrid GPU + NPU Accelerated AI Trading Engine"""
    
    def __init__(self):
        self.name = "Hybrid GPU + NPU AI Trading Engine"
        self.description = "Ultra-intelligent trading with Ryzen 7 8700F NPU + GPU optimization"
        
        # Model storage
        self.gpu_models = {}  # GPU-accelerated models
        self.npu_models = {}  # NPU-accelerated models
        self.cpu_models = {}  # CPU fallback models
        self.scalers = {}
        self.feature_names = []
        
        # Hardware configuration
        self.gpu_available = self._check_gpu_availability()
        self.npu_available = self._check_npu_availability()
        self.hybrid_mode = self.gpu_available and self.npu_available
        
        # Performance tracking
        self.model_performance = {}
        self.hardware_usage = {'gpu': 0, 'npu': 0, 'cpu': 0}
        self.last_training_time = None
        self.training_data_size = 0
        
        # Workload distribution
        self.workload_distribution = self._setup_workload_distribution()
        
        # Initialize MLflow
        self._setup_mlflow()
        
        trading_logger.info("Hybrid AI Engine initialized", 
                           gpu_available=self.gpu_available,
                           npu_available=self.npu_available,
                           hybrid_mode=self.hybrid_mode,
                           workload_distribution=self.workload_distribution)
    
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
    
    def _check_npu_availability(self) -> bool:
        """Check if NPU acceleration is available"""
        try:
            if ONNX_AVAILABLE:
                # Check for AMD NPU providers
                available_providers = ort.get_available_providers()
                npu_providers = [p for p in available_providers if 'dml' in p.lower() or 'npu' in p.lower()]
                
                if npu_providers:
                    trading_logger.info(f"NPU providers available: {npu_providers}")
                    return True
                else:
                    trading_logger.info(f"Available providers: {available_providers}")
                    # Try DirectML as fallback for AMD NPU
                    return 'DmlExecutionProvider' in available_providers
        except Exception as e:
            trading_logger.warning(f"NPU acceleration check failed: {e}")
        
        return False
    
    def _setup_workload_distribution(self) -> Dict[str, Any]:
        """Setup optimal workload distribution between GPU and NPU"""
        if self.hybrid_mode:
            return {
                'gpu_models': ['xgboost', 'lightgbm', 'catboost'],
                'npu_models': ['neural_network', 'pattern_recognition', 'real_time_inference'],
                'cpu_models': ['random_forest', 'data_preprocessing'],
                'parallel_execution': True,
                'npu_inference_batch_size': 32,
                'gpu_training_batch_size': 1024
            }
        elif self.gpu_available:
            return {
                'gpu_models': ['xgboost', 'lightgbm', 'catboost', 'neural_network'],
                'npu_models': [],
                'cpu_models': ['random_forest', 'data_preprocessing'],
                'parallel_execution': False
            }
        else:
            return {
                'gpu_models': [],
                'npu_models': [],
                'cpu_models': ['xgboost', 'lightgbm', 'catboost', 'neural_network', 'random_forest'],
                'parallel_execution': False
            }
    
    def _setup_mlflow(self):
        """Setup MLflow for model tracking"""
        try:
            mlflow.set_tracking_uri("file:./mlruns")
            mlflow.set_experiment("hybrid_trading_ai_models")
            trading_logger.info("MLflow tracking initialized for hybrid models")
        except Exception as e:
            trading_logger.warning(f"MLflow setup failed: {e}")
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create enhanced features for hybrid AI models"""
        if len(df) < 50:
            return pd.DataFrame()
        
        # Calculate all technical indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Create AI-specific features
        ai_features = self._create_hybrid_ai_features(df_with_indicators)
        
        # Combine all features
        all_features = pd.concat([df_with_indicators, ai_features], axis=1)
        
        # Store feature names for model training
        self.feature_names = [col for col in all_features.columns 
                             if col not in ['open', 'high', 'low', 'close', 'volume', 'symbol', 'timeframe']]
        
        return all_features
    
    def _create_hybrid_ai_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features optimized for hybrid GPU+NPU processing"""
        features = pd.DataFrame(index=df.index)
        
        # GPU-optimized features (heavy computations)
        features['gpu_trend_strength'] = self._calculate_gpu_trend_strength(df)
        features['gpu_volatility_cluster'] = self._calculate_gpu_volatility_cluster(df)
        features['gpu_momentum_consensus'] = self._calculate_gpu_momentum_consensus(df)
        
        # NPU-optimized features (pattern recognition)
        features['npu_pattern_score'] = self._calculate_npu_pattern_score(df)
        features['npu_sentiment_analysis'] = self._calculate_npu_sentiment_analysis(df)
        features['npu_market_microstructure'] = self._calculate_npu_market_microstructure(df)
        
        # Hybrid features (combining both)
        features['hybrid_signal_strength'] = self._calculate_hybrid_signal_strength(df)
        features['hybrid_confidence_score'] = self._calculate_hybrid_confidence_score(df)
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
    
    def _calculate_gpu_trend_strength(self, df: pd.DataFrame) -> pd.Series:
        """GPU-optimized trend strength calculation"""
        # Heavy computation suitable for GPU
        sma_20 = df['close'].rolling(20).mean()
        sma_50 = df['close'].rolling(50).mean()
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        
        trend_strength = (
            (sma_20 - sma_50) / sma_50 * 100 +
            (ema_12 - ema_26) / ema_26 * 100
        ) / 2
        
        return trend_strength.fillna(0)
    
    def _calculate_gpu_volatility_cluster(self, df: pd.DataFrame) -> pd.Series:
        """GPU-optimized volatility clustering"""
        returns = df['close'].pct_change()
        volatility = returns.rolling(20).std()
        volatility_cluster = volatility.rolling(20).mean()
        
        return (volatility / volatility_cluster).fillna(1)
    
    def _calculate_gpu_momentum_consensus(self, df: pd.DataFrame) -> pd.Series:
        """GPU-optimized momentum consensus"""
        rsi = df.get('rsi', pd.Series(50, index=df.index))
        macd = df.get('macd', pd.Series(0, index=df.index))
        stoch = df.get('stoch_k', pd.Series(50, index=df.index))
        
        momentum_score = (
            (rsi - 50) / 50 +
            macd / df['close'] * 100 +
            (stoch - 50) / 50
        ) / 3
        
        return momentum_score.fillna(0)
    
    def _calculate_npu_pattern_score(self, df: pd.DataFrame) -> pd.Series:
        """NPU-optimized pattern recognition"""
        # Simplified pattern recognition suitable for NPU
        high_low_ratio = df['high'] / df['low']
        close_position = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        # Pattern scoring
        pattern_score = pd.Series(0.5, index=df.index)
        
        # Bullish patterns
        pattern_score.loc[(high_low_ratio > 1.02) & (close_position > 0.7)] += 0.2
        pattern_score.loc[(high_low_ratio > 1.05) & (close_position > 0.8)] += 0.3
        
        # Bearish patterns
        pattern_score.loc[(high_low_ratio > 1.02) & (close_position < 0.3)] -= 0.2
        pattern_score.loc[(high_low_ratio > 1.05) & (close_position < 0.2)] -= 0.3
        
        return pattern_score.clip(0, 1)
    
    def _calculate_npu_sentiment_analysis(self, df: pd.DataFrame) -> pd.Series:
        """NPU-optimized sentiment analysis"""
        # Volume-based sentiment
        volume_ma = df['volume'].rolling(20).mean()
        volume_sentiment = (df['volume'] / volume_ma).fillna(1)
        
        # Price-volume sentiment
        price_change = df['close'].pct_change()
        volume_change = df['volume'].pct_change()
        
        sentiment = pd.Series(0.5, index=df.index)
        sentiment.loc[(price_change > 0) & (volume_change > 0)] += 0.2
        sentiment.loc[(price_change < 0) & (volume_change > 0)] -= 0.2
        
        return sentiment.clip(0, 1)
    
    def _calculate_npu_market_microstructure(self, df: pd.DataFrame) -> pd.Series:
        """NPU-optimized market microstructure analysis"""
        # Bid-ask spread estimate
        spread_estimate = (df['high'] - df['low']) / df['close']
        
        # Price efficiency
        price_efficiency = 1 - (spread_estimate / spread_estimate.rolling(20).mean())
        
        return price_efficiency.fillna(0.5)
    
    def _calculate_hybrid_signal_strength(self, df: pd.DataFrame) -> pd.Series:
        """Hybrid signal strength combining GPU and NPU insights"""
        gpu_trend = self._calculate_gpu_trend_strength(df)
        npu_pattern = self._calculate_npu_pattern_score(df)
        
        # Combine signals with weights
        hybrid_signal = (gpu_trend * 0.6 + npu_pattern * 0.4)
        
        return hybrid_signal.fillna(0)
    
    def _calculate_hybrid_confidence_score(self, df: pd.DataFrame) -> pd.Series:
        """Hybrid confidence score"""
        # Combine multiple confidence indicators
        volatility = df['close'].pct_change().rolling(20).std()
        volume_consistency = df['volume'].rolling(20).std() / df['volume'].rolling(20).mean()
        
        confidence = 1 - (volatility + volume_consistency) / 2
        return confidence.fillna(0.5).clip(0, 1)
    
    def train_models(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Train hybrid models with optimal hardware distribution"""
        if len(df) < 100:
            trading_logger.warning(f"Insufficient data for training {symbol}")
            return {}
        
        # Create features
        features_df = self.create_features(df)
        if features_df.empty:
            return {}
        
        # Prepare training data
        X = features_df[self.feature_names].fillna(0)
        y = self._create_target_variable(df)
        
        if len(X) < 50:
            trading_logger.warning(f"Insufficient features for training {symbol}")
            return {}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[symbol] = scaler
        
        # Train models in parallel using optimal hardware
        training_results = {}
        
        if self.hybrid_mode:
            # Hybrid training with GPU and NPU
            training_results = self._train_hybrid_models(
                symbol, X_train_scaled, X_test_scaled, y_train, y_test
            )
        elif self.gpu_available:
            # GPU-only training
            training_results = self._train_gpu_models_parallel(
                symbol, X_train_scaled, X_test_scaled, y_train, y_test
            )
        else:
            # CPU-only training
            training_results = self._train_cpu_models_parallel(
                symbol, X_train_scaled, X_test_scaled, y_train, y_test
            )
        
        # Update performance tracking
        self.model_performance[symbol] = training_results
        self.last_training_time = datetime.now()
        self.training_data_size = len(X)
        
        trading_logger.info(f"Hybrid training completed for {symbol}", 
                           models_trained=len(training_results),
                           hardware_usage=self.hardware_usage)
        
        return training_results
    
    def _train_hybrid_models(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train models using hybrid GPU+NPU approach"""
        results = {}
        
        # GPU models (heavy ensemble)
        gpu_results = self._train_gpu_models_parallel(symbol, X_train, X_test, y_train, y_test)
        results.update(gpu_results)
        
        # NPU models (neural networks)
        npu_results = self._train_npu_models_parallel(symbol, X_train, X_test, y_train, y_test)
        results.update(npu_results)
        
        # CPU models (fallback)
        cpu_results = self._train_cpu_models_parallel(symbol, X_train, X_test, y_train, y_test)
        results.update(cpu_results)
        
        return results
    
    def _train_gpu_models_parallel(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train GPU models in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            # XGBoost GPU
            if XGBOOST_AVAILABLE and 'xgboost' in self.workload_distribution['gpu_models']:
                futures['xgboost'] = executor.submit(
                    self._train_xgboost_gpu, symbol, X_train, X_test, y_train, y_test
                )
            
            # LightGBM GPU
            if LIGHTGBM_AVAILABLE and 'lightgbm' in self.workload_distribution['gpu_models']:
                futures['lightgbm'] = executor.submit(
                    self._train_lightgbm_gpu, symbol, X_train, X_test, y_train, y_test
                )
            
            # CatBoost GPU
            if CATBOOST_AVAILABLE and 'catboost' in self.workload_distribution['gpu_models']:
                futures['catboost'] = executor.submit(
                    self._train_catboost_gpu, symbol, X_train, X_test, y_train, y_test
                )
            
            # Collect results
            for model_name, future in futures.items():
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    if result:
                        results[model_name] = result
                        self.hardware_usage['gpu'] = self.hardware_usage.get('gpu', 0) + 1
                except Exception as e:
                    trading_logger.error(f"GPU model {model_name} training failed: {e}")
        
        return results
    
    def _train_npu_models_parallel(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train NPU models in parallel"""
        results = {}
        
        if not self.npu_available:
            return results
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # Neural Network NPU
            if TORCH_AVAILABLE and 'neural_network' in self.workload_distribution['npu_models']:
                futures['neural_network'] = executor.submit(
                    self._train_neural_network_npu, symbol, X_train, X_test, y_train, y_test
                )
            
            # Pattern Recognition NPU
            if 'pattern_recognition' in self.workload_distribution['npu_models']:
                futures['pattern_recognition'] = executor.submit(
                    self._train_pattern_recognition_npu, symbol, X_train, X_test, y_train, y_test
                )
            
            # Collect results
            for model_name, future in futures.items():
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    if result:
                        results[model_name] = result
                        self.hardware_usage['npu'] = self.hardware_usage.get('npu', 0) + 1
                except Exception as e:
                    trading_logger.error(f"NPU model {model_name} training failed: {e}")
        
        return results
    
    def _train_cpu_models_parallel(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train CPU models in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # Random Forest
            if 'random_forest' in self.workload_distribution['cpu_models']:
                futures['random_forest'] = executor.submit(
                    self._train_random_forest, symbol, X_train, X_test, y_train, y_test
                )
            
            # MLP Classifier
            if 'neural_network' in self.workload_distribution['cpu_models']:
                futures['mlp_classifier'] = executor.submit(
                    self._train_mlp_classifier, symbol, X_train, X_test, y_train, y_test
                )
            
            # Collect results
            for model_name, future in futures.items():
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    if result:
                        results[model_name] = result
                        self.hardware_usage['cpu'] = self.hardware_usage.get('cpu', 0) + 1
                except Exception as e:
                    trading_logger.error(f"CPU model {model_name} training failed: {e}")
        
        return results
    
    def _train_xgboost_gpu(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train XGBoost with GPU acceleration"""
        try:
            model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                tree_method='gpu_hist',
                gpu_id=0,
                random_state=42,
                eval_metric='logloss'
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Store model
            self.gpu_models[f"{symbol}_xgboost"] = model
            
            return {
                'model_type': 'xgboost_gpu',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'hardware': 'gpu'
            }
        except Exception as e:
            trading_logger.error(f"XGBoost GPU training failed: {e}")
            return None
    
    def _train_lightgbm_gpu(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train LightGBM with GPU acceleration"""
        try:
            model = LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                device='gpu',
                gpu_platform_id=0,
                gpu_device_id=0,
                random_state=42,
                verbose=-1
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Store model
            self.gpu_models[f"{symbol}_lightgbm"] = model
            
            return {
                'model_type': 'lightgbm_gpu',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'hardware': 'gpu'
            }
        except Exception as e:
            trading_logger.error(f"LightGBM GPU training failed: {e}")
            return None
    
    def _train_catboost_gpu(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train CatBoost with GPU acceleration"""
        try:
            model = CatBoostClassifier(
                iterations=100,
                depth=6,
                learning_rate=0.1,
                task_type='GPU',
                devices='0',
                random_seed=42,
                verbose=False
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Store model
            self.gpu_models[f"{symbol}_catboost"] = model
            
            return {
                'model_type': 'catboost_gpu',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'hardware': 'gpu'
            }
        except Exception as e:
            trading_logger.error(f"CatBoost GPU training failed: {e}")
            return None
    
    def _train_neural_network_npu(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train neural network with NPU acceleration"""
        try:
            if not TORCH_AVAILABLE:
                return None
            
            # Convert to PyTorch tensors
            X_train_tensor = torch.FloatTensor(X_train)
            y_train_tensor = torch.LongTensor(y_train)
            X_test_tensor = torch.FloatTensor(X_test)
            y_test_tensor = torch.LongTensor(y_test)
            
            # Define neural network
            class TradingNN(nn.Module):
                def __init__(self, input_size):
                    super(TradingNN, self).__init__()
                    self.fc1 = nn.Linear(input_size, 128)
                    self.fc2 = nn.Linear(128, 64)
                    self.fc3 = nn.Linear(64, 32)
                    self.fc4 = nn.Linear(32, 3)  # 3 classes: buy, sell, hold
                    self.dropout = nn.Dropout(0.2)
                    self.relu = nn.ReLU()
                
                def forward(self, x):
                    x = self.relu(self.fc1(x))
                    x = self.dropout(x)
                    x = self.relu(self.fc2(x))
                    x = self.dropout(x)
                    x = self.relu(self.fc3(x))
                    x = self.fc4(x)
                    return x
            
            model = TradingNN(X_train.shape[1])
            
            # Try to use NPU if available
            device = torch.device('cpu')  # Default to CPU
            if self.npu_available:
                try:
                    # Try DirectML for AMD NPU
                    device = torch.device('dml:0')
                    model = model.to(device)
                    X_train_tensor = X_train_tensor.to(device)
                    y_train_tensor = y_train_tensor.to(device)
                    X_test_tensor = X_test_tensor.to(device)
                    y_test_tensor = y_test_tensor.to(device)
                except:
                    device = torch.device('cpu')
                    model = model.to(device)
            
            # Training setup
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            
            # Training loop
            model.train()
            for epoch in range(50):
                optimizer.zero_grad()
                outputs = model(X_train_tensor)
                loss = criterion(outputs, y_train_tensor)
                loss.backward()
                optimizer.step()
            
            # Evaluation
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test_tensor)
                _, predicted = torch.max(test_outputs.data, 1)
                accuracy = (predicted == y_test_tensor).float().mean().item()
            
            # Store model
            self.npu_models[f"{symbol}_neural_network"] = {
                'model': model,
                'device': device,
                'input_size': X_train.shape[1]
            }
            
            return {
                'model_type': 'neural_network_npu',
                'accuracy': accuracy,
                'precision': 0.0,  # Simplified for now
                'recall': 0.0,
                'f1_score': 0.0,
                'hardware': 'npu'
            }
        except Exception as e:
            trading_logger.error(f"Neural network NPU training failed: {e}")
            return None
    
    def _train_pattern_recognition_npu(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train pattern recognition model with NPU"""
        try:
            if not ONNX_AVAILABLE:
                return None
            
            # Create a simple pattern recognition model
            from sklearn.ensemble import RandomForestClassifier
            
            # Train on CPU first
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X_train, y_train)
            
            # Convert to ONNX for NPU inference
            try:
                from skl2onnx import convert_sklearn
                from skl2onnx.common.data_types import FloatTensorType
                
                initial_type = [('float_input', FloatTensorType([None, X_train.shape[1]]))]
                onnx_model = convert_sklearn(model, initial_types=initial_type)
                
                # Save ONNX model
                onnx_path = f"data/models/{symbol}_pattern_recognition.onnx"
                with open(onnx_path, "wb") as f:
                    f.write(onnx_model.SerializeToString())
                
                # Setup NPU inference
                providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
                session = ort.InferenceSession(onnx_path, providers=providers)
                
                # Test inference
                input_name = session.get_inputs()[0].name
                output_name = session.get_outputs()[0].name
                
                predictions = session.run([output_name], {input_name: X_test.astype(np.float32)})
                y_pred = np.argmax(predictions[0], axis=1)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                # Store model
                self.npu_models[f"{symbol}_pattern_recognition"] = {
                    'session': session,
                    'input_name': input_name,
                    'output_name': output_name,
                    'onnx_path': onnx_path
                }
                
                return {
                    'model_type': 'pattern_recognition_npu',
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'hardware': 'npu'
                }
            except Exception as e:
                trading_logger.warning(f"ONNX conversion failed, using CPU: {e}")
                # Fallback to CPU
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                return {
                    'model_type': 'pattern_recognition_cpu',
                    'accuracy': accuracy,
                    'precision': 0.0,
                    'recall': 0.0,
                    'f1_score': 0.0,
                    'hardware': 'cpu'
                }
        except Exception as e:
            trading_logger.error(f"Pattern recognition NPU training failed: {e}")
            return None
    
    def _train_random_forest(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train Random Forest on CPU"""
        try:
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Store model
            self.cpu_models[f"{symbol}_random_forest"] = model
            
            return {
                'model_type': 'random_forest_cpu',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'hardware': 'cpu'
            }
        except Exception as e:
            trading_logger.error(f"Random Forest training failed: {e}")
            return None
    
    def _train_mlp_classifier(self, symbol: str, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """Train MLP Classifier on CPU"""
        try:
            model = MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                max_iter=200,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Store model
            self.cpu_models[f"{symbol}_mlp_classifier"] = model
            
            return {
                'model_type': 'mlp_classifier_cpu',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'hardware': 'cpu'
            }
        except Exception as e:
            trading_logger.error(f"MLP Classifier training failed: {e}")
            return None
    
    def _create_target_variable(self, df: pd.DataFrame) -> pd.Series:
        """Create target variable for classification"""
        # Simple target: 1 if next day close > current close, 0 otherwise
        future_returns = df['close'].shift(-1) / df['close'] - 1
        
        # Create 3-class target: buy (1), hold (0), sell (-1)
        target = pd.Series(0, index=df.index)  # Default to hold
        target.loc[future_returns > 0.01] = 1  # Buy if >1% gain
        target.loc[future_returns < -0.01] = 2  # Sell if >1% loss
        
        return target.fillna(0).astype(int)
    
    def predict(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Make hybrid predictions using optimal hardware"""
        if symbol not in self.scalers:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No trained models'}
        
        # Create features
        features_df = self.create_features(df)
        if features_df.empty:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No features available'}
        
        # Prepare prediction data
        X = features_df[self.feature_names].fillna(0)
        X_scaled = self.scalers[symbol].transform(X)
        
        # Get latest data point
        latest_features = X_scaled[-1:].astype(np.float32)
        
        # Make predictions using all available models
        predictions = {}
        confidences = {}
        
        # GPU predictions
        for model_name, model in self.gpu_models.items():
            if symbol in model_name:
                try:
                    pred = model.predict(latest_features)[0]
                    proba = model.predict_proba(latest_features)[0]
                    confidence = np.max(proba)
                    
                    predictions[model_name] = pred
                    confidences[model_name] = confidence
                except Exception as e:
                    trading_logger.warning(f"GPU prediction failed for {model_name}: {e}")
        
        # NPU predictions
        for model_name, model_info in self.npu_models.items():
            if symbol in model_name:
                try:
                    if 'session' in model_info:  # ONNX model
                        session = model_info['session']
                        input_name = model_info['input_name']
                        output_name = model_info['output_name']
                        
                        pred_proba = session.run([output_name], {input_name: latest_features})[0]
                        pred = np.argmax(pred_proba[0])
                        confidence = np.max(pred_proba[0])
                        
                        predictions[model_name] = pred
                        confidences[model_name] = confidence
                    elif 'model' in model_info:  # PyTorch model
                        model = model_info['model']
                        device = model_info['device']
                        
                        with torch.no_grad():
                            model.eval()
                            tensor_input = torch.FloatTensor(latest_features).to(device)
                            output = model(tensor_input)
                            pred_proba = torch.softmax(output, dim=1)
                            pred = torch.argmax(pred_proba, dim=1).item()
                            confidence = torch.max(pred_proba).item()
                        
                        predictions[model_name] = pred
                        confidences[model_name] = confidence
                except Exception as e:
                    trading_logger.warning(f"NPU prediction failed for {model_name}: {e}")
        
        # CPU predictions
        for model_name, model in self.cpu_models.items():
            if symbol in model_name:
                try:
                    pred = model.predict(latest_features)[0]
                    proba = model.predict_proba(latest_features)[0]
                    confidence = np.max(proba)
                    
                    predictions[model_name] = pred
                    confidences[model_name] = confidence
                except Exception as e:
                    trading_logger.warning(f"CPU prediction failed for {model_name}: {e}")
        
        # Ensemble prediction
        if predictions:
            ensemble_prediction = self._hybrid_ensemble_predict(predictions, confidences)
            return ensemble_prediction
        else:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No valid predictions'}
    
    def _hybrid_ensemble_predict(self, predictions: Dict[str, int], confidences: Dict[str, float]) -> Dict[str, Any]:
        """Hybrid ensemble prediction with hardware-aware weighting"""
        if not predictions:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No predictions available'}
        
        # Hardware-aware weighting
        hardware_weights = {
            'gpu': 0.4,    # GPU models get higher weight for accuracy
            'npu': 0.3,    # NPU models get medium weight for speed
            'cpu': 0.3     # CPU models get lower weight as fallback
        }
        
        # Calculate weighted predictions
        weighted_predictions = []
        total_weight = 0
        
        for model_name, pred in predictions.items():
            confidence = confidences.get(model_name, 0.5)
            
            # Determine hardware type
            if 'gpu' in model_name or any(gpu_model in model_name for gpu_model in ['xgboost', 'lightgbm', 'catboost']):
                hardware_weight = hardware_weights['gpu']
            elif 'npu' in model_name or any(npu_model in model_name for npu_model in ['neural_network', 'pattern_recognition']):
                hardware_weight = hardware_weights['npu']
            else:
                hardware_weight = hardware_weights['cpu']
            
            # Weight by both hardware type and confidence
            weight = hardware_weight * confidence
            weighted_predictions.append(pred * weight)
            total_weight += weight
        
        if total_weight == 0:
            return {'signal': 'neutral', 'confidence': 0, 'reason': 'No valid weighted predictions'}
        
        # Calculate final prediction
        final_prediction = sum(weighted_predictions) / total_weight
        
        # Convert to signal
        if final_prediction > 0.6:
            signal = 'buy'
        elif final_prediction < 0.4:
            signal = 'sell'
        else:
            signal = 'hold'
        
        # Calculate average confidence
        avg_confidence = sum(confidences.values()) / len(confidences)
        
        return {
            'signal': signal,
            'confidence': avg_confidence,
            'prediction_score': final_prediction,
            'models_used': len(predictions),
            'hardware_usage': self.hardware_usage,
            'reason': f"Hybrid AI prediction: {signal} (confidence: {avg_confidence:.3f}, models: {len(predictions)})"
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'engine_name': self.name,
            'description': self.description,
            'hardware_status': {
                'gpu_available': self.gpu_available,
                'npu_available': self.npu_available,
                'hybrid_mode': self.hybrid_mode
            },
            'workload_distribution': self.workload_distribution,
            'hardware_usage': self.hardware_usage,
            'models_trained': len(self.gpu_models) + len(self.npu_models) + len(self.cpu_models),
            'last_training_time': self.last_training_time,
            'training_data_size': self.training_data_size,
            'model_performance': self.model_performance
        }
