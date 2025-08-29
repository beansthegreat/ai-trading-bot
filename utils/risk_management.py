import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.logger import trading_logger
from config import config

class RiskManager:
    """Risk management system for the trading bot"""
    
    def __init__(self):
        self.daily_loss = 0.0
        self.daily_trades = []
        self.max_drawdown = 0.0
        self.peak_portfolio_value = 0.0
        self.wash_sale_tracker = {}  # Track wash sale periods for each symbol
    
    def can_trade(self, account_info: Dict[str, Any], symbol: str = None) -> Dict[str, Any]:
        """Check if trading is allowed based on risk rules"""
        checks = {
            'account_blocked': not account_info.get('account_blocked', False),
            'trading_blocked': not account_info.get('trading_blocked', False),
            'sufficient_cash': account_info.get('cash', 0) > 100,  # Minimum $100
            'daily_loss_limit': self.daily_loss < config.DAILY_LOSS_LIMIT,
            'max_positions': len(self._get_current_positions()) < config.MAX_POSITIONS,
            'market_open': True  # Will be checked separately
        }
        
        can_trade = all(checks.values())
        
        if not can_trade:
            failed_checks = [k for k, v in checks.items() if not v]
            trading_logger.warning(f"Trading blocked", failed_checks=failed_checks)
        
        return {
            'can_trade': can_trade,
            'checks': checks,
            'failed_checks': [k for k, v in checks.items() if not v]
        }
    
    def calculate_position_size(self, symbol: str, current_price: float, 
                              available_cash: float, signal_strength: float, 
                              volatility: float = None) -> Dict[str, Any]:
        """Calculate intelligent position size with volatility-adjusted scaling"""
        
        # Base position size on signal strength with aggressive scaling for small accounts
        if signal_strength > 0.7:
            risk_multiplier = 1.0
        elif signal_strength > 0.5:
            risk_multiplier = 0.8
        elif signal_strength > 0.3:
            risk_multiplier = 0.6
        else:
            risk_multiplier = 0.4
        
        # Volatility-adjusted risk scaling
        volatility_multiplier = self._calculate_volatility_multiplier(volatility)
        
        # More aggressive scaling for smaller accounts
        if available_cash < 100:
            # Small account: use very aggressive risk percentage
            risk_percentage = min(40.0, config.RISK_PERCENTAGE * 10)  # Up to 40% for small accounts
        elif available_cash < 500:
            # Medium account: high risk
            risk_percentage = min(25.0, config.RISK_PERCENTAGE * 6)  # Up to 25% for medium accounts
        else:
            # Large account: aggressive risk
            risk_percentage = config.RISK_PERCENTAGE
        
        # Calculate maximum position value with signal strength and volatility scaling
        base_position_value = min(
            config.MAX_POSITION_SIZE,
            available_cash * (risk_percentage / 100)
        )
        
        # Apply signal strength and volatility multipliers
        max_position_value = base_position_value * risk_multiplier * volatility_multiplier
        
        # Intelligent scaling logic
        position_info = self._calculate_intelligent_position(
            symbol, current_price, available_cash, max_position_value, signal_strength
        )
        
        trading_logger.debug(
            f"Volatility-adjusted position size calculated for {symbol}",
            price=current_price,
            available_cash=available_cash,
            position_type=position_info['type'],
            amount=position_info['amount'],
            shares=position_info.get('shares'),
            signal_strength=signal_strength,
            volatility=volatility,
            volatility_multiplier=volatility_multiplier
        )
        
        return position_info
    
    def _calculate_volatility_multiplier(self, volatility: float) -> float:
        """Calculate position size multiplier based on volatility (ATR-based)"""
        if volatility is None:
            return 1.0  # Default multiplier
        
        # Volatility scaling: higher volatility = smaller position size
        # This ensures equal dollar volatility risk per trade
        
        # Define volatility thresholds
        LOW_VOLATILITY = 0.01    # 1% daily volatility
        MEDIUM_VOLATILITY = 0.02  # 2% daily volatility  
        HIGH_VOLATILITY = 0.04    # 4% daily volatility
        
        if volatility <= LOW_VOLATILITY:
            # Low volatility: can take larger positions
            return 1.5
        elif volatility <= MEDIUM_VOLATILITY:
            # Medium volatility: standard position size
            return 1.0
        elif volatility <= HIGH_VOLATILITY:
            # High volatility: smaller positions
            return 0.7
        else:
            # Very high volatility: much smaller positions
            return 0.5
    
    def _calculate_intelligent_position(self, symbol: str, current_price: float, 
                                      available_cash: float, max_position_value: float, 
                                      signal_strength: float) -> Dict[str, Any]:
        """Calculate whether to use dollar amount or share quantity based on funds and price"""
        
        # Define thresholds for intelligent scaling
        LOW_PRICE_THRESHOLD = 50.0    # Below $50: prefer shares
        HIGH_PRICE_THRESHOLD = 200.0  # Above $200: prefer dollar amounts
        
        # Dynamic minimums based on account size
        if available_cash < 100:
            MIN_DOLLAR_AMOUNT = 1.0   # Minimum $1 for small accounts
            MAX_DOLLAR_AMOUNT = available_cash * 0.8  # Up to 80% of cash
        else:
            MIN_DOLLAR_AMOUNT = 5.0   # Minimum $5 for larger accounts
            MAX_DOLLAR_AMOUNT = 1000.0  # Maximum $1000 for dollar amounts
        
        MIN_SHARES = 0.01             # Minimum 0.01 shares
        MAX_SHARES = 100              # Maximum 100 shares
        
        # Calculate potential shares and dollar amounts
        potential_shares = max_position_value / current_price
        potential_dollar_amount = max_position_value
        
        # Decision matrix based on price and available cash
        if current_price <= LOW_PRICE_THRESHOLD:
            # Low price stocks: prefer shares for better precision
            if potential_shares >= MIN_SHARES and potential_shares <= MAX_SHARES:
                return {
                    'type': 'shares',
                    'amount': round(potential_shares, 4),
                    'shares': round(potential_shares, 4),
                    'dollar_value': round(potential_shares * current_price, 2),
                    'reason': f'Low price stock (${current_price:.2f}) - using shares for precision'
                }
            else:
                # Fall back to dollar amount if share constraints not met
                dollar_amount = min(potential_dollar_amount, MAX_DOLLAR_AMOUNT)
                dollar_amount = max(dollar_amount, MIN_DOLLAR_AMOUNT)
                return {
                    'type': 'dollar_amount',
                    'amount': round(dollar_amount, 2),
                    'shares': round(dollar_amount / current_price, 4),
                    'dollar_value': round(dollar_amount, 2),
                    'reason': f'Low price but share constraints not met - using dollar amount'
                }
                
        elif current_price >= HIGH_PRICE_THRESHOLD:
            # High price stocks: prefer dollar amounts for accessibility
            if potential_dollar_amount >= MIN_DOLLAR_AMOUNT and potential_dollar_amount <= MAX_DOLLAR_AMOUNT:
                return {
                    'type': 'dollar_amount',
                    'amount': round(potential_dollar_amount, 2),
                    'shares': round(potential_dollar_amount / current_price, 4),
                    'dollar_value': round(potential_dollar_amount, 2),
                    'reason': f'High price stock (${current_price:.2f}) - using dollar amount for accessibility'
                }
            else:
                # Fall back to shares if dollar constraints not met
                shares = min(potential_shares, MAX_SHARES)
                shares = max(shares, MIN_SHARES)
                return {
                    'type': 'shares',
                    'amount': round(shares, 4),
                    'shares': round(shares, 4),
                    'dollar_value': round(shares * current_price, 2),
                    'reason': f'High price but dollar constraints not met - using shares'
                }
        
        else:
            # Medium price stocks: intelligent choice based on available cash
            if available_cash >= 500:
                # High cash: prefer shares for better execution
                if potential_shares >= MIN_SHARES and potential_shares <= MAX_SHARES:
                    return {
                        'type': 'shares',
                        'amount': round(potential_shares, 4),
                        'shares': round(potential_shares, 4),
                        'dollar_value': round(potential_shares * current_price, 2),
                        'reason': f'Medium price, high cash (${available_cash:.2f}) - using shares'
                    }
            
            # Default to dollar amount for medium prices or low cash
            dollar_amount = min(potential_dollar_amount, MAX_DOLLAR_AMOUNT)
            dollar_amount = max(dollar_amount, MIN_DOLLAR_AMOUNT)
            return {
                'type': 'dollar_amount',
                'amount': round(dollar_amount, 2),
                'shares': round(dollar_amount / current_price, 4),
                'dollar_value': round(dollar_amount, 2),
                'reason': f'Medium price stock (${current_price:.2f}) - using dollar amount'
            }
    
    def should_stop_loss(self, position: Dict[str, Any], current_price: float) -> bool:
        """Check if stop loss should be triggered"""
        if not position:
            return False
        
        entry_price = position.get('average_price', 0)
        if entry_price == 0:
            return False
        
        # Calculate loss percentage
        if position.get('side') == 'long':
            loss_percent = ((entry_price - current_price) / entry_price) * 100
        else:  # short position
            loss_percent = ((current_price - entry_price) / entry_price) * 100
        
        should_stop = loss_percent >= config.STOP_LOSS_PERCENT
        
        if should_stop:
            trading_logger.warning(
                f"Stop loss triggered for {position.get('symbol')}",
                entry_price=entry_price,
                current_price=current_price,
                loss_percent=loss_percent
            )
        
        return should_stop
    
    def should_take_profit(self, position: Dict[str, Any], current_price: float) -> bool:
        """Check if take profit should be triggered"""
        if not position:
            return False
        
        entry_price = position.get('average_price', 0)
        if entry_price == 0:
            return False
        
        # Calculate profit percentage
        if position.get('side') == 'long':
            profit_percent = ((current_price - entry_price) / entry_price) * 100
        else:  # short position
            profit_percent = ((entry_price - current_price) / entry_price) * 100
        
        should_take_profit = profit_percent >= config.TAKE_PROFIT_PERCENT
        
        if should_take_profit:
            trading_logger.info(
                f"Take profit triggered for {position.get('symbol')}",
                entry_price=entry_price,
                current_price=current_price,
                profit_percent=profit_percent
            )
        
        return should_take_profit
    
    def update_daily_loss(self, trade_result: Dict[str, Any]) -> None:
        """Update daily loss tracking"""
        if trade_result.get('realized_pl'):
            self.daily_loss += abs(trade_result['realized_pl'])
            self.daily_trades.append(trade_result)
            
            trading_logger.info(
                f"Daily loss updated",
                daily_loss=self.daily_loss,
                daily_limit=config.DAILY_LOSS_LIMIT
            )
    
    def update_drawdown(self, portfolio_value: float) -> None:
        """Update maximum drawdown tracking"""
        if portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = portfolio_value
        
        if self.peak_portfolio_value > 0:
            current_drawdown = ((self.peak_portfolio_value - portfolio_value) / self.peak_portfolio_value) * 100
            self.max_drawdown = max(self.max_drawdown, current_drawdown)
    
    def should_emergency_stop(self, portfolio_value: float) -> bool:
        """Check if emergency stop should be triggered"""
        self.update_drawdown(portfolio_value)
        
        should_stop = (
            self.daily_loss >= config.DAILY_LOSS_LIMIT or
            self.max_drawdown >= config.MAX_PORTFOLIO_DRAWDOWN
        )
        
        if should_stop:
            trading_logger.error(
                f"Emergency stop triggered",
                daily_loss=self.daily_loss,
                max_drawdown=self.max_drawdown,
                portfolio_value=portfolio_value
            )
        
        return should_stop
    
    def reset_daily_tracking(self) -> None:
        """Reset daily tracking (call at start of new day)"""
        self.daily_loss = 0.0
        self.daily_trades = []
        trading_logger.info("Daily risk tracking reset")
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get current risk summary"""
        return {
            'daily_loss': self.daily_loss,
            'daily_loss_limit': config.DAILY_LOSS_LIMIT,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_limit': config.MAX_PORTFOLIO_DRAWDOWN,
            'daily_trades_count': len(self.daily_trades),
            'peak_portfolio_value': self.peak_portfolio_value,
            'wash_sale_tracker': self.wash_sale_tracker
        }
    
    def check_wash_sale_restriction(self, symbol: str, side: str) -> bool:
        """Check if a trade would violate wash sale rules"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        if symbol not in self.wash_sale_tracker:
            return False  # No wash sale restriction
        
        wash_sale_info = self.wash_sale_tracker[symbol]
        wash_sale_date = wash_sale_info['date']
        wash_sale_side = wash_sale_info['side']
        
        # Check if we're within the wash sale window (30 days)
        days_since_wash_sale = (now - wash_sale_date).days
        
        if days_since_wash_sale < config.WASH_SALE_WINDOW_DAYS:
            # Check if we're trying to buy back a stock we sold at a loss
            if wash_sale_side == 'sell' and side == 'buy':
                trading_logger.warning(
                    f"Wash sale prevention: Cannot buy {symbol} within {config.WASH_SALE_WINDOW_DAYS} days of selling at a loss"
                )
                return True  # Wash sale restriction applies
        
        return False  # No wash sale restriction
    
    def record_wash_sale(self, symbol: str, side: str, loss_amount: float):
        """Record a wash sale for future prevention"""
        from datetime import datetime
        
        if loss_amount > 0:  # Only record if there was a loss
            self.wash_sale_tracker[symbol] = {
                'date': datetime.now(),
                'side': side,
                'loss_amount': loss_amount
            }
            trading_logger.warning(
                f"Wash sale recorded for {symbol}: {side} with loss ${loss_amount:.2f}"
            )
    
    def check_minimum_holding_time(self, symbol: str, buy_time: datetime) -> bool:
        """Check if minimum holding time has passed"""
        from datetime import datetime
        
        now = datetime.now()
        holding_time = now - buy_time
        min_holding_hours = config.MIN_HOLDING_TIME_HOURS
        
        if holding_time.total_seconds() < (min_holding_hours * 3600):
            remaining_time = (min_holding_hours * 3600) - holding_time.total_seconds()
            trading_logger.warning(
                f"Minimum holding time not met for {symbol}. "
                f"Need {remaining_time/3600:.1f} more hours"
            )
            return False
        
        return True
    
    def _get_current_positions(self) -> List[Dict[str, Any]]:
        """Get current positions from Alpaca client"""
        try:
            from utils.alpaca_client import alpaca_client
            positions = alpaca_client.get_positions()
            return positions
        except Exception as e:
            trading_logger.warning(f"Failed to get current positions: {e}")
            return []
    
    def validate_trade(self, symbol: str, side: str, amount: float, 
                      price: float, account_info: Dict[str, Any], position_type: str = 'dollar_amount') -> Dict[str, Any]:
        """Validate a trade before execution with intelligent position sizing"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check basic requirements
        if amount <= 0:
            validation['valid'] = False
            validation['errors'].append("Amount must be positive")
        
        if price <= 0:
            validation['valid'] = False
            validation['errors'].append("Price must be positive")
        
        # Check account status
        if account_info.get('account_blocked'):
            validation['valid'] = False
            validation['errors'].append("Account is blocked")
        
        if account_info.get('trading_blocked'):
            validation['valid'] = False
            validation['errors'].append("Trading is blocked")
        
        # Check available cash based on position type
        available_cash = account_info.get('cash', 0)
        if position_type == 'dollar_amount':
            # For dollar amounts, check if we have enough cash
            if amount > available_cash:
                validation['valid'] = False
                validation['errors'].append(f"Insufficient cash: need ${amount:.2f}, have ${available_cash:.2f}")
            
            # Check position limits for dollar amounts
            if amount > config.MAX_POSITION_SIZE:
                validation['warnings'].append(f"Position size ${amount:.2f} exceeds max ${config.MAX_POSITION_SIZE}")
        else:
            # For shares, check if we have enough cash for the shares
            required_cash = amount * price
            if required_cash > available_cash:
                validation['valid'] = False
                validation['errors'].append(f"Insufficient cash: need ${required_cash:.2f} for {amount} shares at ${price:.2f}, have ${available_cash:.2f}")
            
            # Check position limits for shares
            if required_cash > config.MAX_POSITION_SIZE:
                validation['warnings'].append(f"Position value ${required_cash:.2f} exceeds max ${config.MAX_POSITION_SIZE}")
        
        # Check daily loss limit
        if self.daily_loss >= config.DAILY_LOSS_LIMIT:
            validation['valid'] = False
            validation['errors'].append("Daily loss limit reached")
        
        if not validation['valid']:
            trading_logger.warning(
                f"Trade validation failed for {symbol}",
                errors=validation['errors'],
                warnings=validation['warnings']
            )
        
        return validation

# Global risk manager instance
risk_manager = RiskManager()
