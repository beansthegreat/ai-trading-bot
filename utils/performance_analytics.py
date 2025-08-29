import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from utils.logger import trading_logger

class PerformanceAnalytics:
    """Performance analytics and tracking system"""
    
    def __init__(self):
        self.trades = []
        self.daily_stats = defaultdict(lambda: {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'pnl': 0.0,
            'volume': 0.0
        })
        self.symbol_stats = defaultdict(lambda: {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_win': 0.0,
            'max_loss': 0.0,
            'last_trade': None
        })
        
    def record_trade(self, trade_data: Dict[str, Any]):
        """Record a completed trade for analytics"""
        trade = {
            'timestamp': datetime.now(),
            'symbol': trade_data['symbol'],
            'action': trade_data['action'],
            'quantity': trade_data.get('quantity', 0),
            'price': trade_data['price'],
            'pnl': trade_data.get('pnl', 0.0),
            'fees': trade_data.get('fees', 0.0),
            'signal_strength': trade_data.get('signal_strength', 0.0),
            'confirmation_passed': trade_data.get('confirmation_passed', False),
            'cooldown_active': trade_data.get('cooldown_active', False)
        }
        
        self.trades.append(trade)
        self._update_stats(trade)
        
        trading_logger.info(f"Trade recorded for analytics", 
                           symbol=trade['symbol'],
                           action=trade['action'],
                           pnl=trade['pnl'])
    
    def _update_stats(self, trade: Dict[str, Any]):
        """Update daily and symbol statistics"""
        date_key = trade['timestamp'].date()
        symbol = trade['symbol']
        
        # Update daily stats
        self.daily_stats[date_key]['trades'] += 1
        self.daily_stats[date_key]['pnl'] += trade['pnl']
        self.daily_stats[date_key]['volume'] += trade['quantity'] * trade['price']
        
        if trade['pnl'] > 0:
            self.daily_stats[date_key]['wins'] += 1
        else:
            self.daily_stats[date_key]['losses'] += 1
        
        # Update symbol stats
        self.symbol_stats[symbol]['trades'] += 1
        self.symbol_stats[symbol]['total_pnl'] += trade['pnl']
        self.symbol_stats[symbol]['last_trade'] = trade['timestamp']
        
        if trade['pnl'] > 0:
            self.symbol_stats[symbol]['wins'] += 1
            self.symbol_stats[symbol]['max_win'] = max(self.symbol_stats[symbol]['max_win'], trade['pnl'])
        else:
            self.symbol_stats[symbol]['losses'] += 1
            self.symbol_stats[symbol]['max_loss'] = min(self.symbol_stats[symbol]['max_loss'], trade['pnl'])
        
        # Recalculate derived metrics
        self._recalculate_symbol_metrics(symbol)
    
    def _recalculate_symbol_metrics(self, symbol: str):
        """Recalculate win rate, profit factor, and averages for a symbol"""
        stats = self.symbol_stats[symbol]
        
        if stats['trades'] > 0:
            stats['win_rate'] = stats['wins'] / stats['trades']
        
        # Calculate profit factor
        total_wins = sum(trade['pnl'] for trade in self.trades 
                        if trade['symbol'] == symbol and trade['pnl'] > 0)
        total_losses = abs(sum(trade['pnl'] for trade in self.trades 
                              if trade['symbol'] == symbol and trade['pnl'] < 0))
        
        if total_losses > 0:
            stats['profit_factor'] = total_wins / total_losses
        else:
            stats['profit_factor'] = float('inf') if total_wins > 0 else 0.0
        
        # Calculate averages
        wins = [trade['pnl'] for trade in self.trades 
                if trade['symbol'] == symbol and trade['pnl'] > 0]
        losses = [trade['pnl'] for trade in self.trades 
                 if trade['symbol'] == symbol and trade['pnl'] < 0]
        
        stats['avg_win'] = sum(wins) / len(wins) if wins else 0.0
        stats['avg_loss'] = sum(losses) / len(losses) if losses else 0.0
    
    def get_symbol_performance(self, symbol: str) -> Dict[str, Any]:
        """Get performance metrics for a specific symbol"""
        if symbol not in self.symbol_stats:
            return {}
        
        stats = self.symbol_stats[symbol].copy()
        
        # Add recent performance (last 7 days)
        recent_trades = [t for t in self.trades 
                        if t['symbol'] == symbol and 
                        t['timestamp'] > datetime.now() - timedelta(days=7)]
        
        stats['recent_trades'] = len(recent_trades)
        stats['recent_pnl'] = sum(t['pnl'] for t in recent_trades)
        stats['recent_win_rate'] = len([t for t in recent_trades if t['pnl'] > 0]) / len(recent_trades) if recent_trades else 0.0
        
        return stats
    
    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing symbols by profit factor"""
        performers = []
        
        for symbol, stats in self.symbol_stats.items():
            if stats['trades'] >= 3:  # Minimum 3 trades for meaningful stats
                performers.append({
                    'symbol': symbol,
                    'trades': stats['trades'],
                    'win_rate': stats['win_rate'],
                    'profit_factor': stats['profit_factor'],
                    'total_pnl': stats['total_pnl'],
                    'avg_win': stats['avg_win'],
                    'avg_loss': stats['avg_loss']
                })
        
        # Sort by profit factor (descending)
        performers.sort(key=lambda x: x['profit_factor'], reverse=True)
        return performers[:limit]
    
    def get_worst_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get worst performing symbols by profit factor"""
        performers = []
        
        for symbol, stats in self.symbol_stats.items():
            if stats['trades'] >= 3:  # Minimum 3 trades for meaningful stats
                performers.append({
                    'symbol': symbol,
                    'trades': stats['trades'],
                    'win_rate': stats['win_rate'],
                    'profit_factor': stats['profit_factor'],
                    'total_pnl': stats['total_pnl'],
                    'avg_win': stats['avg_win'],
                    'avg_loss': stats['avg_loss']
                })
        
        # Sort by profit factor (ascending)
        performers.sort(key=lambda x: x['profit_factor'])
        return performers[:limit]
    
    def get_daily_summary(self, date: datetime.date = None) -> Dict[str, Any]:
        """Get daily trading summary"""
        if date is None:
            date = datetime.now().date()
        
        if date not in self.daily_stats:
            return {}
        
        stats = self.daily_stats[date]
        
        return {
            'date': date,
            'trades': stats['trades'],
            'wins': stats['wins'],
            'losses': stats['losses'],
            'pnl': stats['pnl'],
            'volume': stats['volume'],
            'win_rate': stats['wins'] / stats['trades'] if stats['trades'] > 0 else 0.0
        }
    
    def get_overall_performance(self) -> Dict[str, Any]:
        """Get overall performance metrics"""
        if not self.trades:
            return {}
        
        total_trades = len(self.trades)
        total_wins = len([t for t in self.trades if t['pnl'] > 0])
        total_losses = len([t for t in self.trades if t['pnl'] < 0])
        total_pnl = sum(t['pnl'] for t in self.trades)
        
        wins = [t['pnl'] for t in self.trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in self.trades if t['pnl'] < 0]
        
        return {
            'total_trades': total_trades,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_pnl': total_pnl,
            'win_rate': total_wins / total_trades if total_trades > 0 else 0.0,
            'avg_win': sum(wins) / len(wins) if wins else 0.0,
            'avg_loss': sum(losses) / len(losses) if losses else 0.0,
            'max_win': max(wins) if wins else 0.0,
            'max_loss': min(losses) if losses else 0.0,
            'profit_factor': sum(wins) / abs(sum(losses)) if losses else float('inf'),
            'symbols_traded': len(self.symbol_stats)
        }
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        overall = self.get_overall_performance()
        top_performers = self.get_top_performers()
        worst_performers = self.get_worst_performers()
        
        report = []
        report.append("📊 PERFORMANCE ANALYTICS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Overall Performance
        report.append("🎯 OVERALL PERFORMANCE:")
        report.append(f"   Total Trades: {overall.get('total_trades', 0)}")
        report.append(f"   Win Rate: {overall.get('win_rate', 0):.1%}")
        report.append(f"   Total P&L: ${overall.get('total_pnl', 0):.2f}")
        report.append(f"   Profit Factor: {overall.get('profit_factor', 0):.2f}")
        report.append(f"   Avg Win: ${overall.get('avg_win', 0):.2f}")
        report.append(f"   Avg Loss: ${overall.get('avg_loss', 0):.2f}")
        report.append("")
        
        # Top Performers
        report.append("🏆 TOP PERFORMERS:")
        for i, perf in enumerate(top_performers, 1):
            report.append(f"   {i}. {perf['symbol']}: {perf['profit_factor']:.2f} PF, {perf['win_rate']:.1%} WR, ${perf['total_pnl']:.2f}")
        report.append("")
        
        # Worst Performers
        report.append("📉 WORST PERFORMERS:")
        for i, perf in enumerate(worst_performers, 1):
            report.append(f"   {i}. {perf['symbol']}: {perf['profit_factor']:.2f} PF, {perf['win_rate']:.1%} WR, ${perf['total_pnl']:.2f}")
        report.append("")
        
        return "\n".join(report)

# Global instance
performance_analytics = PerformanceAnalytics()
