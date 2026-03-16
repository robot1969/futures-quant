"""指标计算引擎 - 100+ 指标全周期版本"""
import pandas as pd
import numpy as np
import pandas_ta as ta

class IndicatorEngine:
    """技术指标计算引擎 - 100+ 指标"""
    
    def __init__(self):
        self.indicators_count = 0
    
    def calculate_all(self, df):
        """计算所有指标"""
        result = df.copy()
        self.indicators_count = 0
        
        # === 移动平均线 (20个) ===
        for length in [3, 5, 8, 10, 12, 15, 20, 30, 60, 90, 120, 150, 180, 200, 250]:
            result[f"MA{length}"] = ta.sma(df["close"], length=length)
            result[f"EMA{length}"] = ta.ema(df["close"], length=length)
            self.indicators_count += 2
            # 添加加权移动平均
            result[f"WMA{length}"] = ta.wma(df["close"], length=length)
            self.indicators_count += 1
        
        # === RSI (6个) ===
        for length in [6, 7, 9, 14, 21, 28]:
            result[f"RSI_{length}"] = ta.rsi(df["close"], length=length)
            self.indicators_count += 1
        
        # === MACD (9个) ===
        for fast, slow, sig in [(12, 26, 9), (8, 17, 9), (5, 35, 5), (6, 19, 6), (4, 12, 4)]:
            macd = ta.macd(df["close"], fast=fast, slow=slow, signal=sig)
            if macd is not None:
                result = pd.concat([result, macd], axis=1)
                self.indicators_count += 3
        
        # === 布林带 (12个) ===
        for period in [10, 15, 20, 25, 30]:
            for std in [1.5, 2.0, 2.5]:
                bbands = ta.bbands(df["close"], length=period, std=std)
                if bbands is not None:
                    result = pd.concat([result, bbands], axis=1)
                    self.indicators_count += 3
        
        # === ATR (6个) ===
        for period in [7, 10, 14, 20, 28]:
            result[f"ATR_{period}"] = ta.atr(df["high"], df["low"], df["close"], length=period)
            self.indicators_count += 1
        
        # === ADX (4个) ===
        for period in [7, 14, 20, 28]:
            adx = ta.adx(df["high"], df["low"], df["close"], length=period)
            if adx is not None:
                result = pd.concat([result, adx], axis=1)
                self.indicators_count += 1
        
        # === KDJ (4个) ===
        for k, d in [(9, 3), (14, 3), (21, 5), (28, 7)]:
            stoch = ta.stoch(df["high"], df["low"], df["close"], k=k, d=d)
            if stoch is not None:
                result = pd.concat([result, stoch], axis=1)
                self.indicators_count += 2
        
        # === CCI (4个) ===
        for period in [10, 14, 20, 28]:
            result[f"CCI_{period}"] = ta.cci(df["high"], df["low"], df["close"], length=period)
            self.indicators_count += 1
        
        # === 威廉指标 (3个) ===
        for period in [10, 14, 28]:
            result[f"WILLR_{period}"] = ta.willr(df["high"], df["low"], df["close"], length=period)
            self.indicators_count += 1
        
        # === 动量指标 (10个) ===
        for period in [5, 8, 10, 12, 15, 20]:
            result[f"MOM_{period}"] = ta.mom(df["close"], length=period)
            result[f"ROC_{period}"] = ta.roc(df["close"], length=period)
            self.indicators_count += 2
        
        # === MFI (3个) ===
        for period in [10, 14, 28]:
            result[f"MFI_{period}"] = ta.mfi(df["high"], df["low"], df["close"], df["volume"], length=period)
            self.indicators_count += 1
        
        # === 成交量指标 (10个) ===
        for period in [5, 10, 20]:
            result[f"VOL_MA{period}"] = ta.sma(df["volume"], length=period)
            result[f"OBV_MA{period}"] = ta.obv(df["close"], df["volume"]).rolling(period).mean()
            self.indicators_count += 2
        result["VOL_RATIO"] = df["volume"] / df["volume"].rolling(20).mean()
        self.indicators_count += 1
        
        # === 成交量加权价格 (3个) ===
        result["VWAP"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
        self.indicators_count += 1
        
        # === 最高最低 (8个) ===
        for period in [10, 20, 30, 60]:
            result[f"HIGH_{period}"] = df["high"].rolling(period).max()
            result[f"LOW_{period}"] = df["low"].rolling(period).min()
            self.indicators_count += 2
        
        # === 波动率 (4个) ===
        for period in [10, 20, 30, 60]:
            result[f"STDDEV_{period}"] = df["close"].rolling(period).std()
            self.indicators_count += 1
        
        # === 价格变化 (8个) ===
        for period in [1, 2, 3, 5, 8, 10, 20, 30]:
            result[f"CHANGE_{period}"] = df["close"].pct_change(period)
            self.indicators_count += 1
        
        # === 平均真实范围 (3个) ===
        for period in [10, 20, 30]:
            result[f"ATR_PCT_{period}"] = result.get(f"ATR_{period}", ta.atr(df["high"], df["low"], df["close"], length=period)) / df["close"] * 100
            self.indicators_count += 1
        
        # === 均价差 (6个) ===
        result["OPEN_CLOSE_DIFF"] = df["close"] - df["open"]
        result["HIGH_LOW_DIFF"] = df["high"] - df["low"]
        result["CLOSE_EMA20_DIFF"] = df["close"] - ta.ema(df["close"], 20)
        result["CLOSE_MA20_DIFF"] = df["close"] - ta.sma(df["close"], 20)
        self.indicators_count += 4
        
        # === Keltner Channel (3个) ===
        for period in [10, 20, 30]:
            kc = ta.kc(df["high"], df["low"], df["close"], length=period)
            if kc is not None:
                result = pd.concat([result, kc], axis=1)
                self.indicators_count += 3
        
        # === Donchian Channel (3个) ===
        for period in [10, 20, 30]:
            dc = ta.donchian(df["high"], df["low"], length=period)
            if dc is not None:
                result = pd.concat([result, dc], axis=1)
                self.indicators_count += 3
        
        print(f"   📊 计算了 {self.indicators_count} 个技术指标")
        return result
    
    def get_indicator(self, df, indicator_name):
        """获取单个指标"""
        if indicator_name in df.columns:
            return df[indicator_name]
        return None
    
    def get_signal(self, df):
        """综合信号"""
        signals = {"buy": 0, "sell": 0, "neutral": 0}
        
        # MA 信号
        for fast, slow in [(5, 20), (10, 60), (20, 120)]:
            if f"MA{fast}" in df.columns and f"MA{slow}" in df.columns:
                if df[f"MA{fast}"].iloc[-1] > df[f"MA{slow}"].iloc[-1]:
                    signals["buy"] += 1
                else:
                    signals["sell"] += 1
        
        # RSI 信号
        for period in [7, 14]:
            if f"RSI_{period}" in df.columns:
                rsi = df[f"RSI_{period}"].iloc[-1]
                if rsi < 30:
                    signals["buy"] += 1
                elif rsi > 70:
                    signals["sell"] += 1
        
        # MACD 信号
        if "MACD_12_26_9" in df.columns and "MACDs_12_26_9" in df.columns:
            if df["MACD_12_26_9"].iloc[-1] > df["MACDs_12_26_9"].iloc[-1]:
                signals["buy"] += 1
            else:
                signals["sell"] += 1
        
        return signals


# 导出指标数量
print("✅ 指标引擎已升级: 100+ 指标")
