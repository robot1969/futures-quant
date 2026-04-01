# 🦞 期货量化模拟盘系统

> **完全本地化的期货量化交易系统** | 53 合约 | 232 策略 | 203 指标 | 10 周期

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📋 项目简介

这是一个**完全本地化**的期货量化交易模拟系统，支持：

- ✅ **53 个期货合约** - 股指/能化/黑色/有色/农产品全覆盖
- ✅ **10 个时间周期** - 1 分钟~月线
- ✅ **203 个技术指标** - MA/EMA/RSI/MACD/布林带/ATR 等
- ✅ **232 个交易策略** - 均线/突破/RSI/MACD/KDJ/形态/组合
- ✅ **公平数据生成** - 本地随机生成，确保公平测试
- ✅ **风险管理** - 止损/止盈/仓位管理
- ✅ **Web Dashboard** - 实时绩效监控 + 专业版分析

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/futures_quant.git
cd futures_quant
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行系统

```bash
# 命令行运行（文本输出）
python main.py

# 启动桌面仪表盘（GUI 界面）
python main.py --gui
# 或
./start_gui.sh

# 或启动 Web Dashboard
python web/app.py
```

访问 Dashboard:
- **桌面版**: 运行 `python main.py --gui`
- **标准版**: http://localhost:5001/
- **专业版**: http://localhost:5001/pro

---

## 📊 系统配置

### 期货合约（53 个）

| 分类 | 数量 | 合约代码 |
|------|------|----------|
| **股指期货** | 4 | IF, IC, IH, IM |
| **能化期货** | 14 | SC, LU, FU, TA, MA, EG, PF, RU, NR, BU, V, PP, L, EB |
| **黑色期货** | 9 | RB, HC, J, JM, ZC, I, SS, FG, SF |
| **有色金属** | 9 | CU, AL, ZN, PB, NI, SN, AU, AG, RC |
| **农产品** | 17 | M, Y, P, A, B, C, CS, SR, CF, SM, AP, CJ, JR, LR, OI, RS, SP |

### 技术指标（203 个）

- **趋势指标**: MA, EMA, WMA (多周期)
- **动量指标**: RSI, KDJ, MACD, CCI, MOM, ROC
- **波动指标**: 布林带，ATR, Keltner, Donchian
- **成交量指标**: VOL_MA, OBV, VWAP, AD, CMF
- **形态指标**: Doji, Hammer, Engulfing 等
- **组合因子**: MA+RSI, MACD+BB, KDJ+RSI 等

### 交易策略（232 个）

| 类型 | 数量 | 说明 |
|------|------|------|
| 均线交叉 | 30 | 快慢均线金叉/死叉 |
| 突破策略 | 20 | 高低点突破 |
| RSI 策略 | 18 | 超买超卖 |
| 布林策略 | 15 | 布林带收口/扩张 |
| MACD 策略 | 12 | MACD 金叉/死叉 |
| KDJ 策略 | 12 | KDJ 超买超卖 |
| 成交量策略 | 12 | 成交量突破 |
| 形态策略 | 15 | K 线形态识别 |
| 组合策略 | 20 | 多指标组合 |
| 其他策略 | 78 | 波动率/动量/ADX 等 |

---

## 📁 项目结构

```
futures_quant/
├── main.py                  # 主程序入口
├── config.py                # 配置文件（合约/周期/参数）
├── requirements.txt         # Python 依赖
├── README.md                # 项目说明
├── .gitignore              # Git 忽略文件
│
├── market/
│   └── feeder.py           # 行情数据（公平随机生成）
│
├── strategy/
│   ├── indicators.py       # 203 个技术指标
│   └── signals.py          # 232 个策略信号
│
├── trading/
│   ├── executor.py         # 订单执行器
│   ├── portfolio.py        # 持仓管理（含风控）
│   └── risk_manager.py     # 风险管理系统
│
├── analysis/
│   ├── evaluator.py        # 绩效评估
│   ├── ranker.py           # 策略排名
│   └── backtester.py       # 回测引擎
│
├── web/
│   ├── app.py              # Flask Web 应用
│   └── templates/
│       ├── dashboard.html      # 标准版 Dashboard
│       └── dashboard_pro.html  # 专业版 Dashboard
│
├── data/                   # 数据目录（自动生成）
├── logs/                   # 日志目录（自动生成）
├── reports/                # 报告目录（自动生成）
└── cache/                  # 缓存目录（自动生成）
```

---

## 🎯 核心特性

### 1. 公平数据生成

所有合约使用统一的公平随机生成机制：
- 统一起点价格（5000 点）
- 统一波动率范围（1%-2.5%）
- 独立随机种子（每合约唯一）
- 可重复验证

### 2. 智能信号过滤

**信号处理流程：**
1. 信号生成 → 为每个合约生成多个候选信号
2. 强度过滤 → 只保留强度 > 0.7 的高质量信号
3. 权重排序 → 按策略类型赋予不同权重
4. 去重冲突 → 每个合约只保留一个方向的最强信号
5. 趋势过滤 → 根据 200 日均线判断趋势方向
6. 执行交易 → 执行最终筛选后的信号

**信号优先级权重：**
```python
Resonance (多指标共振): 1.0    # 最强
Breakout (突破): 0.9
MA_Multiple (多均线): 0.85
MACD_Strong: 0.85
BB_Break (布林突破): 0.8
RSI_Deep: 0.8
KDJ_Deep: 0.75
Default: 0.7
```

### 3. 动态止损止盈

基于 ATR 自动计算：
- **止损**: 2 倍 ATR（最多不超过 10%）
- **止盈**: 3 倍 ATR（最多不超过 20%）

