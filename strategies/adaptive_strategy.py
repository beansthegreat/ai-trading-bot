#!/usr/bin/env python3
"""
Adaptive Strategy Intelligence Engine
Switches between different strategies based on market conditions
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.indicators import TechnicalIndicators
from utils.logger import trading_logger
from config import config

class StrategyIntelligence:
    """Intelligent strategy switching based on market conditions"""
    
    def __init__(self):
        self.name = "Adaptive Strategy Intelligence"
        self.description = "Multi-strategy system that adapts to market conditions"
        
        # Strategy cache and performance tracking
        self.strategies = {}
        self.current_strategy = None
        self.strategy_performance = {}
        self.market_regime = "unknown"
        
        # Market condition thresholds
        self.trend_threshold = 25  # ADX threshold for trend detection
        self.volatility_threshold = 0.02  # Volatility threshold
        self.volume_threshold = 1.5  # Volume spike threshold
        
        # Strategy switching rules
        self.switch_cooldown_minutes = 30  # Don't switch too frequently
        self.last_switch_time = None
        
        # Initialize strategies
        self._initialize_strategies()
        
        trading_logger.info("Strategy Intelligence initialized", 
                           strategy_count=len(self.strategies),
                           switch_cooldown=self.switch_cooldown_minutes)
    
    def _initialize_strategies(self):
        """Initialize all available strategies"""
        from strategies.momentum_strategy import MomentumStrategy
        
        # Strategy 1: Buy Low Sell High (for trending markets)
        self.strategies['buy_low_sell_high'] = {
            'strategy': MomentumStrategy(),
            'description': 'RSI-based buy low, sell high strategy',
            'best_for': ['trending', 'volatile'],
            'conditions': {
                'adx_min': 20,
                'volatility_min': 0.01,
                'rsi_range': [20, 80]
            }
        }
        
        # Strategy 2: Momentum Micro-Movement (for choppy markets)
        self.strategies['momentum_micro'] = {
            'strategy': MomentumStrategy(),
            'description': 'Ultra-sensitive micro-movement detection',
            'best_for': ['choppy', 'sideways'],
            'conditions': {
                'adx_max': 25,
                'volatility_max': 0.03,
                'rsi_range': [30, 70]
            }
        }
        
        # Strategy 3: Breakout Strategy (for high volatility)
        self.strategies['breakout'] = {
            'strategy': MomentumStrategy(),
            'description': 'Breakout detection with volume confirmation',
            'best_for': ['volatile', 'breakout'],
            'conditions': {
                'volatility_min': 0.03,
                'volume_min': 2.0,
                'adx_min': 30
            }
        }
        
        # Strategy 4: Conservative Range Trading (for stable markets)
        self.strategies['conservative'] = {
            'strategy': MomentumStrategy(),
            'description': 'Conservative range-bound trading',
            'best_for': ['stable', 'low_volatility'],
            'conditions': {
                'volatility_max': 0.015,
                'adx_max': 20,
                'rsi_range': [35, 65]
            }
        }
    
    def analyze_market_conditions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze current market conditions to determine optimal strategy"""
        if len(df) < 20:
            return {'regime': 'unknown', 'confidence': 0}
        
        # Calculate indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Extract key metrics
        current_rsi = df_with_indicators['rsi'].iloc[-1]
        current_adx = df_with_indicators.get('adx', [0]).iloc[-1] if 'adx' in df_with_indicators.columns else 0
        current_volume = df_with_indicators['volume'].iloc[-1]
        avg_volume = df_with_indicators['volume'].rolling(20).mean().iloc[-1]
        
        # Calculate volatility
        returns = df_with_indicators['close'].pct_change().dropna()
        volatility = returns.std() if len(returns) > 0 else 0
        
        # Calculate volume ratio
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Determine market regime
        regime = self._classify_market_regime(
            adx=current_adx,
            volatility=volatility,
            volume_ratio=volume_ratio,
            rsi=current_rsi
        )
        
        return {
            'regime': regime,
            'confidence': self._calculate_regime_confidence(regime, current_adx, volatility, volume_ratio),
            'metrics': {
                'adx': current_adx,
                'volatility': volatility,
                'volume_ratio': volume_ratio,
                'rsi': current_rsi
            }
        }
    
    def _classify_market_regime(self, adx: float, volatility: float, volume_ratio: float, rsi: float) -> str:
        """Classify market into different regimes"""
        
        # High volatility breakout
        if volatility > 0.04 and volume_ratio > 2.0 and adx > 30:
            return 'breakout'
        
        # Trending market
        elif adx > 25 and volatility > 0.02:
            return 'trending'
        
        # High volatility choppy
        elif volatility > 0.03 and adx < 25:
            return 'volatile'
        
        # Sideways/choppy market
        elif adx < 20 and volatility < 0.025:
            return 'choppy'
        
        # Stable range-bound
        elif volatility < 0.015 and adx < 15:
            return 'stable'
        
        # Default to trending if unclear
        else:
            return 'trending'
    
    def _calculate_regime_confidence(self, regime: str, adx: float, volatility: float, volume_ratio: float) -> float:
        """Calculate confidence in regime classification (0-1)"""
        confidence = 0.5  # Base confidence
        
        if regime == 'breakout':
            if volatility > 0.05 and volume_ratio > 2.5:
                confidence = 0.9
            elif volatility > 0.04 and volume_ratio > 2.0:
                confidence = 0.8
        elif regime == 'trending':
            if adx > 30:
                confidence = 0.9
            elif adx > 25:
                confidence = 0.8
        elif regime == 'volatile':
            if volatility > 0.04:
                confidence = 0.9
            elif volatility > 0.03:
                confidence = 0.8
        elif regime == 'choppy':
            if adx < 15 and volatility < 0.02:
                confidence = 0.9
            elif adx < 20 and volatility < 0.025:
                confidence = 0.8
        elif regime == 'stable':
            if volatility < 0.01:
                confidence = 0.9
            elif volatility < 0.015:
                confidence = 0.8
        
        return min(confidence, 1.0)
    
    def select_optimal_strategy(self, market_conditions: Dict[str, Any]) -> str:
        """Select the best strategy for current market conditions"""
        regime = market_conditions['regime']
        confidence = market_conditions['confidence']
        
        # Don't switch if confidence is low
        if confidence < 0.6:
            return self.current_strategy or 'buy_low_sell_high'
        
        # Check if we can switch (cooldown)
        if self._is_switch_allowed():
            # Find best strategy for current regime
            best_strategy = self._find_best_strategy_for_regime(regime)
            
            if best_strategy != self.current_strategy:
                self._switch_strategy(best_strategy, regime, confidence)
                return best_strategy
        
        return self.current_strategy or 'buy_low_sell_high'
    
    def _find_best_strategy_for_regime(self, regime: str) -> str:
        """Find the best strategy for a given market regime"""
        strategy_scores = {}
        
        for strategy_name, strategy_info in self.strategies.items():
            score = 0
            
            # PRIORITY: Always prefer buy_low_sell_high for smart buy low detection
            if strategy_name == 'buy_low_sell_high':
                score += 10  # Much higher priority
            
            # Check if strategy is designed for this regime
            elif regime in strategy_info['best_for']:
                score += 3
            
            # Check historical performance
            if strategy_name in self.strategy_performance:
                performance = self.strategy_performance[strategy_name]
                if performance.get('win_rate', 0) > 0.6:
                    score += 2
                if performance.get('profit_factor', 0) > 1.5:
                    score += 1
            
            strategy_scores[strategy_name] = score
        
        # Return strategy with highest score
        if strategy_scores:
            return max(strategy_scores, key=strategy_scores.get)
        
        return 'buy_low_sell_high'  # Default
    
    def _switch_strategy(self, new_strategy: str, regime: str, confidence: float):
        """Switch to a new strategy"""
        old_strategy = self.current_strategy
        self.current_strategy = new_strategy
        self.last_switch_time = datetime.now()
        self.market_regime = regime
        
        trading_logger.info(f"Strategy switched: {old_strategy} → {new_strategy}",
                           regime=regime,
                           confidence=confidence,
                           strategy_description=self.strategies[new_strategy]['description'])
    
    def _is_switch_allowed(self) -> bool:
        """Check if strategy switching is allowed (cooldown)"""
        if not self.last_switch_time:
            return True
        
        time_since_switch = datetime.now() - self.last_switch_time
        return time_since_switch > timedelta(minutes=self.switch_cooldown_minutes)
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market data using adaptive strategy selection"""
        if len(df) < 20:
            return {
                'signal': 'neutral',
                'strength': 0,
                'reason': 'Insufficient data for analysis'
            }
        
        # Analyze market conditions
        market_conditions = self.analyze_market_conditions(df)
        
        # Select optimal strategy
        optimal_strategy_name = self.select_optimal_strategy(market_conditions)
        strategy_info = self.strategies[optimal_strategy_name]
        
        # Get analysis from selected strategy
        strategy_analysis = strategy_info['strategy'].analyze(df)
        
        # Add intelligence metadata
        strategy_analysis.update({
            'strategy_used': optimal_strategy_name,
            'strategy_description': strategy_info['description'],
            'market_regime': market_conditions['regime'],
            'regime_confidence': market_conditions['confidence'],
            'market_metrics': market_conditions['metrics']
        })
        
        # Log strategy intelligence
        trading_logger.strategy(
            strategy_name=f"Adaptive Intelligence ({optimal_strategy_name})",
            signal=strategy_analysis['signal'],
            symbol=df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown',
            strength=strategy_analysis['strength'],
            rsi=market_conditions['metrics']['rsi'],
            macd_histogram=0,  # Will be filled by strategy
            adx=market_conditions['metrics']['adx'],
            confirmation_passed=strategy_analysis.get('confirmation_passed', False),
            cooldown_active=strategy_analysis.get('cooldown_active', False),
            market_regime=market_conditions['regime'],
            strategy_confidence=market_conditions['confidence']
        )
        
        return strategy_analysis
    
    def record_trade(self, symbol: str, strategy_used: str, profit_loss: float = 0):
        """Record trade performance for strategy optimization"""
        if strategy_used not in self.strategy_performance:
            self.strategy_performance[strategy_used] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'profit_factor': 0
            }
        
        perf = self.strategy_performance[strategy_used]
        perf['trades'] += 1
        perf['total_pnl'] += profit_loss
        
        if profit_loss > 0:
            perf['wins'] += 1
        else:
            perf['losses'] += 1
        
        # Update metrics
        if perf['trades'] > 0:
            perf['win_rate'] = perf['wins'] / perf['trades']
        
        if perf['losses'] > 0:
            perf['profit_factor'] = abs(perf['wins'] * 0.01) / abs(perf['losses'] * 0.01)  # Simplified
        
        trading_logger.info(f"Trade recorded for {strategy_used}",
                           symbol=symbol,
                           pnl=profit_loss,
                           win_rate=perf['win_rate'],
                           profit_factor=perf['profit_factor'])
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """Get summary of all strategies and their performance"""
        return {
            'current_strategy': self.current_strategy,
            'market_regime': self.market_regime,
            'available_strategies': list(self.strategies.keys()),
            'strategy_performance': self.strategy_performance,
            'last_switch_time': self.last_switch_time.isoformat() if self.last_switch_time else None
        }
