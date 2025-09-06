#!/usr/bin/env python3
"""
📊 Chart Pattern Recognition System
Advanced chart pattern detection for historical training
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from utils.logger import trading_logger

class ChartPatternRecognizer:
    """Advanced chart pattern recognition system"""
    
    def __init__(self):
        self.name = "Chart Pattern Recognizer"
        self.patterns = {
            'head_shoulders': self._detect_head_shoulders,
            'double_top': self._detect_double_top,
            'double_bottom': self._detect_double_bottom,
            'triangle_ascending': self._detect_ascending_triangle,
            'triangle_descending': self._detect_descending_triangle,
            'triangle_symmetrical': self._detect_symmetrical_triangle,
            'flag_bull': self._detect_bull_flag,
            'flag_bear': self._detect_bear_flag,
            'wedge_rising': self._detect_rising_wedge,
            'wedge_falling': self._detect_falling_wedge,
            'cup_handle': self._detect_cup_handle,
            'pennant': self._detect_pennant
        }
    
    def detect_all_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect all chart patterns in the data"""
        result_df = df.copy()
        
        for pattern_name, pattern_func in self.patterns.items():
            try:
                result_df[f'pattern_{pattern_name}'] = pattern_func(df)
            except Exception as e:
                trading_logger.warning(f"Error detecting {pattern_name}: {e}")
                result_df[f'pattern_{pattern_name}'] = 0
        
        return result_df
    
    def _detect_head_shoulders(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Head and Shoulders pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Find three peaks
            left_shoulder = df['high'].iloc[i-window:i].max()
            head = df['high'].iloc[i-window//2:i+window//2].max()
            right_shoulder = df['high'].iloc[i:i+window].max()
            
            # Check pattern conditions
            if (head > left_shoulder and head > right_shoulder and 
                abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_double_top(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Double Top pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            peak1 = df['high'].iloc[i-window:i].max()
            peak2 = df['high'].iloc[i:i+window].max()
            
            if abs(peak1 - peak2) / peak1 < 0.03:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_double_bottom(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Double Bottom pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            trough1 = df['low'].iloc[i-window:i].min()
            trough2 = df['low'].iloc[i:i+window].min()
            
            if abs(trough1 - trough2) / trough1 < 0.03:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_ascending_triangle(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Ascending Triangle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            resistance = df['high'].iloc[i-window:i+window].max()
            support_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            if support_trend > 0 and abs(resistance - df['high'].iloc[i-window:i].mean()) / resistance < 0.02:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_descending_triangle(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Descending Triangle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            support = df['low'].iloc[i-window:i+window].min()
            resistance_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            
            if resistance_trend < 0 and abs(support - df['low'].iloc[i-window:i].mean()) / support < 0.02:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_symmetrical_triangle(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Symmetrical Triangle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            high_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            low_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            if high_trend < 0 and low_trend > 0:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_bull_flag(self, df: pd.DataFrame, window: int = 15) -> pd.Series:
        """Detect Bull Flag pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            initial_move = (df['close'].iloc[i-window] - df['close'].iloc[i-window*2]) / df['close'].iloc[i-window*2]
            consolidation_range = (df['high'].iloc[i-window:i+window].max() - df['low'].iloc[i-window:i+window].min()) / df['close'].iloc[i]
            
            if initial_move > 0.05 and consolidation_range < 0.03:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_bear_flag(self, df: pd.DataFrame, window: int = 15) -> pd.Series:
        """Detect Bear Flag pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            initial_move = (df['close'].iloc[i-window] - df['close'].iloc[i-window*2]) / df['close'].iloc[i-window*2]
            consolidation_range = (df['high'].iloc[i-window:i+window].max() - df['low'].iloc[i-window:i+window].min()) / df['close'].iloc[i]
            
            if initial_move < -0.05 and consolidation_range < 0.03:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_rising_wedge(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Rising Wedge pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            high_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            low_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            if high_trend > 0 and low_trend > 0 and high_trend > low_trend:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_falling_wedge(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detect Falling Wedge pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            high_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            low_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            if high_trend < 0 and low_trend < 0 and high_trend > low_trend:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_cup_handle(self, df: pd.DataFrame, window: int = 30) -> pd.Series:
        """Detect Cup and Handle pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for cup formation (U-shaped)
            cup_start = df['close'].iloc[i-window]
            cup_bottom = df['low'].iloc[i-window//2:i+window//2].min()
            cup_end = df['close'].iloc[i]
            
            # Check for handle formation (small pullback)
            handle_start = cup_end
            handle_bottom = df['low'].iloc[i:i+window//2].min()
            
            cup_depth = (cup_start - cup_bottom) / cup_start
            handle_depth = (handle_start - handle_bottom) / handle_start
            
            if cup_depth > 0.1 and handle_depth < 0.05:
                pattern.iloc[i] = 1
        
        return pattern
    
    def _detect_pennant(self, df: pd.DataFrame, window: int = 15) -> pd.Series:
        """Detect Pennant pattern"""
        pattern = pd.Series(0, index=df.index)
        
        for i in range(window, len(df) - window):
            # Check for strong initial move
            initial_move = abs(df['close'].iloc[i-window] - df['close'].iloc[i-window*2]) / df['close'].iloc[i-window*2]
            
            # Check for converging trend lines
            high_trend = np.polyfit(range(window), df['high'].iloc[i-window:i], 1)[0]
            low_trend = np.polyfit(range(window), df['low'].iloc[i-window:i], 1)[0]
            
            if initial_move > 0.05 and high_trend < 0 and low_trend > 0:
                pattern.iloc[i] = 1
        
        return pattern
