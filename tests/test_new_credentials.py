#!/usr/bin/env python3
"""
Test script for new Alpaca credentials
"""

import alpaca_trade_api as tradeapi

def test_credentials():
    """Test the new Alpaca credentials"""
    
    # New credentials from dashboard
    API_KEY = 'PKW5F9J9XIBBWVD83D1Z'
    SECRET_KEY = 'AbQe1hte5yBjJcnMlirqTspOx5GSxmfiGZ6Yoqyy'
    BASE_URL = 'https://paper-api.alpaca.markets'
    
    print("🔍 Testing New Alpaca Credentials")
    print("=" * 50)
    print(f"API Key: {API_KEY[:4]}...{API_KEY[-4:]}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Initialize API
        api = tradeapi.REST(
            key_id=API_KEY,
            secret_key=SECRET_KEY,
            base_url=BASE_URL,
            api_version='v2'
        )
        
        print("✅ API initialized successfully")
        
        # Get account info
        account = api.get_account()
        print(f"✅ Account ID: {account.id}")
        print(f"✅ Status: {account.status}")
        print(f"✅ Cash: ${float(account.cash):.2f}")
        print(f"✅ Buying Power: ${float(account.buying_power):.2f}")
        print(f"✅ Portfolio Value: ${float(account.portfolio_value):.2f}")
        print(f"✅ Equity: ${float(account.equity):.2f}")
        
        # Check if trading is blocked
        print(f"✅ Trading Blocked: {account.trading_blocked}")
        print(f"✅ Account Blocked: {account.account_blocked}")
        
        print("\n🎉 Credentials are working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if the API key and secret are correct")
        print("2. Make sure the account is active")
        print("3. Verify the base URL is correct")

if __name__ == "__main__":
    test_credentials()
