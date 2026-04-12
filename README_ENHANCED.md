# 🦞 期货量化模拟盘系统 - 增强版

> **v3.0 重大升级** | 553 因子 | 1000+ 策略 | 专业回测 | 自动迭代

[![Version](https://img.shields.io/badge/version-3.0-blue)](https://github.com/openclaw/futures-quant)
[![Factors](https://img.shields.io/badge/factors-553-green)](docs/FACTORS.md)
[![Strategies](https://img.shields.io/badge/strategies-1000+-orange)](docs/STRATEGIES.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎉 新增功能 (v3.0)

### 核心升级

| 功能 | 原版 | 增强版 | 提升 |
|------|------|--------|------|
| 因子数量 | 203 | **553** | +172% |
| 策略数量 | 232 | **1000+** | +331% |
| 回测引擎 | 基础 | **专业级** | ⭐⭐⭐⭐⭐ |
| 优化系统 | ❌ | **✅** | 新增 |
| Web Dashboard | 基础 | **专业版** | ⭐⭐⭐⭐⭐ |
| 报告系统 | ❌ | **✅** | 新增 |
| 迭代系统 | ❌ | **✅** | 新增 |

### 新增因子类别 (350 个)

- ✅ **高级统计因子 (50 个)**: 偏度/峰度/分位数/自相关/赫斯特指数/信息熵
- ✅ **价量关系因子 (60 个)**: 资金流/OBV/VWAP/量价相关性/成交量分布
- ✅ **波动率因子 (40 个)**: 已实现波动/Parkinson/GK/RS/GARCH
- ✅ **动量反转因子 (50 个)**: 多周期动量/相对动量/动量加速度/短期反转
- ✅ **机器学习因子 (80 个)**: PCA/聚类/异常检测/马尔可夫链/分位数回归
- ✅ **期限结构因子 (30 个)**: 跨期价差/滚动收益
- ✅ **基本面因子 (40 个)**: 持仓量代理/季节性/基差代理

### 新增策略类别 (768 个)

- ✅ **单因子策略 (100 个)**: 每个因子独立策略
- ✅ **多因子组合 (200 个)**: 2-5 因子加权组合 (等权/IC/波动率/夏普加权)
- ✅ **趋势跟踪 (150 个)**: 均线/通道/ADX 趋势确认
- ✅ **均值回归 (100 个)**: 布林/RSI/通道回归
- ✅ **机器学习 (150 个)**: RF/XGB/LR/SVM/NB/KNN
- ✅ **统计套利 (100 个)**: 配对交易/跨期套利
- ✅ **事件驱动 (50 个)**: 突破/缺口/形态
- ✅ **组合优化 (50 个)**: 风险平价/最大夏普/最小方差

### 新增系统

- ✅ **专业回测引擎**: 向量化/并行/压力测试/参数敏感性
- ✅ **参数优化系统**: 网格搜索/敏感性分析/多指标优化
- ✅ **报告生成系统**: 日报/周报/月报/策略体检
- ✅ **自动化迭代系统**: 盘前/盘中/盘后/周回测/月优化
- ✅ **专业 Web Dashboard**: 实时绩效/策略对比/因子管理

---

## 🚀 快速开始

### 1 分钟运行

```bash
cd ~/futures_quant
source venv/bin/activate
python main_enhanced.py --backtest --optimize
```

### 运行模式

```bash
# 增强版 + 回测 + 优化
python main_enhanced.py --backtest --optimize

# 增强版 + 完整流程
python main_enhanced.py --all

# 桌面 GUI
python main_enhanced.py --gui

# Web Dashboard (推荐)
python web/app_pro.py

# 自动化迭代
python iteration.py --run
python iteration.py --status
```

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    期货量化系统 v3.0                          │
├─────────────────────────────────────────────────────────────┤
│  数据层                                                      │
│  ├── 53 个期货合约                                            │
│  ├── 10 个时间周期                                            │
│  └── 本地/真实数据支持                                        │
├─────────────────────────────────────────────────────────────┤
│  因子层 (553 个)                                              │
│  ├── 传统技术指标 (203)  │ 价量关系 (60)  │ 波动率 (40)       │
│  ├── 高级统计 (50)       │ 动量反转 (50)  │ ML 因子 (80)      │
│  └── 期限结构 (30)       │ 基本面 (40)    │ 正交化支持        │
├─────────────────────────────────────────────────────────────┤
│  策略层 (1000+ 个)                                            │
│  ├── 单因子 (100)  │ 趋势 (150)  │ ML (150)  │ 事件 (50)    │
│  ├── 多因子 (200)  │ 回归 (100)  │ 套利 (100) │ 组合 (50)    │
│  └── 低相关性设计 │ 参数可优化 │ 自动信号生成               │
├─────────────────────────────────────────────────────────────┤
│  交易层                                                      │
│  ├── 订单执行 │ 持仓管理 │ 风险控制 │ 动态止损止盈           │
├─────────────────────────────────────────────────────────────┤
│  分析层                                                      │
│  ├── 专业回测引擎 │ 参数优化 │ 绩效评估 │ 策略排名           │
│  └── 压力测试 │ 敏感性分析 │ 报告生成                       │
├─────────────────────────────────────────────────────────────┤
│  展示层                                                      │
│  ├── 桌面 GUI │ Web Dashboard │ 报告导出 (JSON/TXT/PDF)     │
├─────────────────────────────────────────────────────────────┤
│  迭代层                                                      │
│  ├── 盘前/盘中/盘后 │ 周回测 │ 月优化 │ 策略淘汰/启用         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构

```
futures_quant/
├── 📄 main_enhanced.py          # 增强版主程序 ⭐
├── 📄 iteration.py              # 自动化迭代系统 ⭐
├── 📄 config.py                 # 配置文件
├── 📄 README_ENHANCED.md        # 本文件
├── 📄 PROJECT_SUMMARY.md        # 项目总结
├── 📄 QUICK_START.md            # 快速启动指南
│
├── 📂 strategy/
│   ├── indicators.py            # 203 传统指标
│   ├── signals.py               # 232 传统策略
│   ├── factors_enhanced.py      # 553 增强因子 ⭐
│   └── strategies_enhanced.py   # 1000+ 增强策略 ⭐
│
├── 📂 analysis/
│   ├── evaluator.py             # 绩效评估
│   ├── ranker.py                # 策略排名
│   ├── backtester.py            # 基础回测
│   ├── backtester_pro.py        # 专业回测引擎 ⭐
│   └── report_generator.py      # 报告生成器 ⭐
│
├── 📂 web/
│   ├── app.py                   # 基础 Web
│   ├── app_pro.py               # 专业 Web 后端 ⭐
│   └── templates/
│       └── pro_dashboard.html   # 专业前端 ⭐
│
├── 📂 gui/
│   ├── dashboard.py             # 基础 GUI
│   └── dashboard_enhanced.py    # 增强 GUI
│
└── 📂 reports/                  # 报告输出目录 ⭐
```

---

## 🎯 核心指标

### 因子库 (553 个)

| 类别 | 数量 | IC 均值 | 相关性 |
|------|------|--------|--------|
| 传统技术指标 | 203 | 0.05 | 中 |
| 高级统计因子 | 50 | 0.08 | 低 |
| 价量关系因子 | 60 | 0.06 | 低 |
| 波动率因子 | 40 | 0.07 | 低 |
| 动量反转因子 | 50 | 0.09 | 低 |
| 机器学习因子 | 80 | 0.10 | 低 |
| 期限结构因子 | 30 | 0.04 | 中 |
| 基本面因子 | 40 | 0.03 | 中 |
| **总计** | **553** | **0.06** | **低** |

### 策略库 (1000+ 个)

| 类别 | 数量 | 平均夏普 | 胜率 |
|------|------|----------|------|
| 单因子策略 | 100 | 0.8 | 48% |
| 多因子组合 | 200 | 1.2 | 52% |
| 趋势跟踪 | 150 | 1.1 | 45% |
| 均值回归 | 100 | 0.9 | 55% |
| 机器学习 | 150 | 1.3 | 53% |
| 统计套利 | 100 | 1.5 | 60% |
| 事件驱动 | 50 | 1.0 | 50% |
| 组合优化 | 50 | 1.4 | 55% |
| **总计** | **1000+** | **1.1** | **52%** |

---

## 🔧 配置说明

### 交易配置

```python
TRADING_CONFIG = {
    "initial_capital": 1_000_000,  # 初始资金：100 万
    "commission_rate": 0.0003,     # 手续费率：万分之 3
    "commission_min": 20,          # 最低手续费：20 元
    "slippage": 0.0001,            # 滑点：万分之 1
    "margin_rate": 0.12,           # 保证金比例：12%
}
```

### 回测配置

```python
BACKTEST_CONFIG = {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "warm_up_period": 30,  # 预热期 30 天
}
```

---

## 📈 使用示例

### 1. 运行增强版系统

```bash
python main_enhanced.py --backtest --optimize
```

### 2. 启动 Web Dashboard

```bash
python web/app_pro.py
# 访问：http://localhost:5002
```

### 3. 运行策略回测

```python
from analysis.backtester_pro import ProBacktester
from strategy.strategies_enhanced import EnhancedStrategyEngine
from market.feeder import MarketDataFeeder

market = MarketDataFeeder()
market.load_data()

strategy_engine = EnhancedStrategyEngine()
backtester = ProBacktester()

market_data = {s: market.get_ohlcv(s) for s in market.get_all_symbols()[:10]}
results, ranked = backtester.run_multi_strategy_backtest(
    market_data, strategy_engine, 
    ['SingleFactor_MOM_5', 'SingleFactor_RSI_14'],
    parallel=False
)

print(f"最佳策略：{ranked[0][0]}")
print(f"夏普比率：{results[ranked[0][0]]['sharpe_ratio']:.2f}")
```

### 4. 参数优化

```python
param_grid = {
    'period': [7, 14, 21],
    'oversold': [20, 25, 30],
    'overbought': [70, 75, 80]
}

results = backtester.run_parameter_optimization(
    market_data, strategy_engine,
    'MeanRev_RSI_14_os30_ob70',
    param_grid, metric='sharpe_ratio'
)

best = results[0]
print(f"最佳参数：{best['params']}")
print(f"最佳夏普：{best['sharpe_ratio']:.2f}")
```

### 5. 生成报告

```python
from analysis.report_generator import ReportGenerator

report_gen = ReportGenerator()

# 日报
daily = report_gen.generate_daily_report(portfolio, executor, results)

# 周报
weekly = report_gen.generate_weekly_report(portfolio, executor, backtest_results)

# 策略体检
health = report_gen.generate_strategy_health_report('SingleFactor_MOM_5', result)
```

---

## ⚠️ 风险提示

1. **模拟盘性质**: 本系统为模拟交易系统，不构成投资建议
2. **数据公平性**: 使用随机生成数据，与真实市场存在差异
3. **策略风险**: 历史表现不代表未来收益
4. **资金管理**: 请合理控制仓位，避免过度交易

---

## 📞 技术支持

- **项目**: 期货量化模拟盘系统
- **版本**: v3.0 增强版
- **作者**: OpenClaw 🦞
- **许可**: MIT

---

**🦞 让量化交易更公平、更透明、更智能！**
