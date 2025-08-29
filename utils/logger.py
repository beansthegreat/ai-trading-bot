import os
import sys
from datetime import datetime
from loguru import logger
from config import config

class TradingLogger:
    """Custom logger for the trading bot"""
    
    def __init__(self):
        # Remove default handler
        logger.remove()
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
        
        # Add console handler with color
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=config.LOG_LEVEL,
            colorize=True
        )
        
        # Add file handler
        logger.add(
            config.LOG_FILE,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=config.LOG_LEVEL,
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )
        
        # Add error log file
        logger.add(
            "./logs/error.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="1 day",
            retention="90 days",
            compression="zip"
        )
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        if kwargs:
            logger.info(f"{message} | {kwargs}")
        else:
            logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        if kwargs:
            logger.warning(f"{message} | {kwargs}")
        else:
            logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        if kwargs:
            logger.error(f"{message} | {kwargs}")
        else:
            logger.error(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if kwargs:
            logger.debug(f"{message} | {kwargs}")
        else:
            logger.debug(message)
    
    def success(self, message: str, **kwargs):
        """Log success message"""
        if kwargs:
            logger.success(f"{message} | {kwargs}")
        else:
            logger.success(message)
    
    def trade(self, action: str, symbol: str, quantity: int = None, price: float = None, dollar_amount: float = None, **kwargs):
        """Log trading action"""
        if dollar_amount:
            trade_info = f"TRADE: {action.upper()} ${dollar_amount:.2f} {symbol}"
        elif quantity:
            trade_info = f"TRADE: {action.upper()} {quantity} {symbol}"
        else:
            trade_info = f"TRADE: {action.upper()} {symbol}"
            
        if price:
            trade_info += f" @ ${price:.2f}"
        
        if kwargs:
            trade_info += f" | {kwargs}"
        
        logger.info(trade_info)
    
    def strategy(self, strategy_name: str, signal: str, symbol: str, **kwargs):
        """Log strategy signal"""
        signal_info = f"STRATEGY: {strategy_name} | {signal.upper()} | {symbol}"
        if kwargs:
            signal_info += f" | {kwargs}"
        
        logger.info(signal_info)

# Global logger instance
trading_logger = TradingLogger()
