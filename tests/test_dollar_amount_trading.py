#!/usr/bin/env python3
"""
Test script to verify dollar amount trading functionality
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

def test_dollar_amount_trading():
    """Test dollar amount trading functionality"""
    print("💰 Testing Dollar Amount Trading")
    print("=" * 50)
    
    try:
        # Get account information
        account = alpaca_client.get_account()
        print(f"💰 Account Cash: ${account['cash']:.2f}")
        print(f"📊 Portfolio Value: ${account['portfolio_value']:.2f}")
        print()
        
        # Test position size calculation with dollar amounts
        print("📈 Testing Dollar Amount Position Size Calculation:")
        
        # Test with different stock prices
        test_cases = [
            ("AAPL", 230.24),  # Expensive stock
            ("MSFT", 400.50),  # Very expensive stock
            ("TSLA", 250.00),  # Medium expensive stock
            ("AMZN", 150.00),  # Medium price stock
        ]
        
        for symbol, price in test_cases:
            # Calculate position size with $96.71 cash
            position_info = risk_manager.calculate_position_size(
                symbol, price, 96.71, 0.8  # Strong signal
            )
            
            estimated_shares = position_info['shares']
            
            print(f"   {symbol} @ ${price:.2f}:")
            print(f"      Type: {position_info['type']}")
            print(f"      Amount: ${position_info['amount']:.2f}")
            print(f"      Estimated Shares: {estimated_shares:.4f}")
            print(f"      Percentage of cash: {(position_info['amount']/96.71)*100:.1f}%")
            print()
        
        # Test with different signal strengths
        print("🎯 Testing Signal Strength Impact:")
        signal_strengths = [0.9, 0.7, 0.5, 0.3]
        
        for strength in signal_strengths:
            position_info = risk_manager.calculate_position_size(
                "AAPL", 230.24, 96.71, strength
            )
            estimated_shares = position_info['shares']
            
            print(f"   Signal Strength {strength:.1f}:")
            print(f"      Type: {position_info['type']}")
            print(f"      Amount: ${position_info['amount']:.2f}")
            print(f"      Estimated Shares: {estimated_shares:.4f}")
            print()
        
        # Test actual order placement (optional)
        print("🔧 Optional: Test dollar amount order...")
        response = input("Do you want to test placing a $10 AAPL order? (y/N): ")
        
        if response.lower() == 'y':
            print(f"   Placing order for $10.00 worth of AAPL...")
            print(f"   Estimated shares: {10.00 / 230.24:.4f}")
            
            # Place the order
            order = alpaca_client.place_dollar_amount_order("AAPL", "buy", 10.00)
            
            print(f"   ✅ Order placed successfully!")
            print(f"   Order ID: {order['id']}")
            print(f"   Status: {order['status']}")
            print(f"   Dollar Amount: ${order['dollar_amount']}")
            if order['quantity']:
                print(f"   Actual Shares: {order['quantity']}")
            
            # Cancel the order immediately
            print(f"   Cancelling order...")
            try:
                alpaca_client.cancel_order(order['id'])
                print(f"   ✅ Order cancelled")
            except Exception as e:
                print(f"   ⚠️  Order may have already filled: {e}")
        
        print("🎉 Dollar amount trading test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        trading_logger.error(f"Dollar amount trading test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Python Trading Bot - Dollar Amount Trading Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Run test
    test_dollar_amount_trading()
    
    print("\n✅ Test completed!")
