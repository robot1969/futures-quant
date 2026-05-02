"""行情数据模块 - 增强版（带趋势和波动聚集）
=============================================================================
改进：
  - 趋势阶段模拟（3-5 个完整趋势周期）
  - 波动聚集性（GARCH 简化版）
  - 更接近真实市场的价格行为
=============================================================================
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class MarketDataFeeder:
    """市场数据获取"""
    
    def __init__(self, data_dir="data/"):
        self.data_dir = data_dir
        self.data = {}
        self.last_update = None
    
    def load_data(self):
        """加载所有市场数据"""
        print("📂 加载行情数据...")
        
        # 1. 尝试从本地 CSV 加载
        if os.path.exists(self.data_dir):
            for f in os.listdir(self.data_dir):
                if f.endswith(".csv"):
                    symbol = f.replace(".csv", "")
                    self.data[symbol] = pd.read_csv(
                        f"{self.data_dir}{f}", 
                        parse_dates=["date"], 
                        index_col="date"
                    )
                    print(f"   ✅ {symbol}: {len(self.data[symbol])} 条")
        
        # 2. 如果没有数据，生成模拟数据并保存
        if not self.data:
            print("⚠️ 无本地数据，生成模拟数据...")
            self._generate_mock_data()
            self._save_data()
        
        self.last_update = datetime.now()
        return self.data
    
    def _generate_mock_data(self, days=500):
        """生成带趋势和波动聚集的模拟 K 线数据（更接近真实市场）"""
        from config import CONTRACTS
        
        # 统一的基础价格（所有合约相同起点，保证公平）
        base_price = 5000
        
        for symbol, info in CONTRACTS.items():
            # 使用合约代码的 hash 作为种子，确保每次运行结果一致且公平
            seed = sum(ord(c) * (10**i) for i, c in enumerate(symbol))
            np.random.seed(seed)
            
            dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
            
            # ========== 改进的价格生成：趋势 + 波动聚集 ==========
            
            # 1. 生成趋势阶段（3-5 个完整周期）
            num_trends = np.random.randint(3, 6)
            trend_length = days // num_trends
            trend = np.zeros(days)
            
            for i in range(num_trends):
                start_idx = i * trend_length
                end_idx = min((i + 1) * trend_length, days)
                
                # 随机趋势方向
                trend_direction = np.random.choice([-1, 1])
                # 趋势强度（每个阶段 10%-30% 涨跌幅）
                trend_strength = np.random.uniform(0.1, 0.3)
                # 平滑过渡（S 曲线）
                t = np.linspace(0, 1, end_idx - start_idx)
                smooth_trend = (1 / (1 + np.exp(-10 * (t - 0.3)))) - (1 / (1 + np.exp(-10 * (t - 0.7))))
                trend[start_idx:end_idx] = trend_direction * trend_strength * base_price * smooth_trend
            
            trend = np.cumsum(trend)  # 累积趋势
            
            # 2. 波动聚集（GARCH 简化版：高波动后跟高波动）
            volatility_base = np.random.uniform(0.015, 0.025)
            volatility = np.zeros(days)
            volatility[0] = volatility_base
            
            for i in range(1, days):
                # 波动率持续性（80% 继承 + 20% 随机）
                volatility[i] = 0.8 * volatility[i-1] + 0.2 * np.random.uniform(0.01, 0.04)
            
            # 3. 随机游走（带波动聚集）
            returns = np.random.randn(days) * volatility
            random_walk = np.cumsum(returns) * base_price * 0.1
            
            # 4. 周期成分（正弦波，模拟市场波动）
            cycle_period = np.random.uniform(30, 90)
            cycle = np.sin(np.linspace(0, 2 * np.pi * days / cycle_period, days)) * base_price * 0.03
            
            # 合并所有成分
            prices = base_price + trend + random_walk + cycle
            
            # 确保价格为正（设置合理范围）
            prices = np.clip(prices, base_price * 0.5, base_price * 2.5)
            
            # 5. 生成 OHLC（带日内波动）
            daily_range = volatility * prices * np.random.uniform(1.5, 3.0, days)
            
            open_prices = prices + np.random.randn(days) * daily_range * 0.3
            close_prices = prices + np.random.randn(days) * daily_range * 0.3
            high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(days)) * daily_range * 0.5
            low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(days)) * daily_range * 0.5
            
            self.data[symbol] = pd.DataFrame({
                "open": open_prices,
                "high": high_prices,
                "low": low_prices,
                "close": close_prices,
                "volume": np.random.randint(50000, 200000, days).astype(float)
            }, index=dates)
            
            # 修正 high/low 关系
            self.data[symbol]["high"] = self.data[symbol][["open", "high", "close"]].max(axis=1)
            self.data[symbol]["low"] = self.data[symbol][["open", "low", "close"]].min(axis=1)
        
        # 打印统计信息
        print(f"   ✅ 生成了 {len(self.data)} 个合约的公平模拟数据")
        
        # 统计各类型数量
        categories = {}
        for symbol in self.data.keys():
            cat = CONTRACTS.get(symbol, {}).get("category", "其他")
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in categories.items():
            print(f"      {cat}: {count} 个")
    
    def _save_data(self):
        """保存数据到 CSV 文件"""
        os.makedirs(self.data_dir, exist_ok=True)
        for symbol, df in self.data.items():
            filepath = f"{self.data_dir}{symbol}.csv"
            # 确保 date 列作为普通列保存（不是索引）
            df_reset = df.reset_index()
            df_reset.rename(columns={'index': 'date'}, inplace=True)
            df_reset.to_csv(filepath, index=False)
        print(f"   💾 已保存 {len(self.data)} 个合约数据到 {self.data_dir}")
    
    def get_ohlcv(self, symbol, start_date=None, end_date=None):
        """获取 OHLCV 数据"""
        if symbol not in self.data:
            return None
        df = self.data[symbol].copy()
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        return df
    
    def get_latest(self, symbol, n=1):
        """获取最新 n 条"""
        if symbol in self.data:
            return self.data[symbol].iloc[-n:]
        return None
    
    def get_price_dict(self):
        """获取最新价格字典"""
        return {symbol: df["close"].iloc[-1] for symbol, df in self.data.items()}
    
    def get_prices_history(self, symbol, n=100):
        """获取历史价格序列"""
        if symbol in self.data:
            return self.data[symbol]["close"].iloc[-n:]
        return None
