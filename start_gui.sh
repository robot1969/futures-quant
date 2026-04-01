#!/bin/bash
# 期货量化模拟盘 - GUI 启动脚本

set -e  # 遇到错误立即退出

echo "🦞 期货量化桌面仪表盘启动器"
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误：未找到虚拟环境 venv"
    echo "请先运行：python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查数据目录
if [ ! -d "data" ] || [ -z "$(ls -A data 2>/dev/null)" ]; then
    echo "⚠️  数据目录为空，正在生成模拟数据..."
    python main.py || {
        echo "❌ 数据生成失败"
        exit 1
    }
fi

# 启动模式选择
if [ "$1" == "--enhanced" ] || [ "$1" == "-e" ]; then
    echo "✅ 启动增强版仪表盘 (10 指标 + 5 Tabs + 图表分析)..."
    echo ""
    python gui/dashboard_enhanced.py
else
    echo "✅ 启动标准版仪表盘..."
    echo ""
    echo "💡 提示：使用 --enhanced 或 -e 参数启动增强版"
    echo ""
    python main.py --gui
fi
