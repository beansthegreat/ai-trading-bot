#!/usr/bin/env python3
"""
Backtesting script for the trading bot
Run historical simulations to validate strategy performance
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.backtesting import backtester
from utils.performance_analytics import performance_analytics

def main():
    """Run backtest on trading strategy"""
    print("🔬 Trading Bot Backtest")
    print("=" * 50)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    symbols = config.SYMBOLS[:3]  # Test with first 3 symbols for speed
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # Last 7 days
    
    print(f"📊 Backtest Configuration:")
    print(f"   Symbols: {', '.join(symbols)}")
    print(f"   Start Date: {start_date}")
    print(f"   End Date: {end_date}")
    print(f"   Initial Portfolio: $10,000")
    print()
    
    try:
        # Run backtest
        print("🚀 Starting backtest...")
        results = backtester.run_backtest(symbols, start_date, end_date)
        
        if not results:
            print("❌ Backtest failed - no results generated")
            return
        
        # Generate and display report
        print("\n" + "=" * 50)
        report = backtester.generate_backtest_report(results)
        print(report)
        
        # Generate performance analytics
        print("\n" + "=" * 50)
        analytics_report = performance_analytics.generate_performance_report()
        print(analytics_report)
        
        # Recommendations
        print("\n" + "=" * 50)
        print("💡 RECOMMENDATIONS:")
        
        if results['total_return'] > 0.05:  # 5% return
            print("   ✅ Strategy shows positive returns - consider live trading")
        elif results['total_return'] > 0:
            print("   ⚠️  Strategy shows small positive returns - needs optimization")
        else:
            print("   ❌ Strategy shows negative returns - requires significant changes")
        
        if results['win_rate'] > 0.6:
            print("   ✅ High win rate - good signal quality")
        elif results['win_rate'] > 0.4:
            print("   ⚠️  Moderate win rate - consider signal improvements")
        else:
            print("   ❌ Low win rate - signals need major improvement")
        
        if results['profit_factor'] > 1.5:
            print("   ✅ Strong profit factor - good risk/reward")
        elif results['profit_factor'] > 1.0:
            print("   ⚠️  Positive profit factor but needs improvement")
        else:
            print("   ❌ Poor profit factor - high losses relative to wins")
        
        if results['max_drawdown'] < 0.1:  # 10% max drawdown
            print("   ✅ Low maximum drawdown - good risk management")
        elif results['max_drawdown'] < 0.2:  # 20% max drawdown
            print("   ⚠️  Moderate drawdown - consider tighter stops")
        else:
            print("   ❌ High drawdown - risk management needs improvement")
        
        print()
        print("🎯 Next Steps:")
        print("   1. Review individual symbol performance")
        print("   2. Adjust strategy parameters if needed")
        print("   3. Run longer backtest periods")
        print("   4. Test with different market conditions")
        print("   5. Consider live paper trading")
        
    except Exception as e:
        print(f"❌ Backtest error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
