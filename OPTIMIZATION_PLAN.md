# 策略优化建议

## 当前问题分析

### 1. 收益率为负的原因

**观察到的现象：**
- 总收益率：-0.70%
- 已实现盈亏：-1913.98 元
- 胜率：0.00%（因为没有平仓盈利）

**根本原因：**
1. **信号冲突严重** - 同一合约同时出现买入和卖出信号
   - 例如：`Y_MA_Multiple_Buy: buy Y` 和 `Y_RSI_Deep_Overbought: sell Y` 同时出现
   - 导致频繁开平仓，增加手续费支出

2. **信号强度过滤不足** - 虽然有强度阈值，但多个低质量信号仍然被执行

3. **缺乏趋势过滤** - 没有考虑整体市场趋势，逆势交易较多

4. **手续费累积** - 每笔交易都有手续费（最低 20 元/手），频繁交易导致成本上升

---

## 优化方案

### 方案 1: 信号去重与优先级（推荐优先实施）

**问题：** 同一合约多个信号冲突

**解决方案：**
```python
# 为每个策略类型设置权重
SIGNAL_WEIGHTS = {
    "resonance": 1.0,    # 多指标共振（最强）
    "breakout": 0.9,     # 突破信号
    "ma_multiple": 0.85, # 多均线确认
    "macd_strong": 0.85, # MACD 强信号
    "bb_break": 0.8,     # 布林带突破
    "rsi_deep": 0.8,     # RSI 深度超买超卖
    "kdj_deep": 0.75,    # KDJ 深度超买超卖
    "ma_cross": 0.7,     # 均线交叉
    "default": 0.6       # 默认信号
}

# 每个合约只保留最强信号
def filter_conflicting_signals(signals):
    """过滤冲突信号，每个合约只保留一个方向的最强信号"""
    symbol_signals = {}
    
    for name, sig in signals.items():
        symbol = extract_symbol(name)
        direction = sig.get("direction")
        strength = sig.get("strength", 0.5)
        
        if symbol not in symbol_signals:
            symbol_signals[symbol] = {"buy": None, "sell": None}
        
        # 更新最强信号
        if direction == "buy":
            if symbol_signals[symbol]["buy"] is None or strength > symbol_signals[symbol]["buy"]["strength"]:
                symbol_signals[symbol]["buy"] = sig
        elif direction == "sell":
            if symbol_signals[symbol]["sell"] is None or strength > symbol_signals[symbol]["sell"]["strength"]:
                symbol_signals[symbol]["sell"] = sig
    
    # 如果同时有买入和卖出信号，只保留更强的那个
    final_signals = {}
    for symbol, sigs in symbol_signals.items():
        if sigs["buy"] and sigs["sell"]:
            if sigs["buy"]["strength"] >= sigs["sell"]["strength"]:
                final_signals[sigs["buy"]["name"]] = sigs["buy"]
            else:
                final_signals[sigs["sell"]["name"]] = sigs["sell"]
        elif sigs["buy"]:
            final_signals[sigs["buy"]["name"]] = sigs["buy"]
        elif sigs["sell"]:
            final_signals[sigs["sell"]["name"]] = sigs["sell"]
    
    return final_signals
```

---

### 方案 2: 增加趋势过滤

**问题：** 逆势交易导致亏损

**解决方案：**
```python
# 在 signals.py 中添加趋势过滤
def check_trend_filter(self, symbol, df):
    """趋势过滤：只在趋势方向交易"""
    if len(df) < 200:
        return "neutral"
    
    # 使用 200 日均线判断长期趋势
    ma200 = df.get("MA200", df["close"].rolling(200).mean()).iloc[-1]
    current_price = df["close"].iloc[-1]
    
    if pd.notna(ma200):
        if current_price > ma200 * 1.02:  # 价格在均线上方 2%
            return "bullish"
        elif current_price < ma200 * 0.98:  # 价格在均线下方 2%
            return "bearish"
    
    return "neutral"

# 在生成信号时应用过滤
trend = self.check_trend_filter(symbol, df)
if trend == "bullish" and direction == "sell":
    # 降低做空信号强度或跳过
    continue
elif trend == "bearish" and direction == "buy":
    # 降低做多信号强度或跳过
    continue
```

---

### 方案 3: 优化止损止盈策略

**当前设置：**
- 止损：5%
- 止盈：10%

**问题：** 固定比例不适合所有品种

