import pandas as pd
import numpy as np
import ta
from typing import Dict, Any
from config import config

class TechnicalIndicators:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = None) -> pd.Series:
        """Calculate Relative Strength Index"""
        if period is None:
            period = config.RSI_PERIOD
        
        return ta.momentum.RSIIndicator(df['close'], window=period).rsi()
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = None, slow: int = None, signal: int = None) -> Dict[str, pd.Series]:
        """Calculate MACD"""
        if fast is None:
            fast = config.MACD_FAST
        if slow is None:
            slow = config.MACD_SLOW
        if signal is None:
            signal = config.MACD_SIGNAL
        
        macd_indicator = ta.trend.MACD(
            df['close'], 
            window_fast=fast, 
            window_slow=slow, 
            window_sign=signal
        )
        
        return {
            'macd': macd_indicator.macd(),
            'macd_signal': macd_indicator.macd_signal(),
            'macd_histogram': macd_indicator.macd_diff()
        }
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return ta.trend.SMAIndicator(df['close'], window=period).sma_indicator()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return ta.trend.EMAIndicator(df['close'], window=period).ema_indicator()
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = None, std_dev: float = None) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        if period is None:
            period = config.BOLLINGER_PERIOD
        if std_dev is None:
            std_dev = config.BOLLINGER_STD_DEV
        
        bb_indicator = ta.volatility.BollingerBands(
            df['close'], 
            window=period, 
            window_dev=std_dev
        )
        
        return {
            'bb_upper': bb_indicator.bollinger_hband(),
            'bb_middle': bb_indicator.bollinger_mavg(),
            'bb_lower': bb_indicator.bollinger_lband(),
            'bb_width': bb_indicator.bollinger_wband(),
            'bb_percent': bb_indicator.bollinger_pband()
        }
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        stoch_indicator = ta.momentum.StochasticOscillator(
            df['high'], 
            df['low'], 
            df['close'],
            window=k_period,
            smooth_window=d_period
        )
        
        return {
            'stoch_k': stoch_indicator.stoch(),
            'stoch_d': stoch_indicator.stoch_signal()
        }
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        return ta.volatility.AverageTrueRange(
            df['high'], 
            df['low'], 
            df['close'], 
            window=period
        ).average_true_range()
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        return ta.trend.ADXIndicator(
            df['high'], 
            df['low'], 
            df['close'], 
            window=period
        ).adx()
    
    @staticmethod
    def calculate_volume_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Volume Simple Moving Average"""
        return df['volume'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for a dataframe"""
        df = df.copy()
        
        # RSI
        df['rsi'] = TechnicalIndicators.calculate_rsi(df)
        
        # MACD
        macd_data = TechnicalIndicators.calculate_macd(df)
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['macd_signal']
        df['macd_histogram'] = macd_data['macd_histogram']
        
        # Moving Averages
        df['sma_short'] = TechnicalIndicators.calculate_sma(df, config.SMA_SHORT)
        df['sma_long'] = TechnicalIndicators.calculate_sma(df, config.SMA_LONG)
        df['ema_short'] = TechnicalIndicators.calculate_ema(df, config.EMA_SHORT)
        df['ema_long'] = TechnicalIndicators.calculate_ema(df, config.EMA_LONG)
        
        # Bollinger Bands
        bb_data = TechnicalIndicators.calculate_bollinger_bands(df)
        df['bb_upper'] = bb_data['bb_upper']
        df['bb_middle'] = bb_data['bb_middle']
        df['bb_lower'] = bb_data['bb_lower']
        df['bb_width'] = bb_data['bb_width']
        df['bb_percent'] = bb_data['bb_percent']
        
        # Stochastic
        stoch_data = TechnicalIndicators.calculate_stochastic(df)
        df['stoch_k'] = stoch_data['stoch_k']
        df['stoch_d'] = stoch_data['stoch_d']
        
        # ATR
        df['atr'] = TechnicalIndicators.calculate_atr(df)
        
        # ADX
        df['adx'] = TechnicalIndicators.calculate_adx(df)
        
        # Volume
        df['volume_sma'] = TechnicalIndicators.calculate_volume_sma(df)
        
        return df
    
    @staticmethod
    def get_signal_strength(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate signal strength based on multiple indicators"""
        if len(df) < 50:  # Need enough data
            return {'strength': 0, 'signal': 'neutral'}
        
        latest = df.iloc[-1]
        
        # RSI signals
        rsi_signal = 0
        if latest['rsi'] < config.RSI_OVERSOLD:
            rsi_signal = 1  # Oversold - bullish
        elif latest['rsi'] > config.RSI_OVERBOUGHT:
            rsi_signal = -1  # Overbought - bearish
        
        # MACD signals
        macd_signal = 0
        if latest['macd'] > latest['macd_signal'] and latest['macd_histogram'] > 0:
            macd_signal = 1  # Bullish
        elif latest['macd'] < latest['macd_signal'] and latest['macd_histogram'] < 0:
            macd_signal = -1  # Bearish
        
        # Moving Average signals
        ma_signal = 0
        if latest['ema_short'] > latest['ema_long']:
            ma_signal = 1  # Bullish
        elif latest['ema_short'] < latest['ema_long']:
            ma_signal = -1  # Bearish
        
        # Bollinger Band signals
        bb_signal = 0
        if latest['close'] < latest['bb_lower']:
            bb_signal = 1  # Oversold - bullish
        elif latest['close'] > latest['bb_upper']:
            bb_signal = -1  # Overbought - bearish
        
        # Stochastic signals
        stoch_signal = 0
        if latest['stoch_k'] < 20 and latest['stoch_k'] > latest['stoch_d']:
            stoch_signal = 1  # Bullish
        elif latest['stoch_k'] > 80 and latest['stoch_k'] < latest['stoch_d']:
            stoch_signal = -1  # Bearish
        
        # Calculate overall strength
        signals = [rsi_signal, macd_signal, ma_signal, bb_signal, stoch_signal]
        strength = sum(signals) / len(signals)
        
        # Determine signal
        if strength > 0.3:
            signal = 'buy'
        elif strength < -0.3:
            signal = 'sell'
        else:
            signal = 'neutral'
        
        return {
            'strength': strength,
            'signal': signal,
            'rsi_signal': rsi_signal,
            'macd_signal': macd_signal,
            'ma_signal': ma_signal,
            'bb_signal': bb_signal,
            'stoch_signal': stoch_signal
        }
