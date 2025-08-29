#!/usr/bin/env python3
"""
Simple test script to verify Alpaca connection and basic functionality
"""

import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.alpaca_client import alpaca_client
from utils.logger import trading_logger

def test_connection():
    """Test Alpaca connection and basic functionality"""
    print("🔍 Testing Alpaca Connection...")
    print(f"   Base URL: {config.ALPACA_BASE_URL}")
    print(f"   API Key: {config.ALPACA_API_KEY[:4]}...{config.ALPACA_API_KEY[-4:]}")
    print(f"   Trading Mode: {config.TRADING_MODE}")
    print()
    
    try:
        # Test 1: Get account information
        print("📊 Test 1: Getting account information...")
        account = alpaca_client.get_account()
        print(f"   ✅ Account ID: {account['id']}")
        print(f"   ✅ Status: {account['status']}")
        print(f"   ✅ Cash: ${account['cash']:.2f}")
        print(f"   ✅ Portfolio Value: ${account['portfolio_value']:.2f}")
        print(f"   ✅ Equity: ${account['equity']:.2f}")
        print()
        
        # Test 2: Check market status
        print("🏛️  Test 2: Checking market status...")
        is_open = alpaca_client.is_market_open()
        print(f"   ✅ Market Open: {is_open}")
        print()
        
        # Test 3: Get positions
        print("📈 Test 3: Getting current positions...")
        positions = alpaca_client.get_positions()
        print(f"   ✅ Found {len(positions)} positions")
        for pos in positions:
            print(f"      - {pos['symbol']}: {pos['quantity']} shares @ ${pos['average_price']:.2f}")
        print()
        
        # Test 4: Get historical data for AAPL
        print("📊 Test 4: Getting historical data for AAPL...")
        df = alpaca_client.get_historical_data('AAPL', timeframe='1D', limit=5)
        print(f"   ✅ Retrieved {len(df)} data points")
        if not df.empty:
            latest = df.iloc[-1]
            print(f"   ✅ Latest AAPL price: ${latest['close']:.2f}")
        print()
        
        # Test 5: Get orders
        print("📋 Test 5: Getting recent orders...")
        orders = alpaca_client.get_orders(limit=5)
        print(f"   ✅ Found {len(orders)} recent orders")
        for order in orders[:3]:  # Show first 3
            print(f"      - {order['symbol']} {order['side']} {order['quantity']} @ ${order.get('price', 'market')}")
        print()
        
        print("🎉 All tests passed! Alpaca connection is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        trading_logger.error(f"Connection test failed: {e}")
        return False

def test_small_order():
    """Test placing a small market order (optional)"""
    print("\n🔧 Optional: Test small market order...")
    response = input("Do you want to test placing a small AAPL order? (y/N): ")
    
    if response.lower() != 'y':
        print("   Skipping order test")
        return True
    
    try:
        # Get current AAPL price
        df = alpaca_client.get_historical_data('AAPL', timeframe='1D', limit=1)
        current_price = df['close'].iloc[-1]
        
        print(f"   Current AAPL price: ${current_price:.2f}")
        print(f"   Placing order for 1 share...")
        
        # Place order for 1 share
        order = alpaca_client.place_market_order('AAPL', 'buy', 1)
        
        print(f"   ✅ Order placed successfully!")
        print(f"   Order ID: {order['id']}")
        print(f"   Status: {order['status']}")
        
        # Cancel the order immediately
        print(f"   Cancelling order...")
        alpaca_client.cancel_order(order['id'])
        print(f"   ✅ Order cancelled")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Order test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Python Trading Bot - Connection Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    if test_connection():
        test_small_order()
    
    print("\n✅ Test completed!")
