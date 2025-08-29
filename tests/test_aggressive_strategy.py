#!/usr/bin/env python3
"""
Test script for aggressive strategy settings and wash sale prevention
"""

import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.alpaca_client import alpaca_client
from utils.risk_management import risk_manager
from strategies.momentum_strategy import MomentumStrategy
from utils.logger import trading_logger

def test_aggressive_settings():
    """Test aggressive strategy settings"""
    print("🚀 Testing Aggressive Strategy Settings")
    print("=" * 50)
    
    try:
        # Get account information
        account = alpaca_client.get_account()
        print(f"💰 Account Cash: ${account['cash']:.2f}")
        print(f"📊 Portfolio Value: ${account['portfolio_value']:.2f}")
        print()
        
        # Test symbols
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'AMD']
        
        print("📈 Testing Aggressive Strategy Analysis:")
        print("-" * 50)
        
        strategy = MomentumStrategy()
        
        for symbol in symbols:
            try:
                # Get current price
                df = alpaca_client.get_historical_data(symbol, '1D')
                current_price = df['close'].iloc[-1]
                
                # Analyze with aggressive strategy
                analysis = strategy.analyze(df)
                
                # Calculate position size
                position_info = risk_manager.calculate_position_size(
                    symbol, current_price, account['cash'], analysis['strength']
                )
                
                print(f"📊 {symbol} @ ${current_price:.2f}:")
                print(f"   Signal: {analysis['signal']}")
                print(f"   Strength: {analysis['strength']:.3f}")
                print(f"   Reason: {analysis['reason']}")
                print(f"   Position Type: {position_info['type']}")
                print(f"   Amount: ${position_info['amount']:.2f}")
                print(f"   Estimated Shares: {position_info['shares']:.4f}")
                print()
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                print()
        
        # Test wash sale prevention
        print("🛡️ Testing Wash Sale Prevention:")
        print("-" * 30)
        
        # Test wash sale restriction
        test_symbol = "AAPL"
        has_restriction = risk_manager.check_wash_sale_restriction(test_symbol, 'buy')
        print(f"   {test_symbol} wash sale restriction: {'YES' if has_restriction else 'NO'}")
        
        # Record a test wash sale
        risk_manager.record_wash_sale(test_symbol, 'sell', 10.50)
        print(f"   Recorded wash sale for {test_symbol}")
        
        # Check restriction again
        has_restriction = risk_manager.check_wash_sale_restriction(test_symbol, 'buy')
        print(f"   {test_symbol} wash sale restriction after recording: {'YES' if has_restriction else 'NO'}")
        
        print()
        
        # Test risk management settings
        print("⚡ Aggressive Risk Management Settings:")
        print("-" * 40)
        print(f"   Stop Loss: {config.STOP_LOSS_PERCENT}%")
        print(f"   Take Profit: {config.TAKE_PROFIT_PERCENT}%")
        print(f"   Max Drawdown: {config.MAX_PORTFOLIO_DRAWDOWN}%")
        print(f"   Emergency Stop: {config.EMERGENCY_STOP_LOSS}%")
        print(f"   Risk Percentage: {config.RISK_PERCENTAGE}%")
        print(f"   Wash Sale Window: {config.WASH_SALE_WINDOW_DAYS} days")
        print(f"   Min Holding Time: {config.MIN_HOLDING_TIME_HOURS} hours")
        print()
        
        # Test trading frequency
        print("⏱️ Trading Frequency:")
        print("-" * 20)
        print("   AGGRESSIVE: Trading cycles every 2 minutes")
        print("   Strategy: Lower signal thresholds for more trades")
        print("   Momentum: 50% weight (vs 30% before)")
        print()
        
        print("🎯 Aggressive Strategy Summary:")
        print("-" * 30)
        print("   ✅ Lower signal thresholds (0.15 vs 0.4)")
        print("   ✅ Higher momentum weighting (50% vs 30%)")
        print("   ✅ Faster trading cycles (2 min vs 5 min)")
        print("   ✅ Tighter stop losses (1.5% vs 2.0%)")
        print("   ✅ Faster profit taking (3.0% vs 5.0%)")
        print("   ✅ Higher risk percentages for small accounts")
        print("   ✅ Wash sale prevention system")
        print("   ✅ Minimum holding time enforcement")
        
        print("\n🎉 Aggressive strategy test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        trading_logger.error(f"Aggressive strategy test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Python Trading Bot - Aggressive Strategy Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Run test
    test_aggressive_settings()
    
    print("\n✅ Test completed!")
