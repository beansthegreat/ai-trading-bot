#!/usr/bin/env python3
"""
🔴 Live Data Manager - On-Demand API Data Access
Fetches market data from APIs on-demand instead of storing large chunks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import time
from collections import OrderedDict
import threading
import warnings
warnings.filterwarnings('ignore')

from utils.logger import trading_logger
from config import config

class LiveDataCache:
    """Smart in-memory cache with TTL (Time To Live)"""

    def __init__(self, max_size: int = 100, default_ttl_minutes: int = 5):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.default_ttl_minutes = default_ttl_minutes
        self.lock = threading.Lock()

        # Cache statistics
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Get data from cache if not expired"""
        with self.lock:
            if key in self.cache:
                data, expiry = self.cache[key]

                # Check if expired
                if datetime.now() < expiry:
                    # Move to end (LRU)
                    self.cache.move_to_end(key)
                    self.hits += 1
                    return data.copy()
                else:
                    # Expired - remove
                    del self.cache[key]

            self.misses += 1
            return None

    def set(self, key: str, data: pd.DataFrame, ttl_minutes: Optional[int] = None):
        """Set data in cache with TTL"""
        with self.lock:
            if ttl_minutes is None:
                ttl_minutes = self.default_ttl_minutes

            expiry = datetime.now() + timedelta(minutes=ttl_minutes)

            # Add to cache
            self.cache[key] = (data.copy(), expiry)

            # Enforce max size (LRU eviction)
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def invalidate(self, key: str):
        """Invalidate specific cache entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


class LiveDataManager:
    """
    Live Data Manager - Fetches data on-demand from APIs

    Key Features:
    - On-demand data fetching (no large downloads)
    - Smart memory caching with TTL
    - Multiple data sources (Alpaca, yfinance)
    - Minimal disk storage
    - Real-time data access
    """

    def __init__(self):
        self.name = "Live Data Manager"
        self.description = "On-demand API data access with smart caching"

        # Cache configuration
        self.cache = LiveDataCache(
            max_size=config.LIVE_DATA_CACHE_SIZE if hasattr(config, 'LIVE_DATA_CACHE_SIZE') else 100,
            default_ttl_minutes=config.LIVE_DATA_TTL_MINUTES if hasattr(config, 'LIVE_DATA_TTL_MINUTES') else 5
        )

        # API configuration
        self.use_alpaca = config.USE_ALPACA_DATA if hasattr(config, 'USE_ALPACA_DATA') else False
        self.use_yfinance = True  # Fallback

        # Rate limiting
        self.last_api_call = {}
        self.min_api_interval = 0.5  # Minimum seconds between calls per symbol

        # Performance tracking
        self.api_calls_count = 0
        self.total_data_fetched_mb = 0

        trading_logger.info("Live Data Manager initialized",
                           cache_size=self.cache.max_size,
                           ttl_minutes=self.cache.default_ttl_minutes,
                           use_alpaca=self.use_alpaca)

    def get_live_data(self, symbol: str, timeframe: str = '1D',
                     lookback_bars: int = 100, force_refresh: bool = False) -> pd.DataFrame:
        """
        Get live market data for a symbol

        Args:
            symbol: Stock symbol
            timeframe: Data timeframe ('1D', '1H', '5M', '1M')
            lookback_bars: Number of bars to fetch
            force_refresh: Force API call even if cached

        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{symbol}_{timeframe}_{lookback_bars}"

        # Check cache first (unless forced refresh)
        if not force_refresh:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                trading_logger.debug(f"Cache hit: {cache_key}")
                return cached_data

        # Fetch from API
        trading_logger.debug(f"Fetching live data: {cache_key}")
        data = self._fetch_from_api(symbol, timeframe, lookback_bars)

        # Cache the result
        if data is not None and not data.empty:
            # Determine TTL based on timeframe
            ttl_minutes = self._get_ttl_for_timeframe(timeframe)
            self.cache.set(cache_key, data, ttl_minutes)

            # Track data size
            data_size_mb = data.memory_usage(deep=True).sum() / (1024 * 1024)
            self.total_data_fetched_mb += data_size_mb

        return data

    def _fetch_from_api(self, symbol: str, timeframe: str, lookback_bars: int) -> pd.DataFrame:
        """Fetch data from API sources"""
        # Rate limiting per symbol
        self._enforce_rate_limit(symbol)

        # Try Alpaca first if enabled
        if self.use_alpaca:
            try:
                data = self._fetch_from_alpaca(symbol, timeframe, lookback_bars)
                if data is not None and not data.empty:
                    self.api_calls_count += 1
                    return data
            except Exception as e:
                trading_logger.warning(f"Alpaca fetch failed for {symbol}: {e}")

        # Fallback to yfinance
        if self.use_yfinance:
            try:
                data = self._fetch_from_yfinance(symbol, timeframe, lookback_bars)
                if data is not None and not data.empty:
                    self.api_calls_count += 1
                    return data
            except Exception as e:
                trading_logger.error(f"yfinance fetch failed for {symbol}: {e}")

        # Return empty dataframe if all sources fail
        return pd.DataFrame()

    def _fetch_from_alpaca(self, symbol: str, timeframe: str, lookback_bars: int) -> pd.DataFrame:
        """Fetch data from Alpaca API"""
        from utils.alpaca_client import alpaca_client

        # Convert timeframe to Alpaca format
        alpaca_timeframe = self._convert_timeframe_to_alpaca(timeframe)

        # Calculate date range
        end_date = datetime.now()
        start_date = self._calculate_start_date(timeframe, lookback_bars)

        # Fetch data
        data = alpaca_client.get_historical_data(
            symbol,
            timeframe=alpaca_timeframe,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        # Limit to requested bars
        if not data.empty and len(data) > lookback_bars:
            data = data.tail(lookback_bars)

        return data

    def _fetch_from_yfinance(self, symbol: str, timeframe: str, lookback_bars: int) -> pd.DataFrame:
        """Fetch data from yfinance (minimal, on-demand)"""
        import yfinance as yf

        # Convert timeframe to yfinance format
        yf_interval = self._convert_timeframe_to_yfinance(timeframe)

        # Calculate period (fetch only what's needed)
        period = self._calculate_yfinance_period(timeframe, lookback_bars)

        # Fetch minimal data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=yf_interval, auto_adjust=True)

        if data.empty:
            return pd.DataFrame()

        # Clean and format
        data = data.reset_index()
        data.columns = [col.lower() for col in data.columns]

        # Ensure required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                return pd.DataFrame()

        # Limit to requested bars
        if len(data) > lookback_bars:
            data = data.tail(lookback_bars)

        return data

    def _enforce_rate_limit(self, symbol: str):
        """Enforce rate limiting per symbol"""
        if symbol in self.last_api_call:
            elapsed = time.time() - self.last_api_call[symbol]
            if elapsed < self.min_api_interval:
                time.sleep(self.min_api_interval - elapsed)

        self.last_api_call[symbol] = time.time()

    def _get_ttl_for_timeframe(self, timeframe: str) -> int:
        """Get appropriate cache TTL based on timeframe"""
        ttl_map = {
            '1M': 1,    # 1 minute bars cache for 1 minute
            '5M': 3,    # 5 minute bars cache for 3 minutes
            '15M': 10,  # 15 minute bars cache for 10 minutes
            '1H': 30,   # 1 hour bars cache for 30 minutes
            '1D': 60,   # 1 day bars cache for 1 hour
        }
        return ttl_map.get(timeframe.upper(), 5)

    def _calculate_start_date(self, timeframe: str, lookback_bars: int) -> datetime:
        """Calculate start date based on timeframe and lookback"""
        now = datetime.now()

        # Estimate days needed based on timeframe
        timeframe_to_days = {
            '1M': lookback_bars / (6.5 * 60),      # Trading hours per day
            '5M': lookback_bars / (6.5 * 60 / 5),
            '15M': lookback_bars / (6.5 * 60 / 15),
            '1H': lookback_bars / 6.5,
            '1D': lookback_bars,
        }

        days_needed = timeframe_to_days.get(timeframe.upper(), lookback_bars)
        # Add buffer for weekends/holidays
        days_needed = int(days_needed * 1.5)

        return now - timedelta(days=days_needed)

    def _calculate_yfinance_period(self, timeframe: str, lookback_bars: int) -> str:
        """Calculate appropriate yfinance period string"""
        # Map to yfinance period strings
        timeframe_upper = timeframe.upper()

        if timeframe_upper == '1M':
            # 1 minute bars - limited to 7 days by yfinance
            return '7d'
        elif timeframe_upper == '5M':
            return '1mo'
        elif timeframe_upper == '15M':
            return '1mo'
        elif timeframe_upper == '1H':
            return '3mo'
        elif timeframe_upper == '1D':
            # For daily, calculate based on bars
            if lookback_bars <= 30:
                return '1mo'
            elif lookback_bars <= 90:
                return '3mo'
            elif lookback_bars <= 180:
                return '6mo'
            elif lookback_bars <= 365:
                return '1y'
            else:
                return '2y'

        return '1mo'  # Default

    def _convert_timeframe_to_alpaca(self, timeframe: str) -> str:
        """Convert timeframe to Alpaca format"""
        conversion = {
            '1M': '1Min',
            '5M': '5Min',
            '15M': '15Min',
            '1H': '1Hour',
            '1D': '1Day',
        }
        return conversion.get(timeframe.upper(), '1Day')

    def _convert_timeframe_to_yfinance(self, timeframe: str) -> str:
        """Convert timeframe to yfinance format"""
        conversion = {
            '1M': '1m',
            '5M': '5m',
            '15M': '15m',
            '1H': '1h',
            '1D': '1d',
        }
        return conversion.get(timeframe.upper(), '1d')

    def get_realtime_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for a symbol (no caching for quotes)

        Returns:
            Dict with current price, bid, ask, volume
        """
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'bid': info.get('bid'),
                'ask': info.get('ask'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
                'timestamp': datetime.now()
            }
        except Exception as e:
            trading_logger.error(f"Failed to get realtime quote for {symbol}: {e}")
            return None

    def get_multi_symbol_data(self, symbols: List[str], timeframe: str = '1D',
                             lookback_bars: int = 100) -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple symbols efficiently

        Returns:
            Dict mapping symbol to DataFrame
        """
        results = {}

        for symbol in symbols:
            data = self.get_live_data(symbol, timeframe, lookback_bars)
            if data is not None and not data.empty:
                results[symbol] = data

        return results

    def invalidate_cache(self, symbol: Optional[str] = None, timeframe: Optional[str] = None):
        """Invalidate cache for specific symbol/timeframe or entire cache"""
        if symbol is None and timeframe is None:
            self.cache.clear()
            trading_logger.info("Entire cache cleared")
        elif symbol and timeframe:
            # Invalidate specific entries
            for lookback in [50, 100, 200, 500]:
                key = f"{symbol}_{timeframe}_{lookback}"
                self.cache.invalidate(key)
            trading_logger.info(f"Cache invalidated for {symbol} {timeframe}")
        elif symbol:
            # Invalidate all entries for symbol
            with self.cache.lock:
                keys_to_remove = [k for k in self.cache.cache.keys() if k.startswith(f"{symbol}_")]
                for key in keys_to_remove:
                    del self.cache.cache[key]
            trading_logger.info(f"Cache invalidated for {symbol}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status and statistics"""
        cache_stats = self.cache.get_stats()

        return {
            'name': self.name,
            'description': self.description,
            'cache': cache_stats,
            'api_calls': self.api_calls_count,
            'total_data_fetched_mb': round(self.total_data_fetched_mb, 2),
            'data_sources': {
                'alpaca_enabled': self.use_alpaca,
                'yfinance_enabled': self.use_yfinance
            },
            'rate_limiting': {
                'min_interval_seconds': self.min_api_interval,
                'tracked_symbols': len(self.last_api_call)
            }
        }

    def prefetch_symbols(self, symbols: List[str], timeframe: str = '1D',
                        lookback_bars: int = 100):
        """
        Prefetch data for multiple symbols to warm up cache
        Useful before market open
        """
        trading_logger.info(f"Prefetching data for {len(symbols)} symbols...")

        for i, symbol in enumerate(symbols, 1):
            try:
                self.get_live_data(symbol, timeframe, lookback_bars, force_refresh=True)

                if i % 10 == 0:
                    trading_logger.info(f"Prefetched {i}/{len(symbols)} symbols")
            except Exception as e:
                trading_logger.warning(f"Failed to prefetch {symbol}: {e}")

        trading_logger.info(f"Prefetch completed: {len(symbols)} symbols")


# Global instance
live_data_manager = LiveDataManager()
