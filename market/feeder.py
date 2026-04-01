"""行情数据模块 - Day 2 优化版"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import requests

class MarketDataFeeder:
    """市场数据获取"""
    
    def __init__(self, data_dir="data/"):
        self.data_dir = data_dir
        self.data = {}
        self.last_update = None
    
    def load_data(self):
        """加载所有市场数据"""
        print("📂 加载行情数据...")
        
        # 1. 尝试从本地CSV加载
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
            self._save_data()  # 保存生成的数据到 CSV
        
        self.last_update = datetime.now()
        return self.data
    
    def _generate_mock_data(self, days=500):
        """生成公平公正的模拟K线数据"""
        from config import CONTRACTS
        
        # 统一的基础价格（所有合约相同起点，保证公平）
        base_price = 5000
        
        for symbol, info in CONTRACTS.items():
            # 使用合约代码的hash作为种子，确保每次运行结果一致且公平
            seed = sum(ord(c) * (10**i) for i, c in enumerate(symbol))
            np.random.seed(seed)
            
            dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
            
            # ========== 公平的价格生成 ==========
            
            # 1. 随机方向（50%上涨，50%下跌）
            direction = np.random.choice([-1, 1])
            
            # 2. 趋势成分（较小且随机）
            trend = np.cumsum(np.random.randn(days) * 0.005 * direction)
            
            # 3. 周期成分（正弦波，模拟市场波动）
            cycle_period = np.random.uniform(30, 90)  # 随机周期
            cycle = np.sin(np.linspace(0, 2 * np.pi * days / cycle_period, days)) * base_price * 0.05
            
            # 4. 波动率（统一范围，避免某些合约波动更大）
            volatility = np.random.uniform(0.01, 0.025)  # 1%-2.5%固定波动率
            
            # 5. 随机游走
            random_walk = np.cumsum(np.random.randn(days) * volatility * base_price * 0.3)
            
            # 合并所有成分（公平组合）
            prices = base_price + trend + cycle + random_walk
            
            # 确保价格为正（设置合理范围）
            prices = np.clip(prices, base_price * 0.3, base_price * 3)
            
            # 6. 生成OHLC（公平的价格分布）
            daily_range = np.abs(np.random.randn(days)) * volatility * base_price + base_price * 0.005
            
            self.data[symbol] = pd.DataFrame({
                "open": prices + np.random.randn(days) * volatility * base_price * 0.1,
                "high": prices + daily_range * np.random.rand(days),
                "low": prices - daily_range * np.random.rand(days),
                "close": prices,
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
        """获取OHLCV数据"""
        if symbol not in self.data:
            return None
        df = self.data[symbol].copy()
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        return df
    
    def get_latest(self, symbol, n=1):
        """获取最新n条"""
        if symbol in self.data:
            return self.data[symbol].tail(n)
        return None
    
    def get_close_series(self, symbol):
        """获取收盘价序列"""
        if symbol in self.data:
            return self.data[symbol]["close"]
        return None
    
    def get_multiple_symbols(self, symbols):
        """获取多个合约数据"""
        result = {}
        for symbol in symbols:
            if symbol in self.data:
                result[symbol] = self.data[symbol]
        return result
    
    def get_all_symbols(self):
        """获取所有可用合约"""
        return list(self.data.keys())
    
    def get_price_dict(self):
        """获取最新价格字典"""
        return {symbol: df["close"].iloc[-1] for symbol, df in self.data.items() if len(df) > 0}
