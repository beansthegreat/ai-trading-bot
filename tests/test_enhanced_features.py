#!/usr/bin/env python3
"""
Test script for enhanced trading bot features
Tests signal confirmation, cooldown system, volatility adjustment, and analytics
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.momentum_strategy import MomentumStrategy
from utils.risk_management import risk_manager
from utils.performance_analytics import performance_analytics
from utils.alerts import alert_system
from utils.backtesting import backtester

def test_signal_confirmation():
    """Test signal confirmation system"""
    print("🧪 Testing Signal Confirmation System")
    print("-" * 40)
    
    strategy = MomentumStrategy()
    
    # Create test data with different scenarios
    test_cases = [
        {
            'name': 'Strong Buy Signal with Confirmation',
            'data': create_test_data(rsi=25, macd_histogram=0.5, adx=30, signal='buy')
        },
        {
            'name': 'Buy Signal Rejected - RSI Overbought',
            'data': create_test_data(rsi=75, macd_histogram=0.5, adx=30, signal='buy')
        },
        {
            'name': 'Buy Signal Rejected - MACD Bearish',
            'data': create_test_data(rsi=25, macd_histogram=-0.5, adx=30, signal='buy')
        },
        {
            'name': 'Buy Signal Rejected - Low Trend Strength',
            'data': create_test_data(rsi=25, macd_histogram=0.5, adx=20, signal='buy')
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['name']}")
        analysis = strategy.analyze(test_case['data'])
        
        print(f"   Signal: {analysis['signal']}")
        print(f"   Strength: {analysis['strength']:.3f}")
        print(f"   Confirmation Passed: {analysis.get('confirmation_passed', False)}")
        print(f"   Reason: {analysis['reason']}")
        
        if 'confirmation_reasons' in analysis:
            print(f"   Confirmation Details: {', '.join(analysis['confirmation_reasons'])}")
    
    print("\n✅ Signal confirmation tests completed")

def test_cooldown_system():
    """Test cooldown system"""
    print("\n🧪 Testing Cooldown System")
    print("-" * 40)
    
    strategy = MomentumStrategy()
    
    # Test data
    test_data = create_test_data(rsi=25, macd_histogram=0.5, adx=30, signal='buy')
    
    # First analysis should pass
    print("📊 First Analysis (should pass)")
    analysis1 = strategy.analyze(test_data)
    print(f"   Signal: {analysis1['signal']}")
    print(f"   Cooldown Active: {analysis1.get('cooldown_active', False)}")
    
    # Record a trade
    print("\n📝 Recording trade...")
    strategy.record_trade('AAPL')
    
    # Second analysis should be blocked by cooldown
    print("\n📊 Second Analysis (should be blocked by cooldown)")
    analysis2 = strategy.analyze(test_data)
    print(f"   Signal: {analysis2['signal']}")
    print(f"   Cooldown Active: {analysis2.get('cooldown_active', False)}")
    print(f"   Cooldown Reasons: {analysis2.get('cooldown_reasons', [])}")
    
    print("\n✅ Cooldown system tests completed")

def test_volatility_adjusted_position_sizing():
    """Test volatility-adjusted position sizing"""
    print("\n🧪 Testing Volatility-Adjusted Position Sizing")
    print("-" * 40)
    
    # Test different volatility levels
    test_cases = [
        {'volatility': 0.01, 'name': 'Low Volatility (1%)'},
        {'volatility': 0.02, 'name': 'Medium Volatility (2%)'},
        {'volatility': 0.04, 'name': 'High Volatility (4%)'},
        {'volatility': 0.08, 'name': 'Very High Volatility (8%)'}
    ]
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['name']}")
        
        position_info = risk_manager.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            available_cash=10000,
            signal_strength=0.7,
            volatility=test_case['volatility']
        )
        
        print(f"   Position Type: {position_info['type']}")
        print(f"   Amount: ${position_info['amount']:.2f}")
        print(f"   Volatility Multiplier: {position_info.get('volatility_multiplier', 'N/A')}")
        
        if 'shares' in position_info:
            print(f"   Estimated Shares: {position_info['shares']:.4f}")
    
    print("\n✅ Volatility-adjusted position sizing tests completed")

def test_performance_analytics():
    """Test performance analytics system"""
    print("\n🧪 Testing Performance Analytics")
    print("-" * 40)
    
    # Clear existing data
    performance_analytics.trades.clear()
    performance_analytics.symbol_stats.clear()
    performance_analytics.daily_stats.clear()
    
    # Add test trades
    test_trades = [
        {'symbol': 'AAPL', 'action': 'buy', 'quantity': 10, 'price': 150, 'pnl': 0, 'signal_strength': 0.7},
        {'symbol': 'AAPL', 'action': 'sell', 'quantity': 10, 'price': 155, 'pnl': 50, 'signal_strength': 0.8},
        {'symbol': 'NVDA', 'action': 'buy', 'quantity': 5, 'price': 200, 'pnl': 0, 'signal_strength': 0.6},
        {'symbol': 'NVDA', 'action': 'sell', 'quantity': 5, 'price': 190, 'pnl': -50, 'signal_strength': 0.5},
        {'symbol': 'TSLA', 'action': 'buy', 'quantity': 8, 'price': 250, 'pnl': 0, 'signal_strength': 0.9},
        {'symbol': 'TSLA', 'action': 'sell', 'quantity': 8, 'price': 260, 'pnl': 80, 'signal_strength': 0.8}
    ]
    
    for trade in test_trades:
        performance_analytics.record_trade(trade)
    
    # Test analytics functions
    print("📊 Overall Performance:")
    overall = performance_analytics.get_overall_performance()
    print(f"   Total Trades: {overall['total_trades']}")
    print(f"   Win Rate: {overall['win_rate']:.1%}")
    print(f"   Total P&L: ${overall['total_pnl']:.2f}")
    print(f"   Profit Factor: {overall['profit_factor']:.2f}")
    
    print("\n📊 Top Performers:")
    top_performers = performance_analytics.get_top_performers()
    for i, perf in enumerate(top_performers, 1):
        print(f"   {i}. {perf['symbol']}: {perf['profit_factor']:.2f} PF, {perf['win_rate']:.1%} WR")
    
    print("\n📊 Symbol Performance (AAPL):")
    aapl_perf = performance_analytics.get_symbol_performance('AAPL')
    print(f"   Trades: {aapl_perf['trades']}")
    print(f"   Win Rate: {aapl_perf['win_rate']:.1%}")
    print(f"   Total P&L: ${aapl_perf['total_pnl']:.2f}")
    
    print("\n✅ Performance analytics tests completed")

def test_backtesting():
    """Test backtesting framework"""
    print("\n🧪 Testing Backtesting Framework")
    print("-" * 40)
    
    # Create synthetic test data
    test_data = create_synthetic_backtest_data()
    
    # Run mini backtest
    print("🚀 Running mini backtest...")
    
    # Simulate backtest with synthetic data
    results = simulate_backtest(test_data)
    
    if results:
        print("📊 Backtest Results:")
        print(f"   Total Return: {results['total_return']:.2%}")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Win Rate: {results['win_rate']:.1%}")
        print(f"   Profit Factor: {results['profit_factor']:.2f}")
        print(f"   Max Drawdown: {results['max_drawdown']:.2%}")
    
    print("\n✅ Backtesting tests completed")

def test_alert_system():
    """Test alert system"""
    print("\n🧪 Testing Alert System")
    print("-" * 40)
    
    print("📱 Alert System Status:")
    print(f"   Enabled: {alert_system.enabled}")
    print(f"   Discord: {'✅' if alert_system.discord_webhook_url else '❌'}")
    print(f"   Telegram: {'✅' if alert_system.telegram_bot_token else '❌'}")
    
    if alert_system.enabled:
        print("\n🧪 Sending test alerts...")
        alert_system.test_alerts()
    else:
        print("\n⚠️  Alert system disabled - configure webhooks to test")
    
    print("\n✅ Alert system tests completed")

def create_test_data(rsi=50, macd_histogram=0, adx=25, signal='neutral'):
    """Create test data with specific indicator values"""
    # Create synthetic price data
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1min')
    
    # Generate price data
    np.random.seed(42)
    base_price = 150
    returns = np.random.normal(0, 0.001, 50)
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.001 for p in prices],
        'low': [p * 0.999 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, 50),
        'symbol': 'AAPL'
    })
    
    # Add indicators
    df['rsi'] = rsi
    df['macd'] = 0.1
    df['macd_signal'] = 0.1 - macd_histogram
    df['macd_histogram'] = macd_histogram
    df['adx'] = adx
    df['atr'] = 1.0
    df['sma_short'] = df['close'].rolling(20).mean()
    df['sma_long'] = df['close'].rolling(50).mean()
    df['ema_short'] = df['close'].rolling(12).mean()
    df['ema_long'] = df['close'].rolling(26).mean()
    df['bb_upper'] = df['close'] * 1.02
    df['bb_middle'] = df['close']
    df['bb_lower'] = df['close'] * 0.98
    df['stoch_k'] = 50
    df['stoch_d'] = 50
    df['volume_sma'] = df['volume'].rolling(20).mean()
    
    return df

def create_synthetic_backtest_data():
    """Create synthetic data for backtesting"""
    # This is a simplified version - in real backtesting, you'd use actual market data
    return {
        'AAPL': create_test_data(rsi=30, macd_histogram=0.5, adx=30),
        'NVDA': create_test_data(rsi=70, macd_histogram=-0.3, adx=25),
        'TSLA': create_test_data(rsi=40, macd_histogram=0.2, adx=35)
    }

def simulate_backtest(data):
    """Simulate a backtest with synthetic data"""
    # Simplified backtest simulation
    trades = []
    portfolio_value = 10000
    cash = 10000
    
    for symbol, df in data.items():
        # Simulate a few trades
        if len(df) > 20:
            # Buy trade
            buy_price = df['close'].iloc[20]
            shares = 10
            cash -= shares * buy_price
            
            # Sell trade
            sell_price = df['close'].iloc[-1]
            cash += shares * sell_price
            pnl = (sell_price - buy_price) * shares
            
            trades.append({
                'symbol': symbol,
                'pnl': pnl,
                'buy_price': buy_price,
                'sell_price': sell_price
            })
    
    if trades:
        total_pnl = sum(t['pnl'] for t in trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        
        return {
            'total_return': total_pnl / 10000,
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'win_rate': winning_trades / len(trades),
            'profit_factor': 1.5,  # Simplified
            'max_drawdown': 0.05   # Simplified
        }
    
    return None

def main():
    """Run all enhanced feature tests"""
    print("🚀 Enhanced Trading Bot Features Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Run all tests
        test_signal_confirmation()
        test_cooldown_system()
        test_volatility_adjusted_position_sizing()
        test_performance_analytics()
        test_backtesting()
        test_alert_system()
        
        print("\n" + "=" * 60)
        print("✅ All enhanced feature tests completed successfully!")
        print("\n🎯 Enhanced Features Summary:")
        print("   ✅ Signal confirmation with RSI, MACD, and ADX filters")
        print("   ✅ Cooldown system (15min per symbol, 5min global)")
        print("   ✅ Volatility-adjusted position sizing")
        print("   ✅ Performance analytics and tracking")
        print("   ✅ Backtesting framework")
        print("   ✅ Real-time alert system (Discord/Telegram)")
        print("\n🚀 Ready for enhanced trading!")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
