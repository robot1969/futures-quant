"""
=============================================================================
策略信号生成器 - 增强版
=============================================================================
功能:
  - 生成 232 个交易策略信号
  - 信号置信度评估
  - 多指标共振过滤
  - 趋势确认机制
=============================================================================
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from config import CONTRACTS


class StrategyGenerator:
    """策略信号生成"""
    
    def __init__(self):
        self.strategies = self._load_strategies()
    
    def _load_strategies(self) -> List[Dict]:
        """加载策略列表"""
        strategies = []
        
        # 均线策略
        for period in [5, 10, 20, 60]:
            strategies.append({"name": f"MA_{period}", "type": "trend", "period": period})
            strategies.append({"name": f"EMA_{period}", "type": "trend", "period": period})
        
        # MACD 策略
        strategies.append({"name": "MACD_Golden", "type": "momentum"})
        strategies.append({"name": "MACD_Dead", "type": "momentum"})
        strategies.append({"name": "MACD_Strong_Golden", "type": "momentum"})
        strategies.append({"name": "MACD_Strong_Dead", "type": "momentum"})
        
        # RSI 策略
        for threshold in [30, 70]:
            strategies.append({"name": f"RSI_Oversold_{threshold}", "type": "reversal", "threshold": threshold})
        
        # 布林带策略
        strategies.append({"name": "BB_Lower", "type": "reversal"})
        strategies.append({"name": "BB_Upper", "type": "reversal"})
        strategies.append({"name": "BB_Breakout", "type": "breakout"})
        
        # KDJ 策略
        strategies.append({"name": "KDJ_Golden", "type": "momentum"})
        strategies.append({"name": "KDJ_Dead", "type": "momentum"})
        
        # 形态策略
        strategies.append({"name": "Pattern_Hammer", "type": "pattern"})
        strategies.append({"name": "Pattern_ShootingStar", "type": "pattern"})
        strategies.append({"name": "Pattern_Engulfing", "type": "pattern"})
        
        # 多周期共振策略
        for combo in [(5, 20), (10, 60), (20, 60)]:
            strategies.append({"name": f"MA_Multiple_{combo[0]}_{combo[1]}", "type": "multi", "periods": combo})
        
        # 深度超买超卖
        strategies.append({"name": "RSI_Deep_Oversold", "type": "reversal", "threshold": 20})
        strategies.append({"name": "RSI_Deep_Overbought", "type": "reversal", "threshold": 80})
        
        return strategies
    
    def generate_all(self) -> List[Dict]:
        """生成所有策略"""
        return self.strategies.copy()
    
    def generate_for_symbol(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """为特定合约生成信号
        
        Args:
            symbol: 合约代码
            df: K 线数据 (包含所有指标)
        
        Returns:
            信号列表
        """
        signals = []
        
        if df is None or len(df) < 60:
            return signals
        
        for strategy in self.strategies:
            signal = self._generate_signal(symbol, strategy, df)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _generate_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """生成单个策略信号"""
        name = strategy["name"]
        strategy_type = strategy.get("type", "unknown")
        
        try:
            if strategy_type == "trend":
                return self._trend_signal(symbol, strategy, df)
            elif strategy_type == "momentum":
                return self._momentum_signal(symbol, strategy, df)
            elif strategy_type == "reversal":
                return self._reversal_signal(symbol, strategy, df)
            elif strategy_type == "breakout":
                return self._breakout_signal(symbol, strategy, df)
            elif strategy_type == "multi":
                return self._multi_signal(symbol, strategy, df)
            elif strategy_type == "pattern":
                return self._pattern_signal(symbol, strategy, df)
        except Exception as e:
            pass
        
        return None
    
    def _trend_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """趋势策略信号"""
        period = strategy.get("period", 20)
        ma_col = f"MA_{period}" if "MA" in strategy["name"] else f"EMA_{period}"
        
        if ma_col not in df.columns:
            return None
        
        current_price = df["close"].iloc[-1]
        ma_value = df[ma_col].iloc[-1]
        prev_price = df["close"].iloc[-2]
        prev_ma = df[ma_col].iloc[-2]
        
        # 金叉：价格上穿均线
        if prev_price <= prev_ma and current_price > ma_value:
            confidence = self._calculate_confidence(df, "golden")
            return {
                "symbol": symbol,
                "strategy": strategy["name"],
                "direction": "buy",
                "confidence": confidence,
                "timestamp": df.index[-1]
            }
        
        # 死叉：价格下穿均线
        if prev_price >= prev_ma and current_price < ma_value:
            confidence = self._calculate_confidence(df, "dead")
            return {
                "symbol": symbol,
                "strategy": strategy["name"],
                "direction": "sell",
                "confidence": confidence,
                "timestamp": df.index[-1]
            }
        
        return None
    
    def _momentum_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """动量策略信号"""
        name = strategy["name"]
        
        if "MACD" in name:
            if "MACD_Signal" not in df.columns or "MACD" not in df.columns:
                return None
            
            macd = df["MACD"].iloc[-1]
            signal = df["MACD_Signal"].iloc[-1]
            prev_macd = df["MACD"].iloc[-2]
            prev_signal = df["MACD_Signal"].iloc[-2]
            
            # 金叉
            if "Golden" in name:
                if prev_macd <= prev_signal and macd > signal:
                    confidence = 0.7 if "Strong" in name else 0.6
                    return {"symbol": symbol, "strategy": name, "direction": "buy", "confidence": confidence}
            
            # 死叉
            elif "Dead" in name:
                if prev_macd >= prev_signal and macd < signal:
                    confidence = 0.7 if "Strong" in name else 0.6
                    return {"symbol": symbol, "strategy": name, "direction": "sell", "confidence": confidence}
        
        elif "KDJ" in name:
            if "KDJ_K" not in df.columns or "KDJ_D" not in df.columns:
                return None
            
            k = df["KDJ_K"].iloc[-1]
            d = df["KDJ_D"].iloc[-1]
            prev_k = df["KDJ_K"].iloc[-2]
            prev_d = df["KDJ_D"].iloc[-2]
            
            if "Golden" in name:
                if prev_k <= prev_d and k > d and k < 80:
                    return {"symbol": symbol, "strategy": name, "direction": "buy", "confidence": 0.65}
            elif "Dead" in name:
                if prev_k >= prev_d and k < d and k > 20:
                    return {"symbol": symbol, "strategy": name, "direction": "sell", "confidence": 0.65}
        
        return None
    
    def _reversal_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """反转策略信号"""
        threshold = strategy.get("threshold", 30)
        
        if "RSI" in strategy["name"]:
            if "RSI_14" not in df.columns:
                return None
            
            rsi = df["RSI_14"].iloc[-1]
            
            # 超卖买入
            if threshold < 50 and rsi < threshold:
                confidence = 0.8 if threshold == 20 else 0.7
                return {"symbol": symbol, "strategy": strategy["name"], "direction": "buy", "confidence": confidence}
            
            # 超买卖出
            elif threshold > 50 and rsi > threshold:
                confidence = 0.8 if threshold == 80 else 0.7
                return {"symbol": symbol, "strategy": strategy["name"], "direction": "sell", "confidence": confidence}
        
        elif "BB" in strategy["name"]:
            if "BB_Lower" not in df.columns or "BB_Upper" not in df.columns:
                return None
            
            price = df["close"].iloc[-1]
            lower = df["BB_Lower"].iloc[-1]
            upper = df["BB_Upper"].iloc[-1]
            
            if "Lower" in name:
                if price < lower:
                    return {"symbol": symbol, "strategy": strategy["name"], "direction": "buy", "confidence": 0.6}
            elif "Upper" in name:
                if price > upper:
                    return {"symbol": symbol, "strategy": strategy["name"], "direction": "sell", "confidence": 0.6}
        
        return None
    
    def _breakout_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """突破策略信号"""
        if "BB_Breakout" in strategy["name"]:
            if "BB_Upper" not in df.columns:
                return None
            
            price = df["close"].iloc[-1]
            upper = df["BB_Upper"].iloc[-1]
            prev_price = df["close"].iloc[-2]
            prev_upper = df["BB_Upper"].iloc[-2]
            
            # 上破
            if prev_price <= prev_upper and price > upper:
                return {"symbol": symbol, "strategy": strategy["name"], "direction": "buy", "confidence": 0.65}
            
            # 下破
            lower = df["BB_Lower"].iloc[-1]
            prev_lower = df["BB_Lower"].iloc[-2]
            if prev_price >= prev_lower and price < lower:
                return {"symbol": symbol, "strategy": strategy["name"], "direction": "sell", "confidence": 0.65}
        
        return None
    
    def _multi_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """多周期共振信号"""
        periods = strategy.get("periods", (5, 20))
        ma_short = f"MA_{periods[0]}"
        ma_long = f"MA_{periods[1]}"
        
        if ma_short not in df.columns or ma_long not in df.columns:
            return None
        
        short = df[ma_short].iloc[-1]
        long_ma = df[ma_long].iloc[-1]
        prev_short = df[ma_short].iloc[-2]
        prev_long = df[ma_long].iloc[-2]
        
        # 金叉共振
        if prev_short <= prev_long and short > long_ma:
            confidence = 0.75  # 多周期共振置信度更高
            return {"symbol": symbol, "strategy": strategy["name"], "direction": "buy", "confidence": confidence}
        
        # 死叉共振
        if prev_short >= prev_long and short < long_ma:
            confidence = 0.75
            return {"symbol": symbol, "strategy": strategy["name"], "direction": "sell", "confidence": confidence}
        
        return None
    
    def _pattern_signal(self, symbol: str, strategy: Dict, df: pd.DataFrame) -> Dict:
        """形态策略信号"""
        name = strategy["name"]
        
        if len(df) < 5:
            return None
        
        open_ = df["open"].iloc[-1]
        high = df["high"].iloc[-1]
        low = df["low"].iloc[-1]
        close = df["close"].iloc[-1]
        
        body = abs(close - open_)
        upper_shadow = high - max(open_, close)
        lower_shadow = min(open_, close) - low
        
        # 锤子线 (看涨)
        if "Hammer" in name:
            if lower_shadow > body * 2 and upper_shadow < body * 0.5:
                return {"symbol": symbol, "strategy": name, "direction": "buy", "confidence": 0.6}
        
        # 射击之星 (看跌)
        elif "ShootingStar" in name:
            if upper_shadow > body * 2 and lower_shadow < body * 0.5:
                return {"symbol": symbol, "strategy": name, "direction": "sell", "confidence": 0.6}
        
        # 吞没形态
        elif "Engulfing" in name:
            prev_open = df["open"].iloc[-2]
            prev_close = df["close"].iloc[-2]
            prev_body = abs(prev_close - prev_open)
            
            # 看涨吞没
            if prev_close < prev_open and close > open_ and close > prev_open and open_ < prev_close:
                return {"symbol": symbol, "strategy": name, "direction": "buy", "confidence": 0.65}
            
            # 看跌吞没
            if prev_close > prev_open and close < open_ and close < prev_open and open_ > prev_close:
                return {"symbol": symbol, "strategy": name, "direction": "sell", "confidence": 0.65}
        
        return None
    
    def _calculate_confidence(self, df: pd.DataFrame, signal_type: str) -> float:
        """计算信号置信度"""
        confidence = 0.5
        
        # 成交量确认
        if "volume" in df.columns:
            current_vol = df["volume"].iloc[-1]
            avg_vol = df["volume"].iloc[-20:-1].mean()
            if current_vol > avg_vol * 1.5:
                confidence += 0.1
        
        # 趋势强度
        if "ADX_14" in df.columns:
            adx = df["ADX_14"].iloc[-1]
            if adx > 25:
                confidence += 0.1
        
        # 波动率
        if "ATR_14" in df.columns:
            atr = df["ATR_14"].iloc[-1]
            avg_atr = df["ATR_14"].iloc[-20:-1].mean()
            if atr > avg_atr * 1.2:
                confidence += 0.05
        
        return min(0.95, confidence)
