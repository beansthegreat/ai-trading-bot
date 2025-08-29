#!/usr/bin/env python3
"""
Test script for buy and sell orders with all symbols
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

def test_buy_sell_orders():
    """Test buy and sell orders with all symbols"""
    print("🔄 Testing Buy and Sell Orders")
    print("=" * 50)
    
    try:
        # Get account information
        account = alpaca_client.get_account()
        print(f"💰 Account Cash: ${account['cash']:.2f}")
        print(f"📊 Portfolio Value: ${account['portfolio_value']:.2f}")
        print()
        
        # Test symbols including NVDA and AMD
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'AMD']
        
        print("📈 Testing Position Size Calculation for All Symbols:")
        print("-" * 50)
        
        for symbol in symbols:
            try:
                # Get current price
                df = alpaca_client.get_historical_data(symbol, '1D')
                current_price = df['close'].iloc[-1]
                
                # Calculate position size
                position_info = risk_manager.calculate_position_size(
                    symbol, current_price, account['cash'], 0.8  # Strong signal
                )
                
                print(f"📊 {symbol} @ ${current_price:.2f}:")
                print(f"   Type: {position_info['type']}")
                print(f"   Amount: ${position_info['amount']:.2f}")
                print(f"   Estimated Shares: {position_info['shares']:.4f}")
                print()
                
            except Exception as e:
                print(f"❌ Error getting data for {symbol}: {e}")
                print()
        
        # Test buy order
        print("🟢 Testing Buy Order:")
        print("-" * 30)
        
        # Choose a symbol for testing
        test_symbol = "NVDA"
        print(f"Testing buy order for {test_symbol}...")
        
        # Get current price
        df = alpaca_client.get_historical_data(test_symbol, '1D')
        current_price = df['close'].iloc[-1]
        
        # Calculate position size
        position_info = risk_manager.calculate_position_size(
            test_symbol, current_price, account['cash'], 0.8
        )
        
        print(f"   Current Price: ${current_price:.2f}")
        print(f"   Position Type: {position_info['type']}")
        print(f"   Amount: ${position_info['amount']:.2f}")
        print(f"   Estimated Shares: {position_info['shares']:.4f}")
        
        # Place buy order
        if position_info['type'] == 'dollar_amount':
            order = alpaca_client.place_dollar_amount_order(test_symbol, 'buy', position_info['amount'])
            print(f"   ✅ Buy order placed: ${position_info['amount']:.2f} worth of {test_symbol}")
        else:
            order = alpaca_client.place_market_order(test_symbol, 'buy', position_info['amount'])
            print(f"   ✅ Buy order placed: {position_info['amount']:.4f} shares of {test_symbol}")
        
        print(f"   Order ID: {order['id']}")
        print(f"   Status: {order['status']}")
        
        # Wait a moment for order to potentially fill
        import time
        time.sleep(2)
        
        # Check if order filled
        order_status = alpaca_client.get_order(order['id'])
        print(f"   Final Status: {order_status['status']}")
        
        if order_status['status'] == 'filled':
            print(f"   ✅ Order filled successfully!")
            print(f"   Filled Quantity: {order_status['quantity']}")
            if 'fill_price' in order_status and order_status['fill_price']:
                print(f"   Fill Price: ${order_status['fill_price']}")
            else:
                print(f"   Fill Price: Not available")
            
            # Test sell order
            print("\n🔴 Testing Sell Order:")
            print("-" * 30)
            
            # Get current position
            position = alpaca_client.get_position(test_symbol)
            if position:
                quantity = abs(float(position['quantity']))
                print(f"   Current Position: {quantity:.4f} shares")
                
                # Place sell order
                sell_order = alpaca_client.place_market_order(test_symbol, 'sell', quantity)
                print(f"   ✅ Sell order placed: {quantity:.4f} shares of {test_symbol}")
                print(f"   Order ID: {sell_order['id']}")
                print(f"   Status: {sell_order['status']}")
                
                # Wait for sell order to potentially fill
                time.sleep(2)
                
                # Check sell order status
                sell_order_status = alpaca_client.get_order(sell_order['id'])
                print(f"   Final Status: {sell_order_status['status']}")
                
                if sell_order_status['status'] == 'filled':
                    print(f"   ✅ Sell order filled successfully!")
                    print(f"   Filled Quantity: {sell_order_status['quantity']}")
                    if 'fill_price' in sell_order_status and sell_order_status['fill_price']:
                        print(f"   Fill Price: ${sell_order_status['fill_price']}")
                    else:
                        print(f"   Fill Price: Not available")
                else:
                    print(f"   ⚠️  Sell order status: {sell_order_status['status']}")
                    # Cancel if not filled
                    try:
                        alpaca_client.cancel_order(sell_order['id'])
                        print(f"   ✅ Sell order cancelled")
                    except Exception as e:
                        print(f"   ⚠️  Could not cancel sell order: {e}")
            else:
                print(f"   ⚠️  No position found for {test_symbol}")
        else:
            print(f"   ⚠️  Buy order status: {order_status['status']}")
            # Cancel if not filled
            try:
                alpaca_client.cancel_order(order['id'])
                print(f"   ✅ Buy order cancelled")
            except Exception as e:
                print(f"   ⚠️  Could not cancel buy order: {e}")
        
        print("\n🎉 Buy/Sell test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        trading_logger.error(f"Buy/Sell test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Python Trading Bot - Buy/Sell Order Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Run test
    test_buy_sell_orders()
    
    print("\n✅ Test completed!")
