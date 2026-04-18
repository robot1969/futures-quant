# 期货量化系统 - 项目结构

## 📁 目录结构

```
futures_quant/
├── core/                    # 核心模块 (新增)
│   ├── __init__.py
│   └── manager.py           # 系统管理器 - 统一入口
│
├── analysis/                # 分析模块
│   ├── __init__.py          # ✅ 已更新
│   ├── evaluator.py         # 基础绩效评估
│   ├── evaluation_system.py # ✅ 公平公正评估系统 (新增)
│   ├── analytics_engine.py  # ✅ 深度分析引擎 (新增)
│   ├── backtester.py        # 基础回测引擎
│   ├── backtester_pro.py    # 专业回测引擎
│   ├── ranker.py            # 策略排名
│   └── report_generator.py  # 报告生成器
│
├── strategy/                # 策略模块
│   ├── __init__.py          # ✅ 已更新
│   ├── indicators.py        # 技术指标引擎
│   ├── signals.py           # 策略信号生成
│   ├── strategies_enhanced.py  # 增强策略库
│   └── factors_enhanced.py  # 因子库
│
├── market/                  # 市场数据模块
│   ├── __init__.py
│   └── feeder.py            # 行情数据源
│
├── trading/                 # 交易模块
│   ├── __init__.py
│   ├── portfolio.py         # 持仓管理
│   ├── executor.py          # 订单执行
│   └── risk_manager.py      # 风险管理
│
├── gui/                     # GUI 仪表盘
│   ├── __init__.py
│   ├── dashboard.py         # 基础仪表盘
│   ├── dashboard_enhanced.py # 增强仪表盘
│   └── charts.py            # 图表组件
│
├── web/                     # Web 界面
│   ├── __init__.py
│   ├── app.py               # Flask 应用
│   └── app_pro.py           # 专业版
│
├── scripts/                 # 工具脚本
│   └── ...
│
├── config.py                # 配置文件
├── run.py                   # ✅ 统一入口脚本 (新增)
├── main.py                  # 旧入口 (保留兼容)
└── requirements.txt         # 依赖
```

## 🚀 使用方式

### 方式 1: 使用统一入口 (推荐)
```bash
# 运行完整流程
python run.py

# 启动 GUI
python run.py --gui

# 生成报告
python run.py --report

# 自定义资金
python run.py --capital 500000
```

### 方式 2: 使用核心管理器 (编程方式)
```python
from core.manager import FuturesQuantManager, run_quant_system

# 一键运行
result = run_quant_system(initial_capital=1_000_000)

# 或使用管理器类
manager = FuturesQuantManager()
manager.initialize()
manager.load_market_data()
manager.generate_signals()
manager.execute_trades()
manager.evaluate_performance()
manager.analyze()
result = manager.get_status()
```

### 方式 3: 使用旧入口 (兼容模式)
```bash
python main.py
python main.py --gui
```

## 📦 模块说明

### core (核心模块)
- **manager.py**: 系统管理器，统一初始化、执行流程、错误处理
- 提供单一入口点和简洁的 API

### analysis (分析模块)
- **evaluator.py**: 基础绩效评估 (收益率/夏普/回撤等)
- **evaluation_system.py**: ✅ 公平公正评估系统
  - 多维度指标 (夏普/索提诺/卡玛/信息比率)
  - 尾部风险 (VaR/CVaR)
  - 统计显著性检验
  - 综合评分 (0-100)
- **analytics_engine.py**: ✅ 深度分析引擎
  - 绩效归因 (品种/方向/策略/时间/仓位)
  - 因子分析 (IC/IR/暴露/衰减)
  - 相关性分析
  - 市场状态识别
  - 策略诊断
- **backtester_pro.py**: 专业回测引擎 (向量化/并行)
- **report_generator.py**: 日/周/月报生成

### strategy (策略模块)
- **indicators.py**: 203 个技术指标计算
- **signals.py**: 232 个策略信号生成
- **strategies_enhanced.py**: 增强策略库
- **factors_enhanced.py**: 因子库 (553 个因子)

### market (市场数据)
- **feeder.py**: 行情数据加载 (支持本地/模拟/Tushare)

### trading (交易模块)
- **portfolio.py**: 持仓管理 + 风控
- **executor.py**: 订单执行 (滑点/手续费)
- **risk_manager.py**: 风险控制

## 🎯 核心 API

### FuturesQuantManager 类

```python
manager = FuturesQuantManager(
    initial_capital=1_000_000,
    log_level='INFO'
)

# 分步执行
manager.initialize()           # 初始化组件
manager.load_market_data()     # 加载数据
manager.generate_signals()     # 生成信号
manager.execute_trades()       # 执行交易
results = manager.evaluate_performance()  # 评估
analysis = manager.analyze()   # 深度分析
manager.generate_report('daily')  # 生成报告
status = manager.get_status()  # 获取状态
manager.shutdown()             # 关闭
```

### run_quant_system 函数

```python
result = run_quant_system(
    initial_capital=1_000_000,
    generate_report=False
)

# 返回结构
{
    'success': True,
    'results': {...},      # 绩效评估结果
    'analysis': {...},     # 分析结果
    'duration_seconds': 12.5,
    'portfolio_stats': {...}
}
```

## 📊 评估指标

### 基础指标
- 总收益率 / 年化收益率
- 夏普比率 / 索提诺比率 / 卡玛比率
- 最大回撤 / 平均回撤 / 回撤持续期
- 胜率 / 盈亏比 / 波动率

### 高级指标 (公平公正评估系统)
- 信息比率
- VaR (95%/99%) / CVaR (95%/99%)
- 统计显著性 (t 检验/p 值/置信区间)
- 综合评分 (0-100，6 维度加权)

### 分析功能 (深度分析引擎)
- 绩效归因 (品种/方向/策略/时间/仓位)
- 因子分析 (IC/IR/暴露/衰减/相关性)
- 市场状态识别 (趋势/震荡/波动率)
- 策略诊断 (问题定位/健康度评分)

## 🔄 执行流程

```
┌─────────────────────────────────────────────────────────┐
│                   run.py / manager                       │
├─────────────────────────────────────────────────────────┤
│  1. initialize()    → 初始化所有组件                    │
│  2. load_data()     → 加载市场数据 (53 合约)              │
│  3. generate_signals() → 生成策略信号 (232 策略)          │
│  4. execute_trades() → 执行交易 (滑点/手续费)            │
│  5. evaluate()      → 绩效评估 (基础 + 公平)              │
│  6. analyze()       → 深度分析 (归因/诊断)               │
│  7. generate_report() → 生成报告 (可选)                  │
└─────────────────────────────────────────────────────────┘
```

## 📝 更新日志

### 2026-04-18
- ✅ 新增 `core/manager.py` - 统一系统管理器
- ✅ 新增 `run.py` - 统一入口脚本
- ✅ 新增 `analysis/evaluation_system.py` - 公平公正评估系统
- ✅ 新增 `analysis/analytics_engine.py` - 深度分析引擎
- ✅ 更新所有模块 `__init__.py` - 统一导出接口
- ✅ 优化项目结构，模块化管理

### 2026-03-12
- 基础版本完成 (53 合约/232 策略/203 指标)
