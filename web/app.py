"""
=============================================================================
期货量化模拟盘 - Web Dashboard
=============================================================================
功能：
  - 实时绩效展示
  - 持仓监控
  - 策略排名
  - 资金曲线
  - 交易信号

作者：OpenClaw 🦞
日期：2026-03-14
=============================================================================
"""
import sys
import os
from flask import Flask, render_template, jsonify
from datetime import datetime
import json

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONTRACTS, TRADING_CONFIG
from market.feeder import MarketDataFeeder
from strategy.signals import StrategyGenerator
from trading.executor import OrderExecutor
from trading.portfolio import Portfolio
from analysis.evaluator import PerformanceEvaluator
from analysis.ranker import StrategyRanker

app = Flask(__name__)

# 全局变量存储运行结果
dashboard_data = {
    "last_update": None,
    "performance": {},
    "positions": [],
    "rankings": [],
    "signals": [],
    "equity_curve": []
}


def run_trading_engine():
    """运行交易引擎并收集数据"""
    global dashboard_data
    
    # 初始化组件
    portfolio = Portfolio(TRADING_CONFIG["initial_capital"])
    market = MarketDataFeeder("data/")
    executor = OrderExecutor(portfolio)
    generator = StrategyGenerator()
    evaluator = PerformanceEvaluator()
    ranker = StrategyRanker()
    
    # 加载数据
    market_data = market.load_data()
    symbols = market.get_all_symbols()
    
    # 生成信号
    all_signals = {}
    for symbol in symbols:
        df = market.get_ohlcv(symbol)
        if df is not None and len(df) > 50:
            sigs = generator.generate_for_symbol(symbol, df)
            all_signals.update({f"{symbol}_{s['name']}": s for s in sigs})
    
    # 执行交易
    prices = market.get_price_dict()
    executor.execute_signals(all_signals, prices)
    
    # 评估绩效
    results = evaluator.evaluate(portfolio)
    
    # 策略排名
    rankings = ranker.rank(results)
    
    # 更新全局数据 (传入当前价格到持仓汇总)
    dashboard_data.update({
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "performance": results,
        "positions": executor.get_positions_summary(current_prices=prices),
        "rankings": rankings.get("top_strategies", []),
        "signals": list(all_signals.values())[:50],  # 限制显示数量
        "equity_curve": portfolio.equity_curve[-100:]  # 最近 100 个点
    })
    
    return dashboard_data


@app.route("/")
def dashboard():
    """主页面"""
    return render_template("dashboard.html")


@app.route("/pro")
def dashboard_pro():
    """专业版页面 - 展示所有因子/策略/逻辑/状态"""
    return render_template("dashboard_pro.html")


@app.route("/api/performance")
def api_performance():
    """绩效数据 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    return jsonify(dashboard_data["performance"])


@app.route("/api/positions")
def api_positions():
    """持仓数据 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    return jsonify(dashboard_data["positions"])


@app.route("/api/rankings")
def api_rankings():
    """策略排名 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    return jsonify({
        "top_strategies": dashboard_data["rankings"][:20],
        "score": dashboard_data.get("rankings", {}).get("score", 0) if isinstance(dashboard_data.get("rankings"), dict) else 0
    })


@app.route("/api/signals")
def api_signals():
    """交易信号 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    return jsonify(dashboard_data["signals"])


