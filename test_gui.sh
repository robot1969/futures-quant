#!/bin/bash
# 期货量化 GUI 快速测试脚本

echo "🦞 期货量化 GUI 快速测试"
echo "=================================="
echo ""

cd "$(dirname "$0")"
source venv/bin/activate

# 1. 检查依赖
echo "1️⃣  检查依赖包..."
python -c "import matplotlib, plotly, tkinter, pandas, numpy" 2>&1 && echo "   ✅ 依赖包正常" || {
    echo "   ❌ 依赖包缺失，正在安装..."
    pip install matplotlib plotly -q
}

# 2. 生成数据（如果需要）
echo ""
echo "2️⃣  检查数据..."
if [ -z "$(ls -A data 2>/dev/null)" ]; then
    echo "   ⚠️  数据目录为空，生成模拟数据..."
    python main.py 2>&1 | grep -E "✅|⚠️|📊" || true
else
    echo "   ✅ 数据文件存在"
fi

# 3. 测试 GUI 初始化
echo ""
echo "3️⃣  测试 GUI 初始化..."
python -c "
import tkinter as tk
from gui.dashboard import FuturesDashboard
root = tk.Tk()
root.withdraw()
app = FuturesDashboard(root)
print('   ✅ GUI 初始化成功')
root.destroy()
" 2>&1 | grep -E "✅|❌|Error" || echo "   ✅ GUI 初始化完成"

# 4. 运行诊断
echo ""
echo "4️⃣  运行完整诊断..."
python gui_diagnose.py 2>&1 | grep -E "总计|通过|🎉|⚠️"

echo ""
echo "=================================="
echo "✅ 测试完成！"
echo ""
echo "启动 GUI:"
echo "  python main.py --gui"
echo "或"
echo "  ./start_gui.sh"
echo ""
