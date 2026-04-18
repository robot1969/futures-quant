# 🦞 期货量化模拟盘系统

> 全品种全周期的期货量化交易模拟系统，支持 53 个合约、232 个策略、203 个技术指标

## 🚀 快速开始

### 安装依赖
```bash
cd ~/futures_quant
source venv/bin/activate
pip install -r requirements.txt
```

### 运行系统
```bash
# 方式 1: 使用统一入口 (推荐)
python run.py

# 方式 2: 启动 GUI 仪表盘
python run.py --gui

# 方式 3: 生成报告
python run.py --report

# 方式 4: 查看系统状态
python run.py --status
```

## 📊 系统特性

### 核心功能
- ✅ **53 个期货合约** - 股指/能化/黑色/有色/农产品全覆盖
- ✅ **10 个时间周期** - 1 分钟~月线
- ✅ **203 个技术指标** - MA/EMA/RSI/MACD/布林/KDJ/CCI...
- ✅ **232 个交易策略** - 均线/突破/形态/多因子...
- ✅ **公平公正评估系统** - 多维度绩效评估 + 统计显著性检验
- ✅ **深度分析引擎** - 绩效归因/因子分析/策略诊断

### 评估系统
| 指标类型 | 具体指标 |
|---------|---------|
| 基础收益 | 总收益率/年化收益率 |
| 风险调整 | 夏普/索提诺/卡玛/信息比率 |
| 风险指标 | 最大回撤/平均回撤/波动率 |
| 尾部风险 | VaR(95/99%)/CVaR(95/99%) |
| 交易分析 | 胜率/盈亏比/持仓周期 |
| 统计检验 | t 检验/p 值/置信区间 |
| 综合评分 | 0-100 分 (6 维度加权) |

### 分析功能
- 📈 **绩效归因**: 品种/方向/策略/时间/仓位贡献分析
- 🔬 **因子分析**: IC/IR/因子暴露/因子衰减/相关性矩阵
- 🌊 **市场状态**: 趋势/震荡/波动率识别
- 🩺 **策略诊断**: 问题定位/健康度评分/优化建议

## 📁 项目结构

```
futures_quant/
├── core/                    # 核心模块
│   ├── manager.py           # 系统管理器 (统一入口)
│   └── __init__.py
│
├── analysis/                # 分析模块
│   ├── evaluation_system.py # 公平公正评估系统
│   ├── analytics_engine.py  # 深度分析引擎
│   ├── evaluator.py         # 基础绩效评估
│   ├── backtester_pro.py    # 专业回测引擎
│   └── report_generator.py  # 报告生成器
│
├── strategy/                # 策略模块
│   ├── indicators.py        # 203 个技术指标
│   ├── signals.py           # 232 个策略信号
│   └── factors_enhanced.py  # 因子库
│
├── market/                  # 市场数据
│   └── feeder.py            # 行情数据源
│
├── trading/                 # 交易模块
│   ├── portfolio.py         # 持仓管理
│   ├── executor.py          # 订单执行
│   └── risk_manager.py      # 风险管理
│
├── gui/                     # GUI 仪表盘
├── web/                     # Web 界面
├── run.py                   # 统一入口脚本
└── config.py                # 配置文件
```

## 🎯 核心 API

### 一键运行
```python
from core.manager import run_quant_system

result = run_quant_system(initial_capital=1_000_000)
print(f"综合评分：{result['results']['composite_score']:.1f}/100")
print(f"总收益率：{result['results']['total_return']:.2%}")
```

### 分步控制
```python
from core.manager import FuturesQuantManager

manager = FuturesQuantManager()
manager.initialize()           # 初始化
manager.load_market_data()     # 加载数据
manager.generate_signals()     # 生成信号
manager.execute_trades()       # 执行交易
results = manager.evaluate_performance()  # 评估
analysis = manager.analyze()   # 深度分析
manager.shutdown()             # 关闭
```

## 📈 输出示例

```
======================================================================
🦞 期货量化系统 | 2026-04-18 19:15:45
======================================================================

📊 【绩效评估结果】
   总收益率：-0.32%
   当前权益：¥996,831.20

🔍 【公平公正评估】
   综合评分：39.4/100
   夏普比率：0.00
   索提诺比率：0.00
   卡玛比率：-1.00
   最大回撤：0.32%
   
⚠️ 【尾部风险】
   VaR(95%): 0.00%
   CVaR(95%): 0.00%
   统计显著性：❌ 不显著

📈 【绩效归因 - 品种 Top5】
   1. 🟢 IF: ¥1,234.56 (12.3%)
   2. 🔴 RB: ¥-567.89 (-5.6%)
   ...

⚠️ 【策略诊断】
   健康度：GOOD
   建议:
      💡 建议进行参数敏感性分析
      💡 优化入场信号质量
```

## 🛠️ 配置说明

### config.py
```python
# 交易配置
TRADING_CONFIG = {
    'initial_capital': 1_000_000,  # 初始资金
    'commission_rate': 0.0003,     # 手续费率
    'slippage': 0.0001,            # 滑点
    'margin_rate': 0.12,           # 保证金率
}

# 风控配置
RISK_CONFIG = {
    'stop_loss_pct': 0.02,         # 止损比例
    'take_profit_pct': 0.04,       # 止盈比例
    'max_positions': 20,           # 最大持仓数
}
```

## 📝 更新日志

### 2026-04-18 - 系统整合
- ✅ 新增 `core/manager.py` - 统一系统管理器
- ✅ 新增 `run.py` - 统一入口脚本
- ✅ 新增 `evaluation_system.py` - 公平公正评估系统
- ✅ 新增 `analytics_engine.py` - 深度分析引擎
- ✅ 优化项目结构，模块化管理

### 2026-03-12 - 基础版本
- 53 个合约支持
- 232 个策略
- 203 个指标

## 📚 文档

- [项目结构说明](PROJECT_STRUCTURE.md)
- [快速启动指南](QUICK_START.md)
- [配置说明](config.py)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License
