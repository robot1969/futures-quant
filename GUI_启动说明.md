# 🖥️ 期货量化桌面仪表盘 - 启动说明

## ⚡ 快速启动（3 步）

### 第 1 步：安装依赖
```bash
cd ~/futures_quant
source venv/bin/activate
pip install matplotlib plotly
```

### 第 2 步：生成数据
```bash
python main.py
```

### 第 3 步：启动 GUI
```bash
python main.py --gui
```

---

## 🚀 三种启动方式

### 方式 1: 命令行参数（推荐）
```bash
python main.py --gui
```

### 方式 2: 启动脚本
```bash
./start_gui.sh
```

### 方式 3: 直接运行
```bash
python gui/dashboard.py
```

---

## 🔧 故障排查

### 运行诊断工具
```bash
python gui_diagnose.py
```

### 常见问题

#### ❌ matplotlib 缺失
```bash
pip install matplotlib plotly
```

#### ❌ 数据缺失
```bash
python main.py  # 生成数据
```

#### ❌ tkinter 不可用
```bash
# macOS
brew install python-tk

# Linux
sudo apt-get install python3-tk
```

---

## 📋 完整修复流程

如果启动失败，执行以下命令：

```bash
cd ~/futures_quant
source venv/bin/activate

# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成数据
python main.py

# 3. 运行诊断
python gui_diagnose.py

# 4. 启动 GUI
python main.py --gui
```

---

## 📖 详细文档

- **GUI_GUIDE.md** - 详细使用指南
- **桌面仪表盘快速启动.md** - 快速参考
- **修复指南.md** - 问题修复方案
- **CHANGELOG.md** - 更新日志

---

## 💡 界面预览

```
┌─────────────────────────────────────────────────────────────┐
│  🦞 期货量化模拟盘系统              [时间] [🔄刷新]         │
├─────────────────────────────────┬───────────────────────────┤
│  📊 绩效概览                    │  🎯 活跃策略              │
│  收益率  │  夏普比率            │  策略名  │信号│强度      │
│  最大回撤│  胜率                │  ...     │... │...       │
├─────────────────────────────────┼───────────────────────────┤
│  📋 持仓明细（可筛选/排序）      │  📈 统计分析              │
│  合约│方向│盈亏│盈亏%           │  交易次数：156           │
│  IF  │多  │+1.2 万│+2.3%        │  权益：¥954,322         │
└─────────────────────────────────┴───────────────────────────┘
```

---

## ⌨️ 快捷键

| 按键 | 功能 |
|------|------|
| `F5` | 刷新数据 |
| `Alt+F4` / `Cmd+W` | 关闭窗口 |

---

## 🎯 核心功能

- ✅ 实时绩效监控（收益率/夏普/回撤/胜率）
- ✅ 持仓明细表格（筛选/排序）
- ✅ 活跃策略列表（信号类型 + 强度）
- ✅ 统计分析面板（交易统计/资金状况）
- ✅ 自动刷新（30 秒间隔）
- ✅ 高级图表分析（K 线/权益曲线/收益分布）
- ✅ 报告导出功能

---

**🦞 祝交易顺利！**
