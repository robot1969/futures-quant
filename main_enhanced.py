"""
=============================================================================
期货量化模拟盘系统 - 增强版
=============================================================================
功能升级:
  - 553 个增强因子 (203 传统 + 350 新增)
  - 1000+ 增强策略 (232 传统 + 768 新增)
  - 专业回测引擎 (向量化/并行/压力测试)
  - 参数优化系统 (网格搜索/敏感性分析)
  - 专业 Web Dashboard
  - 自动化迭代系统
=============================================================================
"""
import sys
import os
from datetime import datetime
import argparse
import json

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TRADING_CONFIG, CONTRACTS, TIMEFRAMES
from market.feeder import MarketDataFeeder
from strategy.indicators import IndicatorEngine
from strategy.signals import StrategyGenerator
from strategy.factors_enhanced import EnhancedFactorEngine
from strategy.strategies_enhanced import EnhancedStrategyEngine
from trading.executor import OrderExecutor
from trading.portfolio import Portfolio
from analysis.evaluator import PerformanceEvaluator
from analysis.ranker import StrategyRanker
from analysis.backtester_pro import ProBacktester


def print_header():
    """打印标题"""
    print("=" * 80)
    print("🦞 期货量化模拟盘系统 | 增强版")
    print("=" * 80)
    print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   因子数量：553 个 (203 传统 + 350 增强)")
    print(f"   策略数量：1000+ 个 (232 传统 + 768 增强)")
    print("=" * 80)


