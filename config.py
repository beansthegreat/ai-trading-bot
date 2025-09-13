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
    
    # S&P 500 Configuration
    USE_SP500_MODE = os.getenv('USE_SP500_MODE', 'True').lower() == 'true'
    SP500_MAX_STOCKS = int(os.getenv('SP500_MAX_STOCKS', '500'))
    SP500_TOP_PERFORMERS = int(os.getenv('SP500_TOP_PERFORMERS', '50'))
    SP500_RETRAIN_DAYS = int(os.getenv('SP500_RETRAIN_DAYS', '7'))
    SP500_CLEANUP_DELAY_DAYS = int(os.getenv('SP500_CLEANUP_DELAY_DAYS', '30'))
    SP500_MIN_TRAINING_DATA_DAYS = int(os.getenv('SP500_MIN_TRAINING_DATA_DAYS', '252'))
    
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
    
    # AI/Hardware Configuration
    USE_GPU = os.getenv('USE_GPU', 'True').lower() == 'true'
    USE_NPU = os.getenv('USE_NPU', 'True').lower() == 'true'
    USE_HYBRID_MODE = os.getenv('USE_HYBRID_MODE', 'True').lower() == 'true'
    AI_ENGINE = os.getenv('AI_ENGINE', 'hybrid')  # 'standard', 'advanced', 'hybrid'
    
    # Model Configuration
    MODEL_RETRAIN_HOURS = int(os.getenv('MODEL_RETRAIN_HOURS', '24'))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
    MAX_MODELS_PER_SYMBOL = int(os.getenv('MAX_MODELS_PER_SYMBOL', '5'))
    
    # Hardware-specific settings
    GPU_MEMORY_LIMIT = int(os.getenv('GPU_MEMORY_LIMIT', '4096'))  # MB
    NPU_BATCH_SIZE = int(os.getenv('NPU_BATCH_SIZE', '32'))
    CPU_THREADS = int(os.getenv('CPU_THREADS', '4'))
    
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
        print(f"   AI Engine: {cls.AI_ENGINE}")
        print(f"   GPU Enabled: {cls.USE_GPU}")
        print(f"   NPU Enabled: {cls.USE_NPU}")
        print(f"   Hybrid Mode: {cls.USE_HYBRID_MODE}")
        print(f"   S&P 500 Mode: {cls.USE_SP500_MODE}")
        if cls.USE_SP500_MODE:
            print(f"   S&P 500 Top Performers: {cls.SP500_TOP_PERFORMERS}")

# Global config instance
config = Config()
