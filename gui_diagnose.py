#!/usr/bin/env python
"""
期货量化 GUI 诊断工具
用于快速定位 GUI 启动失败的原因
"""
import sys
import os
import traceback

def check_step(name, func):
    """检查一个步骤"""
    print(f"\n{'='*60}")
    print(f"检查：{name}")
    print('='*60)
    try:
        result = func()
        print(f"✅ {name} - 通过")
        if result:
            print(f"   详情：{result}")
        return True
    except Exception as e:
        print(f"❌ {name} - 失败")
        print(f"   错误：{e}")
        traceback.print_exc()
        return False

def check_python():
    """检查 Python 版本"""
    version = sys.version.split()[0]
    return f"Python {version}"

def check_tkinter():
    """检查 tkinter"""
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    try:
        version = root.tk.call('tk', 'version')
    except:
        version = str(root.tk)
    root.destroy()
    return f"tkinter {version}"

def check_matplotlib():
    """检查 matplotlib"""
    import matplotlib
    return f"matplotlib {matplotlib.__version__}, 后端：{matplotlib.get_backend()}"

def check_pandas():
    """检查 pandas"""
    import pandas as pd
    return f"pandas {pd.__version__}"

def check_numpy():
    """检查 numpy"""
    import numpy as np
    return f"numpy {np.__version__}"

def check_project_structure():
    """检查项目结构"""
    required_dirs = ['market', 'strategy', 'trading', 'analysis', 'gui', 'data']
    required_files = ['main.py', 'config.py', 'requirements.txt']
    
    missing_dirs = [d for d in required_dirs if not os.path.isdir(d)]
    missing_files = [f for f in required_files if not os.path.isfile(f)]
    
    if missing_dirs:
        raise Exception(f"缺少目录：{', '.join(missing_dirs)}")
    if missing_files:
        raise Exception(f"缺少文件：{', '.join(missing_files)}")
    
    return f"目录：{len(required_dirs)}个，文件：{len(required_files)}个"

def check_data():
    """检查数据文件"""
    data_dir = 'data'
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        return "数据目录已创建（首次运行会自动生成数据）"
    
    files = os.listdir(data_dir)
    if not files:
        return "数据目录为空（首次运行会自动生成数据）"
    
    return f"数据文件：{len(files)}个"

def check_config():
    """检查配置"""
    from config import CONTRACTS, TRADING_CONFIG
    return f"合约：{len(CONTRACTS)}个，初始资金：{TRADING_CONFIG['initial_capital']:,}"

def check_modules():
    """检查核心模块"""
    from market.feeder import MarketDataFeeder
    from strategy.signals import StrategyGenerator
    from strategy.indicators import IndicatorEngine
    from trading.executor import OrderExecutor
    from trading.portfolio import Portfolio
    from analysis.evaluator import PerformanceEvaluator
    return "所有核心模块加载成功"

def check_gui_import():
    """检查 GUI 模块导入"""
    from gui.dashboard import FuturesDashboard
    return "GUI 模块导入成功"

def check_gui_init():
    """检查 GUI 初始化"""
    import tkinter as tk
    from gui.dashboard import FuturesDashboard
    
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    try:
        app = FuturesDashboard(root)
        result = "GUI 初始化成功"
    finally:
        root.destroy()
    
    return result

def check_data_load():
    """检查数据加载"""
    from config import TRADING_CONFIG
    from market.feeder import MarketDataFeeder
    from trading.portfolio import Portfolio
    
    portfolio = Portfolio(TRADING_CONFIG["initial_capital"])
    market = MarketDataFeeder("data/")
    
    market_data = market.load_data()
    symbols = market.get_all_symbols()
    
    return f"加载 {len(symbols)} 个合约数据"

def main():
    """运行诊断"""
    print("\n🔍 期货量化 GUI 诊断工具")
    print("="*60)
    
    # 切换到项目目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"工作目录：{os.getcwd()}")
    
    # 检查清单
    checks = [
        ("Python 版本", check_python),
        ("tkinter", check_tkinter),
        ("matplotlib", check_matplotlib),
        ("pandas", check_pandas),
        ("numpy", check_numpy),
        ("项目结构", check_project_structure),
        ("数据文件", check_data),
        ("配置文件", check_config),
        ("核心模块", check_modules),
        ("GUI 导入", check_gui_import),
        ("GUI 初始化", check_gui_init),
        ("数据加载", check_data_load),
    ]
    
    # 执行检查
    results = []
    for name, func in checks:
        passed = check_step(name, func)
        results.append((name, passed))
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("诊断结果汇总")
    print('='*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✅" if p else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有检查通过！GUI 应该可以正常运行。")
        print("\n启动命令:")
        print("  python main.py --gui")
        print("  或")
        print("  ./start_gui.sh")
    else:
        print("\n⚠️  部分检查失败，请根据上述错误信息进行修复。")
        print("\n常见问题解决:")
        print("  1. tkinter 缺失：重新安装 Python (确保包含 tkinter)")
        print("  2. 数据缺失：运行 python main.py 生成数据")
        print("  3. 模块缺失：pip install -r requirements.txt")
        print("  4. 目录错误：确保在正确的目录下运行")
    
    print()
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
