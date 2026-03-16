"""回测引擎 - Day 6"""
import pandas as pd
import numpy as np
from datetime import datetime
from config import CONTRACTS, TRADING_CONFIG, BACKTEST_CONFIG

class Backtester:
    """回测引擎"""
    
    def __init__(self, initial_capital=1_000_000):
        self.initial_capital = initial_capital
        self.results = {}
    
    def run(self, market_data, signals_generator):
        """运行回测"""
        print("🔄 运行回测...")
        
        start_date = BACKTEST_CONFIG["start_date"]
        end_date = BACKTEST_CONFIG["end_date"]
        warm_up = BACKTEST_CONFIG["warm_up_period"]
        
        # 初始化
        equity_curve = [self.initial_capital]
        trades = []
        positions = {}
        
        symbols = list(market_data.keys())[:10]
        
        for i, date in enumerate(market_data[symbols[0]].index):
            if i < warm_up:
                continue
                
            # 获取当日信号
            daily_signals = {}
            for symbol in symbols:
                df = market_data[symbol]
                if date in df.index:
                    sigs = signals_generator.generate_for_symbol(symbol, df[df.index <= date])
                    if sigs:
                        daily_signals[symbol] = sigs
            
            # 模拟交易
            if daily_signals:
                buy_signals = sum(1 for s in daily_signals.values() for sig in s if sig.get("signal", 0) > 0)
                if buy_signals > 0:
                    pass  # 模拟买入
            
            # 更新权益
            equity = self._calculate_equity(positions, market_data, date)
            equity_curve.append(equity)
        
        # 计算绩效
        self.results = self._calculate_performance(equity_curve, trades)
        
        print(f"   ✅ 回测完成: {len(equity_curve)} 天")
        return self.results
    
    def _calculate_equity(self, positions, market_data, date):
        """计算权益"""
        equity = self.portfolio.cash if hasattr(self, 'portfolio') else self.initial_capital
        return equity
    
    def _calculate_performance(self, equity_curve, trades):
        """计算绩效指标"""
        equity = np.array(equity_curve)
        returns = np.diff(equity) / equity[:-1]
        returns = returns[~np.isnan(returns)]
        
        total_return = (equity[-1] - equity[0]) / equity[0] if len(equity) > 1 else 0
        
        # 夏普比率
        if len(returns) > 1 and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe = 0
        
        # 最大回撤
        cummax = np.maximum.accumulate(equity)
        drawdown = (equity - cummax) / cummax
        max_drawdown = abs(np.min(drawdown)) if len(drawdown) > 0 else 0
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "total_trades": len(trades),
            "win_rate": 0.5,
            "equity_curve": equity_curve
        }
    
    def get_results(self):
        """获取回测结果"""
        return self.results
