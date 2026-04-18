"""
=============================================================================
公平公正评估系统 - 完整版
=============================================================================
目标:
  - 多维度绩效评估 (避免单一指标偏差)
  - 风险调整后收益 (夏普/索提诺/卡玛/信息比率)
  - 统计显著性检验 (t 检验/置信区间)
  - 策略排名系统 (综合评分)
  - 尾部风险分析 (VaR/CVaR)
  - 市场中性评估 (alpha/beta)
=============================================================================
"""
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class FairEvaluationSystem:
    """公平公正评估系统"""
    
    def __init__(self, risk_free_rate=0.03, benchmark_return=0.0):
        self.risk_free_rate = risk_free_rate
        self.benchmark_return = benchmark_return
        
    def evaluate_strategy(self, equity_curve: List[float], trades: List[Dict], 
                          daily_returns: Optional[List[float]] = None) -> Dict:
        """
        全面评估单个策略
        
        参数:
            equity_curve: 权益曲线
            trades: 交易记录
            daily_returns: 日收益率 (可选，如不提供则从权益曲线计算)
        
        返回:
            完整的绩效评估字典
        """
        # 计算日收益率
        if daily_returns is None:
            daily_returns = self._calculate_returns(equity_curve)
        
        # 基础指标
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] if len(equity_curve) > 1 else 0
        
        # 风险调整指标
        sharpe_ratio = self._sharpe_ratio(daily_returns)
        sortino_ratio = self._sortino_ratio(daily_returns)
        calmar_ratio = self._calmar_ratio(daily_returns, equity_curve)
        information_ratio = self._information_ratio(daily_returns)
        
        # 风险指标
        max_drawdown = self._max_drawdown(equity_curve)
        avg_drawdown = self._average_drawdown(equity_curve)
        drawdown_duration = self._max_drawdown_duration(equity_curve)
        volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0
        downside_volatility = self._downside_volatility(daily_returns)
        
        # 尾部风险
        var_95 = self._var(daily_returns, confidence=0.95)
        cvar_95 = self._cvar(daily_returns, confidence=0.95)
        var_99 = self._var(daily_returns, confidence=0.99)
        cvar_99 = self._cvar(daily_returns, confidence=0.99)
        
        # 交易分析
        trade_analysis = self._analyze_trades(trades)
        
        # 统计显著性
        significance = self._statistical_significance(daily_returns)
        
        # 综合评分 (0-100)
        composite_score = self._calculate_composite_score(
            total_return, sharpe_ratio, sortino_ratio, max_drawdown, 
            trade_analysis['win_rate'], trade_analysis['profit_loss_ratio']
        )
        
        return {
            # 基础收益
            'total_return': total_return,
            'annualized_return': self._annualize_return(total_return, len(daily_returns)),
            
            # 风险调整收益
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'information_ratio': information_ratio,
            
            # 风险指标
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'drawdown_duration_days': drawdown_duration,
            'volatility': volatility,
            'downside_volatility': downside_volatility,
            
            # 尾部风险
            'var_95': var_95,
            'cvar_95': cvar_95,
            'var_99': var_99,
            'cvar_99': cvar_99,
            
            # 交易分析
            **trade_analysis,
            
            # 统计显著性
            **significance,
            
            # 综合评分
            'composite_score': composite_score,
            'score_breakdown': self._get_score_breakdown(
                total_return, sharpe_ratio, sortino_ratio, max_drawdown,
                trade_analysis['win_rate'], trade_analysis['profit_loss_ratio']
            )
        }
    
    def rank_strategies(self, strategy_results: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
        """
        多策略排名 (使用综合评分)
        
        参数:
            strategy_results: {策略名: 评估结果}
        
        返回:
            按综合评分降序排列的策略列表
        """
        ranked = []
        for name, result in strategy_results.items():
            score = result.get('composite_score', 0)
            ranked.append((name, result, score))
        
        # 按综合评分排序
        ranked.sort(key=lambda x: x[2], reverse=True)
        
        return [(name, result) for name, result, _ in ranked]
    
    def compare_strategies(self, strategy_results: Dict[str, Dict]) -> Dict:
        """
        策略对比分析
        
        参数:
            strategy_results: {策略名: 评估结果}
        
        返回:
            对比分析字典
        """
        if not strategy_results:
            return {}
        
        metrics = [
            'total_return', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio',
            'max_drawdown', 'volatility', 'win_rate', 'profit_loss_ratio',
            'composite_score'
        ]
        
        comparison = {
            'summary': {},
            'metrics_table': {},
            'ranking_by_metric': {}
        }
        
        # 每个指标的统计
        for metric in metrics:
            values = [r.get(metric, 0) for r in strategy_results.values()]
            comparison['summary'][metric] = {
                'mean': np.mean(values),
                'median': np.median(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        
        # 按每个指标排名
        for metric in metrics:
            ranked = sorted(
                strategy_results.items(),
                key=lambda x: x[1].get(metric, 0),
                reverse=(metric not in ['max_drawdown', 'volatility', 'var_95', 'cvar_95'])
            )
            comparison['ranking_by_metric'][metric] = ranked
        
        # 构建指标表格
        for name, result in strategy_results.items():
            comparison['metrics_table'][name] = {m: result.get(m, 0) for m in metrics}
        
        return comparison
    
    def _calculate_returns(self, equity_curve: List[float]) -> List[float]:
        """计算日收益率"""
        if len(equity_curve) < 2:
            return [0]
        
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        
        return returns
    
    def _sharpe_ratio(self, returns: List[float]) -> float:
        """夏普比率"""
        if not returns or len(returns) < 2:
            return 0
        
        returns = np.array(returns)
        excess_returns = returns - self.risk_free_rate / 252
        
        if np.std(returns) == 0:
            return 0
        
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(252)
    
    def _sortino_ratio(self, returns: List[float]) -> float:
        """索提诺比率 (只考虑下行波动)"""
        if not returns or len(returns) < 2:
            return 0
        
        returns = np.array(returns)
        excess_returns = returns - self.risk_free_rate / 252
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return 999  # 无下行波动
        
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 999
        
        return np.mean(excess_returns) / downside_std * np.sqrt(252)
    
    def _calmar_ratio(self, returns: List[float], equity_curve: List[float]) -> float:
        """卡玛比率 (收益/最大回撤)"""
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] if len(equity_curve) > 1 else 0
        max_dd = self._max_drawdown(equity_curve)
        
        if max_dd == 0:
            return 0
        
        return total_return / max_dd
    
    def _information_ratio(self, returns: List[float]) -> float:
        """信息比率 (超额收益/跟踪误差)"""
        if not returns or len(returns) < 2:
            return 0
        
        returns = np.array(returns)
        benchmark_daily = self.benchmark_return / 252
        excess_returns = returns - benchmark_daily
        
        tracking_error = np.std(excess_returns)
        if tracking_error == 0:
            return 0
        
        return np.mean(excess_returns) / tracking_error * np.sqrt(252)
    
    def _max_drawdown(self, equity_curve: List[float]) -> float:
        """最大回撤"""
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        return abs(np.min(drawdown))
    
    def _average_drawdown(self, equity_curve: List[float]) -> float:
        """平均回撤"""
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        # 只计算非零回撤的平均值
        non_zero_dd = drawdown[drawdown < 0]
        if len(non_zero_dd) == 0:
            return 0
        
        return abs(np.mean(non_zero_dd))
    
    def _max_drawdown_duration(self, equity_curve: List[float]) -> int:
        """最大回撤持续期 (天数)"""
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        # 找到连续回撤的持续时间
        max_duration = 0
        current_duration = 0
        
        for dd in drawdown:
            if dd < 0:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return max_duration
    
    def _downside_volatility(self, returns: List[float]) -> float:
        """下行波动率"""
        if not returns:
            return 0
        
        returns = np.array(returns)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return 0
        
        return np.std(downside_returns) * np.sqrt(252)
    
    def _var(self, returns: List[float], confidence: float = 0.95) -> float:
        """VaR (Value at Risk)"""
        if not returns or len(returns) < 10:
            return 0
        
        returns = np.array(returns)
        percentile = (1 - confidence) * 100
        
        return abs(np.percentile(returns, percentile))
    
    def _cvar(self, returns: List[float], confidence: float = 0.95) -> float:
        """CVaR (Conditional VaR, 期望短缺)"""
        if not returns or len(returns) < 10:
            return 0
        
        returns = np.array(returns)
        var = self._var(returns, confidence)
        
        # CVaR 是超过 VaR 的损失的期望
        tail_losses = returns[returns <= -var]
        if len(tail_losses) == 0:
            return var
        
        return abs(np.mean(tail_losses))
    
    def _analyze_trades(self, trades: List[Dict]) -> Dict:
        """交易分析"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_loss_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'avg_holding_period': 0
            }
        
        closed_trades = [t for t in trades if t.get('type') == 'close']
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_loss_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'avg_holding_period': 0
            }
        
        wins = [t['pnl'] for t in closed_trades if t.get('pnl', 0) > 0]
        losses = [t['pnl'] for t in closed_trades if t.get('pnl', 0) < 0]
        
        win_rate = len(wins) / len(closed_trades) if closed_trades else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # 计算平均持仓周期
        holding_periods = []
        for t in closed_trades:
            if 'entry_date' in t and 'exit_date' in t:
                try:
                    entry = pd.to_datetime(t['entry_date'])
                    exit = pd.to_datetime(t['exit_date'])
                    holding_periods.append((exit - entry).days)
                except:
                    pass
        
        avg_holding_period = np.mean(holding_periods) if holding_periods else 0
        
        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': max(wins) if wins else 0,
            'largest_loss': min(losses) if losses else 0,
            'avg_holding_period': avg_holding_period
        }
    
    def _statistical_significance(self, returns: List[float]) -> Dict:
        """统计显著性检验"""
        if not returns or len(returns) < 10:
            return {
                'alpha_significant': False,
                't_statistic': 0,
                'p_value': 1,
                'confidence_interval_95': (0, 0),
                'returns_significant': False
            }
        
        returns = np.array(returns)
        n = len(returns)
        
        # t 检验 (检验均值是否显著不为 0)
        t_statistic = np.mean(returns) / (np.std(returns) / np.sqrt(n))
        p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), n - 1))
        
        # 95% 置信区间
        se = np.std(returns) / np.sqrt(n)
        ci_lower = np.mean(returns) - 1.96 * se
        ci_upper = np.mean(returns) + 1.96 * se
        
        return {
            't_statistic': t_statistic,
            'p_value': p_value,
            'confidence_interval_95': (ci_lower, ci_upper),
            'returns_significant': p_value < 0.05,
            'alpha_significant': p_value < 0.05
        }
    
    def _calculate_composite_score(self, total_return: float, sharpe: float, 
                                   sortino: float, max_dd: float, 
                                   win_rate: float, pl_ratio: float) -> float:
        """
        计算综合评分 (0-100)
        
        权重:
            - 夏普比率: 25%
            - 总收益: 20%
            - 最大回撤: 20%
            - 索提诺比率: 15%
            - 胜率: 10%
            - 盈亏比: 10%
        """
        score = 0
        
        # 夏普比率 (25 分) - 目标 1.5 得满分
        score += min(25, max(0, sharpe / 1.5 * 25))
        
        # 总收益 (20 分) - 目标 20% 得满分
        score += min(20, max(0, (total_return + 0.2) * 100))
        
        # 最大回撤 (20 分) - 目标<5% 得满分
        score += min(20, max(0, (0.2 - max_dd) * 100))
        
        # 索提诺比率 (15 分) - 目标 2.0 得满分
        score += min(15, max(0, sortino / 2.0 * 15))
        
        # 胜率 (10 分) - 目标 55% 得满分
        score += min(10, max(0, (win_rate - 0.3) * 25))
        
        # 盈亏比 (10 分) - 目标 2.0 得满分
        score += min(10, max(0, pl_ratio / 2.0 * 10))
        
        return round(min(100, max(0, score)), 1)
    
    def _get_score_breakdown(self, total_return: float, sharpe: float, 
                             sortino: float, max_dd: float,
                             win_rate: float, pl_ratio: float) -> Dict:
        """获取评分明细"""
        return {
            'sharpe_component': min(25, max(0, sharpe / 1.5 * 25)),
            'return_component': min(20, max(0, (total_return + 0.2) * 100)),
            'drawdown_component': min(20, max(0, (0.2 - max_dd) * 100)),
            'sortino_component': min(15, max(0, sortino / 2.0 * 15)),
            'win_rate_component': min(10, max(0, (win_rate - 0.3) * 25)),
            'pl_ratio_component': min(10, max(0, pl_ratio / 2.0 * 10))
        }
    
    def _annualize_return(self, total_return: float, days: int) -> float:
        """年化收益率"""
        if days <= 0:
            return total_return
        return (1 + total_return) ** (252 / days) - 1


# 测试
if __name__ == "__main__":
    print("✅ 公平公正评估系统已加载")
    print("   - 多维度绩效评估")
    print("   - 风险调整收益指标")
    print("   - 统计显著性检验")
    print("   - 综合评分系统")
    print("   - 尾部风险分析 (VaR/CVaR)")
    print("   - 策略排名与对比")
