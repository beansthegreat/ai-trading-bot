#!/usr/bin/env python3
"""
📺 News Anchor System for Trading Bot
Provides live market commentary and updates
"""

import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random
from utils.logger import trading_logger

class NewsAnchor:
    """AI News Anchor that provides live market commentary"""
    
    def __init__(self):
        self.name = "AI Market Reporter"
        self.last_update = None
        self.update_interval = 120  # 2 minutes in seconds
        self.market_summary = {}
        self.trade_count = 0
        self.buy_signals = 0
        self.sell_signals = 0
        self.wait_signals = 0
        
        # News anchor phrases
        self.greetings = [
            "Good morning traders!",
            "Welcome back to the market floor!",
            "Here's your live market update!",
            "Breaking news from the trading floor!",
            "Market update coming your way!",
            "Live from the AI trading desk!"
        ]
        
        self.transitions = [
            "Moving on to our market analysis...",
            "Let's take a look at what's happening...",
            "Here's what our AI has been up to...",
            "Switching gears to market activity...",
            "Now for the trading highlights...",
            "Let's dive into the numbers..."
        ]
        
        self.closings = [
            "That's all for now, stay tuned for more updates!",
            "We'll be back in 2 minutes with more market news!",
            "Keep your eyes on the market, more updates coming!",
            "Stay sharp traders, we'll be right back!",
            "More market action coming your way soon!",
            "That's a wrap for this update, see you in 2!"
        ]
        
        trading_logger.info("News Anchor initialized", anchor_name=self.name)
    
    def _type_text(self, text: str, delay: float = 0.03):
        """Type out text character by character for realistic effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
    
    def _type_line(self, text: str, delay: float = 0.03):
        """Type out a line and add newline"""
        self._type_text(text, delay)
        print()  # Add newline after typing
    
    def should_give_update(self) -> bool:
        """Check if it's time for a news update"""
        if self.last_update is None:
            return True
        
        time_since_update = (datetime.now() - self.last_update).total_seconds()
        return time_since_update >= self.update_interval
    
    def give_market_update(self, recent_activity: Dict[str, Any] = None) -> str:
        """Generate and deliver a market update"""
        try:
            # Update our tracking
            self.last_update = datetime.now()
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Generate the news update
            update = self._generate_news_update(recent_activity, current_time)
            
            # Display the update prominently
            self._display_news_update(update)
            
            return update
            
        except Exception as e:
            trading_logger.error(f"Failed to generate news update: {e}")
            return "News update temporarily unavailable..."
    
    def _generate_news_update(self, recent_activity: Dict[str, Any], current_time: str) -> str:
        """Generate the actual news update content"""
        greeting = random.choice(self.greetings)
        transition = random.choice(self.transitions)
        closing = random.choice(self.closings)
        
        # Build the update
        update_parts = [f"📺 {greeting} It's {current_time} and here's what's happening in the markets:"]
        
        # Add market summary
        if recent_activity:
            update_parts.append(f"\n{transition}")
            update_parts.append(self._analyze_recent_activity(recent_activity))
        
        # Add general market commentary
        update_parts.append(f"\n{self._get_market_commentary()}")
        
        # Add closing
        update_parts.append(f"\n{closing}")
        
        return "\n".join(update_parts)
    
    def _analyze_recent_activity(self, activity: Dict[str, Any]) -> str:
        """Analyze recent trading activity for the update"""
        if not activity:
            return "Our AI is currently analyzing the market conditions..."
        
        total_signals = activity.get('total_signals', 0)
        buy_signals = activity.get('buy_signals', 0)
        sell_signals = activity.get('sell_signals', 0)
        wait_signals = activity.get('wait_signals', 0)
        
        if total_signals == 0:
            return "The market is quiet right now - our AI is waiting for the right opportunities."
        
        # Generate commentary based on activity
        if buy_signals > sell_signals:
            sentiment = "bullish"
            commentary = f"Our AI is feeling optimistic! We've seen {buy_signals} buy signals vs {sell_signals} sell signals in the last 2 minutes."
        elif sell_signals > buy_signals:
            sentiment = "bearish"
            commentary = f"Our AI is being cautious! We've seen {sell_signals} sell signals vs {buy_signals} buy signals in the last 2 minutes."
        else:
            sentiment = "neutral"
            commentary = f"Our AI is playing it safe! We've seen {buy_signals} buy signals and {sell_signals} sell signals - pretty balanced."
        
        if wait_signals > 0:
            commentary += f" Plus {wait_signals} wait signals as our AI waits for better opportunities."
        
        return commentary
    
    def _get_market_commentary(self) -> str:
        """Get general market commentary"""
        commentaries = [
            "The AI is constantly scanning for the best opportunities across all sectors.",
            "Our advanced algorithms are processing thousands of data points every second.",
            "Risk management is our top priority - we never take unnecessary chances.",
            "The market is like a puzzle, and our AI is the master puzzle solver.",
            "We're looking for those sweet spots where risk meets reward perfectly.",
            "Patience is key in trading - our AI knows when to wait and when to act.",
            "Every trade is backed by solid analysis and careful consideration.",
            "The market never sleeps, and neither does our AI trading system."
        ]
        
        return random.choice(commentaries)
    
    def _display_news_update(self, update: str):
        """Display the news update prominently in the console with typing effect"""
        # Type out the header
        print()  # Start with newline
        self._type_line(f"{'📺'*25} LIVE MARKET NEWS {'📺'*25}", 0.01)
        
        # Split update into lines and type each one
        lines = update.split('\n')
        for line in lines:
            if line.strip():  # Only type non-empty lines
                self._type_line(line, 0.03)
            else:
                print()  # Just add newline for empty lines
        
        # Type out the footer
        self._type_line(f"{'📺'*25} LIVE MARKET NEWS {'📺'*25}", 0.01)
        print()  # Final newline
        
        # Also log it
        trading_logger.info("News Update Delivered", update_length=len(update))
    
    def record_signal(self, signal_type: str, symbol: str):
        """Record a trading signal for the next update"""
        if signal_type.upper() == 'BUY':
            self.buy_signals += 1
        elif signal_type.upper() == 'SELL':
            self.sell_signals += 1
        else:
            self.wait_signals += 1
        
        self.trade_count += 1
    
    def get_recent_activity(self) -> Dict[str, Any]:
        """Get summary of recent activity for news updates"""
        return {
            'total_signals': self.trade_count,
            'buy_signals': self.buy_signals,
            'sell_signals': self.sell_signals,
            'wait_signals': self.wait_signals,
            'last_update': self.last_update
        }
    
    def reset_counters(self):
        """Reset activity counters (call this after each news update)"""
        self.trade_count = 0
        self.buy_signals = 0
        self.sell_signals = 0
        self.wait_signals = 0
