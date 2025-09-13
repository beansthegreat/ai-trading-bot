#!/usr/bin/env python3
"""
🚀 Start S&P 500 Autonomous System
One-click startup for fully autonomous S&P 500 management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sp500_autonomous_system import SP500AutonomousSystem

def main():
    """Start the autonomous system"""
    print("🚀 Starting S&P 500 Autonomous System...")
    print("This system will run completely automatically with no user interaction required.")
    print("It will:")
    print("  📊 Monitor S&P 500 changes every 6 hours")
    print("  📥 Collect data for new stocks automatically")
    print("  🤖 Train AI models using hybrid GPU+NPU acceleration")
    print("  🗑️ Clean up delisted stock data")
    print("  📈 Rank stocks by performance")
    print("  🎯 Trade the best performing stocks")
    print()
    print("Press Ctrl+C to stop the system")
    print()
    
    # Start the autonomous system
    autonomous_system = SP500AutonomousSystem()
    autonomous_system.start_autonomous_system()

if __name__ == "__main__":
    main()
