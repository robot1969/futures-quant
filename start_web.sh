#!/bin/bash
# 期货量化 Web Dashboard 启动脚本

echo "🦞 期货量化 Web Dashboard 启动中..."
echo "=" * 60

cd ~/futures_quant

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果缺失）
pip install -q flask 2>/dev/null

# 启动 Flask 应用
echo "📊 访问地址：http://localhost:5000"
echo "📊 局域网访问：http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):5000"
echo "=" * 60

python web/app.py