**优化方案：**
```python
# 基于 ATR 动态设置止损止盈
def calculate_dynamic_stop_loss(self, symbol, df, entry_price):
    """基于 ATR 的动态止损"""
    if "ATR_14" not in df.columns:
        return entry_price * 0.95  # 默认 5% 止损
    
    atr = df["ATR_14"].iloc[-1]
    if pd.notna(atr):
        # 2 倍 ATR 作为止损
        stop_loss = entry_price - (2 * atr)
        return max(stop_loss, entry_price * 0.90)  # 最多不超过 10%
    
    return entry_price * 0.95

def calculate_dynamic_take_profit(self, symbol, df, entry_price):
    """基于 ATR 的动态止盈"""
    if "ATR_14" not in df.columns:
        return entry_price * 1.10  # 默认 10% 止盈
    
    atr = df["ATR_14"].iloc[-1]
    if pd.notna(atr):
        # 3 倍 ATR 作为止盈
        take_profit = entry_price + (3 * atr)
        return min(take_profit, entry_price * 1.20)  # 最多不超过 20%
    
    return entry_price * 1.10
```

---

### 方案 4: 减少交易频率

**问题：** 过度交易导致手续费累积

**解决方案：**
```python
# 1. 增加信号冷却时间
class SignalCooldown:
    def __init__(self):
        self.last_trade_time = {}  # {symbol: timestamp}
        self.cooldown_period = 3600  # 1 小时冷却期
    
    def can_trade(self, symbol):
        """检查是否可以交易（冷却期检查）"""
        now = datetime.now().timestamp()
        if symbol in self.last_trade_time:
            if now - self.last_trade_time[symbol] < self.cooldown_period:
                return False
        return True
    
    def record_trade(self, symbol):
        """记录交易时间"""
        self.last_trade_time[symbol] = datetime.now().timestamp()

# 2. 提高信号强度阈值
# 从 0.7 提高到 0.85
filtered_signals = self.filter_signals(all_signals, min_strength=0.85)

# 3. 限制每日交易次数
MAX_DAILY_TRADES = 50
if len(executor.executed_orders) >= MAX_DAILY_TRADES:
    print(f"⚠️  已达到每日交易上限 ({MAX_DAILY_TRADES} 次)")
    return
```

---

### 方案 5: 增加仓位管理优化

**当前问题：** 固定仓位不适合不同波动率的品种

**优化方案：**
```python
# 基于波动率调整仓位
def calculate_position_size_by_volatility(self, symbol, price, equity):
    """基于波动率调整仓位大小"""
    # 获取品种波动率（使用 ATR）
    if "ATR_14" in self.df.columns:
        atr = self.df["ATR_14"].iloc[-1]
        if pd.notna(atr):
            # 波动率越高，仓位越小
            volatility_factor = 1.0 / (atr / price)  # ATR 百分比的倒数
            base_size = equity * 0.02 / (atr * CONTRACTS[symbol]["multiplier"])
            return int(base_size * min(volatility_factor, 2.0))  # 最多 2 倍
    
    # 默认仓位
    return self.calculate_position_size(symbol, price, equity)
```

---

## 实施优先级

### 🔥 紧急（立即实施）
1. **信号去重与优先级** - 解决信号冲突问题
2. **提高信号强度阈值** - 从 0.7 提高到 0.85

### ⚡ 重要（本周实施）
3. **增加趋势过滤** - 避免逆势交易
4. **限制每日交易次数** - 减少过度交易

### 📈 优化（下周实施）
5. **动态止损止盈** - 基于 ATR 调整
6. **波动率仓位管理** - 优化风险收益比

---

## 预期效果

实施以上优化后，预期：
- 胜率：从 0% 提升到 45-55%
- 总收益率：从 -0.7% 提升到 +5-15%
- 夏普比率：从 0 提升到 1.0+
- 最大回撤：控制在 5% 以内
- 交易频率：减少 50%，但质量提高

---

## 下一步行动

1. ✅ 修改 `strategy/signals.py` - 添加信号去重逻辑
2. ⏳ 修改 `strategy/signals.py` - 增加趋势过滤
3. ⏳ 修改 `trading/portfolio.py` - 动态止损止盈
4. ⏳ 修改 `trading/executor.py` - 冷却期控制
5. ⏳ 运行回测验证效果
6. ⏳ 对比优化前后绩效

---

*版本：v1.0*
*日期：2026-03-16*
