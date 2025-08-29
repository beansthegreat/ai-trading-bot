# 🐍 Python Trading Bot

A comprehensive algorithmic trading bot built in Python using the Alpaca API. This bot implements momentum-based trading strategies with advanced risk management and technical analysis.

## 🚀 Features

- **Momentum Trading Strategy**: Uses RSI, MACD, moving averages, and Bollinger Bands
- **Risk Management**: Stop-loss, take-profit, daily loss limits, and position sizing
- **Technical Analysis**: Comprehensive indicator calculations using `ta` library
- **Scheduled Trading**: Automated trading during market hours
- **Logging**: Detailed logging with rotation and error tracking
- **Paper Trading**: Safe testing with paper trading account

## 📁 Project Structure

```
├── config.py                 # Configuration management
├── trading_bot.py            # Main trading bot class
├── requirements.txt          # Python dependencies
├── test_connection.py        # Connection test script
├── utils/
│   ├── alpaca_client.py      # Alpaca API client
│   ├── logger.py             # Logging utilities
│   ├── indicators.py         # Technical indicators
│   └── risk_management.py    # Risk management system
├── strategies/
│   └── momentum_strategy.py  # Momentum trading strategy
└── logs/                     # Log files (auto-created)
```

## 🛠️ Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   ALPACA_KEY_ID=your_api_key_here
   ALPACA_SECRET=your_secret_key_here
   ALPACA_BASE=https://paper-api.alpaca.markets
   TRADING_MODE=paper
   MAX_POSITION_SIZE=1000
   DAILY_LOSS_LIMIT=500
   RISK_PERCENTAGE=2
   TRADING_SYMBOLS=AAPL,MSFT,GOOGL,TSLA,AMZN
   ```

3. **Test the connection:**
   ```bash
   python test_connection.py
   ```

## 🎯 Usage

### Start the Trading Bot
```bash
python trading_bot.py
```

### Test Connection
```bash
python test_connection.py
```

## 📊 Configuration

The bot is highly configurable through the `config.py` file and environment variables:

### Trading Parameters
- `MAX_POSITION_SIZE`: Maximum dollar amount per position
- `DAILY_LOSS_LIMIT`: Maximum daily loss in dollars
- `RISK_PERCENTAGE`: Risk per trade as percentage of portfolio
- `TRADING_SYMBOLS`: Comma-separated list of symbols to trade

### Strategy Parameters
- `RSI_PERIOD`: RSI calculation period (default: 14)
- `RSI_OVERBOUGHT`: RSI overbought threshold (default: 70)
- `RSI_OVERSOLD`: RSI oversold threshold (default: 30)
- `MACD_FAST`: MACD fast period (default: 12)
- `MACD_SLOW`: MACD slow period (default: 26)
- `SMA_SHORT`: Short SMA period (default: 20)
- `SMA_LONG`: Long SMA period (default: 50)

### Risk Management
- `STOP_LOSS_PERCENT`: Stop loss percentage (default: 2.0%)
- `TAKE_PROFIT_PERCENT`: Take profit percentage (default: 5.0%)
- `MAX_PORTFOLIO_DRAWDOWN`: Maximum portfolio drawdown (default: 10.0%)

## 🔧 Strategy Details

### Momentum Strategy
The bot uses a momentum-based strategy that combines:

1. **Technical Indicators:**
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Simple and Exponential Moving Averages
   - Bollinger Bands
   - Stochastic Oscillator
   - ATR (Average True Range)

2. **Signal Generation:**
   - Buy signals when indicators show oversold conditions
   - Sell signals when indicators show overbought conditions
   - Position sizing based on signal strength

3. **Risk Management:**
   - Stop-loss orders to limit losses
   - Take-profit orders to secure gains
   - Daily loss limits
   - Maximum position size limits

## 📈 Trading Schedule

The bot operates during market hours (9:30 AM - 4:00 PM ET, Monday-Friday):

- **Market Open (9:30 AM)**: Reset daily tracking
- **Every 5 Minutes**: Run trading cycle
- **Market Close (4:00 PM)**: End-of-day cleanup

## 🛡️ Risk Management

### Position Sizing
- Dynamic position sizing based on signal strength
- Maximum position size limits
- Risk percentage per trade

### Stop Loss & Take Profit
- Automatic stop-loss at configured percentage
- Take-profit orders at configured percentage
- Emergency stops for extreme losses

### Daily Limits
- Daily loss limits to prevent excessive losses
- Maximum drawdown protection
- Automatic position closure at limits

## 📝 Logging

The bot provides comprehensive logging:

- **Console Output**: Colored, real-time logging
- **File Logging**: Rotated log files with compression
- **Error Logging**: Separate error log file
- **Trade Logging**: Detailed trade execution logs

Log files are stored in the `logs/` directory:
- `trading-bot.log`: General trading logs
- `error.log`: Error logs only

## 🧪 Testing

### Connection Test
```bash
python test_connection.py
```

This will test:
- Alpaca API connection
- Account information retrieval
- Market status check
- Position and order retrieval
- Historical data access
- Optional small order placement

### Paper Trading
The bot is configured for paper trading by default, allowing safe testing without real money.

## ⚠️ Important Notes

1. **Paper Trading**: Always test with paper trading first
2. **Risk Management**: The bot includes risk management, but monitor its performance
3. **Market Hours**: The bot only trades during market hours
4. **API Limits**: Be aware of Alpaca API rate limits
5. **Backtesting**: Consider backtesting strategies before live trading

## 🔄 Migration from TypeScript

This Python version replaces the TypeScript implementation with:

- **Better Performance**: Python's data analysis libraries (pandas, numpy)
- **Easier Maintenance**: More readable Python code
- **Rich Ecosystem**: Access to Python's trading and analysis libraries
- **Better Error Handling**: Python's exception handling
- **Simplified Deployment**: No compilation needed

## 📞 Support

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Verify your Alpaca API credentials
3. Ensure the market is open for testing
4. Check your IP allowlist in Alpaca dashboard

## 📄 License

This project is for educational purposes. Use at your own risk.

---

**Happy Trading! 🚀📈**
