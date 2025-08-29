#!/usr/bin/env python3
"""
Test script to demonstrate intelligent position scaling
Shows how the bot switches between dollar amounts and shares based on stock prices and funds
"""

import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.risk_management import risk_manager
from utils.logger import trading_logger

def test_intelligent_scaling():
    """Test intelligent position scaling with different scenarios"""
    print("🧠 Testing Intelligent Position Scaling")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        # Low price stocks (prefer shares)
        {"symbol": "F", "price": 12.50, "cash": 1000, "signal": 0.8, "description": "Low price stock - should use shares"},
        {"symbol": "GE", "price": 25.75, "cash": 500, "signal": 0.6, "description": "Low price stock - should use shares"},
        
        # High price stocks (prefer dollar amounts)
        {"symbol": "AAPL", "price": 230.50, "cash": 1000, "signal": 0.7, "description": "High price stock - should use dollar amount"},
        {"symbol": "TSLA", "price": 450.25, "cash": 500, "signal": 0.5, "description": "High price stock - should use dollar amount"},
        
        # Medium price stocks (intelligent choice)
        {"symbol": "MSFT", "price": 85.30, "cash": 1000, "signal": 0.6, "description": "Medium price, high cash - should use shares"},
        {"symbol": "GOOGL", "price": 120.45, "cash": 200, "signal": 0.4, "description": "Medium price, low cash - should use dollar amount"},
        
        # Edge cases
        {"symbol": "BRK.A", "price": 85000.00, "cash": 1000, "signal": 0.9, "description": "Extreme high price - should use dollar amount"},
        {"symbol": "PENNY", "price": 0.05, "cash": 100, "signal": 0.3, "description": "Penny stock - should use shares"},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📊 Scenario {i}: {scenario['description']}")
        print(f"   Symbol: {scenario['symbol']}")
        print(f"   Price: ${scenario['price']:.2f}")
        print(f"   Available Cash: ${scenario['cash']:.2f}")
        print(f"   Signal Strength: {scenario['signal']:.2f}")
        
        try:
            # Calculate intelligent position
            position_info = risk_manager.calculate_position_size(
                scenario['symbol'],
                scenario['price'],
                scenario['cash'],
                scenario['signal']
            )
            
            print(f"   🎯 Decision: {position_info['type'].upper()}")
            print(f"   💰 Amount: {position_info['amount']}")
            print(f"   📈 Estimated Shares: {position_info['shares']:.4f}")
            print(f"   💵 Dollar Value: ${position_info['dollar_value']:.2f}")
            print(f"   💭 Reason: {position_info['reason']}")
            
            # Validate the trade
            account_info = {'cash': scenario['cash'], 'account_blocked': False, 'trading_blocked': False}
            validation = risk_manager.validate_trade(
                scenario['symbol'], 'buy', position_info['amount'], 
                scenario['price'], account_info, position_info['type']
            )
            
            if validation['valid']:
                print(f"   ✅ Validation: PASSED")
            else:
                print(f"   ❌ Validation: FAILED - {validation['errors']}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 60)

def test_scaling_with_real_prices():
    """Test with current market prices"""
    print("\n🎯 Testing with Real Market Prices")
    print("=" * 60)
    
    # Get current prices (you can update these)
    real_scenarios = [
        {"symbol": "AAPL", "price": 230.50, "cash": 1000},
        {"symbol": "MSFT", "price": 85.30, "cash": 1000},
        {"symbol": "TSLA", "price": 450.25, "cash": 1000},
        {"symbol": "AMZN", "price": 180.75, "cash": 1000},
        {"symbol": "GOOGL", "price": 120.45, "cash": 1000},
    ]
    
    for scenario in real_scenarios:
        print(f"\n📊 {scenario['symbol']} @ ${scenario['price']:.2f}")
        
        # Test different signal strengths
        for signal_strength in [0.3, 0.5, 0.7, 0.9]:
            try:
                position_info = risk_manager.calculate_position_size(
                    scenario['symbol'],
                    scenario['price'],
                    scenario['cash'],
                    signal_strength
                )
                
                print(f"   Signal {signal_strength:.1f}: {position_info['type']} - ${position_info['amount']:.2f} ({position_info['shares']:.4f} shares)")
                
            except Exception as e:
                print(f"   Signal {signal_strength:.1f}: Error - {e}")

if __name__ == "__main__":
    test_intelligent_scaling()
    test_scaling_with_real_prices()
    
    print("\n🎉 Intelligent Scaling Test Complete!")
    print("\n💡 Key Features:")
    print("   • Low price stocks (<$50): Prefer shares for precision")
    print("   • High price stocks (>$200): Prefer dollar amounts for accessibility")
    print("   • Medium price stocks: Intelligent choice based on available cash")
    print("   • Signal strength affects position size")
    print("   • Automatic validation and constraints")