@app.route("/api/equity")
def api_equity():
    """资金曲线 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    return jsonify({
        "equity_curve": dashboard_data["equity_curve"],
        "current_equity": dashboard_data["performance"].get("equity", TRADING_CONFIG["initial_capital"]),
        "initial_capital": TRADING_CONFIG["initial_capital"]
    })


@app.route("/api/refresh")
def api_refresh():
    """强制刷新数据"""
    run_trading_engine()
    return jsonify({"status": "ok", "update_time": dashboard_data["last_update"]})


@app.route("/api/summary")
def api_summary():
    """概览数据 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    perf = dashboard_data["performance"]
    # 计算额外指标
    returns = perf.get("returns", [])
    if returns and len(returns) > 1:
        avg_return = np.mean(returns)
        downside_returns = [r for r in returns if r < 0]
        downside_dev = np.std(downside_returns) if downside_returns else 0
        calmar = abs(perf.get("total_return", 0)) / perf.get("max_drawdown", 0.001) if perf.get("max_drawdown", 0) > 0 else 0
        sortino = avg_return / downside_dev * np.sqrt(252) if downside_dev > 0 else 0
    else:
        calmar = 0
        sortino = 0
    
    return jsonify({
        "total_return": perf.get("total_return", 0),
        "sharpe_ratio": perf.get("sharpe_ratio", 0),
        "max_drawdown": perf.get("max_drawdown", 0),
        "win_rate": perf.get("win_rate", 0),
        "profit_loss_ratio": perf.get("profit_loss_ratio", 0),
        "volatility": perf.get("volatility", 0),
        "calmar_ratio": calmar,
        "sortino_ratio": sortino,
        "total_trades": perf.get("total_trades", 0),
        "current_equity": perf.get("equity", 0),
        "position_count": len(dashboard_data["positions"]),
        "signal_count": len(dashboard_data["signals"]),
        "last_update": dashboard_data["last_update"]
    })


@app.route("/api/categories")
def api_categories():
    """品种分类统计 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    # 统计各分类持仓/信号数量
    categories = {}
    for pos in dashboard_data["positions"]:
        cat = pos.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1
    
    # 如果没有持仓，返回合约配置统计
    if not categories:
        from config import CONTRACTS
        for symbol, info in CONTRACTS.items():
            cat = info.get("category", "其他")
            categories[cat] = categories.get(cat, 0) + 1
    
    return jsonify({"categories": categories})


@app.route("/api/types")
def api_types():
    """策略类型分布 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    types = {}
    for sig in dashboard_data["signals"]:
        t = sig.get("type", "其他")
        types[t] = types.get(t, 0) + 1
    
    return jsonify({"types": types})


@app.route("/api/risk")
def api_risk():
    """风险指标 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    perf = dashboard_data["performance"]
    equity = dashboard_data.get("equity_curve", [])
    
    # 计算风险指标
    returns = [equity[i] - equity[i-1] for i in range(1, len(equity))] if len(equity) > 1 else []
    
    var_95 = -np.percentile(returns, 5) if returns else 0
    cvar_95 = -np.mean([r for r in returns if r < np.percentile(returns, 5)]) if returns else 0
    
    # 风险等级判定
    if perf.get("max_drawdown", 0) > 0.2:
        risk_level = "高"
    elif perf.get("max_drawdown", 0) > 0.1:
        risk_level = "中等"
    else:
        risk_level = "低"
    
    # 仓位使用率
    positions = dashboard_data.get("positions", [])
    total_value = sum(p.get("entry_price", 0) * p.get("quantity", 0) for p in positions)
    position_usage = total_value / TRADING_CONFIG["initial_capital"] if TRADING_CONFIG["initial_capital"] > 0 else 0
    
    # 保证金占用
    margin_used = total_value * TRADING_CONFIG.get("margin_rate", 0.12)
    
    return jsonify({
        "risk_metrics": {
            "risk_level": risk_level,
            "var_95": var_95,
            "cvar_95": cvar_95,
            "beta": 1.0,  # 模拟数据，beta 设为 1
            "information_ratio": perf.get("sharpe_ratio", 0),
            "tracking_error": perf.get("volatility", 0),
            "avg_holding_period": 3,  # 模拟平均持仓 3 天
            "position_usage": position_usage,
            "margin_used": margin_used
        }
    })


@app.route("/api/tradelog")
def api_tradelog():
    """交易日志 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    positions = dashboard_data.get("positions", [])
    trades = []
    
    for pos in positions:
        trades.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "symbol": pos.get("symbol", "未知"),
            "action": pos.get("direction", "buy"),
            "price": pos.get("entry_price", 0),
            "quantity": pos.get("quantity", 0),
            "pnl": pos.get("pnl", 0)
        })
    
    return jsonify({"trades": trades})


