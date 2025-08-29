# 🤖 Alpaca Trading Bot - Dynamic Market Scanner & Day Trading System

A sophisticated algorithmic trading bot that continuously scans the market for high-momentum opportunities and executes trades automatically. Built for day trading with advanced risk management and dynamic position sizing.

## 🚀 Key Features

- **🔍 Dynamic Market Scanner** - Scans 80+ high-volume stocks every 60 seconds
- **📊 Technical Analysis** - RSI, MACD, SMA, momentum, and volatility analysis
- **💰 Dynamic Position Sizing** - Adjusts trade amounts based on available funds and signal strength
- **🛡️ Risk Management** - Stop-loss, take-profit, portfolio limits, and wash sale detection
- **⏰ Timezone-Aware Scheduling** - Automatically starts/stops based on NYSE market hours relative to Netherlands timezone
- **🌍 Multi-Timeframe Support** - Handles daylight saving time changes automatically
- **📈 Real-time Monitoring** - Comprehensive logging and performance tracking

## 📋 Table of Contents

1. [Investment Strategies](#-investment-strategies)
2. [Market Scanner](#-market-scanner)
3. [Technical Analysis](#-technical-analysis)
4. [Risk Management](#-risk-management)
5. [Position Sizing](#-position-sizing)
6. [Timezone-Aware Trading Schedule](#-timezone-aware-trading-schedule)
7. [Installation & Setup](#-installation--setup)
8. [Configuration](#-configuration)
9. [Usage](#-usage)
10. [Monitoring & Logs](#-monitoring--logs)

---

## 🎯 Investment Strategies

### 1. **Momentum Strategy** (Primary)
The core strategy that identifies stocks with strong upward momentum and high volume.

**What it looks for:**
- **Price Momentum**: Stocks moving up 2%+ in recent periods
- **Volume Spikes**: 50%+ increase in trading volume
- **Technical Confirmation**: RSI, MACD, and SMA alignments
- **Low Volatility**: Stable price movement (not erratic)

**Scoring System (0-100):**
- **Signal Strength (30%)**: Price change + Volume + Momentum
- **Signal Confidence (25%)**: Technical score - Volatility
- **Technical Score (20%)**: RSI + MACD + SMA analysis
- **Momentum (15%)**: Recent price trend
- **Volume Change (10%)**: Volume spike percentage

**Trade Execution:**
- Only trades opportunities with **75+ overall score**
- Uses dynamic position sizing based on signal strength
- Applies stop-loss and take-profit automatically

### 2. **Technical Analysis Strategy**
Uses multiple technical indicators to confirm trading signals.

**Indicators Used:**
- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
  - RSI < 30: Oversold (bullish signal)
  - RSI > 70: Overbought (bearish signal)
- **MACD (Moving Average Convergence Divergence)**: Momentum and trend changes
  - MACD > Signal Line: Bullish crossover
  - MACD < Signal Line: Bearish crossover
- **SMA (Simple Moving Average)**: Trend direction
  - 20-day SMA > 50-day SMA: Golden cross (bullish)
  - 20-day SMA < 50-day SMA: Death cross (bearish)

### 3. **Volume Analysis Strategy**
Focuses on unusual trading volume as a leading indicator.

**Volume Criteria:**
- **Minimum Volume**: $1,000,000 daily volume
- **Volume Spike**: 50%+ above average volume
- **Volume Confirmation**: High volume on price increases

---

## 🔍 Market Scanner

### **Real-Time Scanning**
The bot continuously scans 80+ high-volume stocks across multiple sectors:

**Technology (20 stocks):**
- AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX, AMD, CRM
- ADBE, PYPL, INTC, ORCL, CSCO, QCOM, TXN, AVGO, MU, ADI

**Finance (10 stocks):**
- JPM, BAC, WFC, GS, MS, C, USB, PNC, TFC, COF

**Healthcare (10 stocks):**
- JNJ, PFE, UNH, ABBV, TMO, ABT, DHR, BMY, AMGN, GILD

**Consumer (10 stocks):**
- HD, WMT, PG, KO, PEP, COST, TGT, LOW, SBUX, NKE

**Energy (10 stocks):**
- XOM, CVX, COP, EOG, SLB, PSX, VLO, MPC, OXY, HAL

**ETFs (10 stocks):**
- SPY, QQQ, IWM, DIA, VTI, VOO, VEA, VWO, BND, TLT

**Growth/Momentum (20 stocks):**
- PLTR, SNOW, CRWD, ZM, SHOP, SQ, ROKU, SPOT, UBER, LYFT
- DASH, ABNB, COIN, HOOD, RBLX, SNAP, PINS, TWTR, BYND, NIO

### **Scanning Process**
1. **Every 60 seconds** - Analyzes all 80+ stocks
2. **Data Collection** - Gets current price, volume, and historical data
3. **Technical Analysis** - Calculates RSI, MACD, SMA, momentum, volatility
4. **Opportunity Scoring** - Ranks stocks 0-100 based on multiple factors
5. **Top Selection** - Identifies top 10 opportunities
6. **Trade Execution** - Automatically trades top 3 high-score opportunities

### **Scanner Criteria**
- **Price Range**: $5 - $1,000 per share
- **Minimum Volume**: $1,000,000 daily volume
- **Price Change**: 2%+ movement required
- **Volume Change**: 50%+ spike required
- **Momentum Threshold**: 70+ score required
- **Volatility Threshold**: 3% maximum volatility

---

## 📊 Technical Analysis

### **RSI (Relative Strength Index)**
**Purpose**: Identifies overbought and oversold conditions
**Calculation**: 14-period RSI
**Signals**:
- **Oversold (RSI < 30)**: Potential buy signal
- **Overbought (RSI > 70)**: Potential sell signal
- **Neutral (30-70)**: No clear signal

### **MACD (Moving Average Convergence Divergence)**
**Purpose**: Identifies momentum changes and trend reversals
**Parameters**: 12, 26, 9 (fast, slow, signal)
**Signals**:
- **Bullish Crossover**: MACD line crosses above signal line
- **Bearish Crossover**: MACD line crosses below signal line
- **Divergence**: Price and MACD moving in opposite directions

### **SMA (Simple Moving Average)**
**Purpose**: Identifies trend direction and support/resistance
**Periods**: 20-day and 50-day SMAs
**Signals**:
- **Golden Cross**: 20-day SMA crosses above 50-day SMA (bullish)
- **Death Cross**: 20-day SMA crosses below 50-day SMA (bearish)
- **Support/Resistance**: Price bouncing off moving averages

### **Momentum Analysis**
**Purpose**: Measures the strength of price movement
**Calculation**: Recent price change over 5 periods
**Scoring**: Normalized to 0-100 scale

### **Volatility Analysis**
**Purpose**: Measures price stability and risk
**Calculation**: Standard deviation of returns
**Usage**: Lower volatility = higher confidence in signals

---

## 🛡️ Risk Management

### **Position Limits**
- **Maximum Positions**: 5 concurrent positions
- **Portfolio Limit**: 10% maximum per position
- **Daily Loss Limit**: $500 maximum daily loss
- **Emergency Stop**: 5% portfolio drawdown

### **Stop-Loss & Take-Profit**
- **Stop-Loss**: 2% below entry price
- **Take-Profit**: 5% above entry price
- **Trailing Stop**: Adjusts with price movement

### **Wash Sale Detection**
- **30-Day Window**: Detects wash sales for tax compliance
- **Day Trading Exception**: Allows sells despite wash sales to avoid overnight risk
- **Logging**: Records all wash sales for tax reporting

### **Portfolio Protection**
- **Diversification**: Spreads risk across multiple stocks
- **Sector Limits**: No more than 30% in any single sector
- **Correlation Check**: Avoids highly correlated positions

---

## 💰 Position Sizing

### **Dynamic Position Sizing**
The bot automatically adjusts position sizes based on:

**Signal Quality:**
- **90%+ signal**: Full position size (up to $1,000)
- **80%+ signal**: 80% of max position
- **70%+ signal**: 60% of max position
- **60%+ signal**: 40% of max position
- **<60% signal**: Minimum position ($100)

**Stock Price Adjustments:**
- **$1000+ stocks**: Max $300 position (expensive stocks)
- **$500+ stocks**: Max $500 position
- **$10- stocks**: 50% larger position (affordable stocks)
- **Normal stocks**: Standard position size

**Available Funds:**
- **Risk Per Trade**: 2% of buying power
- **Buffer**: Leaves 5% buying power for safety
- **Minimum**: $100 minimum position size

### **Position Size Formula**
```
Position Size = Signal Quality × Available Funds × Stock Price Factor × Risk Percentage
```

---

## ⏰ Timezone-Aware Trading Schedule

### **🌍 Automatic Timezone Scheduling**
The bot automatically starts and stops based on NYSE market hours relative to Netherlands timezone:

**NYSE Market Hours (ET)**: 9:30 AM - 4:00 PM
**Netherlands Time**: 15:30 - 22:00 (CEST) / 16:30 - 23:00 (CET)

**🕐 Timezone Features:**
- **Automatic Timezone Detection**: Handles CET/CEST transitions
- **Automatic Start**: Begins trading at NYSE open (15:30 Netherlands time)
- **Automatic Stop**: Ends trading at NYSE close (22:00 Netherlands time)
- **Weekend Skip**: No trading on weekends
- **Holiday Skip**: Respects NYSE holidays
- **Real-time Conversion**: Live timezone conversion during operation

### **📅 Trading Schedule by Season**

**Summer (CEST - Central European Summer Time):**
- NYSE Open: 15:30 Netherlands time
- NYSE Close: 22:00 Netherlands time
- Time Difference: +6 hours from NYSE

**Winter (CET - Central European Time):**
- NYSE Open: 16:30 Netherlands time  
- NYSE Close: 23:00 Netherlands time
- Time Difference: +5 hours from NYSE

### **🔄 Trading Cycle**
1. **Market Open**: Scanner starts, begins monitoring
2. **Continuous Scanning**: Every 5 minutes during market hours
3. **Opportunity Detection**: Identifies high-score stocks
4. **Trade Execution**: Places orders automatically
5. **Position Monitoring**: Tracks performance and risk
6. **Market Close**: Closes positions, stops scanning

### **🚀 Quick Start Commands**
```bash
# Start the timezone-aware trading bot
python start_trading_bot.py

# Test timezone functionality
python test_timezone.py

# Check current bot status
python -c "from trading_bot import trading_bot; print(trading_bot.get_status())"
```

---

## 🛠️ Installation & Setup

### **Prerequisites**
- Node.js 18+ installed
- Alpaca trading account (paper or live)
- API credentials from Alpaca

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd alpaca-trading-bot

# Install dependencies
npm install

# Build the project
npm run build
```

### **Configuration**
1. **Edit `config.json`** with your Alpaca credentials
2. **Adjust trading parameters** as needed
3. **Set risk management limits** for your comfort level

### **Alpaca Setup**
1. Create account at [alpaca.markets](https://alpaca.markets)
2. Get API key and secret
3. Choose paper trading for testing
4. Add funds to your account

---

## ⚙️ Configuration

### **config.json Structure**
```json
{
  "alpaca": {
    "apiKey": "your-api-key",
    "secretKey": "your-secret-key",
    "baseUrl": "https://paper-api.alpaca.markets/v2"
  },
  "trading": {
    "mode": "paper",
    "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"],
    "maxPositionSize": 1000,
    "dailyLossLimit": 500,
    "maxPositions": 5
  },
  "strategy": {
    "rsiPeriod": 14,
    "rsiOverbought": 70,
    "rsiOversold": 30,
    "macdFast": 12,
    "macdSlow": 26,
    "macdSignal": 9,
    "smaShort": 20,
    "smaLong": 50
  },
  "risk": {
    "stopLossPercent": 2.0,
    "takeProfitPercent": 5.0,
    "maxPortfolioDrawdown": 10.0,
    "emergencyStopLoss": 5.0
  }
}
```

---

## 🚀 Usage

### **Start the Bot**
```bash
# Development mode (with logs)
npm run dev

# Production mode
npm start
```

### **Test Individual Components**
```bash
# Test API connection
npm run test:connection

# Test market scanner
npm run test:scanner

# Test position sizing
npm run test:position-sizing

# Test wash sale detection
npm run test:wash-sale

# Test trading scheduler
npm run test:scheduler
```

### **Monitor Performance**
- **Real-time Logs**: Check `logs/trading-bot.log`
- **Error Logs**: Check `logs/error.log`
- **Console Output**: Live trading activity

---

## 📈 Monitoring & Logs

### **Log Files**
- **`logs/trading-bot.log`**: All trading activity and decisions
- **`logs/error.log`**: Error messages and debugging info

### **Key Metrics to Monitor**
- **Win Rate**: Percentage of profitable trades
- **Average Return**: Average profit/loss per trade
- **Max Drawdown**: Largest portfolio decline
- **Sharpe Ratio**: Risk-adjusted returns
- **Total Trades**: Number of trades executed

### **Performance Dashboard**
The bot logs comprehensive metrics including:
- Trade execution details
- Position sizing decisions
- Risk management events
- Scanner opportunities
- Market conditions

---

## ⚠️ Risk Disclaimer

**This is experimental software for educational purposes. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.**

**Key Risks:**
- **Market Risk**: Stock prices can go down
- **Technical Risk**: Software bugs or API failures
- **Liquidity Risk**: Unable to exit positions quickly
- **Regulatory Risk**: Changes in trading rules
- **Tax Risk**: Complex tax implications of frequent trading

**Recommendations:**
- Start with paper trading
- Use only risk capital you can afford to lose
- Monitor the bot closely initially
- Understand all strategies before live trading
- Consult with a financial advisor

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## 🧠 Intelligent Position Scaling

The bot features **intelligent position scaling** that automatically switches between dollar amounts and share quantities based on stock prices and available funds.

### **🎯 Smart Decision Matrix**

**Low Price Stocks (<$50):**
- ✅ **Prefer Shares** for better precision
- ✅ **Example**: Buy 1.6 shares of Ford (F) @ $12.50 = $20

**High Price Stocks (>$200):**
- ✅ **Prefer Dollar Amounts** for accessibility
- ✅ **Example**: Buy $20 worth of AAPL @ $230.50 = 0.087 shares

**Medium Price Stocks ($50-$200):**
- ✅ **Intelligent Choice** based on available cash
- ✅ **High cash** ($500+): Prefer shares
- ✅ **Low cash** (<$500): Prefer dollar amounts

### **💰 Scaling Examples**

| Stock | Price | Cash | Signal | Decision | Amount | Shares |
|-------|-------|------|--------|----------|--------|--------|
| **F** | $12.50 | $1000 | 0.8 | **SHARES** | 1.6 | 1.6000 |
| **AAPL** | $230.50 | $1000 | 0.7 | **DOLLAR** | $20.00 | 0.0868 |
| **TSLA** | $450.25 | $500 | 0.5 | **DOLLAR** | $10.00 | 0.0222 |
| **MSFT** | $85.30 | $1000 | 0.6 | **SHARES** | 0.2345 | 0.2345 |

### **🛡️ Safety Features**

- ✅ **Minimum amounts**: $5 for dollar amounts, 0.01 shares
- ✅ **Maximum limits**: $1000 for dollar amounts, 100 shares
- ✅ **Cash validation**: Ensures sufficient funds
- ✅ **Signal strength scaling**: Stronger signals = bigger positions
- ✅ **Automatic fallbacks**: Uses alternative method if constraints not met

### **🚀 Test Intelligent Scaling**
```bash
python test_intelligent_scaling.py
```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support

For questions or issues:
1. Check the logs for error messages
2. Review the configuration settings
3. Test individual components
4. Create an issue with detailed information

**Remember**: This is a sophisticated trading system. Take time to understand how it works before using it with real money!
