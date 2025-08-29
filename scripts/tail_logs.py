#!/usr/bin/env python3
"""
Simple log tailing script for the trading bot
Shows live log updates in real-time
"""

import os
import time
import sys
from datetime import datetime

def tail_logs():
    """Tail the trading bot logs"""
    log_file = "./logs/trading-bot.log"
    
    print("📊 Live Trading Bot Logs")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    # Get current file size
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            # Go to end of file
            f.seek(0, 2)
            current_position = f.tell()
    else:
        current_position = 0
    
    try:
        while True:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(current_position)
                    new_lines = f.readlines()
                    
                    if new_lines:
                        for line in new_lines:
                            # Format the line
                            formatted_line = format_log_line(line.strip())
                            if formatted_line:
                                print(formatted_line)
                        
                        current_position = f.tell()
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n🛑 Log monitoring stopped")

def format_log_line(line):
    """Format log line for display"""
    if not line:
        return None
        
    # Skip old JSON format lines
    if line.startswith('{'):
        return None
        
    # Parse timestamp and message
    try:
        if '|' in line:
            parts = line.split('|', 2)
            if len(parts) >= 3:
                timestamp = parts[0].strip()
                level = parts[1].strip()
                message = parts[2].strip()
                
                # Add emojis based on content
                if 'ERROR' in level:
                    return f"🔴 {timestamp} | {message}"
                elif 'WARNING' in level:
                    return f"🟡 {timestamp} | {message}"
                elif 'SUCCESS' in level:
                    return f"🟢 {timestamp} | {message}"
                elif 'TRADE' in message:
                    return f"💰 {timestamp} | {message}"
                elif 'STRATEGY' in message:
                    return f"📊 {timestamp} | {message}"
                elif 'BUY' in message or 'SELL' in message:
                    return f"💸 {timestamp} | {message}"
                else:
                    return f"ℹ️  {timestamp} | {message}"
        
        return f"ℹ️  {line}"
        
    except Exception:
        return f"ℹ️  {line}"

if __name__ == "__main__":
    tail_logs()
