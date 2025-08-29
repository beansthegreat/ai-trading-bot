# 🤖 Mr. Money - AI Trading Bot

**Ultra-Intelligent Algorithmic Trading System with Adaptive Strategy Intelligence**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 🚀 Features

### 🧠 **Smart Buy Low Sell High Strategy**
- **Multi-timeframe analysis** (1h, 3h, 6h patterns)
- **Chart pattern recognition** beyond simple RSI
- **Intelligent buy/sell detection** based on:
  - Recent price movements
  - RSI levels (oversold/overbought)
  - Momentum indicators
  - Volatility analysis
  - Trend patterns

### 🎯 **Adaptive Strategy Intelligence**
- **Market regime detection** (trending, choppy, volatile, stable)
- **Dynamic strategy switching** based on market conditions
- **Multiple strategy support**:
  - Smart Buy Low Sell High
  - Momentum Micro
  - Breakout
  - Conservative

### 💰 **Advanced Trading Features**
- **Multi-share buying** with fractional shares
- **Dollar amount trading** for expensive stocks
- **Intelligent position sizing** based on signal strength
- **Volatility-adjusted risk management**
- **Real-time market data** via Alpaca API
- **Paper trading support** for safe testing

### 🛡️ **Risk Management**
- **Stop-loss protection** (1.5% default)
- **Take-profit targets** (3.0% default)
- **Daily loss limits** ($500 default)
- **Position size limits** ($1000 max per trade)
- **Wash sale prevention** (30-day window)
- **Cooldown periods** to prevent overtrading

### ⏰ **Timezone-Aware Scheduling**
- **NYSE market hours** (9:30 AM - 4:00 PM ET)
- **Automatic trading sessions**
- **Market open/close detection**
- **Global timezone support**

## 📊 **Current Performance**

The bot is actively trading with:
- **Strategy**: Smart Buy Low Sell High
- **Market Regime**: Trending (80% confidence)
- **Active Symbols**: AAPL, MSFT, GOOGL, TSLA, AMZN, NVDA, AMD
- **Signal Strength**: 0.7 (Strong buy signals detected)

## 🛠️ Installation

### Prerequisites
```bash
Python 3.8+
pip
git
```

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/mr.money.git
cd mr.money

# Install dependencies
pip install -r requirements.txt

# Configure your Alpaca API credentials
cp config.example.py config.py
# Edit config.py with your API keys

# Run the bot
python main.py
```

## 📁 Project Structure

```
mr.money/
├── main.py                 # Main bot entry point
├── config.py              # Configuration and API keys
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── src/
│   └── trading_bot.py   # Core trading bot logic
├── strategies/
│   ├── momentum_strategy.py      # Smart Buy Low Sell High
│   └── adaptive_strategy.py      # Strategy intelligence
├── utils/
│   ├── alpaca_client.py         # Alpaca API client
│   ├── risk_management.py       # Risk management system
│   ├── indicators.py            # Technical indicators
│   ├── logger.py               # Logging system
│   └── performance_analytics.py # Performance tracking
├── scripts/
│   ├── live_monitor.py         # Real-time monitoring
│   ├── clean_monitor.py        # Clean monitoring interface
│   ├── simple_monitor.py       # Ultra-simple monitor
│   └── buy_signal_scanner.py   # Buy signal scanner
├── tests/                     # Test files
└── logs/                     # Log files
```

## 🎮 Usage

### Start Trading Bot
```bash
python main.py
```

### Monitor Trading Activity
```bash
# Real-time monitoring
python scripts/live_monitor.py

# Clean interface
python scripts/clean_monitor.py

# Simple monitor
python scripts/simple_monitor.py
```

### Scan for Buy Signals
```bash
python scripts/buy_signal_scanner.py
```

### Run Backtests
```bash
python scripts/run_backtest.py
```

## 🔧 Configuration

### Environment Variables
```bash
# Trading mode (paper/live)
TRADING_MODE=paper

# Position sizing
MAX_POSITION_SIZE=1000
DAILY_LOSS_LIMIT=500
MAX_POSITIONS=5

# Risk management
STOP_LOSS_PERCENT=1.5
TAKE_PROFIT_PERCENT=3.0
RISK_PERCENTAGE=4

# API rate limits
MAX_API_CALLS_PER_MINUTE=150
TRADING_CYCLE_MINUTES=2
```

### Trading Symbols
Currently configured for:
- **AAPL** (Apple)
- **MSFT** (Microsoft)
- **GOOGL** (Google)
- **TSLA** (Tesla)
- **AMZN** (Amazon)
- **NVDA** (NVIDIA)
- **AMD** (Advanced Micro Devices)

## 📈 How It Works

### 1. **Market Analysis**
The bot analyzes each stock using:
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **ADX** (Average Directional Index)
- **Volatility** (ATR-based)
- **Volume** analysis

### 2. **Smart Buy Low Detection**
Looks for:
- Recent price drops (1h, 3h, 6h)
- RSI below 45 (approaching oversold)
- Negative momentum
- High volatility (panic selling)
- Multi-day downtrends

### 3. **Smart Sell High Detection**
Looks for:
- Recent price rises (1h, 3h, 6h)
- RSI above 55 (approaching overbought)
- Positive momentum
- High volatility (excitement)
- Multi-day uptrends

### 4. **Position Sizing**
- **Strong signals** (0.7+): Full position
- **Medium signals** (0.5+): 70% position
- **Weak signals** (0.3+): 50% position
- **Volatility adjustment**: Smaller positions for volatile stocks

## 🚨 Disclaimer

**This is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.**

- Use paper trading for testing
- Start with small amounts
- Never invest more than you can afford to lose
- Monitor the bot regularly
- Understand the risks involved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Alpaca Markets** for the trading API
- **yfinance** for market data
- **pandas** for data analysis
- **numpy** for numerical computations
- **ta-lib** for technical indicators

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review the test files for examples

---

**Happy Trading! 🚀💰**