def run_enhanced_system(gui=False, web=False, backtest=False, optimize=False):
    """运行增强版系统"""
    print_header()
    
    # ========== 步骤 1: 初始化组件 ==========
    print("\n📦 【步骤 1/6】初始化交易组件...")
    portfolio = Portfolio(TRADING_CONFIG["initial_capital"])
    market = MarketDataFeeder()
    executor = OrderExecutor(portfolio)
    indicator_engine = IndicatorEngine()
    factor_engine = EnhancedFactorEngine()
    strategy_generator = StrategyGenerator()
    enhanced_strategy_engine = EnhancedStrategyEngine()
    evaluator = PerformanceEvaluator()
    ranker = StrategyRanker()
    backtester = ProBacktester()
    print("   ✅ 组件初始化完成")
    
    # ========== 步骤 2: 加载市场数据 ==========
    print("\n📊 【步骤 2/6】加载市场数据...")
    market_data = market.load_data()
    symbols = market.get_all_symbols()
    print(f"   ✅ 成功加载 {len(symbols)} 个期货合约数据")
    
    # ========== 步骤 3: 计算增强因子 ==========
    print("\n📈 【步骤 3/6】计算增强因子...")
    all_factor_data = {}
    for symbol in symbols[:5]:  # 前 5 个合约
        df = market.get_ohlcv(symbol)
        if df is not None and len(df) > 50:
            df_factors = factor_engine.calculate_all(df)
            all_factor_data[symbol] = df_factors
    print(f"   ✅ 完成 {len(all_factor_data)} 个合约的因子计算")
    
    # ========== 步骤 4: 策略回测 ==========
    print("\n🔄 【步骤 4/6】策略回测...")
    if backtest:
        # 选择代表性策略进行回测
        test_strategies = [
            'SingleFactor_MOM_5',
            'SingleFactor_MOM_10',
            'SingleFactor_MOM_20',
            'SingleFactor_RSI_14',
            'SingleFactor_RSI_21',
            'Trend_MA5_20_ma_cross_trailing_stop_lb10',
            'Trend_MA20_60_ma_cross_trailing_stop_lb20',
            'MeanRev_BB_20_2.0_touch_band',
            'MeanRev_RSI_14_os30_ob70',
        ]
        
        # 准备回测数据
        backtest_data = {symbol: market.get_ohlcv(symbol) for symbol in symbols[:10]}
        
        # 运行回测
        results, ranked = backtester.run_multi_strategy_backtest(
            backtest_data, enhanced_strategy_engine, test_strategies, parallel=False
        )
        
        # 显示结果
        print("\n🏆 【回测结果 Top 5】")
        for i, (name, result) in enumerate(ranked[:5]):
            print(f"   {i+1}. {name}")
            print(f"      总收益：{result['total_return']:.2%}")
            print(f"      夏普比率：{result['sharpe_ratio']:.2f}")
            print(f"      最大回撤：{result['max_drawdown']:.2%}")
            print(f"      胜率：{result['win_rate']:.2%}")
    else:
        print("   ⏭️ 跳过回测 (使用 --backtest 启用)")
    
    # ========== 步骤 5: 参数优化 ==========
    print("\n⚙️ 【步骤 5/6】参数优化...")
    if optimize:
        # 优化 RSI 策略参数
        param_grid = {
            'period': [7, 14, 21],
            'oversold': [20, 25, 30],
            'overbought': [70, 75, 80]
        }
        
        backtest_data = {symbol: market.get_ohlcv(symbol) for symbol in symbols[:5]}
        results = backtester.run_parameter_optimization(
            backtest_data, enhanced_strategy_engine,
            'MeanRev_RSI_14_os30_ob70',
            param_grid, metric='sharpe_ratio'
        )
        
        if results:
            best = results[0]
            print("\n🎯 【最佳参数】")
            print(f"   参数：{best['params']}")
            print(f"   夏普比率：{best['sharpe_ratio']:.2f}")
            print(f"   总收益：{best['total_return']:.2%}")
    else:
        print("   ⏭️ 跳过优化 (使用 --optimize 启用)")
    
    # ========== 步骤 6: 生成交易信号 ==========
    print("\n🎯 【步骤 6/6】生成交易信号...")
    all_signals = {}
    signal_count = 0
    
    for symbol in symbols:
        df = market.get_ohlcv(symbol)
        if df is not None and len(df) > 50:
            df_indicators = indicator_engine.calculate_all(df)
            sigs = strategy_generator.generate_for_symbol(symbol, df_indicators)
            all_signals.update({f"{s['name']}": s for s in sigs})
            signal_count += len(sigs)
    
    print(f"   ✅ 成功生成 {signal_count} 个交易信号")
    
    # ========== 执行交易 ==========
    print("\n💰 【执行交易】...")
    prices = market.get_price_dict()
    executor.execute_signals(all_signals, prices, market_data=market_data)
    
    # ========== 更新持仓盈亏 ==========
    print("\n📈 【更新持仓盈亏】...")
    for symbol, pos in portfolio.positions.items():
        if symbol in prices:
            pos.update_pnl(prices[symbol])
    print("   ✅ 持仓盈亏已更新")
    
    # ========== 评估绩效 ==========
    print("\n📉 【计算绩效指标】...")
    results = evaluator.evaluate(portfolio)
    
    # ========== 输出结果 ==========
    print("\n" + "=" * 80)
    print("📊 【绩效评估结果】")
    print(f"   总收益率：{results.get('total_return', 0):.2%}")
    print(f"   夏普比率：{results.get('sharpe_ratio', 0):.2f}")
    print(f"   最大回撤：{results.get('max_drawdown', 0):.2%}")
    print(f"   胜率：{results.get('win_rate', 0):.2%}")
    print(f"   盈亏比：{results.get('profit_loss_ratio', 0):.2f}")
    print(f"   卡玛比率：{results.get('calmar_ratio', 0):.2f}")
    print(f"   索提诺比率：{results.get('sortino_ratio', 0):.2f}")
    print("=" * 80)
    
    # 显示交易统计
    stats = portfolio.get_stats()
    print("\n📈 【交易统计】")
    print(f"   总交易次数：{stats['total_trades']}")
    print(f"   当前持仓：{stats['open_positions']} 个")
    print(f"   已实现盈亏：{stats['closed_pnl']:.2f} 元")
    print(f"   当前权益：{stats['current_equity']:.2f} 元")
    
    # 显示持仓
    positions = executor.get_positions_summary()
    if positions:
        print("\n📋 【当前持仓明细】")
        positions_sorted = sorted(positions, key=lambda x: x['pnl'], reverse=True)
        for pos in positions_sorted[:10]:
            pnl_icon = "🟢" if pos['pnl'] > 0 else "🔴" if pos['pnl'] < 0 else "⚪"
            print(f"   {pnl_icon} {pos['symbol']}: {pos['direction']} x{pos['quantity']} @ {pos['entry_price']:.2f} | 盈亏：{pos['pnl']:.2f} ({pos['pnl_pct']:.2%})")
        if len(positions) > 10:
            print(f"   ... 还有 {len(positions)-10} 个持仓")
    
    print("\n✅ 增强版量化交易任务执行完成!")
    print("=" * 80)
    
    # 启动 GUI 或 Web
    if gui:
        from gui.dashboard_enhanced import run_dashboard
        run_dashboard()
    elif web:
        from web.app_pro import run_dashboard
        run_dashboard()
    
    return results


def main():
    parser = argparse.ArgumentParser(description='🦞 期货量化模拟盘系统 - 增强版')
    parser.add_argument('--gui', action='store_true', help='启动桌面仪表盘')
    parser.add_argument('--web', action='store_true', help='启动 Web Dashboard')
    parser.add_argument('--backtest', action='store_true', help='运行策略回测')
    parser.add_argument('--optimize', action='store_true', help='运行参数优化')
    parser.add_argument('--all', action='store_true', help='运行完整流程 (回测 + 优化)')
    args = parser.parse_args()
    
    run_enhanced_system(
        gui=args.gui,
        web=args.web,
        backtest=args.backtest or args.all,
        optimize=args.optimize or args.all
    )


if __name__ == "__main__":
    main()
