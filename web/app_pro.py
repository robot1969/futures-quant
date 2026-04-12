"""
=============================================================================
期货量化系统 - 专业 Web Dashboard
=============================================================================
功能:
  - 实时绩效监控
  - 策略对比分析
  - 因子库管理
  - 回测结果可视化
  - 参数优化界面
  - 报告生成
=============================================================================
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONTRACTS, TRADING_CONFIG
from market.feeder import MarketDataFeeder
from strategy.signals import StrategyGenerator
from strategy.indicators import IndicatorEngine
from strategy.factors_enhanced import EnhancedFactorEngine
from strategy.strategies_enhanced import EnhancedStrategyEngine
from trading.executor import OrderExecutor
from trading.portfolio import Portfolio
from analysis.evaluator import PerformanceEvaluator
from analysis.ranker import StrategyRanker
from analysis.backtester_pro import ProBacktester

app = Flask(__name__)
app.config['SECRET_KEY'] = 'futures-quant-2026'

# 全局状态
state = {
    'portfolio': None,
    'market': None,
    'results': {},
    'backtest_results': {},
    'last_update': None
}


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """首页 - 核心绩效仪表板"""
    return render_template('pro_dashboard.html', page='overview')


@app.route('/strategies')
def strategies():
    """策略库页面"""
    return render_template('pro_strategies.html', page='strategies')


@app.route('/factors')
def factors():
    """因子库页面"""
    return render_template('pro_factors.html', page='factors')


@app.route('/backtest')
def backtest():
    """回测页面"""
    return render_template('pro_backtest.html', page='backtest')


@app.route('/optimization')
def optimization():
    """优化页面"""
    return render_template('pro_optimization.html', page='optimization')


@app.route('/reports')
def reports():
    """报告页面"""
    return render_template('pro_reports.html', page='reports')


# ==================== API 接口 ====================

@app.route('/api/overview')
def api_overview():
    """获取概览数据"""
    if state['portfolio'] is None:
        # 初始化
        state['portfolio'] = Portfolio(TRADING_CONFIG['initial_capital'])
        state['market'] = MarketDataFeeder()
        state['market'].load_data()
    
    portfolio = state['portfolio']
    stats = portfolio.get_stats()
    
    return jsonify({
        'equity': stats['current_equity'],
        'cash': stats['cash'],
        'positions': stats['open_positions'],
        'total_trades': stats['total_trades'],
        'closed_pnl': stats['closed_pnl'],
        'last_update': state['last_update'] or datetime.now().isoformat()
    })


@app.route('/api/strategies')
def api_strategies():
    """获取策略列表"""
    engine = EnhancedStrategyEngine()
    strategies = []
    
    for s in engine.strategies[:100]:  # 返回前 100 个
        strategies.append({
            'name': s['name'],
            'type': s['type'],
            'category': s['category'],
            'logic': s['logic'],
            'params': s['params']
        })
    
    # 分类统计
    categories = {}
    for s in engine.strategies:
        cat = s['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    return jsonify({
        'total': engine.get_strategy_count(),
        'categories': categories,
        'strategies': strategies
    })


@app.route('/api/factors')
def api_factors():
    """获取因子列表"""
    # 因子类别
    factor_categories = {
        'traditional': {'count': 203, 'description': '传统技术指标'},
        'statistical': {'count': 50, 'description': '高级统计因子'},
        'volume_price': {'count': 60, 'description': '价量关系因子'},
        'volatility': {'count': 40, 'description': '波动率因子'},
        'momentum': {'count': 50, 'description': '动量反转因子'},
        'ml': {'count': 80, 'description': '机器学习因子'},
        'term_structure': {'count': 30, 'description': '期限结构因子'},
        'fundamental': {'count': 40, 'description': '基本面因子'},
    }
    
    total = sum(c['count'] for c in factor_categories.values())
    
    return jsonify({
        'total': total,
        'categories': factor_categories
    })


@app.route('/api/backtest/run', methods=['POST'])
def api_backtest_run():
    """运行回测"""
    data = request.json
    strategy_name = data.get('strategy', 'SingleFactor_MOM_5')
    
    # 初始化组件
    market = MarketDataFeeder()
    market.load_data()
    
    strategy_engine = EnhancedStrategyEngine()
    backtester = ProBacktester()
    
    # 运行回测
    market_data = {symbol: market.get_ohlcv(symbol) for symbol in market.get_all_symbols()[:10]}
    result = backtester.run_backtest(market_data, strategy_engine, strategy_name)
    
    # 保存结果
    state['backtest_results'][strategy_name] = result
    
    return jsonify({
        'success': True,
        'result': {
            'total_return': result['total_return'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown': result['max_drawdown'],
            'win_rate': result['win_rate'],
            'total_trades': result['total_trades'],
            'final_equity': result['final_equity']
        },
        'equity_curve': result['equity_curve'][-100:]  # 返回最近 100 个点
    })


@app.route('/api/backtest/compare', methods=['POST'])
def api_backtest_compare():
    """多策略对比回测"""
    data = request.json
    strategies = data.get('strategies', [])
    
    if not strategies:
        strategies = [
            'SingleFactor_MOM_5',
            'SingleFactor_RSI_14',
            'Trend_MA5_20_ma_cross_trailing_stop_lb10'
        ]
    
    market = MarketDataFeeder()
    market.load_data()
    
    strategy_engine = EnhancedStrategyEngine()
    backtester = ProBacktester()
    
    market_data = {symbol: market.get_ohlcv(symbol) for symbol in market.get_all_symbols()[:10]}
    results, ranked = backtester.run_multi_strategy_backtest(market_data, strategy_engine, strategies, parallel=False)
    
    # 格式化结果
    comparison = []
    for name, result in results.items():
        comparison.append({
            'name': name,
            'total_return': result['total_return'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown': result['max_drawdown'],
            'win_rate': result['win_rate'],
            'calmar_ratio': result.get('calmar_ratio', 0)
        })
    
    return jsonify({
        'success': True,
        'comparison': comparison,
        'ranked': [r[0] for r in ranked[:10]]
    })


@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    """参数优化"""
    data = request.json
    strategy_name = data.get('strategy', 'SingleFactor_MOM_5')
    param_grid = data.get('param_grid', {})
    
    market = MarketDataFeeder()
    market.load_data()
    
    strategy_engine = EnhancedStrategyEngine()
    backtester = ProBacktester()
    
    market_data = {symbol: market.get_ohlcv(symbol) for symbol in market.get_all_symbols()[:5]}
    results = backtester.run_parameter_optimization(market_data, strategy_engine, strategy_name, param_grid)
    
    # 返回最佳结果
    if results:
        best = results[0]
        return jsonify({
            'success': True,
            'best_params': best['params'],
            'best_sharpe': best['sharpe_ratio'],
            'best_return': best['total_return'],
            'all_results': results[:20]  # 返回前 20 个结果
        })
    
    return jsonify({'success': False, 'error': '优化失败'})


@app.route('/api/positions')
def api_positions():
    """获取持仓信息"""
    if state['portfolio'] is None:
        return jsonify({'positions': []})
    
    executor = OrderExecutor(state['portfolio'])
    positions = executor.get_positions_summary()
    
    return jsonify({'positions': positions})


@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    """生成报告"""
    data = request.json
    report_type = data.get('type', 'daily')
    
    report = {
        'type': report_type,
        'date': datetime.now().isoformat(),
        'summary': {},
        'performance': {},
        'positions': [],
        'trades': [],
        'recommendations': []
    }
    
    if state['portfolio']:
        stats = state['portfolio'].get_stats()
        report['summary'] = {
            'equity': stats['current_equity'],
            'cash': stats['cash'],
            'positions': stats['open_positions'],
            'trades': stats['total_trades']
        }
    
    return jsonify(report)


# ==================== 静态文件 ====================

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


# ==================== 启动服务 ====================

def run_dashboard(host='0.0.0.0', port=5002, debug=True):
    """启动 Dashboard"""
    print(f"🚀 启动专业 Web Dashboard")
    print(f"   访问地址：http://localhost:{port}")
    print(f"   专业版：http://localhost:{port}/pro")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
