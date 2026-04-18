#!/usr/bin/env python3
"""
=============================================================================
期货量化系统 - 统一入口脚本
=============================================================================
用法:
    python run.py              # 运行完整流程
    python run.py --gui        # 启动 GUI 仪表盘
    python run.py --report     # 生成报告
    python run.py --analyze    # 仅分析模式
    python run.py --status     # 查看系统状态
=============================================================================
"""
import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.manager import FuturesQuantManager, run_quant_system
from config import TRADING_CONFIG, CONTRACTS, TIMEFRAMES


def print_header():
    """打印标题"""
    print("=" * 70)
    print(f"🦞 期货量化系统 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


def print_config():
    """打印配置信息"""
    print("\n📊 【系统配置】")
    print(f"   初始资金：¥{TRADING_CONFIG['initial_capital']:,.2f}")
    print(f"   手续费率：{TRADING_CONFIG['commission_rate']:.4%}")
    print(f"   滑点：{TRADING_CONFIG['slippage']:.4%}")
    print(f"   保证金率：{TRADING_CONFIG['margin_rate']:.2%}")
    print(f"\n📦 【支持品种】")
    print(f"   合约总数：{len(CONTRACTS)} 个")
    print(f"   周期总数：{len(TIMEFRAMES)} 个")
    
    # 分类统计
    categories = {}
    for c in CONTRACTS.values():
        cat = c.get('category', '其他')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n   品种分类:")
    for cat, count in sorted(categories.items()):
        print(f"      {cat}: {count}个")


def print_results(result: dict):
    """打印结果"""
    if not result.get('success'):
        print(f"\n❌ 运行失败：{result.get('error', '未知错误')}")
        return
    
    results = result.get('results', {})
    analysis = result.get('analysis', {})
    stats = result.get('portfolio_stats', {})
    
    print("\n" + "=" * 70)
    print("📊 【绩效评估结果】")
    print("=" * 70)
    
    # 基础指标
    print(f"\n   总收益率：{results.get('total_return', 0):.2%}")
    print(f"   当前权益：¥{stats.get('current_equity', 0):,.2f}")
    print(f"   已实现盈亏：¥{stats.get('closed_pnl', 0):,.2f}")
    
    # 公平公正评估
    print("\n🔍 【公平公正评估】")
    print(f"   综合评分：{results.get('composite_score', 0):.1f}/100")
    print(f"   夏普比率：{results.get('sharpe_ratio', 0):.2f}")
    print(f"   索提诺比率：{results.get('sortino_ratio', 0):.2f}")
    print(f"   卡玛比率：{results.get('calmar_ratio', 0):.2f}")
    print(f"   最大回撤：{results.get('max_drawdown', 0):.2%}")
    print(f"   胜率：{results.get('win_rate', 0):.2%}")
    print(f"   盈亏比：{results.get('profit_loss_ratio', 0):.2f}")
    
    # 尾部风险
    print("\n⚠️ 【尾部风险】")
    print(f"   VaR(95%): {results.get('var_95', 0):.2%}")
    print(f"   CVaR(95%): {results.get('cvar_95', 0):.2%}")
    print(f"   统计显著性：{'✅ 显著' if results.get('returns_significant') else '❌ 不显著'}")
    
    # 评分明细
    breakdown = results.get('score_breakdown', {})
    if breakdown:
        print("\n📊 【评分明细】")
        print(f"   夏普比率：{breakdown.get('sharpe_component', 0):.1f}/25")
        print(f"   总收益：{breakdown.get('return_component', 0):.1f}/20")
        print(f"   最大回撤：{breakdown.get('drawdown_component', 0):.1f}/20")
        print(f"   索提诺比率：{breakdown.get('sortino_component', 0):.1f}/15")
        print(f"   胜率：{breakdown.get('win_rate_component', 0):.1f}/10")
        print(f"   盈亏比：{breakdown.get('pl_ratio_component', 0):.1f}/10")
    
    # 绩效归因
    attribution = analysis.get('attribution', {})
    if attribution.get('by_symbol'):
        print("\n📈 【绩效归因 - 品种 Top5】")
        for i, (symbol, data) in enumerate(list(attribution['by_symbol'].items())[:5]):
            icon = "🟢" if data['total_pnl'] > 0 else "🔴"
            print(f"   {i+1}. {icon} {symbol}: ¥{data['total_pnl']:,.2f} ({data['contribution_pct']:.1f}%)")
    
    # 策略诊断
    diagnosis = analysis.get('diagnosis', {})
    if diagnosis:
        print(f"\n⚠️ 【策略诊断】")
        print(f"   健康度：{diagnosis.get('overall_health', 'UNKNOWN').upper()}")
        
        issues = diagnosis.get('issues', [])
        warnings = diagnosis.get('warnings', [])
        suggestions = diagnosis.get('suggestions', [])
        
        if issues:
            print("\n   问题:")
            for issue in issues:
                print(f"      ❌ [{issue['severity']}] {issue['description']}")
        
        if warnings:
            print("\n   警告:")
            for w in warnings:
                print(f"      ⚠️ {w['description']}")
        
        if suggestions:
            print("\n   建议:")
            for s in suggestions:
                print(f"      💡 {s}")
    
    # 交易统计
    print("\n📈 【交易统计】")
    print(f"   总交易次数：{stats.get('total_trades', 0)}")
    print(f"   当前持仓：{stats.get('open_positions', 0)} 个")
    print(f"   运行耗时：{result.get('duration_seconds', 0):.2f}秒")
    
    print("\n" + "=" * 70)
    print("✅ 系统运行完成!")
    print("=" * 70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='🦞 期货量化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python run.py                 # 运行完整流程
    python run.py --gui           # 启动 GUI 仪表盘
    python run.py --report        # 生成报告
    python run.py --capital 500000  # 使用 50 万资金
        """
    )
    
    parser.add_argument('--gui', action='store_true', help='启动 GUI 仪表盘')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--analyze', action='store_true', help='仅分析模式')
    parser.add_argument('--status', action='store_true', help='查看系统状态')
    parser.add_argument('--capital', type=float, default=1_000_000, help='初始资金')
    parser.add_argument('--log-level', type=str, default='INFO', help='日志级别')
    
    args = parser.parse_args()
    
    # GUI 模式
    if args.gui:
        from gui.dashboard import run_dashboard
        run_dashboard()
        return
    
    # 状态模式
    if args.status:
        print_header()
        print_config()
        print("\n📊 【系统状态】")
        print("   模块加载：✅")
        print(f"   策略数量：232 个")
        print(f"   指标数量：203 个")
        print(f"   合约数量：{len(CONTRACTS)} 个")
        return
    
    # 运行系统
    print_header()
    print_config()
    
    manager = FuturesQuantManager(args.capital, args.log_level)
    result = manager.run_full_pipeline(generate_report=args.report)
    
    print_results(result)
    
    # 清理
    manager.shutdown()


if __name__ == "__main__":
    main()
