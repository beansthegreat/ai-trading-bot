#!/usr/bin/env python3
"""
🧪 Hybrid Acceleration Test Script
Test GPU + NPU acceleration capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from src.hybrid_ai_engine import HybridAIEngine
from utils.logger import trading_logger
from config import config

def test_hardware_detection():
    """Test hardware detection capabilities"""
    print("🔍 Testing Hardware Detection...")
    print("=" * 50)
    
    engine = HybridAIEngine()
    
    print(f"GPU Available: {engine.gpu_available}")
    print(f"NPU Available: {engine.npu_available}")
    print(f"Hybrid Mode: {engine.hybrid_mode}")
    print(f"Workload Distribution: {engine.workload_distribution}")
    print()

def test_model_training():
    """Test model training with different hardware configurations"""
    print("🚀 Testing Model Training...")
    print("=" * 50)
    
    engine = HybridAIEngine()
    
    # Generate synthetic trading data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='1H')
    np.random.seed(42)
    
    data = {
        'open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.1),
        'high': np.zeros(len(dates)),
        'low': np.zeros(len(dates)),
        'close': np.zeros(len(dates)),
        'volume': np.random.randint(1000, 10000, len(dates))
    }
    
    # Calculate high, low, close
    for i in range(len(dates)):
        base_price = data['open'][i]
        data['high'][i] = base_price + abs(np.random.randn() * 0.5)
        data['low'][i] = base_price - abs(np.random.randn() * 0.5)
        data['close'][i] = base_price + np.random.randn() * 0.2
    
    df = pd.DataFrame(data, index=dates)
    df['symbol'] = 'TEST'
    
    print(f"Generated {len(df)} data points")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print()
    
    # Test training
    start_time = time.time()
    results = engine.train_models('TEST', df)
    training_time = time.time() - start_time
    
    print(f"Training completed in {training_time:.2f} seconds")
    print(f"Models trained: {len(results)}")
    
    for model_name, result in results.items():
        print(f"  {model_name}: {result['model_type']} - Accuracy: {result['accuracy']:.3f} - Hardware: {result['hardware']}")
    
    print(f"Hardware usage: {engine.hardware_usage}")
    print()

def test_prediction_performance():
    """Test prediction performance"""
    print("🎯 Testing Prediction Performance...")
    print("=" * 50)
    
    engine = HybridAIEngine()
    
    # Generate test data
    dates = pd.date_range(start='2024-01-01', end='2024-01-02', freq='1H')
    np.random.seed(123)
    
    data = {
        'open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.1),
        'high': np.zeros(len(dates)),
        'low': np.zeros(len(dates)),
        'close': np.zeros(len(dates)),
        'volume': np.random.randint(1000, 10000, len(dates))
    }
    
    for i in range(len(dates)):
        base_price = data['open'][i]
        data['high'][i] = base_price + abs(np.random.randn() * 0.5)
        data['low'][i] = base_price - abs(np.random.randn() * 0.5)
        data['close'][i] = base_price + np.random.randn() * 0.2
    
    df = pd.DataFrame(data, index=dates)
    df['symbol'] = 'TEST'
    
    # Train models first
    print("Training models for prediction test...")
    engine.train_models('TEST', df)
    
    # Test predictions
    prediction_times = []
    predictions = []
    
    for i in range(10):
        test_df = df.iloc[:100+i*10]  # Use different amounts of data
        
        start_time = time.time()
        prediction = engine.predict('TEST', test_df)
        prediction_time = time.time() - start_time
        
        prediction_times.append(prediction_time)
        predictions.append(prediction)
        
        print(f"Prediction {i+1}: {prediction['signal']} (confidence: {prediction['confidence']:.3f}) - {prediction_time*1000:.1f}ms")
    
    avg_prediction_time = np.mean(prediction_times)
    print(f"\nAverage prediction time: {avg_prediction_time*1000:.1f}ms")
    print(f"Prediction throughput: {1/avg_prediction_time:.1f} predictions/second")
    print()

def test_benchmarking():
    """Benchmark different hardware configurations"""
    print("📊 Benchmarking Hardware Configurations...")
    print("=" * 50)
    
    # This would compare:
    # 1. CPU-only performance
    # 2. GPU-only performance  
    # 3. NPU-only performance
    # 4. Hybrid GPU+NPU performance
    
    print("Benchmarking would compare:")
    print("  - CPU-only: Traditional scikit-learn models")
    print("  - GPU-only: CUDA-accelerated XGBoost/LightGBM")
    print("  - NPU-only: ONNX Runtime with DirectML")
    print("  - Hybrid: Optimal distribution between GPU and NPU")
    print()
    print("This requires running the bot with different configurations")
    print("and measuring training time, prediction speed, and accuracy.")
    print()

def main():
    """Run all tests"""
    print("🚀 Hybrid AI Engine Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        test_hardware_detection()
        test_model_training()
        test_prediction_performance()
        test_benchmarking()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        trading_logger.error(f"Hybrid acceleration test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
