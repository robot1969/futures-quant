# 🚀 期货量化系统 - 快速启动指南

## 1 分钟快速开始

```bash
# 1. 进入项目目录
cd ~/futures_quant

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行增强版 (带回测和优化)
python main_enhanced.py --backtest --optimize
```

---

## 运行模式

### 模式 1: 命令行运行 (基础)

```bash
# 基础运行
python main.py

# 增强版运行 (推荐)
python main_enhanced.py

# 增强版 + 回测
python main_enhanced.py --backtest

# 增强版 + 回测 + 优化
python main_enhanced.py --backtest --optimize

# 增强版 + 完整流程
python main_enhanced.py --all
```

### 模式 2: 桌面 GUI

```bash
# 基础 GUI
python main.py --gui

# 增强版 GUI
python main_enhanced.py --gui
```

### 模式 3: Web Dashboard (推荐) ⭐

```bash
# 启动专业 Web Dashboard
python web/app_pro.py

# 访问地址
# 标准版：http://localhost:5001
# 专业版：http://localhost:5002
```

### 模式 4: 自动化迭代

```bash
# 查看状态
python iteration.py --status

# 运行完整流程
python iteration.py --run

# 盘前运行 (08:00)
python iteration.py --morning

# 盘中运行 (09:00)
python iteration.py --trading

# 盘后运行 (15:00)
python iteration.py --evening

# 周回测 (周日)
python iteration.py --backtest

# 月优化 (月初)
python iteration.py --optimize
```

---

## 输出示例

### 命令行输出

```
================================================================================
🦞 期货量化模拟盘系统 | 增强版
================================================================================
   时间：2026-04-12 12:45:00
   因子数量：553 个 (203 传统 + 350 增强)
   策略数量：1000+ 个 (232 传统 + 768 增强)
================================================================================

📦 【步骤 1/6】初始化交易组件...
   ✅ 组件初始化完成

📊 【步骤 2/6】加载市场数据...
   ✅ 成功加载 53 个期货合约数据

📈 【步骤 3/6】计算增强因子...
   📊 计算了 553 个增强因子
   ✅ 完成 5 个合约的因子计算

🔄 【步骤 4/6】策略回测...
🚀 开始多策略回测：10 个策略
   ✅ 回测完成：总收益 5.23%, 夏普 1.25
   ...

🏆 【回测结果 Top 5】
   1. SingleFactor_MOM_5
      总收益：5.23%
      夏普比率：1.25
      最大回撤：8.50%
      胜率：52.30%
   ...

================================================================================
📊 【绩效评估结果】
   总收益率：-0.32%
   夏普比率：0.00
   最大回撤：0.00%
   胜率：0.00%
   盈亏比：0.00
   卡玛比率：0.00
   索提诺比率：0.00
================================================================================
```

---

## 目录结构

```
futures_quant/
├── main.py                    # 原版主程序
├── main_enhanced.py           # 增强版主程序 ⭐
├── iteration.py               # 自动化迭代系统 ⭐
├── config.py                  # 配置文件
├── QUICK_START.md             # 本文件
├── PROJECT_SUMMARY.md         # 项目总结
├── UPGRADE_PLAN.md            # 升级计划
│
├── strategy/
│   ├── factors_enhanced.py    # 553 增强因子 ⭐
│   └── strategies_enhanced.py # 1000+ 增强策略 ⭐
│
├── analysis/
│   ├── backtester_pro.py      # 专业回测引擎 ⭐
│   └── report_generator.py    # 报告生成器 ⭐
│
├── web/
│   ├── app_pro.py             # 专业 Web 后端 ⭐
│   └── templates/
│       └── pro_dashboard.html # 专业前端 ⭐
│
└── reports/                   # 报告输出目录 ⭐
```

---

## 常见问题

### Q: 如何查看因子列表？

```python
from strategy.factors_enhanced import EnhancedFactorEngine
engine = EnhancedFactorEngine()
print(f"总因子数：{engine.factor_count}")
```

### Q: 如何查看策略列表？

```python
from strategy.strategies_enhanced import EnhancedStrategyEngine
engine = EnhancedStrategyEngine()
print(f"总策略数：{engine.get_strategy_count()}")

# 按类别查看
trend_strategies = engine.get_strategies_by_category('trend_following')
print(f"趋势策略：{len(trend_strategies)} 个")
```

### Q: 如何运行单个策略回测？

```python
from analysis.backtester_pro import ProBacktester
from strategy.strategies_enhanced import EnhancedStrategyEngine
from market.feeder import MarketDataFeeder

market = MarketDataFeeder()
market.load_data()

strategy_engine = EnhancedStrategyEngine()
backtester = ProBacktester()

market_data = {symbol: market.get_ohlcv(symbol) for symbol in market.get_all_symbols()[:10]}
result = backtester.run_backtest(market_data, strategy_engine, 'SingleFactor_MOM_5')

print(f"总收益：{result['total_return']:.2%}")
print(f"夏普比率：{result['sharpe_ratio']:.2f}")
```

### Q: 如何优化策略参数？

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

### Q: 如何生成报告？

```python
from analysis.report_generator import ReportGenerator

report_gen = ReportGenerator()

# 日报
daily_report = report_gen.generate_daily_report(portfolio, executor, results)

# 周报
weekly_report = report_gen.generate_weekly_report(portfolio, executor, backtest_results)

# 月报
monthly_report = report_gen.generate_monthly_report(portfolio, backtest_results)

# 策略体检
health_report = report_gen.generate_strategy_health_report('SingleFactor_MOM_5', result)
```

---

## 性能优化建议

1. **减少回测合约数量**: 从 53 个减少到 10-20 个代表性合约
2. **使用并行回测**: `parallel=True` 启用多线程
3. **缓存因子计算**: 避免重复计算
4. **增量回测**: 只计算新增数据

---

## 下一步

1. ✅ 阅读 `PROJECT_SUMMARY.md` 了解完整功能
2. ✅ 运行 `python main_enhanced.py --all` 体验完整流程
3. ✅ 启动 Web Dashboard 查看可视化界面
4. ✅ 配置自动化迭代系统

---

**🦞 祝交易顺利！**
