import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config import config
from utils.logger import trading_logger
import time
from collections import deque

class AlpacaClient:
    """Python Alpaca trading client"""
    
    def __init__(self):
        """Initialize Alpaca client with rate limiting"""
        self.api = tradeapi.REST(
            key_id=config.ALPACA_API_KEY,
            secret_key=config.ALPACA_SECRET_KEY,
            base_url=config.ALPACA_BASE_URL,
            api_version='v2'
        )
        
        # Rate limiting - Official Alpaca limit: 200 requests/minute
        self.api_calls_per_minute = deque(maxlen=config.MAX_API_CALLS_PER_MINUTE)
        self.last_api_call = 0
        
        # Log connection info
        trading_logger.info(
            "Alpaca client initialized with rate limiting",
            base_url=config.ALPACA_BASE_URL,
            key_fingerprint=f"{config.ALPACA_API_KEY[:4]}...{config.ALPACA_API_KEY[-4:]}",
            max_calls_per_minute=config.MAX_API_CALLS_PER_MINUTE,
            official_limit="200 requests/minute"
        )
    
    def _rate_limit_check(self):
        """Enforce API rate limits (200 requests/minute per official docs)"""
        now = time.time()
        
        # Remove calls older than 1 minute
        while self.api_calls_per_minute and self.api_calls_per_minute[0] <= now - 60:
            self.api_calls_per_minute.popleft()
        
        # If we're at the limit, wait until we can make another call
        if len(self.api_calls_per_minute) >= config.MAX_API_CALLS_PER_MINUTE:
            sleep_time = 60 - (now - self.api_calls_per_minute[0])
            if sleep_time > 0:
                trading_logger.warning(f"API rate limit approaching. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
        
        # Record this API call
        self.api_calls_per_minute.append(now)
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            self._rate_limit_check()  # Enforce rate limits
            account = self.api.get_account()
            trading_logger.debug("Account info retrieved", account_id=account.id)
            
            return {
                'id': account.id,
                'status': account.status,
                'currency': account.currency,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'transfers_blocked': account.transfers_blocked,
                'account_blocked': account.account_blocked,
                'created_at': account.created_at,
                'daytrade_count': account.daytrade_count
            }
        except Exception as e:
            trading_logger.error(f"Failed to get account info: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all positions"""
        try:
            self._rate_limit_check()  # Enforce rate limits
            positions = self.api.list_positions()
            trading_logger.debug(f"Retrieved {len(positions)} positions")
            
            return [{
                'symbol': pos.symbol,
                'quantity': float(pos.qty),
                'average_price': float(pos.avg_entry_price),
                'market_value': float(pos.market_value),
                'unrealized_pl': float(pos.unrealized_pl),
                'unrealized_plpc': float(pos.unrealized_plpc),
                'side': pos.side
            } for pos in positions]
        except Exception as e:
            trading_logger.error(f"Failed to get positions: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get position for specific symbol"""
        try:
            self._rate_limit_check()  # Enforce rate limits
            position = self.api.get_position(symbol)
            return {
                'symbol': position.symbol,
                'quantity': float(position.qty),
                'average_price': float(position.avg_entry_price),
                'market_value': float(position.market_value),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc),
                'side': position.side
            }
        except Exception as e:
            if "position does not exist" in str(e).lower():
                return None
            trading_logger.error(f"Failed to get position for {symbol}: {e}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Place a market order with support for fractional shares"""
        try:
            self._rate_limit_check()  # Enforce rate limits
            
            # Ensure quantity is a float for fractional shares
            quantity = float(quantity)
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=quantity,
                side=side,
                type='market',
                time_in_force='day'
            )
            
            trading_logger.trade(
                action=side,
                symbol=symbol,
                quantity=quantity,
                order_id=order.id
            )
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.type,
                'quantity': float(order.qty),
                'status': order.status,
                'created_at': order.created_at
            }
        except Exception as e:
            trading_logger.error(f"Failed to place market order: {e}")
            raise
    
    def place_dollar_amount_order(self, symbol: str, side: str, dollar_amount: float) -> Dict[str, Any]:
        """Place a market order for a specific dollar amount"""
        try:
            self._rate_limit_check()  # Enforce rate limits
            
            # Ensure dollar amount is a float
            dollar_amount = float(dollar_amount)
            
            order = self.api.submit_order(
                symbol=symbol,
                notional=dollar_amount,  # Use notional (dollar amount) instead of qty
                side=side,
                type='market',
                time_in_force='day'
            )
            
            trading_logger.trade(
                action=side,
                symbol=symbol,
                dollar_amount=dollar_amount,
                order_id=order.id
            )
            
            # Get the filled quantity if available
            filled_qty = None
            if hasattr(order, 'filled_qty') and order.filled_qty:
                filled_qty = float(order.filled_qty)
            elif hasattr(order, 'qty') and order.qty:
                filled_qty = float(order.qty)
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.type,
                'dollar_amount': dollar_amount,
                'quantity': filled_qty,
                'status': order.status,
                'created_at': order.created_at
            }
        except Exception as e:
            trading_logger.error(f"Failed to place dollar amount order: {e}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """Place a limit order with support for fractional shares"""
        try:
            # Ensure quantity is a float for fractional shares
            quantity = float(quantity)
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=quantity,
                side=side,
                type='limit',
                time_in_force='day',
                limit_price=price
            )
            
            trading_logger.trade(
                action=side,
                symbol=symbol,
                quantity=quantity,
                price=price,
                order_id=order.id
            )
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.type,
                'quantity': float(order.qty),
                'price': price,
                'status': order.status,
                'created_at': order.created_at
            }
        except Exception as e:
            trading_logger.error(f"Failed to place limit order: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> None:
        """Cancel an order"""
        try:
            self.api.cancel_order(order_id)
            trading_logger.info(f"Order cancelled", order_id=order_id)
        except Exception as e:
            trading_logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order by ID"""
        try:
            order = self.api.get_order(order_id)
            
            # Handle None values safely
            qty = order.qty if order.qty is not None else 0.0
            limit_price = order.limit_price if order.limit_price is not None else None
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.type,
                'quantity': float(qty),
                'price': float(limit_price) if limit_price else None,
                'status': order.status,
                'filled_at': order.filled_at,
                'created_at': order.created_at
            }
        except Exception as e:
            trading_logger.error(f"Failed to get order {order_id}: {e}")
            raise
    
    def get_orders(self, status: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Get all orders"""
        try:
            params = {}
            if status:
                params['status'] = status
            if limit:
                params['limit'] = limit
            
            orders = self.api.list_orders(**params)
            result = []
            for order in orders:
                try:
                    # Handle None values safely
                    qty = order.qty if order.qty is not None else 0.0
                    limit_price = order.limit_price if order.limit_price is not None else None
                    
                    result.append({
                        'id': order.id,
                        'symbol': order.symbol,
                        'side': order.side,
                        'type': order.type,
                        'quantity': float(qty),
                        'price': float(limit_price) if limit_price else None,
                        'status': order.status,
                        'filled_at': order.filled_at,
                        'created_at': order.created_at
                    })
                except Exception as order_error:
                    trading_logger.warning(f"Error processing order {order.id}: {order_error}")
                    continue
            
            return result
        except Exception as e:
            trading_logger.error(f"Failed to get orders: {e}")
            raise
    
    def get_historical_data(self, symbol: str, timeframe: str = '1D', 
                           start_date: str = None, end_date: str = None, 
                           limit: int = None) -> pd.DataFrame:
        """Get historical market data using yfinance as fallback"""
        try:
            self._rate_limit_check()  # Enforce rate limits
            
            # Try Alpaca first
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            try:
                bars = self.api.get_bars(
                    symbol,
                    timeframe=timeframe,
                    start=start_date,
                    end=end_date,
                    limit=limit
                )
                
                df = bars.df
                df.reset_index(inplace=True)
                df.rename(columns={
                    'timestamp': 'datetime',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume'
                }, inplace=True)
                
                trading_logger.debug(f"Retrieved {len(df)} bars from Alpaca for {symbol}")
                return df
                
            except Exception as alpaca_error:
                if "subscription does not permit" in str(alpaca_error).lower():
                    # Fallback to yfinance
                    trading_logger.info(f"Using yfinance fallback for {symbol} data")
                    import yfinance as yf
                    
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(period="30d", interval="1d")
                    df.reset_index(inplace=True)
                    df.rename(columns={
                        'Date': 'datetime',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    }, inplace=True)
                    
                    trading_logger.debug(f"Retrieved {len(df)} bars from yfinance for {symbol}")
                    return df
                else:
                    raise alpaca_error
                    
        except Exception as e:
            trading_logger.error(f"Failed to get historical data for {symbol}: {e}")
            raise
    
    def is_market_open(self) -> bool:
        """Check if market is open"""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            trading_logger.error(f"Failed to check market status: {e}")
            raise
    
    def close_all_positions(self) -> None:
        """Close all positions with fractional shares support"""
        try:
            positions = self.get_positions()
            for position in positions:
                if position['quantity'] != 0:
                    side = 'sell' if position['quantity'] > 0 else 'buy'
                    quantity = abs(float(position['quantity']))
                    
                    self.place_market_order(
                        position['symbol'],
                        side,
                        quantity
                    )
                    
                    trading_logger.info(f"Position closed", 
                                      symbol=position['symbol'],
                                      side=side,
                                      quantity=quantity)
        except Exception as e:
            trading_logger.error(f"Failed to close all positions: {e}")
            raise
    
    def close_position(self, symbol: str) -> None:
        """Close position for specific symbol with fractional shares support"""
        try:
            position = self.get_position(symbol)
            if position and position['quantity'] != 0:
                side = 'sell' if position['quantity'] > 0 else 'buy'
                quantity = abs(float(position['quantity']))
                
                self.place_market_order(symbol, side, quantity)
                trading_logger.info(f"Position closed", 
                                  symbol=symbol,
                                  side=side,
                                  quantity=quantity)
        except Exception as e:
            trading_logger.error(f"Failed to close position for {symbol}: {e}")
            raise

# Global client instance
alpaca_client = AlpacaClient()
