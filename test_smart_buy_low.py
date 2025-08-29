#!/usr/bin/env python3
"""
Test Smart Buy Low Conditions
Analyze actual price data to see why conditions aren't being met
"""

import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from strategies.momentum_strategy import MomentumStrategy

def test_smart_buy_low_conditions():
    """Test the smart buy low conditions with real data"""
    print("🧠 Testing Smart Buy Low Conditions")
    print("=" * 50)
    
    strategy = MomentumStrategy()
    
    # Test with AMD (the stock you mentioned)
    symbol = "AMD"
    print(f"\n📊 Analyzing {symbol}:")
    
    # Get more data for better analysis
    df = yf.download(symbol, period='5d', interval='1m')
    df.columns = df.columns.get_level_values(0)
    df.columns = df.columns.str.lower()
    df['symbol'] = symbol
    
    print(f"Data points: {len(df)}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    
    # Calculate price changes
    current_price = df['close'].iloc[-1]
    price_1d_ago = df['close'].iloc[-2] if len(df) > 1 else current_price
    price_3d_ago = df['close'].iloc[-4] if len(df) > 4 else current_price
    price_5d_ago = df['close'].iloc[-6] if len(df) > 6 else current_price
    
    price_change_1d = (current_price - price_1d_ago) / price_1d_ago
    price_change_3d = (current_price - price_3d_ago) / price_3d_ago
    price_change_5d = (current_price - price_5d_ago) / price_5d_ago
    
    print(f"\n💰 Price Analysis:")
    print(f"Current Price: ${current_price:.2f}")
    print(f"1 Day Change: {price_change_1d:.2%}")
    print(f"3 Day Change: {price_change_3d:.2%}")
    print(f"5 Day Change: {price_change_5d:.2%}")
    
    # Calculate volatility
    recent_prices = df['close'].tail(10)
    price_volatility = recent_prices.pct_change().std()
    print(f"Volatility (10 periods): {price_volatility:.2%}")
    
    # Test strategy analysis
    result = strategy.analyze(df)
    print(f"\n🎯 Strategy Result:")
    print(f"Signal: {result['signal']}")
    print(f"Strength: {result['strength']}")
    print(f"Reason: {result['reason']}")
    
    # Check individual conditions (UPDATED for new smart buy low logic)
    print(f"\n🔍 Smart Buy Low Conditions Check (NEW):")
    
    conditions = []
    
    # Calculate new timeframes
    price_1h_ago = df['close'].iloc[-2] if len(df) > 1 else current_price
    price_3h_ago = df['close'].iloc[-4] if len(df) > 4 else current_price
    price_6h_ago = df['close'].iloc[-8] if len(df) > 8 else current_price
    
    price_change_1h = (current_price - price_1h_ago) / price_1h_ago
    price_change_3h = (current_price - price_3h_ago) / price_3h_ago
    price_change_6h = (current_price - price_6h_ago) / price_6h_ago
    
    # Condition 1: Recent drop (more than 1% in recent periods)
    if price_change_1h < -0.01 or price_change_3h < -0.015:
        conditions.append(f"✅ Recent drop: {price_change_1h:.1%}/{price_change_3h:.1%}")
    else:
        conditions.append(f"❌ Recent drop: {price_change_1h:.1%}/{price_change_3h:.1%} (need < -1%/-1.5%)")
    
    # Condition 2: RSI approaching oversold (more lenient)
    rsi = result.get('rsi', 50)
    if rsi < 45:
        conditions.append(f"✅ RSI low: {rsi:.1f}")
    else:
        conditions.append(f"❌ RSI: {rsi:.1f} (need < 45)")
    
    # Condition 3: Negative momentum (more lenient)
    momentum = result.get('strength', 0)
    if momentum < 0:
        conditions.append(f"✅ Negative momentum: {momentum:.3f}")
    else:
        conditions.append(f"❌ Momentum: {momentum:.3f} (need < 0)")
    
    # Condition 4: Moderate volatility
    if price_volatility > 0.01:
        conditions.append(f"✅ Volatility: {price_volatility:.1%}")
    else:
        conditions.append(f"❌ Volatility: {price_volatility:.1%} (need > 1%)")
    
    # Condition 5: Downtrend over longer period
    if price_change_6h < -0.02:
        conditions.append(f"✅ Downtrend: {price_change_6h:.1%}")
    else:
        conditions.append(f"❌ Downtrend: {price_change_6h:.1%} (need < -2%)")
    
    # Condition 6: RSI oversold (traditional)
    if rsi < 35:
        conditions.append(f"✅ RSI oversold: {rsi:.1f}")
    else:
        conditions.append(f"❌ RSI oversold: {rsi:.1f} (need < 35)")
    
    for condition in conditions:
        print(f"  {condition}")
    
    # Count met conditions
    met_conditions = sum(1 for c in conditions if c.startswith("✅"))
    print(f"\n📊 Conditions Met: {met_conditions}/6")
    
    if met_conditions >= 2:
        print("🎉 SHOULD BE BUY SIGNAL!")
    elif met_conditions >= 1:
        print("🤔 MODERATE BUY SIGNAL")
    else:
        print("😴 NOT ENOUGH CONDITIONS")

if __name__ == "__main__":
    test_smart_buy_low_conditions()
