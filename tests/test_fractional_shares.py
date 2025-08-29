#!/usr/bin/env python3
"""
Test script to verify fractional share trading functionality
"""

import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.alpaca_client import alpaca_client
from utils.risk_management import risk_manager
from utils.logger import trading_logger

def test_fractional_shares():
    """Test fractional share trading functionality"""
    print("🔢 Testing Fractional Share Trading")
    print("=" * 50)
    
    try:
        # Get account information
        account = alpaca_client.get_account()
        print(f"💰 Account Cash: ${account['cash']:.2f}")
        print(f"📊 Portfolio Value: ${account['portfolio_value']:.2f}")
        print()
        
        # Test position size calculation with fractional shares
        print("📈 Testing Position Size Calculation:")
        
        # Test with different stock prices
        test_cases = [
            ("AAPL", 230.24),  # Expensive stock
            ("MSFT", 400.50),  # Very expensive stock
            ("TSLA", 250.00),  # Medium expensive stock
            ("AMZN", 150.00),  # Medium price stock
        ]
        
        for symbol, price in test_cases:
            # Calculate position size with $99.01 cash
            position_size = risk_manager.calculate_position_size(
                symbol, price, 99.01, 0.8  # Strong signal
            )
            
            position_value = position_size * price
            
            print(f"   {symbol} @ ${price:.2f}:")
            print(f"      Shares: {position_size:.4f}")
            print(f"      Value: ${position_value:.2f}")
            print(f"      Percentage of cash: {(position_value/99.01)*100:.1f}%")
            print()
        
        # Test with different signal strengths
        print("🎯 Testing Signal Strength Impact:")
        signal_strengths = [0.9, 0.7, 0.5, 0.3]
        
        for strength in signal_strengths:
            position_size = risk_manager.calculate_position_size(
                "AAPL", 230.24, 99.01, strength
            )
            position_value = position_size * 230.24
            
            print(f"   Signal Strength {strength:.1f}:")
            print(f"      Shares: {position_size:.4f}")
            print(f"      Value: ${position_value:.2f}")
            print()
        
        # Test actual order placement (optional)
        print("🔧 Optional: Test fractional share order...")
        response = input("Do you want to test placing a small fractional AAPL order? (y/N): ")
        
        if response.lower() == 'y':
            # Calculate a small fractional position
            small_position = risk_manager.calculate_position_size(
                "AAPL", 230.24, 99.01, 0.3  # Weak signal for small position
            )
            
            print(f"   Placing order for {small_position:.4f} AAPL shares...")
            print(f"   Estimated cost: ${small_position * 230.24:.2f}")
            
            # Place the order
            order = alpaca_client.place_market_order("AAPL", "buy", small_position)
            
            print(f"   ✅ Order placed successfully!")
            print(f"   Order ID: {order['id']}")
            print(f"   Status: {order['status']}")
            print(f"   Quantity: {order['quantity']}")
            
            # Cancel the order immediately
            print(f"   Cancelling order...")
            alpaca_client.cancel_order(order['id'])
            print(f"   ✅ Order cancelled")
        
        print("🎉 Fractional share test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        trading_logger.error(f"Fractional share test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Python Trading Bot - Fractional Share Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Run test
    test_fractional_shares()
    
    print("\n✅ Test completed!")
