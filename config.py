import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the trading bot"""
    
    # Alpaca API Configuration
    ALPACA_API_KEY = 'PKW5F9J9XIBBWVD83D1Z'
    ALPACA_SECRET_KEY = 'AbQe1hte5yBjJcnMIirqTspOx5GSxmfiGZ6Yoqyy'
    ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'
    
    # Trading Configuration
    TRADING_MODE = os.getenv('TRADING_MODE', 'paper')  # paper or live
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'AMD']
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    DAILY_LOSS_LIMIT = float(os.getenv('DAILY_LOSS_LIMIT', '500'))
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '5'))
    
    # Strategy Configuration
    DEFAULT_STRATEGY = os.getenv('DEFAULT_STRATEGY', 'momentum')
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))
    SMA_SHORT = int(os.getenv('SMA_SHORT', '20'))
    SMA_LONG = int(os.getenv('SMA_LONG', '50'))
    EMA_SHORT = int(os.getenv('EMA_SHORT', '12'))
    EMA_LONG = int(os.getenv('EMA_LONG', '26'))
    BOLLINGER_PERIOD = int(os.getenv('BOLLINGER_PERIOD', '20'))
    BOLLINGER_STD_DEV = float(os.getenv('BOLLINGER_STD_DEV', '2'))
    
    # Risk Management - AGGRESSIVE MODE
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '1.5'))  # Tighter stop loss
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '3.0'))  # Faster profit taking
    MAX_PORTFOLIO_DRAWDOWN = float(os.getenv('MAX_PORTFOLIO_DRAWDOWN', '8.0'))  # Tighter drawdown
    EMERGENCY_STOP_LOSS = float(os.getenv('EMERGENCY_STOP_LOSS', '3.0'))  # Faster emergency stop
    RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', '4'))  # Higher risk for more trades
    
    # API Rate Limits - OFFICIAL ALPACA LIMITS
    # Official Alpaca API Documentation: 200 requests every minute per API key
    # We stay conservative at 150 requests/minute to avoid hitting the limit
    TRADING_CYCLE_MINUTES = int(os.getenv('TRADING_CYCLE_MINUTES', '2'))  # Every 2 minutes (conservative)
    MAX_API_CALLS_PER_MINUTE = int(os.getenv('MAX_API_CALLS_PER_MINUTE', '150'))  # Stay under 200 limit
    
    # Wash Sale Prevention
    WASH_SALE_WINDOW_DAYS = int(os.getenv('WASH_SALE_WINDOW_DAYS', '30'))
    MIN_HOLDING_TIME_HOURS = int(os.getenv('MIN_HOLDING_TIME_HOURS', '1'))  # Minimum 1 hour holding
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/trading-bot.log')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not found in environment variables")
        
        if not cls.SYMBOLS:
            raise ValueError("No trading symbols configured")
        
        print(f"✅ Configuration loaded:")
        print(f"   Base URL: {cls.ALPACA_BASE_URL}")
        print(f"   API Key: {cls.ALPACA_API_KEY[:4]}...{cls.ALPACA_API_KEY[-4:]}")
        print(f"   Trading Mode: {cls.TRADING_MODE}")
        print(f"   Symbols: {', '.join(cls.SYMBOLS)}")
        print(f"   Max Position Size: ${cls.MAX_POSITION_SIZE}")
        print(f"   Daily Loss Limit: ${cls.DAILY_LOSS_LIMIT}")

# Global config instance
config = Config()
