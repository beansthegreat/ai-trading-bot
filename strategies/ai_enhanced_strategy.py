#!/usr/bin/env python3
"""
🤖 AI-Enhanced Trading Strategy
Combines traditional momentum strategy with GPU-accelerated AI predictions
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utils.logger import trading_logger
from strategies.momentum_strategy import MomentumStrategy
from src.ai_engine import AIEngine
from config import config

class AIEnhancedStrategy:
    """AI-Enhanced trading strategy with GPU acceleration"""
    
    def __init__(self):
        self.name = "AI-Enhanced Momentum Strategy"
        self.description = "Combines traditional momentum analysis with GPU-accelerated AI predictions"
        
        # Initialize components
        self.momentum_strategy = MomentumStrategy()
        self.ai_engine = AIEngine()
        
        # AI integration settings
        self.ai_weight = 0.6  # Weight for AI predictions
        self.momentum_weight = 0.4  # Weight for traditional momentum
        self.min_ai_confidence = 0.6  # Minimum AI confidence threshold
        
        # Performance tracking
        self.ai_predictions = {}
        self.combined_signals = {}
        self.last_ai_update = None
        
        # Training settings
        self.auto_train = True
        self.training_frequency_hours = 24  # Retrain every 24 hours
        self.min_training_data = 1000  # Minimum data points for training
        
        trading_logger.info("AI-Enhanced Strategy initialized", 
                           ai_weight=self.ai_weight,
                           momentum_weight=self.momentum_weight,
                           gpu_available=self.ai_engine.use_gpu)
    
    def analyze(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """Analyze market data using both traditional and AI methods"""
        if len(df) < 50:
            return {
                'signal': 'neutral',
                'strength': 0,
                'reason': 'Insufficient data for analysis'
            }
        
        # Get traditional momentum analysis
        momentum_analysis = self.momentum_strategy.analyze(df)
        
        # Get AI predictions
        ai_analysis = self._get_ai_analysis(df, symbol)
        
        # Combine signals intelligently
        combined_signal = self._combine_signals(momentum_analysis, ai_analysis, symbol)
        
        # Store for tracking
        self.ai_predictions[symbol] = ai_analysis
        self.combined_signals[symbol] = combined_signal
        
        # Log analysis results
        trading_logger.strategy(
            signal=combined_signal['signal'],
            strategy_name=self.name,
            symbol=symbol,
            momentum_signal=momentum_analysis['signal'],
            momentum_strength=momentum_analysis['strength'],
            ai_signal=ai_analysis['signal'],
            ai_confidence=ai_analysis['confidence'],
            combined_signal=combined_signal['signal'],
            combined_strength=combined_signal['strength'],
            gpu_used=self.ai_engine.use_gpu
        )
        
        return combined_signal
    
    def _get_ai_analysis(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Get AI predictions for the given data"""
        try:
            # Check if we have trained models
            if not self.ai_engine.models or symbol not in self.ai_engine.scalers:
                # Try to load existing models
                self.ai_engine.load_models(symbol)
                
                # If still no models, train new ones if we have enough data
                if (not self.ai_engine.models and 
                    len(df) >= self.min_training_data and 
                    self.auto_train):
                    self._train_ai_models(df, symbol)
            
            # Make AI prediction
            if symbol in self.ai_engine.scalers:
                ai_prediction = self.ai_engine.predict(df, symbol)
                return ai_prediction
            else:
                return {
                    'signal': 'neutral',
                    'confidence': 0,
                    'reason': 'No trained AI models available'
                }
                
        except Exception as e:
            trading_logger.error(f"AI analysis failed for {symbol}: {e}")
            return {
                'signal': 'neutral',
                'confidence': 0,
                'reason': f'AI analysis error: {str(e)}'
            }
    
    def _combine_signals(self, momentum_analysis: Dict[str, Any], 
                        ai_analysis: Dict[str, Any], 
                        symbol: str) -> Dict[str, Any]:
        """Intelligently combine traditional and AI signals"""
        
        # Extract signal strengths
        momentum_signal = momentum_analysis['signal']
        momentum_strength = momentum_analysis['strength']
        
        ai_signal = ai_analysis['signal']
        ai_confidence = ai_analysis['confidence']
        
        # Convert signals to numeric values for combination
        signal_map = {'sell': -1, 'neutral': 0, 'buy': 1}
        
        momentum_numeric = signal_map.get(momentum_signal, 0)
        ai_numeric = signal_map.get(ai_signal, 0)
        
        # Weight the signals
        weighted_momentum = momentum_numeric * self.momentum_weight * abs(momentum_strength)
        weighted_ai = ai_numeric * self.ai_weight * ai_confidence
        
        # Combine signals
        combined_numeric = weighted_momentum + weighted_ai
        
        # Determine final signal
        if combined_numeric > 0.3:
            final_signal = 'buy'
            final_strength = combined_numeric
        elif combined_numeric < -0.3:
            final_signal = 'sell'
            final_strength = combined_numeric
        else:
            final_signal = 'neutral'
            final_strength = combined_numeric
        
        # Create reasoning
        reasons = []
        
        if momentum_signal != 'neutral':
            reasons.append(f"Momentum: {momentum_signal} (strength: {momentum_strength:.3f})")
        
        if ai_signal != 'neutral' and ai_confidence > self.min_ai_confidence:
            reasons.append(f"AI: {ai_signal} (confidence: {ai_confidence:.3f})")
        
        if not reasons:
            reasons.append("No strong signals detected")
        
        # Check for signal conflicts
        if (momentum_signal != ai_signal and 
            momentum_signal != 'neutral' and 
            ai_signal != 'neutral' and 
            ai_confidence > self.min_ai_confidence):
            reasons.append("⚠️ Signal conflict detected - using weighted combination")
        
        return {
            'signal': final_signal,
            'strength': final_strength,
            'reason': ' | '.join(reasons),
            'momentum_signal': momentum_signal,
            'momentum_strength': momentum_strength,
            'ai_signal': ai_signal,
            'ai_confidence': ai_confidence,
            'combined_weight': combined_numeric,
            'gpu_used': self.ai_engine.use_gpu
        }
    
    def _train_ai_models(self, df: pd.DataFrame, symbol: str):
        """Train AI models for the given symbol"""
        try:
            trading_logger.info(f"Training AI models for {symbol}", 
                               data_size=len(df),
                               gpu_available=self.ai_engine.use_gpu)
            
            # Train the models
            self.ai_engine.train_models(df, symbol)
            
            # Save the models
            self.ai_engine.save_models(symbol)
            
            # Update last training time
            self.last_ai_update = datetime.now()
            
            trading_logger.success(f"AI models trained and saved for {symbol}")
            
        except Exception as e:
            trading_logger.error(f"AI model training failed for {symbol}: {e}")
    
    def should_buy(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> bool:
        """Check if we should buy based on AI-enhanced strategy"""
        analysis = self.analyze(df, symbol)
        return (analysis['signal'] == 'buy' and 
                analysis['strength'] > 0.2 and
                analysis['ai_confidence'] > self.min_ai_confidence)
    
    def should_sell(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> bool:
        """Check if we should sell based on AI-enhanced strategy"""
        analysis = self.analyze(df, symbol)
        return (analysis['signal'] == 'sell' and 
                analysis['strength'] < -0.2 and
                analysis['ai_confidence'] > self.min_ai_confidence)
    
    def get_position_size(self, df: pd.DataFrame, available_cash: float, symbol: str = "UNKNOWN") -> int:
        """Calculate position size based on AI-enhanced signal strength"""
        analysis = self.analyze(df, symbol)
        signal_strength = abs(analysis['strength'])
        ai_confidence = analysis['ai_confidence']
        
        # Base position size on combined signal strength
        if signal_strength > 0.7 and ai_confidence > 0.8:
            size_multiplier = 1.0  # Full position
        elif signal_strength > 0.5 and ai_confidence > 0.7:
            size_multiplier = 0.8  # 80% position
        elif signal_strength > 0.3 and ai_confidence > 0.6:
            size_multiplier = 0.6  # 60% position
        else:
            size_multiplier = 0.4  # 40% position
        
        # Calculate shares based on available cash and max position size
        max_position_value = min(config.MAX_POSITION_SIZE, available_cash)
        position_value = max_position_value * size_multiplier
        
        current_price = df['close'].iloc[-1]
        shares = int(position_value / current_price)
        
        return max(1, shares)  # Minimum 1 share
    
    def record_trade(self, symbol: str):
        """Record a trade to update cooldown timers"""
        self.momentum_strategy.record_trade(symbol)
    
    def update_ai_models(self, df: pd.DataFrame, symbol: str):
        """Update AI models with new data"""
        if len(df) >= self.min_training_data:
            # Check if it's time to retrain
            if (self.last_ai_update is None or 
                datetime.now() - self.last_ai_update > timedelta(hours=self.training_frequency_hours)):
                self._train_ai_models(df, symbol)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of the AI-enhanced strategy"""
        ai_summary = self.ai_engine.get_performance_summary()
        
        return {
            'strategy_name': self.name,
            'ai_weight': self.ai_weight,
            'momentum_weight': self.momentum_weight,
            'min_ai_confidence': self.min_ai_confidence,
            'gpu_available': self.ai_engine.use_gpu,
            'total_ai_models': ai_summary['total_models'],
            'last_ai_training': ai_summary['last_training'],
            'ai_model_performance': ai_summary['model_performance'],
            'recent_predictions': self.ai_predictions,
            'recent_signals': self.combined_signals
        }
    
    def set_ai_weight(self, weight: float):
        """Set the weight for AI predictions (0.0 to 1.0)"""
        if 0.0 <= weight <= 1.0:
            self.ai_weight = weight
            self.momentum_weight = 1.0 - weight
            trading_logger.info(f"AI weight updated", 
                               ai_weight=self.ai_weight,
                               momentum_weight=self.momentum_weight)
        else:
            trading_logger.error(f"Invalid AI weight: {weight}. Must be between 0.0 and 1.0")
    
    def set_min_confidence(self, confidence: float):
        """Set minimum AI confidence threshold"""
        if 0.0 <= confidence <= 1.0:
            self.min_ai_confidence = confidence
            trading_logger.info(f"Minimum AI confidence updated: {confidence}")
        else:
            trading_logger.error(f"Invalid confidence threshold: {confidence}. Must be between 0.0 and 1.0")
