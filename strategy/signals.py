"""策略信号生成器 - 150+ 策略全品种全周期版本"""
import pandas as pd
import numpy as np
import pandas_ta as ta
from strategy.indicators import IndicatorEngine


class StrategyGenerator:
    """策略信号生成 - 150+ 策略"""
    
    def __init__(self):
        self.engine = IndicatorEngine()
        self.strategies = self._init_strategies()
    
    def _init_strategies(self):
        """初始化 150+ 策略"""
        strategies = []
        
        # ===== 均线交叉策略 (30个) =====
        for fast in [3, 5, 8, 10, 12, 15, 20]:
            for slow in [20, 30, 60, 90, 120]:
                if fast < slow:
                    strategies.append({"name": f"MA_Cross_{fast}_{slow}", "type": "trend", "params": {"fast": fast, "slow": slow}})
                    strategies.append({"name": f"EMA_Cross_{fast}_{slow}", "type": "trend", "params": {"fast": fast, "slow": slow, "ema": True}})
        
        # ===== 突破策略 (20个) =====
        for period in [5, 10, 15, 20, 30, 60]:
            strategies.append({"name": f"Breakout_High_{period}", "type": "breakout", "params": {"period": period, "direction": "high"}})
            strategies.append({"name": f"Breakout_Low_{period}", "type": "breakout", "params": {"period": period, "direction": "low"}})
            strategies.append({"name": f"Breakout_Channel_{period}", "type": "breakout", "params": {"period": period, "direction": "channel"}})
        
        # ===== RSI 策略 (18个) =====
        for period in [6, 7, 9, 14, 21, 28]:
            strategies.append({"name": f"RSI_Oversold_{period}", "type": "oscillator", "params": {"period": period, "level": 30}})
            strategies.append({"name": f"RSI_Overbought_{period}", "type": "oscillator", "params": {"period": period, "level": 70}})
            strategies.append({"name": f"RSI_Divergence_{period}", "type": "oscillator", "params": {"period": period, "signal": "divergence"}})
        
        # ===== 布林策略 (15个) =====
        for period in [10, 15, 20, 25, 30]:
            strategies.append({"name": f"BB_Squeeze_{period}", "type": "bollinger", "params": {"period": period, "mode": "squeeze"}})
            strategies.append({"name": f"BB_Expand_{period}", "type": "bollinger", "params": {"period": period, "mode": "expand"}})
            strategies.append({"name": f"BB_Touch_{period}", "type": "bollinger", "params": {"period": period, "mode": "touch"}})
        
        # ===== MACD 策略 (12个) =====
        for fast, slow, signal in [(12, 26, 9), (8, 17, 9), (5, 35, 5), (6, 19, 6), (4, 12, 4)]:
            strategies.append({"name": f"MACD_Golden_{fast}_{slow}_{signal}", "type": "macd", "params": {"fast": fast, "slow": slow, "signal": signal, "mode": "golden"}})
            strategies.append({"name": f"MACD_Dead_{fast}_{slow}_{signal}", "type": "macd", "params": {"fast": fast, "slow": slow, "signal": signal, "mode": "dead"}})
            strategies.append({"name": f"MACD_Divergence_{fast}_{slow}_{signal}", "type": "macd", "params": {"fast": fast, "slow": slow, "signal": signal, "mode": "divergence"}})
        
        # ===== KDJ 策略 (12个) =====
        for k, d in [(9, 3), (14, 3), (21, 5), (28, 7)]:
            strategies.append({"name": f"KDJ_Oversold_{k}_{d}", "type": "kdj", "params": {"k": k, "d": d, "level": "oversold"}})
            strategies.append({"name": f"KDJ_Overbought_{k}_{d}", "type": "kdj", "params": {"k": k, "d": d, "level": "overbought"}})
            strategies.append({"name": f"KDJ_Cross_{k}_{d}", "type": "kdj", "params": {"k": k, "d": d, "mode": "cross"}})
        
        # ===== 成交量策略 (12个) =====
        for period in [5, 10, 20, 30]:
            strategies.append({"name": f"VOL_MA_Golden_{period}", "type": "volume", "params": {"period": period, "direction": "golden"}})
            strategies.append({"name": f"VOL_MA_Dead_{period}", "type": "volume", "params": {"period": period, "direction": "dead"}})
            strategies.append({"name": f"VOL_Breakout_{period}", "type": "volume", "params": {"period": period, "mode": "breakout"}})
        
        # ===== 形态策略 (15个) =====
        patterns = ["Doji", "Hammer", "Engulfing_Bull", "Engulfing_Bear", "Morning_Star", 
                   "Evening_Star", "Three_White", "Three_Black", "Piercing", "Dark_Cloud",
                   "Shooting_Star", "Inverted_Hammer", "Harami", "Kicking", "Belt_Hold"]
        for p in patterns:
            strategies.append({"name": f"Pattern_{p}", "type": "pattern", "params": {"pattern": p}})
        
        # ===== 组合策略 (20个) =====
        combos = [
            {"name": "MA_RSI_Combo", "ma": 20, "rsi": 14},
            {"name": "MACD_BB_Combo", "macd_fast": 12, "bb_period": 20},
            {"name": "MA_KDJ_Combo", "ma": 20, "kdj_k": 9},
            {"name": "RSI_MACD_Combo", "rsi": 14, "macd_fast": 12},
            {"name": "BB_RSI_Combo", "bb_period": 20, "rsi": 14},
            {"name": "VOL_MA_Combo", "vol_period": 10, "ma_period": 20},
            {"name": "CCI_RSI_Combo", "cci": 14, "rsi": 14},
            {"name": "WILLR_RSI_Combo", "willr": 14, "rsi": 14},
            {"name": "ADX_TREND_Combo", "adx": 14, "trend": 20},
            {"name": "MFI_VOL_Combo", "mfi": 14, "vol_ma": 20},
        ]
        for c in combos:
            strategies.append({"name": c["name"], "type": "combo", "params": c})
        
        # 多周期共振策略
        for period in ["1h", "4h", "1d"]:
            strategies.append({"name": f"Multi_Timeframe_{period}", "type": "multi_tf", "params": {"timeframe": period}})
        
        # 多均线组合
        for ma_list in ["5_10_20", "10_20_60", "20_60_120", "5_20_60"]:
            strategies.append({"name": f"Multi_MA_{ma_list}", "type": "multi_ma", "params": {"mas": ma_list}})
        
        # ===== 波动率策略 (10个) =====
        for period in [10, 20, 30, 60]:
            strategies.append({"name": f"Volatility_Expand_{period}", "type": "volatility", "params": {"period": period, "mode": "expand"}})
            strategies.append({"name": f"Volatility_Squeeze_{period}", "type": "volatility", "params": {"period": period, "mode": "squeeze"}})
        
        # ===== 动量策略 (12个) =====
        for period in [5, 8, 10, 15, 20, 30]:
            strategies.append({"name": f"Momentum_Golden_{period}", "type": "momentum", "params": {"period": period, "direction": "golden"}})
            strategies.append({"name": f"Momentum_Dead_{period}", "type": "momentum", "params": {"period": period, "direction": "dead"}})
        
        # ===== CCI 策略 (8个) =====
        for period in [10, 14, 20, 28]:
            strategies.append({"name": f"CCI_Oversold_{period}", "type": "cci", "params": {"period": period, "level": -100}})
            strategies.append({"name": f"CCI_Overbought_{period}", "type": "cci", "params": {"period": period, "level": 100}})
        
        # ===== ADX 策略 (6个) =====
        for period in [14, 20, 28]:
            strategies.append({"name": f"ADX_Trend_{period}", "type": "adx", "params": {"period": period, "strength": "strong"}})
            strategies.append({"name": f"ADX_Weak_{period}", "type": "adx", "params": {"period": period, "strength": "weak"}})
        
        # ===== 背离策略 (6个) =====
        for indicator in ["RSI", "MACD", "KDJ", "CCI"]:
            strategies.append(f"{indicator}_Bull_Divergence")
            strategies.append(f"{indicator}_Bear_Divergence")
        
        return strategies
    
    def generate_all(self):
        """生成所有策略信号"""
        signals = {}
        print(f"🎯 生成 {len(self.strategies)} 个策略...")
        
        for strategy in self.strategies:
            if isinstance(strategy, str):
                name = strategy
            else:
                name = strategy.get("name", "unknown")
            
            # 简化处理，直接返回策略名
            signals[name] = {
                "name": name,
                "type": strategy.get("type", "unknown") if isinstance(strategy, dict) else "unknown",
                "direction": "both",
                "strength": 1.0
            }
        
        return signals
    
    def generate_for_symbol(self, symbol, df):
        """为特定合约生成高质量信号（优化版）"""
        signals = []
        
        if df is None or len(df) < 50:
            return signals
        
        close = df["close"]
        
        # ========== 趋势过滤（新增） ==========
        trend = self._check_trend_filter(symbol, df)
        
        # ========== 信号优先级权重 ==========
        SIGNAL_WEIGHTS = {
            "Resonance": 1.0,      # 多指标共振（最强）
            "Breakout": 0.9,       # 突破信号
            "MA_Multiple": 0.85,   # 多均线确认
            "MACD_Strong": 0.85,   # MACD 强信号
            "BB_Break": 0.8,       # 布林带突破
            "RSI_Deep": 0.8,       # RSI 深度超买超卖
            "KDJ_Deep": 0.75,      # KDJ 深度超买超卖
            "default": 0.7         # 默认信号
        }
        
        def get_signal_weight(name):
            """获取信号权重"""
            for key, weight in SIGNAL_WEIGHTS.items():
                if key in name:
                    return weight
            return SIGNAL_WEIGHTS["default"]
        
        # ========== 高质量信号过滤 ==========
        # 只生成强度>0.7 的信号，减少低质量交易
        
        # 1. 均线交叉信号（要求多条均线确认）
        buy_ma_count = 0
        sell_ma_count = 0
        
        for fast, slow in [(5, 20), (10, 60), (20, 120)]:
            if f"MA{fast}" in df.columns and f"MA{slow}" in df.columns:
                ma_fast = df[f"MA{fast}"].iloc[-1]
                ma_slow = df[f"MA{slow}"].iloc[-1]
                if pd.notna(ma_fast) and pd.notna(ma_slow):
                    if ma_fast > ma_slow:
                        buy_ma_count += 1
                    else:
                        sell_ma_count += 1
        
        # 只有当 2 条以上均线确认时才生成信号
        if buy_ma_count >= 2:
            signals.append({"name": f"{symbol}_MA_Multiple_Buy", "direction": "buy", "strength": 0.85})
        elif sell_ma_count >= 2:
            signals.append({"name": f"{symbol}_MA_Multiple_Sell", "direction": "sell", "strength": 0.85})
        
        # 2. RSI 超买超卖（严格要求）
        for period in [14]:
            if f"RSI_{period}" in df.columns:
                rsi = df[f"RSI_{period}"].iloc[-1]
                if pd.notna(rsi):
                    if rsi < 25:  # 更严格的超卖
                        signals.append({"name": f"{symbol}_RSI_Deep_Oversold", "direction": "buy", "strength": 0.8})
                    elif rsi > 75:  # 更严格的超买
                        signals.append({"name": f"{symbol}_RSI_Deep_Overbought", "direction": "sell", "strength": 0.8})
        
        # 3. MACD 信号（要求柱状图确认）
        if "MACD_12_26_9" in df.columns and "MACDs_12_26_9" in df.columns:
            macd = df["MACD_12_26_9"].iloc[-1]
            signal = df["MACDs_12_26_9"].iloc[-1]
            hist = df.get("MACDh_12_26_9", macd - signal).iloc[-1]
            if pd.notna(macd) and pd.notna(signal):
                # 金叉 + 柱状图转正
                if macd > signal and hist > 0:
                    signals.append({"name": f"{symbol}_MACD_Strong_Golden", "direction": "buy", "strength": 0.85})
                # 死叉 + 柱状图转负
                elif macd < signal and hist < 0:
                    signals.append({"name": f"{symbol}_MACD_Strong_Dead", "direction": "sell", "strength": 0.85})
        
        # 4. 成交量确认（要求放量）
        vol_ratio = 1.0
        if "VOL_MA20" in df.columns:
            vol = df["volume"].iloc[-1]
            vol_ma = df["VOL_MA20"].iloc[-1]
            if pd.notna(vol) and pd.notna(vol_ma) and vol_ma > 0:
                vol_ratio = vol / vol_ma
        
        # 5. KDJ 超买超卖（严格要求）
        if "STOCHk_14_3_3" in df.columns:
            k = df["STOCHk_14_3_3"].iloc[-1]
            d = df["STOCHd_14_3_3"].iloc[-1]
            if pd.notna(k) and pd.notna(d):
                if k < 15 and k < d:  # 深度超卖
                    signals.append({"name": f"{symbol}_KDJ_Deep_Oversold", "direction": "buy", "strength": 0.75})
                elif k > 85 and k > d:  # 深度超买
                    signals.append({"name": f"{symbol}_KDJ_Deep_Overbought", "direction": "sell", "strength": 0.75})
        
        # 6. 布林带信号（要求突破）
        if "BBL_20_2.0" in df.columns and "BBU_20_2.0" in df.columns:
            close_price = close.iloc[-1]
            lower = df["BBL_20_2.0"].iloc[-1]
            upper = df["BBU_20_2.0"].iloc[-1]
            if pd.notna(lower) and pd.notna(upper):
                # 突破下轨（超卖反弹机会）
                if close_price < lower * 0.98:
                    signals.append({"name": f"{symbol}_BB_Break_Lower", "direction": "buy", "strength": 0.8})
                # 突破上轨（超买回调机会）
                elif close_price > upper * 1.02:
                    signals.append({"name": f"{symbol}_BB_Break_Upper", "direction": "sell", "strength": 0.8})
        
        # 7. 突破盘整（要求放量确认）
        for period in [20]:
            if f"HIGH_{period}" in df.columns and f"LOW_{period}" in df.columns:
                high = df[f"HIGH_{period}"].iloc[-1]
                low = df[f"LOW_{period}"].iloc[-1]
                current = close.iloc[-1]
                if pd.notna(high) and pd.notna(low):
                    # 向上突破 + 放量
                    if current > high and vol_ratio > 1.3:
                        signals.append({"name": f"{symbol}_Breakout_Vol_Buy", "direction": "buy", "strength": 0.9})
                    # 向下跌破 + 放量
                    elif current < low and vol_ratio > 1.3:
                        signals.append({"name": f"{symbol}_Breakout_Vol_Sell", "direction": "sell", "strength": 0.9})
        
        # 8. 多指标共振（最强信号）
        buy_confidence = 0
        sell_confidence = 0
        
        # 检查多个指标同时看涨/看跌
        if buy_ma_count >= 2:
            buy_confidence += 1
        if sell_ma_count >= 2:
            sell_confidence += 1
        
        for period in [14]:
            if f"RSI_{period}" in df.columns:
                rsi = df[f"RSI_{period}"].iloc[-1]
                if pd.notna(rsi):
                    if rsi < 30:
                        buy_confidence += 1
                    elif rsi > 70:
                        sell_confidence += 1
        
        if "MACD_12_26_9" in df.columns and "MACDs_12_26_9" in df.columns:
            macd = df["MACD_12_26_9"].iloc[-1]
            signal = df["MACDs_12_26_9"].iloc[-1]
            if pd.notna(macd) and pd.notna(signal):
                if macd > signal:
                    buy_confidence += 1
                else:
                    sell_confidence += 1
        
        # 3 个以上指标共振才生成最强信号
        if buy_confidence >= 3:
            signals.append({"name": f"{symbol}_Resonance_Strong_Buy", "direction": "buy", "strength": 0.95})
        elif sell_confidence >= 3:
            signals.append({"name": f"{symbol}_Resonance_Strong_Sell", "direction": "sell", "strength": 0.95})
        
        # ========== 应用趋势过滤（新增） ==========
        # 在牛市趋势中，降低卖出信号强度；在熊市趋势中，降低买入信号强度
        filtered_signals = []
        for sig in signals:
            strength = sig["strength"]
            
            # 如果是熊市趋势，降低买入信号强度
            if trend == "bearish" and sig["direction"] == "buy":
                strength *= 0.7  # 降低 30%
            # 如果是牛市趋势，降低卖出信号强度
            elif trend == "bullish" and sig["direction"] == "sell":
                strength *= 0.7  # 降低 30%
            
            # 只有强度仍然高于阈值的信号才保留
            if strength >= 0.7:
                sig["strength"] = strength
                filtered_signals.append(sig)
        
        signals = filtered_signals
        
        # ========== 信号去重：每个合约只保留一个方向的最强信号 ==========
        if len(signals) <= 1:
            return signals
        
        # 分离买入和卖出信号
        buy_signals = [s for s in signals if s["direction"] == "buy"]
        sell_signals = [s for s in signals if s["direction"] == "sell"]
        
        # 每个方向只保留最强的一个信号
        final_signals = []
        
        if buy_signals:
            best_buy = max(buy_signals, key=lambda s: s["strength"])
            final_signals.append(best_buy)
        
        if sell_signals:
            best_sell = max(sell_signals, key=lambda s: s["strength"])
            
            # 如果同时有买入和卖出信号，只保留更强的那个
            if buy_signals:
                if best_sell["strength"] > best_buy["strength"]:
                    final_signals = [best_sell]  # 只保留卖出
                # 否则只保留买入（已经在列表中）
            else:
                final_signals.append(best_sell)
        
        return final_signals
    
    def filter_signals(self, signals, direction=None, min_strength=0.5):
        """过滤信号"""
        filtered = {}
        for name, sig in signals.items():
            if direction and sig.get("direction") not in [direction, "both"]:
                continue
            if sig.get("strength", 1.0) < min_strength:
                continue
            filtered[name] = sig
        return filtered
    
    def _check_trend_filter(self, symbol, df):
        """趋势过滤：判断当前趋势方向
        
        Returns:
            "bullish": 牛市趋势（只做多）
            "bearish": 熊市趋势（只做空）
            "neutral": 震荡市（双向都可以）
        """
        if len(df) < 200:
            return "neutral"
        
        close = df["close"]
        
        # 方法 1: 使用 200 日均线判断长期趋势
        ma200 = close.rolling(200).mean().iloc[-1]
        current_price = close.iloc[-1]
        
        if pd.notna(ma200):
            # 价格在均线上方 2% 以上 → 牛市
            if current_price > ma200 * 1.02:
                return "bullish"
            # 价格在均线下方 2% 以上 → 熊市
            elif current_price < ma200 * 0.98:
                return "bearish"
        
        # 方法 2: 使用多条均线判断
        if len(df) >= 60:
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            
            if pd.notna(ma20) and pd.notna(ma60):
                # 多头排列：20 日线 > 60 日线
                if ma20 > ma60 * 1.01:
                    return "bullish"
                # 空头排列：20 日线 < 60 日线
                elif ma20 < ma60 * 0.99:
                    return "bearish"
        
        return "neutral"