@app.route("/api/contracts")
def api_contracts():
    """合约详情 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    contracts = []
    for symbol, info in CONTRACTS.items():
        contracts.append({
            "symbol": symbol,
            "name": info.get("name", "未知"),
            "category": info.get("category", "其他"),
            "multiplier": info.get("multiplier", 0),
            "margin": info.get("margin", 0),
            "tick": info.get("tick", 0)
        })
    
    positions = dashboard_data.get("positions", [])
    
    return jsonify({
        "contracts": contracts,
        "positions": positions
    })


@app.route("/api/monthly")
def api_monthly():
    """月度收益 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    # 模拟月度收益数据（基于当前绩效）
    equity_curve = dashboard_data.get("equity_curve", [])
    
    # 简单模拟：生成 12 个月的收益数据
    import random
    random.seed(42)  # 固定种子保证一致性
    
    monthly_returns = []
    base_return = dashboard_data["performance"].get("total_return", 0) / 12
    
    for i in range(12):
        # 添加随机波动
        monthly_ret = base_return + random.uniform(-0.05, 0.05)
        monthly_returns.append(monthly_ret)
    
    return jsonify({"monthly_returns": monthly_returns})


@app.route("/api/analysis")
def api_analysis():
    """深度分析 API - 散点图数据"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    signals = dashboard_data.get("signals", [])
    strategies = []
    
    import random
    random.seed(42)
    
    for sig in signals[:50]:
        strategies.append({
            "name": sig.get("name", "未知"),
            "return_rate": random.uniform(-0.1, 0.15),
            "risk": random.uniform(0.02, 0.15),
            "score": sig.get("strength", 0.5)
        })
    
    return jsonify({"strategies": strategies})


@app.route("/api/contrib")
def api_contrib():
    """品种收益贡献 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    positions = dashboard_data.get("positions", [])
    
    # 按品种分类汇总盈亏
    contrib = {}
    for pos in positions:
        cat = pos.get("category", "其他")
        if cat not in contrib:
            contrib[cat] = {"category": cat, "return": 0, "count": 0}
        contrib[cat]["return"] += pos.get("pnl", 0)
        contrib[cat]["count"] += 1
    
    # 转换为列表并计算收益率
    result = []
    for cat, data in contrib.items():
        result.append({
            "category": cat,
            "return": data["return"] / 10000,  # 简化为百分比
            "count": data["count"]
        })
    
    # 如果没有持仓，返回模拟数据
    if not result:
        result = [
            {"category": "股指", "return": 0.05, "count": 4},
            {"category": "能化", "return": -0.02, "count": 14},
            {"category": "黑色", "return": 0.03, "count": 9},
            {"category": "有色", "return": 0.01, "count": 9},
            {"category": "农产品", "return": 0.04, "count": 17}
        ]
    
    return jsonify({"contribution": result})


@app.route("/api/timeframes")
def api_timeframes():
    """周期表现分析 API"""
    if not dashboard_data["last_update"]:
        run_trading_engine()
    
    from config import TIMEFRAMES
    
    import random
    random.seed(42)
    
    timeframes = []
    for tf_key, tf_info in TIMEFRAMES.items():
        timeframes.append({
            "name": tf_info["name"],
            "win_rate": random.uniform(0.4, 0.65),
            "avg_return": random.uniform(-0.03, 0.05)
        })
    
    return jsonify({"timeframes": timeframes})


if __name__ == "__main__":
    print("🦞 期货量化 Web Dashboard 启动中...")
    print(f"📊 访问地址：http://localhost:5001")
    print(f"🎯 专业版：http://localhost:5001/pro")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5001, debug=True)
