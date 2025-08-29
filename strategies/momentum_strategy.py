import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utils.indicators import TechnicalIndicators
from utils.logger import trading_logger
from config import config

class MomentumStrategy:
    """Enhanced momentum-based trading strategy with signal confirmation and cooldown"""
    
    def __init__(self):
        self.name = "Smart Buy Low Sell High Strategy"
        self.description = "Chart pattern analysis with smart buy low AND sell high detection - looks at overall trends, not just RSI"
        
        # Cooldown tracking
        self.last_trade_time = {}  # Per symbol cooldown
        self.last_global_trade = None  # Global cooldown
        
        # Cooldown settings
        self.symbol_cooldown_minutes = 15  # 15 minutes per symbol
        self.global_cooldown_minutes = 5   # 5 minutes between any trades
        
        # Signal confirmation settings
        self.require_rsi_confirmation = True
        self.require_macd_confirmation = True
        self.require_trend_confirmation = True
        
        # RSI thresholds for confirmation
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        
        # ADX threshold for trend confirmation
        self.adx_trend_threshold = 25
        
        trading_logger.info("Enhanced Momentum Strategy initialized", 
                           cooldown_symbol=self.symbol_cooldown_minutes,
                           cooldown_global=self.global_cooldown_minutes)
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market data and generate trading signals with confirmation filters"""
        if len(df) < 20:  # Reduced from 50 for faster response
            return {
                'signal': 'neutral',
                'strength': 0,
                'reason': 'Insufficient data for analysis'
            }
        
        # Calculate all indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Get signal strength
        signal_data = TechnicalIndicators.get_signal_strength(df_with_indicators)
        
        # Additional momentum analysis with micro-movement detection
        momentum_score = self._calculate_momentum_score(df_with_indicators)
        
        # Adaptive thresholds based on stock volatility
        volatility = self._calculate_volatility(df_with_indicators)
        adaptive_thresholds = self._get_adaptive_thresholds(volatility)
        
        # Combine signals with adaptive thresholds
        initial_signal = self._combine_signals_adaptive(signal_data, momentum_score, adaptive_thresholds, df_with_indicators)
        
        # Apply signal confirmation filters
        confirmed_signal = self._apply_signal_confirmation(initial_signal, df_with_indicators)
        
        # Check cooldown restrictions
        final_signal = self._check_cooldown_restrictions(confirmed_signal, df)
        
        trading_logger.strategy(
            strategy_name=self.name,
            signal=final_signal['signal'],
            symbol=df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown',
            strength=final_signal['strength'],
            rsi=df_with_indicators['rsi'].iloc[-1],
            macd_histogram=df_with_indicators['macd_histogram'].iloc[-1],
            adx=df_with_indicators.get('adx', [0]).iloc[-1] if 'adx' in df_with_indicators.columns else 0,
            confirmation_passed=final_signal.get('confirmation_passed', False),
            cooldown_active=final_signal.get('cooldown_active', False)
        )
        
        return final_signal
    
    def _apply_signal_confirmation(self, signal: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Apply signal confirmation filters to reduce false signals"""
        if signal['signal'] == 'neutral':
            return signal
        
        confirmation_passed = True
        confirmation_reasons = []
        
        # RSI Confirmation - Updated for Buy Low, Sell High
        if self.require_rsi_confirmation:
            current_rsi = df['rsi'].iloc[-1]
            if signal['signal'] == 'buy' and current_rsi > self.rsi_overbought:
                confirmation_passed = False
                confirmation_reasons.append(f"RSI overbought ({current_rsi:.1f} > {self.rsi_overbought}) - Not a good buy point")
            elif signal['signal'] == 'sell' and current_rsi < self.rsi_oversold:
                confirmation_passed = False
                confirmation_reasons.append(f"RSI oversold ({current_rsi:.1f} < {self.rsi_oversold}) - Not a good sell point")
            elif signal['signal'] == 'buy' and current_rsi < self.rsi_oversold:
                # BUY LOW: RSI oversold is GOOD for buying
                confirmation_reasons.append(f"BUY LOW confirmed: RSI oversold ({current_rsi:.1f} < {self.rsi_oversold}) - Perfect buy point")
            elif signal['signal'] == 'sell' and current_rsi > self.rsi_overbought:
                # SELL HIGH: RSI overbought is GOOD for selling
                confirmation_reasons.append(f"SELL HIGH confirmed: RSI overbought ({current_rsi:.1f} > {self.rsi_overbought}) - Perfect sell point")
            else:
                confirmation_reasons.append(f"RSI confirmed ({current_rsi:.1f})")
        
        # MACD Confirmation
        if self.require_macd_confirmation and confirmation_passed:
            current_macd = df['macd'].iloc[-1]
            current_signal = df['macd_signal'].iloc[-1]
            macd_histogram = df['macd_histogram'].iloc[-1]
            
            if signal['signal'] == 'buy' and macd_histogram < 0:
                confirmation_passed = False
                confirmation_reasons.append(f"MACD bearish (histogram: {macd_histogram:.4f})")
            elif signal['signal'] == 'sell' and macd_histogram > 0:
                confirmation_passed = False
                confirmation_reasons.append(f"MACD bullish (histogram: {macd_histogram:.4f})")
            else:
                confirmation_reasons.append(f"MACD confirmed (histogram: {macd_histogram:.4f})")
        
        # Trend Confirmation (ADX)
        if self.require_trend_confirmation and confirmation_passed and 'adx' in df.columns:
            current_adx = df['adx'].iloc[-1]
            if current_adx < self.adx_trend_threshold:
                confirmation_passed = False
                confirmation_reasons.append(f"Low trend strength (ADX: {current_adx:.1f} < {self.adx_trend_threshold})")
            else:
                confirmation_reasons.append(f"Trend confirmed (ADX: {current_adx:.1f})")
        
        # Update signal based on confirmation
        if not confirmation_passed:
            signal['signal'] = 'neutral'
            signal['reason'] = f"Signal rejected: {'; '.join(confirmation_reasons)}"
            signal['strength'] *= 0.5  # Reduce strength for rejected signals
        
        signal['confirmation_passed'] = confirmation_passed
        signal['confirmation_reasons'] = confirmation_reasons
        
        return signal
    
    def _check_cooldown_restrictions(self, signal: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Check if trading is allowed based on cooldown periods"""
        if signal['signal'] == 'neutral':
            return signal
        
        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown'
        current_time = datetime.now()
        
        cooldown_active = False
        cooldown_reasons = []
        
        # Check symbol-specific cooldown
        if symbol in self.last_trade_time:
            time_since_symbol_trade = current_time - self.last_trade_time[symbol]
            if time_since_symbol_trade < timedelta(minutes=self.symbol_cooldown_minutes):
                cooldown_active = True
                remaining_minutes = self.symbol_cooldown_minutes - time_since_symbol_trade.total_seconds() / 60
                cooldown_reasons.append(f"Symbol cooldown: {remaining_minutes:.1f} minutes remaining")
        
        # Check global cooldown
        if self.last_global_trade:
            time_since_global_trade = current_time - self.last_global_trade
            if time_since_global_trade < timedelta(minutes=self.global_cooldown_minutes):
                cooldown_active = True
                remaining_minutes = self.global_cooldown_minutes - time_since_global_trade.total_seconds() / 60
                cooldown_reasons.append(f"Global cooldown: {remaining_minutes:.1f} minutes remaining")
        
        # Update signal if cooldown is active
        if cooldown_active:
            signal['signal'] = 'neutral'
            signal['reason'] = f"Cooldown active: {'; '.join(cooldown_reasons)}"
            signal['strength'] *= 0.3  # Significantly reduce strength during cooldown
        
        signal['cooldown_active'] = cooldown_active
        signal['cooldown_reasons'] = cooldown_reasons
        
        return signal
    
    def record_trade(self, symbol: str):
        """Record a trade to update cooldown timers"""
        current_time = datetime.now()
        self.last_trade_time[symbol] = current_time
        self.last_global_trade = current_time
        
        trading_logger.info(f"Trade recorded for {symbol}", 
                           symbol_cooldown_until=current_time + timedelta(minutes=self.symbol_cooldown_minutes),
                           global_cooldown_until=current_time + timedelta(minutes=self.global_cooldown_minutes))
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """Calculate momentum score based on price action and RSI conditions - MICRO-MOMENTUM DETECTION"""
        if len(df) < 20:
            return 0
        
        latest = df.iloc[-1]
        
        # MICRO-MOMENTUM: Detect very small price movements
        # 1-minute price change
        price_change_1m = (latest['close'] - df['close'].iloc[-2]) / df['close'].iloc[-2] if len(df) > 1 else 0
        
        # 5-minute price change
        price_change_5m = (latest['close'] - df['close'].iloc[-6]) / df['close'].iloc[-6] if len(df) > 5 else 0
        
        # 10-minute price change
        price_change_10m = (latest['close'] - df['close'].iloc[-11]) / df['close'].iloc[-11] if len(df) > 10 else 0
        
        # MICRO-VOLUME: Detect small volume spikes
        volume_change_1m = (latest['volume'] - df['volume'].iloc[-2]) / df['volume'].iloc[-2] if len(df) > 1 and df['volume'].iloc[-2] > 0 else 0
        volume_change_5m = (latest['volume'] - df['volume'].rolling(5).mean().iloc[-1]) / df['volume'].rolling(5).mean().iloc[-1] if len(df) > 5 else 0
        
        # MICRO-VOLATILITY: Detect small volatility changes
        atr_change = (latest['atr'] - df['atr'].rolling(5).mean().iloc[-1]) / df['atr'].rolling(5).mean().iloc[-1] if latest['atr'] > 0 else 0
        
        # RSI-BASED MOMENTUM ADJUSTMENT: Add bullish bias when oversold, bearish bias when overbought
        rsi_adjustment = 0
        if 'rsi' in df.columns:
            current_rsi = latest['rsi']
            if current_rsi < self.rsi_oversold:  # Oversold - add bullish bias
                rsi_adjustment = 0.01  # +1% bullish bias
            elif current_rsi > self.rsi_overbought:  # Overbought - add bearish bias
                rsi_adjustment = -0.01  # -1% bearish bias
        
        # MICRO-MOMENTUM: Weight recent changes more heavily + RSI adjustment
        micro_momentum = (
            price_change_1m * 0.35 +     # 35% weight to 1-minute change
            price_change_5m * 0.25 +     # 25% weight to 5-minute change
            price_change_10m * 0.15 +    # 15% weight to 10-minute change
            volume_change_1m * 0.05 +    # 5% weight to volume spike
            volume_change_5m * 0.03 +    # 3% weight to volume trend
            atr_change * 0.02 +          # 2% weight to volatility
            rsi_adjustment * 0.15        # 15% weight to RSI adjustment
        )
        
        return micro_momentum
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate stock volatility for adaptive thresholds"""
        if len(df) < 10:
            return 0.02  # Default volatility
        
        # Calculate price volatility over last 10 periods
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() if len(returns) > 0 else 0.02
        
        return volatility
    
    def _get_adaptive_thresholds(self, volatility: float) -> Dict[str, float]:
        """Get adaptive thresholds based on stock volatility"""
        # High volatility stocks (like TSLA) get higher thresholds
        # Low volatility stocks (like MSFT) get lower thresholds
        
        if volatility > 0.03:  # High volatility (TSLA, NVDA)
            return {
                'strong_buy': 0.01,    # 1% movement
                'weak_buy': 0.005,     # 0.5% movement
                'strong_sell': -0.01,  # -1% movement
                'weak_sell': -0.005    # -0.5% movement
            }
        elif volatility > 0.02:  # Medium volatility (AAPL, GOOGL)
            return {
                'strong_buy': 0.005,   # 0.5% movement
                'weak_buy': 0.002,     # 0.2% movement
                'strong_sell': -0.005, # -0.5% movement
                'weak_sell': -0.002    # -0.2% movement
            }
        else:  # Low volatility (MSFT, AMZN)
            return {
                'strong_buy': 0.002,   # 0.2% movement
                'weak_buy': 0.001,     # 0.1% movement
                'strong_sell': -0.002, # -0.2% movement
                'weak_sell': -0.001    # -0.1% movement
            }
    
    def _combine_signals_adaptive(self, signal_data: Dict[str, Any], momentum_score: float, thresholds: Dict[str, float], df_with_indicators: pd.DataFrame) -> Dict[str, Any]:
        """Combine signals with SMART BUY LOW, SELL HIGH strategy - looks at overall chart patterns"""
        technical_strength = signal_data['strength']
        
        # Get key indicators
        current_rsi = df_with_indicators['rsi'].iloc[-1] if 'rsi' in df_with_indicators.columns else 50
        current_price = df_with_indicators['close'].iloc[-1]
        
        # Calculate recent price movement patterns (using more data points for better analysis)
        recent_prices = df_with_indicators['close'].tail(30)  # Last 30 periods for better trend
        price_change_1h = (current_price - recent_prices.iloc[-2]) / recent_prices.iloc[-2] if len(recent_prices) > 1 else 0
        price_change_3h = (current_price - recent_prices.iloc[-4]) / recent_prices.iloc[-4] if len(recent_prices) > 4 else 0
        price_change_6h = (current_price - recent_prices.iloc[-8]) / recent_prices.iloc[-8] if len(recent_prices) > 8 else 0
        
        # Calculate volatility
        price_volatility = recent_prices.pct_change().std()
        
        # SMART BUY LOW DETECTION - More realistic conditions
        buy_low_conditions = []
        
        # Condition 1: Recent drop (more than 1% in recent periods)
        if price_change_1h < -0.01 or price_change_3h < -0.015:
            buy_low_conditions.append(f"Recent drop: {price_change_1h:.1%}/{price_change_3h:.1%}")
        
        # Condition 2: RSI approaching oversold (more lenient)
        if current_rsi < 45:  # More lenient than 50
            buy_low_conditions.append(f"RSI low: {current_rsi:.1f}")
        
        # Condition 3: Negative momentum (more lenient)
        if momentum_score < 0:
            buy_low_conditions.append(f"Negative momentum: {momentum_score:.3f}")
        
        # Condition 4: Moderate volatility
        if price_volatility > 0.01:  # Lower threshold
            buy_low_conditions.append(f"Volatility: {price_volatility:.1%}")
        
        # Condition 5: Downtrend over longer period
        if price_change_6h < -0.02:
            buy_low_conditions.append(f"Downtrend: {price_change_6h:.1%}")
        
        # Condition 6: RSI oversold (traditional)
        if current_rsi < 35:
            buy_low_conditions.append(f"RSI oversold: {current_rsi:.1f}")
        
        # SMART SELL HIGH DETECTION - Mirror of buy low logic
        sell_high_conditions = []
        
        # Condition 1: Recent rise (more than 1% in recent periods)
        if price_change_1h > 0.01 or price_change_3h > 0.015:
            sell_high_conditions.append(f"Recent rise: {price_change_1h:.1%}/{price_change_3h:.1%}")
        
        # Condition 2: RSI approaching overbought (more lenient)
        if current_rsi > 55:  # More lenient than 70
            sell_high_conditions.append(f"RSI high: {current_rsi:.1f}")
        
        # Condition 3: Positive momentum (more lenient)
        if momentum_score > 0:
            sell_high_conditions.append(f"Positive momentum: {momentum_score:.3f}")
        
        # Condition 4: Moderate volatility
        if price_volatility > 0.01:  # Same threshold as buy
            sell_high_conditions.append(f"Volatility: {price_volatility:.1%}")
        
        # Condition 5: Uptrend over longer period
        if price_change_6h > 0.02:
            sell_high_conditions.append(f"Uptrend: {price_change_6h:.1%}")
        
        # Condition 6: RSI overbought (traditional)
        if current_rsi > 65:
            sell_high_conditions.append(f"RSI overbought: {current_rsi:.1f}")
        
        # SMART BUY LOW SIGNAL
        if len(buy_low_conditions) >= 2:
            signal = 'buy'
            reason = f"SMART BUY LOW: {' | '.join(buy_low_conditions)}"
            combined_strength = 0.7  # Strong buy signal
        elif len(buy_low_conditions) >= 1:
            signal = 'buy'
            reason = f"BUY LOW: {' | '.join(buy_low_conditions)}"
            combined_strength = 0.5  # Moderate buy signal
        # SMART SELL HIGH SIGNAL
        elif len(sell_high_conditions) >= 2:
            signal = 'sell'
            reason = f"SMART SELL HIGH: {' | '.join(sell_high_conditions)}"
            combined_strength = -0.7  # Strong sell signal
        elif len(sell_high_conditions) >= 1:
            signal = 'sell'
            reason = f"SELL HIGH: {' | '.join(sell_high_conditions)}"
            combined_strength = -0.5  # Moderate sell signal
        else:
            # Fallback to original logic for other cases
            if current_rsi < self.rsi_oversold:
                signal = 'buy'
                reason = f"RSI oversold: {current_rsi:.1f}"
                combined_strength = 0.6
            elif current_rsi > self.rsi_overbought:
                signal = 'sell'
                reason = f"RSI overbought: {current_rsi:.1f}"
                combined_strength = -0.6
            else:
                signal = 'neutral'
                reason = f"Waiting for better conditions (RSI: {current_rsi:.1f})"
                combined_strength = 0
        
        return {'signal': signal, 'strength': combined_strength, 'reason': reason}
    
    def _combine_signals(self, signal_data: Dict[str, Any], momentum_score: float) -> Dict[str, Any]:
        """Combine technical signals with momentum score - AGGRESSIVE MODE"""
        technical_strength = signal_data['strength']
        
        # AGGRESSIVE: Weight momentum more heavily for faster signals
        combined_strength = (technical_strength * 0.5) + (momentum_score * 0.5)
        
        # MICRO-MOVEMENT: Ultra-sensitive thresholds for small movements
        if combined_strength > 0.02:  # React to 0.02% movements
            signal = 'buy'
            reason = f"MICRO-MOVEMENT: Bullish micro-momentum (strength: {combined_strength:.4f})"
        elif combined_strength < -0.02:  # React to -0.02% movements
            signal = 'sell'
            reason = f"MICRO-MOVEMENT: Bearish micro-momentum (strength: {combined_strength:.4f})"
        elif combined_strength > 0.005:  # React to 0.005% movements
            signal = 'buy'
            reason = f"MICRO-MOVEMENT: Weak bullish micro-momentum (strength: {combined_strength:.4f})"
        elif combined_strength < -0.005:  # React to -0.005% movements
            signal = 'sell'
            reason = f"MICRO-MOVEMENT: Weak bearish micro-momentum (strength: {combined_strength:.4f})"
        else:
            signal = 'neutral'
            reason = f"Neutral micro-momentum (strength: {combined_strength:.4f})"
        
        return {
            'signal': signal,
            'strength': combined_strength,
            'reason': reason,
            'technical_strength': technical_strength,
            'momentum_score': momentum_score,
            'indicators': signal_data
        }
    
    def should_buy(self, df: pd.DataFrame) -> bool:
        """Check if we should buy based on strategy - MICRO-MOVEMENT MODE"""
        analysis = self.analyze(df)
        return analysis['signal'] == 'buy' and analysis['strength'] > 0.001  # React to 0.001% movements
    
    def should_sell(self, df: pd.DataFrame) -> bool:
        """Check if we should sell based on strategy - MICRO-MOVEMENT MODE"""
        analysis = self.analyze(df)
        return analysis['signal'] == 'sell' and analysis['strength'] < -0.001  # React to -0.001% movements
    
    def get_position_size(self, df: pd.DataFrame, available_cash: float) -> int:
        """Calculate position size based on signal strength"""
        analysis = self.analyze(df)
        signal_strength = abs(analysis['strength'])
        
        # Base position size on signal strength
        if signal_strength > 0.7:
            size_multiplier = 1.0  # Full position
        elif signal_strength > 0.5:
            size_multiplier = 0.7  # 70% position
        elif signal_strength > 0.3:
            size_multiplier = 0.5  # 50% position
        else:
            size_multiplier = 0.3  # 30% position
        
        # Calculate shares based on available cash and max position size
        max_position_value = min(config.MAX_POSITION_SIZE, available_cash)
        position_value = max_position_value * size_multiplier
        
        current_price = df['close'].iloc[-1]
        shares = int(position_value / current_price)
        
        return max(1, shares)  # Minimum 1 share
