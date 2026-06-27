"""
Market Data Engine - Multi-Scale Synthetic Generator (Optimized)
=============================================================================
Generates high-fidelity synthetic market data using a top-down approach:
1. Base Generation (1-minute scale)
2. Temporal Aggregation (Resampling to 15m, 1h, 1d, etc.)
3. Parquet Storage (Efficient I/O)
=============================================================================
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from config import CONTRACTS

# Supported Timeframes for the simulation
TIMEFRAMES = {
    "1m": "1min",
    "15m": "15min",
    "1h": "h",
    "4h": "4h",
    "1d": "D",
    "1w": "W",
    "1M": "ME"
}

class MarketGenerator:
    """Mathematical engines for high-frequency price generation with Regime Switching"""
    
    @staticmethod
    def generate_gbm(start_price, mu, sigma, steps):
        """Geometric Brownian Motion with Drift"""
        returns = np.random.normal(loc=mu, scale=sigma, size=steps)
        price_path = start_price * np.exp(np.cumsum(returns))
        return price_path

    @staticmethod
    def generate_ou(start_price, theta, mu, sigma, steps):
        """Ornstein-Uhlenbeck: Mean Reverting"""
        dt = 1 
        prices = np.zeros(steps)
        prices[0] = start_price
        for i in range(1, steps):
            drift = theta * (mu - prices[i-1]) * dt
            diffusion = sigma * np.sqrt(dt) * np.random.randn()
            prices[i] = prices[i-1] + drift + diffusion
        return np.clip(prices, start_price * 0.1, start_price * 10)

    @staticmethod
    def generate_regime_switching(start_price, steps):
        """
        Enhanced Generator: Switches between Trend, Mean-Rev, and Chaos
        Simulates market phases for better strategy validation.
        """
        prices = [start_price]
        current_price = start_price
        
        # Define regimes: (type, duration_range, volatility_scale)
        regimes = [
            ('trend', (100, 1000), 0.001), 
            ('mean_rev', (50, 500), 0.0005),
            ('chaos', (20, 200), 0.005)
        ]
        
        while len(prices) < steps:
            regime_type, dur_range, vol = np.random.choice(regimes)
            duration = np.random.randint(*dur_range)
            
            if regime_type == 'trend':
                drift = np.random.choice([-0.0001, 0.0001])
                for _ in range(duration):
                    current_price *= np.exp(np.random.normal(drift, vol))
                    prices.append(current_price)
            elif regime_type == 'mean_rev':
                target = current_price * (1 + np.random.uniform(-0.02, 0.02))
                theta = np.random.uniform(0.01, 0.05)
                for _ in range(duration):
                    current_price += theta * (target - current_price) + np.random.normal(0, vol * current_price)
                    prices.append(current_price)
            else: # chaos
                for _ in range(duration):
                    jump = 0
                    if np.random.random() < 0.01: jump = np.random.normal(0, 0.01)
                    current_price *= np.exp(np.random.normal(0, vol + jump))
                    prices.append(current_price)
        
        return np.array(prices[:steps])

    @staticmethod
    def generate_jump_diffusion(start_price, mu, sigma, lambda_j, jump_mu, jump_sigma, steps):
        """Merton Jump-Diffusion: High-freq base + Poisson Jumps"""
        prices = MarketGenerator.generate_gbm(start_price, mu, sigma, steps)
        for i in range(1, steps):
            if np.random.random() < lambda_j:
                jump_size = np.random.normal(jump_mu, jump_sigma)
                prices[i:] *= (1 + jump_size)
        return prices

class MarketDataFeeder:
    """Optimized Market Data Provider with Global Memory Caching"""
    
    def __init__(self, base_dir="data/simulated_history/"):
        self.base_dir = base_dir
        # Global Cache: { timeframe: { symbol: df } }
        self._cache = {} 
        self.last_update = None

    def load_data(self, timeframe="1d"):
        """
        Loads data for a specific timeframe into memory cache.
        Prevents repeated disk I/O across strategy iterations.
        """
        if timeframe in self._cache:
            return self._cache[timeframe]

        print(f"📂 [Cache Miss] Loading Market Data for {timeframe}...")
        tf_dir = os.path.join(self.base_dir, timeframe)
        
        if os.path.exists(tf_dir) and os.listdir(tf_dir):
            tf_data = {}
            for f in os.listdir(tf_dir):
                if f.endswith(".parquet"):
                    symbol = f.replace(".parquet", "")
                    tf_data[symbol] = pd.read_parquet(os.path.join(tf_dir, f))
            
            self._cache[timeframe] = tf_data
            print(f"   ✅ Cached {len(tf_data)} contracts for {timeframe}.")
        else:
            print(f"   ⚠️ Data for {timeframe} not found. Generating...")
            self._generate_full_market_library()
            return self.load_data(timeframe)
        
        self.last_update = datetime.now()
        return self._cache[timeframe]

    def _generate_full_market_library(self, days=365):
        """
        Enhanced Top-Down Generation Pipeline.
        Uses Regime Switching to create a more adversarial market.
        """
        print(f"🧪 Generating Regime-Switching Adversarial Market ({days} days)...")
        np.random.seed(42)
        base_steps = 24 * 60 * days 
        
        for symbol, info in CONTRACTS.items():
            symbol_hash = sum(ord(c) for c in symbol)
            start_price = 5000.0
            
            # USE ENHANCED REGIME GENERATOR
            prices = MarketGenerator.generate_regime_switching(start_price, base_steps)

            dates = pd.date_range(end=datetime.now(), periods=base_steps, freq="1min")
            df_1m = self._create_ohlcv_from_path(prices, dates)
            self._resample_and_save(symbol, df_1m)
            
        print(f"   ✅ Full history generated for {len(CONTRACTS)} contracts.")

    def _create_ohlcv_from_path(self, price_path, dates):
        closes = price_path
        noise = np.random.normal(0, closes * 0.0002, len(closes))
        opens = closes + noise
        highs = np.maximum(opens, closes) + np.abs(np.random.normal(0, closes * 0.0005, len(closes)))
        lows = np.minimum(opens, closes) - np.abs(np.random.normal(0, closes * 0.0005, len(closes)))
        volumes = np.random.randint(10, 1000, len(closes)).astype(float)
        
        return pd.DataFrame({
            "open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes
        }, index=dates)

    def _resample_and_save(self, symbol, df_1m):
        for tf_label, tf_offset in TIMEFRAMES.items():
            resampled = df_1m.resample(tf_offset).agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
            }).dropna()
            
            tf_dir = os.path.join(self.base_dir, tf_label)
            os.makedirs(tf_dir, exist_ok=True)
            resampled.to_parquet(os.path.join(tf_dir, f"{symbol}.parquet"))

    def get_ohlcv(self, symbol, timeframe="1d", start_date=None, end_date=None):
        """Fast getter using memory cache."""
        data = self.load_data(timeframe)
        if symbol not in data: return None
        
        # Avoid deep copy unless slicing is needed
        df = data[symbol]
        if start_date or end_date:
            df = df.copy()
            if start_date: df = df[df.index >= start_date]
            if end_date: df = df[df.index <= end_date]
        return df

    def get_latest(self, symbol, timeframe="1d", n=1):
        df = self.get_ohlcv(symbol, timeframe)
        return df.iloc[-n:] if df is not None else None

    def get_all_symbols(self):
        return list(CONTRACTS.keys())
