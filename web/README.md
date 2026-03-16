# 🦞 期货量化 Web Dashboard

实时可视化监控你的量化交易策略！

## 功能特性

- 📊 **绩效概览** - 收益率/夏普比率/最大回撤/胜率
- 📈 **资金曲线** - 动态展示权益变化
- 🏆 **策略排名** - TOP10 策略得分榜
- 📋 **持仓监控** - 实时持仓明细与盈亏
- 🎯 **交易信号** - 最新生成的交易信号

## 快速启动

```bash
# 方式 1: 使用启动脚本
./start_web.sh

# 方式 2: 手动启动
source venv/bin/activate
python web/app.py
```

## 访问地址

- 本地：http://localhost:5000
- 局域网：http://<你的 IP>:5000

## API 端点

| 端点 | 说明 |
|------|------|
| `/api/summary` | 概览数据 |
| `/api/performance` | 详细绩效 |
| `/api/positions` | 持仓数据 |
| `/api/rankings` | 策略排名 |
| `/api/signals` | 交易信号 |
| `/api/equity` | 资金曲线 |
| `/api/refresh` | 强制刷新 |

## 技术栈

- **后端**: Flask
- **前端**: Chart.js + 原生 HTML/CSS/JS
- **数据**: 来自交易引擎实时计算

## 注意事项

- 首次访问会自动运行交易引擎（约 30-60 秒）
- 点击"刷新数据"可强制重新计算
- 默认端口 5000，可在 app.py 中修改

---

🦞 2026-03-14 | OpenClaw
