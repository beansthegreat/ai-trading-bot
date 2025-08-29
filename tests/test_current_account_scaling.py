#!/usr/bin/env python3
"""
Test intelligent scaling with current account balance
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

def test_current_account_scaling():
    """Test intelligent scaling with current account"""
    print("🧠 Testing Intelligent Scaling with Current Account")
    print("=" * 60)
    
    try:
        # Get current account info
        account = alpaca_client.get_account()
        cash = account['cash']
        
        print(f"💰 Current Account Status:")
        print(f"   Cash: ${cash:.2f}")
        print(f"   Portfolio Value: ${account['portfolio_value']:.2f}")
        print(f"   Equity: ${account['equity']:.2f}")
        print()
        
        # Test with current trading symbols
        symbols = config.SYMBOLS
        
        for symbol in symbols:
            try:
                # Get current price
                df = alpaca_client.get_historical_data(symbol, timeframe='1D', limit=1)
                if df.empty:
                    continue
                    
                current_price = df['close'].iloc[-1]
                
                print(f"📊 {symbol} @ ${current_price:.2f}")
                
                # Test different signal strengths
                for signal_strength in [0.3, 0.5, 0.7, 0.9]:
                    try:
                        position_info = risk_manager.calculate_position_size(
                            symbol, current_price, cash, signal_strength
                        )
                        
                        # Check if we can afford this position
                        account_info = {'cash': cash, 'account_blocked': False, 'trading_blocked': False}
                        validation = risk_manager.validate_trade(
                            symbol, 'buy', position_info['amount'], 
                            current_price, account_info, position_info['type']
                        )
                        
                        status = "✅" if validation['valid'] else "❌"
                        
                        print(f"   Signal {signal_strength:.1f}: {status} {position_info['type']} - ${position_info['amount']:.2f} ({position_info['shares']:.4f} shares)")
                        
                        if not validation['valid']:
                            print(f"      Reason: {validation['errors']}")
                        
                    except Exception as e:
                        print(f"   Signal {signal_strength:.1f}: ❌ Error - {e}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error getting data for {symbol}: {e}")
                print()
        
        # Show intelligent scaling summary
        print("🎯 Intelligent Scaling Summary:")
        print("   • Low price stocks (<$50): Prefer shares for precision")
        print("   • High price stocks (>$200): Prefer dollar amounts for accessibility")
        print("   • Medium price stocks: Intelligent choice based on available cash")
        print("   • Current cash: ${:.2f} - allows for {} positions".format(cash, int(cash / 20)))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_current_account_scaling()
