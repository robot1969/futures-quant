#!/bin/bash
# 增强版 GUI 快速测试脚本

cd "$(dirname "$0")"

echo "🦞 增强版 GUI 测试"
echo "=============================================="
echo ""

# 激活虚拟环境
source venv/bin/activate

# 运行诊断
echo "🔍 运行诊断检查..."
python gui_diagnose.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有检查通过！"
    echo ""
    echo "启动增强版 GUI..."
    echo ""
    python gui/dashboard_enhanced.py
else
    echo ""
    echo "❌ 诊断失败，请先修复上述问题"
    exit 1
fi
