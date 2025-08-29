#!/usr/bin/env python3
"""
Test Sell High Detection
Show how the bot detects sell high opportunities
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

def test_sell_high_conditions():
    """Test the sell high conditions with real data"""
    print("📈 Testing Sell High Detection")
    print("=" * 50)
    
    strategy = MomentumStrategy()
    
    # Test with TSLA (which has RSI 60.7 - approaching overbought)
    symbol = "TSLA"
    print(f"\n📊 Analyzing {symbol} for SELL HIGH opportunities:")
    
    # Get more data for better analysis
    df = yf.download(symbol, period='5d', interval='1m')
    df.columns = df.columns.get_level_values(0)
    df.columns = df.columns.str.lower()
    df['symbol'] = symbol
    
    print(f"Data points: {len(df)}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    
    # Calculate price changes
    current_price = df['close'].iloc[-1]
    price_1h_ago = df['close'].iloc[-2] if len(df) > 1 else current_price
    price_3h_ago = df['close'].iloc[-4] if len(df) > 4 else current_price
    price_6h_ago = df['close'].iloc[-8] if len(df) > 8 else current_price
    
    price_change_1h = (current_price - price_1h_ago) / price_1h_ago
    price_change_3h = (current_price - price_3h_ago) / price_3h_ago
    price_change_6h = (current_price - price_6h_ago) / price_6h_ago
    
    print(f"\n💰 Price Analysis:")
    print(f"Current Price: ${current_price:.2f}")
    print(f"1 Hour Change: {price_change_1h:.2%}")
    print(f"3 Hour Change: {price_change_3h:.2%}")
    print(f"6 Hour Change: {price_change_6h:.2%}")
    
    # Calculate volatility
    recent_prices = df['close'].tail(30)
    price_volatility = recent_prices.pct_change().std()
    print(f"Volatility (30 periods): {price_volatility:.2%}")
    
    # Test strategy analysis
    result = strategy.analyze(df)
    print(f"\n🎯 Strategy Result:")
    print(f"Signal: {result['signal']}")
    print(f"Strength: {result['strength']}")
    print(f"Reason: {result['reason']}")
    
    # Check individual SELL HIGH conditions
    print(f"\n🔍 Sell High Conditions Check:")
    
    conditions = []
    
    # Condition 1: Recent rise (more than 1% in recent periods)
    if price_change_1h > 0.01 or price_change_3h > 0.015:
        conditions.append(f"✅ Recent rise: {price_change_1h:.1%}/{price_change_3h:.1%}")
    else:
        conditions.append(f"❌ Recent rise: {price_change_1h:.1%}/{price_change_3h:.1%} (need > 1%/1.5%)")
    
    # Condition 2: RSI approaching overbought (more lenient)
    rsi = result.get('rsi', 50)
    if rsi > 55:
        conditions.append(f"✅ RSI high: {rsi:.1f}")
    else:
        conditions.append(f"❌ RSI: {rsi:.1f} (need > 55)")
    
    # Condition 3: Positive momentum (more lenient)
    momentum = result.get('strength', 0)
    if momentum > 0:
        conditions.append(f"✅ Positive momentum: {momentum:.3f}")
    else:
        conditions.append(f"❌ Momentum: {momentum:.3f} (need > 0)")
    
    # Condition 4: Moderate volatility
    if price_volatility > 0.01:
        conditions.append(f"✅ Volatility: {price_volatility:.1%}")
    else:
        conditions.append(f"❌ Volatility: {price_volatility:.1%} (need > 1%)")
    
    # Condition 5: Uptrend over longer period
    if price_change_6h > 0.02:
        conditions.append(f"✅ Uptrend: {price_change_6h:.1%}")
    else:
        conditions.append(f"❌ Uptrend: {price_change_6h:.1%} (need > 2%)")
    
    # Condition 6: RSI overbought (traditional)
    if rsi > 65:
        conditions.append(f"✅ RSI overbought: {rsi:.1f}")
    else:
        conditions.append(f"❌ RSI overbought: {rsi:.1f} (need > 65)")
    
    for condition in conditions:
        print(f"  {condition}")
    
    # Count met conditions
    met_conditions = sum(1 for c in conditions if c.startswith("✅"))
    print(f"\n📊 Sell High Conditions Met: {met_conditions}/6")
    
    if met_conditions >= 2:
        print("🎉 SHOULD BE SELL HIGH SIGNAL!")
    elif met_conditions >= 1:
        print("🤔 MODERATE SELL HIGH SIGNAL")
    else:
        print("😴 NOT ENOUGH SELL HIGH CONDITIONS")
    
    print(f"\n💡 Current Market Status:")
    print(f"   TSLA RSI: {rsi:.1f} (approaching overbought)")
    print(f"   Price Change: {price_change_1h:.1%} (1h), {price_change_3h:.1%} (3h)")
    print(f"   Volatility: {price_volatility:.1%}")
    print(f"   Signal: {result['signal'].upper()}")

if __name__ == "__main__":
    test_sell_high_conditions()