### 4. 风险管理

- 单品种仓位 ≤ 30%
- 总杠杆 ≤ 50%
- 止损/止盈自动执行
- 交易冷却期控制

---

## 📈 绩效指标

系统提供完整的绩效评估：

| 指标 | 说明 | 计算公式 |
|------|------|----------|
| **总收益率** | 总体盈利比例 | (期末资金 - 期初资金) / 期初资金 |
| **夏普比率** | 风险调整后收益 | (收益率 - 无风险利率) / 波动率 |
| **最大回撤** | 最大亏损幅度 | 最大连续亏损比例 |
| **胜率** | 盈利交易比例 | 盈利次数 / 总交易次数 |
| **盈亏比** | 平均盈亏比 | 平均盈利 / 平均亏损 |
| **卡尔玛比率** | 收益/回撤比 | 总收益率 / 最大回撤 |
| **索提诺比率** | 下行波动调整 | (收益率 - 无风险利率) / 下行波动率 |
| **波动率** | 收益波动程度 | 收益率的标准差 (年化) |

---

## 🌐 Web Dashboard

### 标准版 Dashboard
- 核心绩效卡片
- 资金曲线
- 持仓明细
- 策略排名
- 交易信号

### 专业版 Dashboard ⭐
- **203 个技术指标** - 分类展示
- **232 个策略逻辑** - 详细逻辑说明
- **实时交易信号** - 强度排序 + 可视化
- **持仓详情** - 含止损止盈价
- **53 个合约** - 完整参数
- **因子分析** - IC 统计 + 热力图
- **风险监控** - VaR + 仓位分析

---

## 🔧 配置说明

### config.py 主要配置

```python
# 交易配置
TRADING_CONFIG = {
    "initial_capital": 1_000_000,  # 初始资金：100 万元
    "commission_rate": 0.0003,     # 手续费率：万分之 3
    "commission_min": 20,          # 最低手续费：20 元/手
    "slippage": 0.0001,            # 滑点：万分之 1
    "margin_rate": 0.12,           # 保证金比例：12%
}

# 风控参数
stop_loss_pct = 0.05    # 止损 5%
take_profit_pct = 0.10  # 止盈 10%
max_position_per_symbol = 0.3  # 单品种最大仓位 30%
```

---

## 📊 运行示例

### 命令行输出

```
============================================================
🦞 期货量化模拟盘 | 2026-03-16 09:00:00
============================================================

📊【系统配置】
   期货合约数量：53 个
   时间周期数量：10 个

📦【步骤 1/8】初始化交易组件...
   ✅ 组件初始化完成

📊【步骤 2/8】加载市场数据...
   ✅ 成功加载 53 个期货合约数据

🎯【步骤 3/8】生成交易策略信号...
   ✅ 共生成 18 个高质量交易信号

💰【步骤 4/8】执行交易订单...
   ✅ 开多 IF x1 @ 5513.36
   ✅ 开多 IC x2 @ 4850.20
   ...

📉【步骤 5/8】计算绩效指标...

🏆【步骤 6/8】策略排名...

============================================================
📊【绩效评估结果】
   总收益率：-0.32%
   夏普比率：0.00
   最大回撤：0.00%
   胜率：0.00%
   盈亏比：0.00

📈【交易统计】
   总交易次数：18
   当前持仓：18 个
   已实现盈亏：0.00 元
   当前权益：996,757.02 元

✅ 每日量化交易任务执行完成!
============================================================
```

---

## ⚠️ 风险提示

1. **模拟盘性质**: 本系统为模拟交易系统，不构成投资建议
2. **数据公平性**: 使用随机生成数据，与真实市场存在差异
3. **策略风险**: 历史表现不代表未来收益
4. **资金管理**: 请合理控制仓位，避免过度交易

---

## 🛠️ 开发环境

- **Python**: 3.10+
- **主要依赖**:
  - pandas
  - numpy
  - pandas-ta
  - flask
  - chart.js (前端)

---

## 📝 更新日志

### v2.0 (2026-03-16)
- ✅ 信号去重系统 - 每个合约只保留最强信号
- ✅ 趋势过滤 - 200 日均线判断趋势
- ✅ 动态止损止盈 - 基于 ATR 自动计算
- ✅ 专业版 Dashboard - 203 因子/232 策略完整展示
- ✅ 绩效评估增强 - 8 项指标 + 详细统计

### v1.0 (2026-03-12)
- ✅ 基础框架搭建
- ✅ 53 个合约支持
- ✅ 203 个技术指标
- ✅ 232 个交易策略

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- **作者**: OpenClaw 🦞
- **项目**: 期货量化模拟盘系统
- **版本**: v2.0

---

**🦞 让量化交易更公平、更透明、更智能！**

---

## 🚀 部署到云平台

### GitHub Actions (CI/CD)

创建 `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python main.py
```

### 部署到 Heroku

1. 创建 `Procfile`:
```
web: python web/app.py
```

2. 创建 `runtime.txt`:
```
python-3.10.0
```

3. 部署:
```bash
heroku create futures-quant
git push heroku main
heroku open
```

### 部署到 Railway

1. 连接 GitHub 仓库
2. 自动检测 Python
3. 设置环境变量
4. 部署完成

### 部署到 VPS

```bash
# 安装依赖
pip install -r requirements.txt

# 使用 gunicorn 运行
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 web.app:app

# 或使用 systemd 服务
sudo systemctl start futures-quant
```

---

## 📚 文档

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考
- [SUMMARY.md](SUMMARY.md) - 项目总结
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Dashboard 使用指南
- [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md) - 优化方案

---

*最后更新：2026-03-16*
