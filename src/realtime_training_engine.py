#!/usr/bin/env python3
"""
🔄 Real-Time Training Engine
Continuously trains AI models on live market data alongside trading
"""

import pandas as pd
import numpy as np
import threading
import time
import queue
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

from src.hybrid_ai_engine import HybridAIEngine
from src.sp500_manager import SP500Manager
from utils.logger import trading_logger
from utils.live_data_manager import live_data_manager
from config import config

class RealTimeTrainingEngine:
    """Real-time training engine that works alongside trading"""
    
    def __init__(self, trading_bot=None):
        self.trading_bot = trading_bot
        self.ai_engine = HybridAIEngine()
        self.sp500_manager = SP500Manager()
        
        # Real-time training configuration
        self.training_interval_minutes = 15  # Train every 15 minutes
        self.data_buffer_size = 1000  # Keep last 1000 data points
        self.min_new_data_points = 10  # Minimum new data to trigger training
        self.max_concurrent_training = 5  # Max stocks training simultaneously
        
        # Data management
        self.live_data_buffer = {}  # Buffer for live data
        self.training_queue = queue.Queue()  # Queue for training tasks
        self.training_status = {}  # Track training status per stock
        
        # Threading
        self.training_thread = None
        self.data_collection_thread = None
        self.is_running = False
        
        # Performance tracking
        self.training_stats = {
            'total_trainings': 0,
            'successful_trainings': 0,
            'failed_trainings': 0,
            'last_training_time': None,
            'stocks_trained_today': set(),
            'training_times': []
        }
        
        trading_logger.info("Real-time training engine initialized")
    
    def start_realtime_training(self):
        """Start real-time training alongside trading"""
        if self.is_running:
            trading_logger.warning("Real-time training already running")
            return
        
        self.is_running = True
        
        # Start training thread
        self.training_thread = threading.Thread(target=self._training_worker, daemon=True)
        self.training_thread.start()
        
        # Start data collection thread
        self.data_collection_thread = threading.Thread(target=self._data_collection_worker, daemon=True)
        self.data_collection_thread.start()
        
        trading_logger.info("Real-time training started", 
                           training_interval=self.training_interval_minutes,
                           max_concurrent=self.max_concurrent_training)
    
    def stop_realtime_training(self):
        """Stop real-time training"""
        self.is_running = False
        
        if self.training_thread:
            self.training_thread.join(timeout=5)
        
        if self.data_collection_thread:
            self.data_collection_thread.join(timeout=5)
        
        trading_logger.info("Real-time training stopped")
    
    def _training_worker(self):
        """Main training worker thread"""
        trading_logger.info("Training worker thread started")
        
        while self.is_running:
            try:
                # Check for training tasks
                if not self.training_queue.empty():
                    self._process_training_queue()
                
                # Check for scheduled training
                self._check_scheduled_training()
                
                # Sleep before next check
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                trading_logger.error(f"Training worker error: {e}")
                time.sleep(60)
    
    def _data_collection_worker(self):
        """Data collection worker thread"""
        trading_logger.info("Data collection worker thread started")
        
        while self.is_running:
            try:
                # Collect live data for active stocks
                self._collect_live_data()
                
                # Sleep before next collection
                time.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                trading_logger.error(f"Data collection worker error: {e}")
                time.sleep(300)
    
    def _collect_live_data(self):
        """Collect live market data for training"""
        try:
            # Get active trading symbols
            if self.trading_bot and hasattr(self.trading_bot, 'active_symbols'):
                symbols = self.trading_bot.active_symbols
            else:
                # Fallback to top S&P 500 performers
                symbols = self.sp500_manager.get_top_performers(50)
            
            for symbol in symbols:
                try:
                    # Get latest data point
                    latest_data = self._fetch_latest_data(symbol)
                    if latest_data is not None:
                        self._add_to_buffer(symbol, latest_data)
                        
                except Exception as e:
                    trading_logger.warning(f"Failed to collect live data for {symbol}: {e}")
            
        except Exception as e:
            trading_logger.error(f"Live data collection failed: {e}")
    
    def _fetch_latest_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch latest data point for a symbol using live data manager"""
        try:
            # Use live data manager for on-demand fetching (with caching)
            if config.USE_LIVE_DATA:
                df = live_data_manager.get_live_data(symbol, timeframe='1M', lookback_bars=1)

                if not df.empty:
                    latest = df.iloc[-1]
                    return {
                        'symbol': symbol,
                        'timestamp': datetime.now(),
                        'open': latest['open'],
                        'high': latest['high'],
                        'low': latest['low'],
                        'close': latest['close'],
                        'volume': latest['volume']
                    }
            else:
                # Fallback to old method
                import yfinance as yf

                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1m")

                if not data.empty:
                    latest = data.iloc[-1]
                    return {
                        'symbol': symbol,
                        'timestamp': datetime.now(),
                        'open': latest['Open'],
                        'high': latest['High'],
                        'low': latest['Low'],
                        'close': latest['Close'],
                        'volume': latest['Volume']
                    }

            return None

        except Exception as e:
            trading_logger.warning(f"Failed to fetch latest data for {symbol}: {e}")
            return None
    
    def _add_to_buffer(self, symbol: str, data: Dict[str, Any]):
        """Add data to live buffer"""
        if symbol not in self.live_data_buffer:
            self.live_data_buffer[symbol] = []
        
        self.live_data_buffer[symbol].append(data)
        
        # Keep only recent data
        if len(self.live_data_buffer[symbol]) > self.data_buffer_size:
            self.live_data_buffer[symbol] = self.live_data_buffer[symbol][-self.data_buffer_size:]
        
        # Check if we have enough new data for training
        if len(self.live_data_buffer[symbol]) >= self.min_new_data_points:
            self._queue_training_task(symbol)
    
    def _queue_training_task(self, symbol: str):
        """Queue a training task for a symbol"""
        if symbol not in self.training_status or not self.training_status[symbol].get('training', False):
            self.training_queue.put({
                'symbol': symbol,
                'type': 'incremental',
                'timestamp': datetime.now()
            })
    
    def _process_training_queue(self):
        """Process training queue"""
        try:
            # Process up to max concurrent training
            processed = 0
            while not self.training_queue.empty() and processed < self.max_concurrent_training:
                try:
                    task = self.training_queue.get_nowait()
                    self._train_symbol_async(task)
                    processed += 1
                except queue.Empty:
                    break
                except Exception as e:
                    trading_logger.error(f"Failed to process training task: {e}")
            
        except Exception as e:
            trading_logger.error(f"Training queue processing failed: {e}")
    
    def _train_symbol_async(self, task: Dict[str, Any]):
        """Train a symbol asynchronously"""
        symbol = task['symbol']
        
        # Mark as training
        self.training_status[symbol] = {
            'training': True,
            'start_time': datetime.now(),
            'type': task['type']
        }
        
        # Start training in separate thread
        training_thread = threading.Thread(
            target=self._train_symbol_worker,
            args=(symbol, task),
            daemon=True
        )
        training_thread.start()
    
    def _train_symbol_worker(self, symbol: str, task: Dict[str, Any]):
        """Worker function for training a symbol"""
        try:
            start_time = time.time()
            
            # Prepare training data
            training_data = self._prepare_training_data(symbol, task['type'])
            
            if training_data is not None and len(training_data) > 50:
                # Train the model
                results = self.ai_engine.train_models(symbol, training_data)
                
                if results:
                    # Update training stats
                    training_time = time.time() - start_time
                    self.training_stats['total_trainings'] += 1
                    self.training_stats['successful_trainings'] += 1
                    self.training_stats['last_training_time'] = datetime.now()
                    self.training_stats['stocks_trained_today'].add(symbol)
                    self.training_stats['training_times'].append(training_time)
                    
                    # Keep only last 100 training times
                    if len(self.training_stats['training_times']) > 100:
                        self.training_stats['training_times'] = self.training_stats['training_times'][-100:]
                    
                    trading_logger.info(f"Real-time training completed for {symbol}", 
                                       training_time=training_time,
                                       models_trained=len(results),
                                       type=task['type'])
                else:
                    self.training_stats['failed_trainings'] += 1
                    trading_logger.warning(f"Real-time training failed for {symbol}")
            else:
                trading_logger.warning(f"Insufficient data for real-time training: {symbol}")
            
        except Exception as e:
            self.training_stats['failed_trainings'] += 1
            trading_logger.error(f"Real-time training error for {symbol}: {e}")
        
        finally:
            # Mark training as complete
            if symbol in self.training_status:
                self.training_status[symbol]['training'] = False
                self.training_status[symbol]['end_time'] = datetime.now()
    
    def _prepare_training_data(self, symbol: str, training_type: str) -> Optional[pd.DataFrame]:
        """Prepare training data for a symbol"""
        try:
            if training_type == 'incremental':
                # Use live buffer data
                if symbol in self.live_data_buffer:
                    buffer_data = self.live_data_buffer[symbol]
                    df = pd.DataFrame(buffer_data)
                    
                    # Convert to proper format
                    df['date'] = pd.to_datetime(df['timestamp'])
                    df = df.set_index('date')
                    
                    return df
            
            elif training_type == 'full':
                # Use historical data + live buffer
                historical_data = self._load_historical_data(symbol)
                live_data = self.live_data_buffer.get(symbol, [])
                
                if historical_data is not None and live_data:
                    # Combine historical and live data
                    live_df = pd.DataFrame(live_data)
                    live_df['date'] = pd.to_datetime(live_df['timestamp'])
                    live_df = live_df.set_index('date')
                    
                    # Combine dataframes
                    combined_df = pd.concat([historical_data, live_df])
                    combined_df = combined_df.drop_duplicates().sort_index()
                    
                    return combined_df
                elif historical_data is not None:
                    return historical_data
            
            return None
            
        except Exception as e:
            trading_logger.error(f"Failed to prepare training data for {symbol}: {e}")
            return None
    
    def _load_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load historical data for a symbol (live or cached)"""
        try:
            # Try live data manager first if enabled
            if config.USE_LIVE_DATA:
                df = live_data_manager.get_live_data(
                    symbol,
                    timeframe='1D',
                    lookback_bars=config.SP500_MIN_TRAINING_DATA_DAYS
                )
                if not df.empty:
                    return df

            # Fallback to disk-based storage if it exists
            filename = f"data/sp500/historical/{symbol}_1d_data.csv"
            if os.path.exists(filename):
                data = pd.read_csv(filename)

                if 'date' in data.columns:
                    data['date'] = pd.to_datetime(data['date'])
                    data = data.set_index('date')
                elif 'datetime' in data.columns:
                    data['datetime'] = pd.to_datetime(data['datetime'])
                    data = data.set_index('datetime')

                return data

            return None

        except Exception as e:
            trading_logger.error(f"Failed to load historical data for {symbol}: {e}")
            return None
    
    def _check_scheduled_training(self):
        """Check for scheduled training tasks"""
        try:
            current_time = datetime.now()
            
            # Check if it's time for scheduled training
            if (self.training_stats['last_training_time'] is None or 
                (current_time - self.training_stats['last_training_time']).total_seconds() > 
                self.training_interval_minutes * 60):
                
                # Queue training for top performers
                top_performers = self.sp500_manager.get_top_performers(20)
                
                for symbol in top_performers:
                    if symbol not in self.training_status or not self.training_status[symbol].get('training', False):
                        self.training_queue.put({
                            'symbol': symbol,
                            'type': 'full',
                            'timestamp': current_time
                        })
                
                trading_logger.info(f"Queued scheduled training for {len(top_performers)} top performers")
            
        except Exception as e:
            trading_logger.error(f"Scheduled training check failed: {e}")
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get real-time training status"""
        try:
            # Calculate average training time
            avg_training_time = 0
            if self.training_stats['training_times']:
                avg_training_time = np.mean(self.training_stats['training_times'])
            
            # Count currently training stocks
            currently_training = sum(1 for status in self.training_status.values() 
                                   if status.get('training', False))
            
            return {
                'engine_name': 'Real-Time Training Engine',
                'is_running': self.is_running,
                'training_interval_minutes': self.training_interval_minutes,
                'max_concurrent_training': self.max_concurrent_training,
                'currently_training': currently_training,
                'queue_size': self.training_queue.qsize(),
                'buffer_size': sum(len(buffer) for buffer in self.live_data_buffer.values()),
                'training_stats': {
                    'total_trainings': self.training_stats['total_trainings'],
                    'successful_trainings': self.training_stats['successful_trainings'],
                    'failed_trainings': self.training_stats['failed_trainings'],
                    'success_rate': (self.training_stats['successful_trainings'] / 
                                   max(1, self.training_stats['total_trainings'])) * 100,
                    'avg_training_time': avg_training_time,
                    'stocks_trained_today': len(self.training_stats['stocks_trained_today']),
                    'last_training_time': self.training_stats['last_training_time']
                },
                'ai_engine_status': self.ai_engine.get_performance_summary(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            trading_logger.error(f"Failed to get training status: {e}")
            return {}
    
    def force_training_update(self, symbol: str):
        """Force immediate training update for a symbol"""
        try:
            self.training_queue.put({
                'symbol': symbol,
                'type': 'full',
                'timestamp': datetime.now()
            })
            
            trading_logger.info(f"Forced training update queued for {symbol}")
            
        except Exception as e:
            trading_logger.error(f"Failed to queue forced training for {symbol}: {e}")
    
    def get_live_predictions(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get live predictions for a symbol using latest model"""
        try:
            if symbol in self.live_data_buffer and self.live_data_buffer[symbol]:
                # Get latest data
                latest_data = self.live_data_buffer[symbol][-1]
                
                # Create DataFrame for prediction
                df = pd.DataFrame([latest_data])
                df['date'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('date')
                
                # Make prediction
                prediction = self.ai_engine.predict(symbol, df)
                
                return prediction
            
            return None
            
        except Exception as e:
            trading_logger.error(f"Failed to get live prediction for {symbol}: {e}")
            return None
