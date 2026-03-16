"""
=============================================================================
期货量化模拟盘系统 - 全品种全周期版本
=============================================================================
功能说明：
  - 支持 53 个期货合约（股指/能化/黑色/有色/农产品）
  - 10 个时间周期（1 分钟~月线）
  - 203 个技术指标
  - 232 个交易策略
  - 本地随机公平数据生成
  - 风险管理（止损/止盈/仓位管理）

作者：OpenClaw 🦞
日期：2026-03-12
=============================================================================
"""
import sys
from datetime import datetime
import os

# 设置项目路径
sys.path.insert(0, __file__.rsplit("/", 1)[0])

# 导入配置和模块
from config import (
    TRADING_CONFIG,  # 交易配置（初始资金/手续费等）
    BACKTEST_CONFIG,  # 回测配置
    PATHS,  # 路径配置
    CONTRACTS,  # 合约配置
    TIMEFRAMES  # 时间周期配置
)
from market.feeder import MarketDataFeeder  # 行情数据模块
from strategy.signals import StrategyGenerator  # 策略信号生成
from strategy.indicators import IndicatorEngine  # 技术指标计算
from trading.executor import OrderExecutor  # 订单执行
from trading.portfolio import Portfolio  # 持仓管理
from analysis.evaluator import PerformanceEvaluator  # 绩效评估
from analysis.ranker import StrategyRanker  # 策略排名
from analysis.backtester import Backtester  # 回测引擎


def main():
    """
    主函数 - 期货量化模拟盘入口
    
    执行流程：
    1. 初始化所有组件
    2. 加载市场数据（本地随机生成）
    3. 生成策略信号
    4. 计算技术指标
    5. 执行交易
    6. 评估绩效
    7. 策略排名
    8. 输出结果
    """
    # 打印标题
    print("=" * 60)
    print(f"🦞 期货量化模拟盘 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # ========== 步骤 1: 显示系统配置信息 ==========
    print("\n📊 【系统配置】")
    print(f"   期货合约数量：{len(CONTRACTS)} 个")
    print(f"   时间周期数量：{len(TIMEFRAMES)} 个")
    
    # 统计各分类合约数量
    categories = {}
    for c in CONTRACTS.values():
        cat = c.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1
    print(f"   品种分类统计:")
    for cat, count in categories.items():
        print(f"      - {cat}: {count} 个合约")
    
    # ========== 步骤 2: 初始化组件 ==========
    print("\n📦 【步骤 1/8】初始化交易组件...")
    # 初始化资金组合
    portfolio = Portfolio(TRADING_CONFIG["initial_capital"])
    # 初始化行情数据源
    market = MarketDataFeeder(PATHS["data"])
    # 初始化订单执行器
    executor = OrderExecutor(portfolio)
    # 初始化策略生成器
    generator = StrategyGenerator()
    # 初始化指标计算引擎
    engine = IndicatorEngine()
    # 初始化绩效评估器
    evaluator = PerformanceEvaluator()
    # 初始化策略排名器
    ranker = StrategyRanker()
    # 初始化回测引擎
    backtester = Backtester(TRADING_CONFIG["initial_capital"])
    print("   ✅ 组件初始化完成")
    
    # ========== 步骤 3: 加载市场数据 ==========
    print("\n📊 【步骤 2/8】加载市场数据...")
    print("   数据来源：本地随机生成（公平公正）")
    market_data = market.load_data()
    symbols = market.get_all_symbols()
    print(f"   ✅ 成功加载 {len(symbols)} 个期货合约数据")
    
    # ========== 步骤 4: 生成策略信号 ==========
    print("\n🎯 【步骤 3/8】生成交易策略信号...")
    all_strategy_signals = generator.generate_all()
    print(f"   ✅ 共生成 {len(all_strategy_signals)} 个交易策略")
    
    # ========== 步骤 5: 计算技术指标 ==========
    print("\n📈 【步骤 4/8】计算技术指标...")
    all_signals = {}  # 存储所有信号
    signal_count = 0
    # 为每个合约计算指标并生成信号
    for symbol in symbols:
        # 获取 K 线数据
        df = market.get_ohlcv(symbol)
        if df is not None and len(df) > 50:
            # 计算技术指标
            df_indicators = engine.calculate_all(df)
            # 生成交易信号
            sigs = generator.generate_for_symbol(symbol, df_indicators)
            all_signals.update({f"{s['name']}": s for s in sigs})
            signal_count += len(sigs)
    print(f"   ✅ 成功生成 {signal_count} 个交易信号")
    
    # ========== 步骤 6: 执行交易 ==========
    print("\n💰 【步骤 5/8】执行交易订单...")
    prices = market.get_price_dict()
    executor.execute_signals(all_signals, prices)
    
    # ========== 步骤 7: 更新持仓盈亏 ==========
    print("\n📈 【步骤 6/8】更新持仓浮动盈亏...")
    # 在评估前，先更新所有持仓的盈亏
    for symbol, pos in portfolio.positions.items():
        if symbol in prices:
            pos.update_pnl(prices[symbol])
    print("   ✅ 持仓盈亏已更新")
    
    # ========== 步骤 8: 评估绩效 ==========
    print("\n📉 【步骤 7/8】计算绩效指标...")
    results = evaluator.evaluate(portfolio)
    
    # ========== 步骤 9: 策略排名 ==========
    print("\n🏆 【步骤 8/8】策略排名...")
    rankings = ranker.rank(results)
    
    # ========== 输出结果 ==========
    print("\n" + "=" * 60)
    print("📊 【绩效评估结果】")
    print(f"   总收益率：{results.get('total_return', 0):.2%}")
    print(f"   夏普比率：{results.get('sharpe_ratio', 0):.2f}")
    print(f"   最大回撤：{results.get('max_drawdown', 0):.2%}")
    print(f"   胜率：{results.get('win_rate', 0):.2%}")
    print(f"   盈亏比：{results.get('profit_loss_ratio', 0):.2f}")
    print(f"   波动率：{results.get('volatility', 0):.2%}")
    print(f"\n🏆 综合得分：{rankings.get('score', 0):.2f}")
    print(f"   策略等级：{rankings.get('grade', 'N/A')}")
    print("=" * 60)
    
    # 显示交易统计
    stats = portfolio.get_stats()
    print("\n📈 【交易统计】")
    print(f"   总交易次数：{stats['total_trades']}")
    print(f"   当前持仓：{stats['open_positions']} 个")
    print(f"   已实现盈亏：{stats['closed_pnl']:.2f} 元")
    print(f"   当前权益：{stats['current_equity']:.2f} 元")
    
    # 显示当前持仓
    positions = executor.get_positions_summary()
    if positions:
        print("\n📋 【当前持仓明细】")
        print(f"   持仓数量：{len(positions)} 个合约")
        # 按盈亏排序
        positions_sorted = sorted(positions, key=lambda x: x['pnl'], reverse=True)
        for pos in positions_sorted[:10]:  # 只显示前 10 个
            pnl_icon = "🟢" if pos['pnl'] > 0 else "🔴" if pos['pnl'] < 0 else "⚪"
            print(f"   {pnl_icon} {pos['symbol']}: {pos['direction']} x{pos['quantity']} @ {pos['entry_price']:.2f} 盈亏：{pos['pnl']:.2f} ({pos['pnl_pct']:.2%})")
        if len(positions) > 10:
            print(f"   ... 还有 {len(positions)-10} 个持仓")
    
    print("\n✅ 每日量化交易任务执行完成!")
    print("=" * 60)
    
    return rankings


if __name__ == "__main__":
    main()
