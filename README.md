# 🚀 Advanced AI Trading Bot

A sophisticated, GPU-accelerated trading bot with comprehensive historical training, advanced AI models, and real-time market analysis.

## ✨ Features

### 🤖 **Advanced AI Engine**
- **GPU-Accelerated ML**: XGBoost, LightGBM, CatBoost with RTX 5070 support
- **Neural Networks**: Multi-layer perceptron for pattern recognition
- **Ensemble Voting**: Combines multiple models for better predictions
- **122+ Features**: Technical indicators, chart patterns, volume analysis

### 📊 **Historical Training System**
- **Multi-Timeframe Data**: 1m, 5m, 15m, 1h, 1d intervals
- **3 Years of History**: Comprehensive market data collection
- **Chart Pattern Recognition**: 12+ patterns (Head & Shoulders, Triangles, etc.)
- **Volume Analysis**: VWAP, volume spikes, volume profiles
- **Market Regime Detection**: Trending, volatile, choppy, stable conditions

### 🎯 **Trading Strategies**
- **Momentum Strategy**: RSI, MACD, ADX confirmation
- **Adaptive Strategy**: Dynamic strategy selection based on market conditions
- **AI-Enhanced Strategy**: Machine learning predictions
- **Risk Management**: Position sizing, stop-loss, take-profit

### 📈 **Real-Time Analysis**
- **Live Market Monitoring**: Real-time price and volume tracking
- **Signal Generation**: Buy/sell signals with confidence scores
- **Performance Analytics**: Comprehensive trading metrics
- **Alerts System**: Customizable notifications

## 🏗️ Project Structure

```
money/
├── 📁 src/                    # Core source code
│   ├── ai_engine.py          # Standard AI engine
│   ├── advanced_ai_engine.py # Advanced AI with ensemble
│   ├── trading_bot.py        # Main trading bot
│   └── ...
├── 📁 scripts/               # Production scripts
│   ├── start_trading_bot.py  # Start the trading bot
│   ├── collect_historical_data.py # Data collection
│   ├── train_historical_models.py # Model training
│   └── ...
├── 📁 data/                  # Data storage
│   ├── models/              # Trained AI models
│   ├── historical/          # Historical market data
│   └── cache/               # Training cache
├── 📁 docs/                  # Documentation
├── 📁 tests/                 # Test files
├── 📁 examples/              # Example scripts
└── 📁 logs/                  # Log files
```

## 🚀 Quick Start

### 1. **Installation**
```bash
# Clone the repository
git clone <your-repo-url>
cd money

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configuration**
```bash
# Copy and configure API keys
cp config.example.py config.py
# Edit config.py with your Alpaca API credentials
```

### 3. **Historical Training** (Recommended)
```bash
# Collect historical data
python scripts/collect_historical_data.py

# Train AI models
python scripts/train_historical_models.py

# Or run complete pipeline
python scripts/run_complete_training.py
```

### 4. **Start Trading**
```bash
# Start the trading bot
python scripts/start_trading_bot.py

# Or run main script
python main.py
```

## 📊 Training Results

Our AI models achieve impressive accuracy across multiple stocks:

| Stock | XGBoost | LightGBM | Ensemble | Best Model |
|-------|---------|----------|----------|------------|
| AAPL  | 70.2%   | 64.0%    | 71.5%    | Ensemble   |
| MSFT  | 69.4%   | 64.5%    | 68.6%    | XGBoost    |
| GOOGL | 68.2%   | 60.7%    | 69.4%    | Ensemble   |
| TSLA  | 75.2%   | 65.7%    | 78.9%    | Ensemble   |
| AMZN  | 63.6%   | 57.0%    | 66.9%    | Ensemble   |
| NVDA  | 73.6%   | 69.4%    | 71.9%    | XGBoost    |
| AMD   | 71.1%   | 63.2%    | 73.6%    | Ensemble   |

## 🛠️ Advanced Features

### **GPU Acceleration**
- **RTX 5070 Support**: Optimized for NVIDIA GPUs
- **CUDA Integration**: XGBoost, LightGBM, CatBoost GPU training
- **Memory Optimization**: Efficient GPU memory usage

### **Data Collection**
- **84,840+ Data Points**: Comprehensive historical coverage
- **Multi-Source**: Alpaca API + Yahoo Finance fallback
- **Real-Time Updates**: Live market data integration

### **Risk Management**
- **Position Sizing**: Dynamic position calculation
- **Stop-Loss/Take-Profit**: Automated risk controls
- **Daily Loss Limits**: Maximum loss protection
- **Wash Sale Prevention**: Tax optimization

## 📚 Documentation

- **[Enhanced Features](docs/ENHANCED_FEATURES.md)**: Detailed feature documentation
- **[Historical Training](docs/HISTORICAL_TRAINING.md)**: Training system guide
- **[Python Setup](docs/README_PYTHON.md)**: Python environment setup
- **[Timezone Implementation](docs/TIMEZONE_IMPLEMENTATION.md)**: Timezone handling

## 🔧 Scripts Overview

### **Core Scripts**
- `start_trading_bot.py`: Main trading bot launcher
- `collect_historical_data.py`: Historical data collection
- `train_historical_models.py`: AI model training
- `run_complete_training.py`: Complete training pipeline

### **Monitoring Scripts**
- `live_monitor.py`: Real-time market monitoring
- `simple_monitor.py`: Basic monitoring
- `tail_logs.py`: Log file monitoring

### **Analysis Scripts**
- `buy_signal_scanner.py`: Signal scanning
- `run_backtest.py`: Backtesting
- `training_dashboard.py`: Training visualization

## ⚙️ Configuration

Key configuration options in `config.py`:

```python
# API Configuration
ALPACA_API_KEY = "your_api_key"
ALPACA_SECRET_KEY = "your_secret_key"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# Trading Parameters
DEFAULT_SYMBOL = "AAPL"
POSITION_SIZE = 0.1  # 10% of portfolio
STOP_LOSS_PCT = 0.02  # 2% stop loss
TAKE_PROFIT_PCT = 0.04  # 4% take profit

# AI Parameters
USE_GPU = True
MODEL_RETRAIN_HOURS = 24
CONFIDENCE_THRESHOLD = 0.7
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_connection.py
python tests/test_enhanced_features.py
```

## 📈 Performance

- **Training Speed**: ~2-3 minutes per symbol (GPU-accelerated)
- **Prediction Speed**: <100ms per prediction
- **Memory Usage**: ~2GB RAM, ~4GB VRAM
- **Accuracy**: 60-80% across different stocks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves risk, and past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the `docs/` folder for detailed guides
- **Examples**: See the `examples/` folder for usage examples

---

**Built with ❤️ for the trading community**