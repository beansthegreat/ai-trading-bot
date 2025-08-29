import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import trading_logger

class AlertSystem:
    """Real-time alert system for trading notifications"""
    
    def __init__(self):
        self.discord_webhook_url = None
        self.telegram_bot_token = None
        self.telegram_chat_id = None
        self.enabled = False
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load alert configuration from environment variables"""
        import os
        
        # Discord configuration
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        # Telegram configuration
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Enable if any alert method is configured
        self.enabled = bool(self.discord_webhook_url or self.telegram_bot_token)
        
        if self.enabled:
            trading_logger.info("Alert system initialized", 
                               discord_enabled=bool(self.discord_webhook_url),
                               telegram_enabled=bool(self.telegram_bot_token))
        else:
            trading_logger.info("Alert system disabled - no webhooks configured")
    
    def send_trade_alert(self, trade_data: Dict[str, Any]):
        """Send trade execution alert"""
        if not self.enabled:
            return
        
        action = trade_data['action'].upper()
        symbol = trade_data['symbol']
        quantity = trade_data.get('quantity', 0)
        price = trade_data['price']
        pnl = trade_data.get('pnl', 0)
        signal_strength = trade_data.get('signal_strength', 0)
        
        # Create message
        message = f"🎯 **{action} ORDER EXECUTED**\n"
        message += f"📈 **{symbol}**\n"
        message += f"💰 Quantity: {quantity:.4f}\n"
        message += f"💵 Price: ${price:.2f}\n"
        
        if pnl != 0:
            pnl_emoji = "🟢" if pnl > 0 else "🔴"
            message += f"{pnl_emoji} P&L: ${pnl:.2f}\n"
        
        message += f"📊 Signal Strength: {signal_strength:.3f}\n"
        message += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        
        self._send_alert(message, "trade")
    
    def send_signal_alert(self, symbol: str, signal: str, strength: float, reason: str):
        """Send trading signal alert"""
        if not self.enabled:
            return
        
        signal_emoji = "🟢" if signal == "buy" else "🔴" if signal == "sell" else "⚪"
        
        message = f"{signal_emoji} **{signal.upper()} SIGNAL**\n"
        message += f"📈 **{symbol}**\n"
        message += f"💪 Strength: {strength:.3f}\n"
        message += f"📝 Reason: {reason}\n"
        message += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        
        self._send_alert(message, "signal")
    
    def send_performance_alert(self, performance_data: Dict[str, Any]):
        """Send performance summary alert"""
        if not self.enabled:
            return
        
        total_return = performance_data.get('total_return', 0)
        win_rate = performance_data.get('win_rate', 0)
        profit_factor = performance_data.get('profit_factor', 0)
        
        # Determine performance emoji
        if total_return > 0.05:  # 5% return
            perf_emoji = "🚀"
        elif total_return > 0:
            perf_emoji = "📈"
        else:
            perf_emoji = "📉"
        
        message = f"{perf_emoji} **DAILY PERFORMANCE SUMMARY**\n"
        message += f"📊 Total Return: {total_return:.2%}\n"
        message += f"🎯 Win Rate: {win_rate:.1%}\n"
        message += f"💰 Profit Factor: {profit_factor:.2f}\n"
        message += f"⏰ Date: {datetime.now().strftime('%Y-%m-%d')}"
        
        self._send_alert(message, "performance")
    
    def send_error_alert(self, error_message: str, context: str = ""):
        """Send error alert"""
        if not self.enabled:
            return
        
        message = f"⚠️ **ERROR ALERT**\n"
        message += f"🚨 {error_message}\n"
        if context:
            message += f"📋 Context: {context}\n"
        message += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        
        self._send_alert(message, "error")
    
    def send_market_alert(self, market_status: str, details: str = ""):
        """Send market status alert"""
        if not self.enabled:
            return
        
        status_emoji = "🟢" if "open" in market_status.lower() else "🔴"
        
        message = f"{status_emoji} **MARKET STATUS**\n"
        message += f"🏛️ {market_status}\n"
        if details:
            message += f"📋 {details}\n"
        message += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        
        self._send_alert(message, "market")
    
    def _send_alert(self, message: str, alert_type: str):
        """Send alert through configured channels"""
        try:
            # Send Discord alert
            if self.discord_webhook_url:
                self._send_discord_alert(message, alert_type)
            
            # Send Telegram alert
            if self.telegram_bot_token and self.telegram_chat_id:
                self._send_telegram_alert(message, alert_type)
                
        except Exception as e:
            trading_logger.error(f"Failed to send alert: {e}")
    
    def _send_discord_alert(self, message: str, alert_type: str):
        """Send alert to Discord webhook"""
        try:
            # Create Discord embed
            color = self._get_discord_color(alert_type)
            
            embed = {
                "title": f"Trading Bot Alert - {alert_type.upper()}",
                "description": message,
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "Python Trading Bot"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 204:
                trading_logger.debug("Discord alert sent successfully")
            else:
                trading_logger.warning(f"Discord alert failed: {response.status_code}")
                
        except Exception as e:
            trading_logger.error(f"Discord alert error: {e}")
    
    def _send_telegram_alert(self, message: str, alert_type: str):
        """Send alert to Telegram bot"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                trading_logger.debug("Telegram alert sent successfully")
            else:
                trading_logger.warning(f"Telegram alert failed: {response.status_code}")
                
        except Exception as e:
            trading_logger.error(f"Telegram alert error: {e}")
    
    def _get_discord_color(self, alert_type: str) -> int:
        """Get Discord embed color based on alert type"""
        colors = {
            "trade": 0x00ff00,      # Green
            "signal": 0x0099ff,     # Blue
            "performance": 0xff9900, # Orange
            "error": 0xff0000,      # Red
            "market": 0x9900ff      # Purple
        }
        return colors.get(alert_type, 0x808080)  # Default gray
    
    def test_alerts(self):
        """Test alert system functionality"""
        if not self.enabled:
            print("❌ Alert system is disabled - no webhooks configured")
            return
        
        print("🧪 Testing alert system...")
        
        # Test trade alert
        test_trade = {
            "action": "buy",
            "symbol": "AAPL",
            "quantity": 10.5,
            "price": 150.25,
            "signal_strength": 0.75
        }
        self.send_trade_alert(test_trade)
        
        # Test signal alert
        self.send_signal_alert("NVDA", "buy", 0.85, "Strong momentum detected")
        
        # Test performance alert
        test_performance = {
            "total_return": 0.025,
            "win_rate": 0.65,
            "profit_factor": 1.8
        }
        self.send_performance_alert(test_performance)
        
        print("✅ Test alerts sent - check your Discord/Telegram")

# Global instance
alert_system = AlertSystem()
