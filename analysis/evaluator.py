"""绩效评估 - 完整版"""
import numpy as np
from datetime import datetime

class PerformanceEvaluator:
    """绩效评估"""
    
    def evaluate(self, portfolio):
        stats = portfolio.get_stats()
        equity = stats["current_equity"]
        initial = stats["initial_capital"]
        total_return = (equity - initial) / initial
        returns = self._calculate_returns(portfolio)
        sharpe_ratio = self._sharpe_ratio(returns)
        max_drawdown = self._max_drawdown(returns)
        win_rate = self._win_rate(portfolio.trades)
        profit_loss_ratio = self._profit_loss_ratio(portfolio.trades)
        volatility = np.std(returns) * np.sqrt(252) if returns else 0
        
        # 计算额外指标
        closed_trades = [t for t in portfolio.trades if t.get("type") == "close"]
        total_closed_pnl = sum(t.get("pnl", 0) for t in closed_trades)
        avg_trade_pnl = total_closed_pnl / len(closed_trades) if closed_trades else 0
        
        # 计算卡玛比率
        calmar_ratio = total_return / max_drawdown if max_drawdown > 0 else 0
        
        # 计算索提诺比率（只考虑下行波动）
        sortino_ratio = self._sortino_ratio(returns)
        
        # 计算连续盈利/亏损次数
        consecutive_wins, consecutive_losses = self._consecutive_trades(portfolio.trades)
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "profit_loss_ratio": profit_loss_ratio,
            "volatility": volatility,
            "total_trades": stats["total_trades"],
            "closed_trades": len(closed_trades),
            "equity": equity,
            "cash": stats["cash"],
            "open_positions": stats["open_positions"],
            "closed_pnl": total_closed_pnl,
            "avg_trade_pnl": avg_trade_pnl,
            "calmar_ratio": calmar_ratio,
            "sortino_ratio": sortino_ratio,
            "consecutive_wins": consecutive_wins,
            "consecutive_losses": consecutive_losses,
            "total_profit": sum(t.get("pnl", 0) for t in closed_trades if t.get("pnl", 0) > 0),
            "total_loss": abs(sum(t.get("pnl", 0) for t in closed_trades if t.get("pnl", 0) < 0))
        }
    
    def _calculate_returns(self, portfolio):
        equity_curve = portfolio.equity_curve
        if len(equity_curve) < 2:
            return [0]
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        return returns
    
    def _sharpe_ratio(self, returns, risk_free_rate=0.03):
        if not returns or len(returns) < 2:
            return 0
        returns = np.array(returns)
        excess_returns = returns - risk_free_rate / 252
        if np.std(returns) == 0:
            return 0
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(252)
    
    def _max_drawdown(self, returns):
        if not returns:
            return 0
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return abs(np.min(drawdown)) if len(drawdown) > 0 else 0
    
    def _win_rate(self, trades):
        if not trades:
            return 0
        closed_trades = [t for t in trades if t.get("type") == "close"]
        if not closed_trades:
            return 0
        winning_trades = [t for t in closed_trades if t.get("pnl", 0) > 0]
        return len(winning_trades) / len(closed_trades)
    
    def _profit_loss_ratio(self, trades):
        closed_trades = [t for t in trades if t.get("type") == "close"]
        if not closed_trades:
            return 0
        wins = [t["pnl"] for t in closed_trades if t.get("pnl", 0) > 0]
        losses = [abs(t["pnl"]) for t in closed_trades if t.get("pnl", 0) < 0]
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        return avg_win / avg_loss if avg_loss > 0 else 0
    
    def _sortino_ratio(self, returns, risk_free_rate=0.03):
        """索提诺比率（只考虑下行波动）"""
        if not returns or len(returns) < 2:
            return 0
        returns = np.array(returns)
        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 999  # 无下行波动
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 999
        return np.mean(excess_returns) / downside_std * np.sqrt(252)
    
    def _consecutive_trades(self, trades):
        """计算连续盈利/亏损次数"""
        closed_trades = [t for t in trades if t.get("type") == "close"]
        if not closed_trades:
            return 0, 0
        
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in closed_trades:
            pnl = trade.get("pnl", 0)
            if pnl > 0:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
        
        return max_consecutive_wins, max_consecutive_losses
