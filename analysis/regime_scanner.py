"""
Regime Analysis Tool - Strategy Gene Mapping
=============================================================================
This script analyzes which strategies perform best in which market regimes
(Trending, Mean-Reverting, Chaotic) based on the synthetic data.
=============================================================================
"""
import pandas as pd
import numpy as np
import os
from config import CONTRACTS
from market.feeder import MarketDataFeeder
from strategy.strategies_enhanced import EnhancedStrategyEngine
from analysis.backtester_pro import ProBacktester

def analyze_regimes():
    print("🔍 Starting Strategy-Regime Gene Mapping...")
    
    # 1. Initialize Data
    feeder = MarketDataFeeder()
    data = feeder.load_data()
    
    # 2. Identify Regimes for each symbol
    # We use the same logic as in feeder.py to identify the regime
    symbol_regimes = {}
    for symbol in CONTRACTS.keys():
        symbol_hash = sum(ord(c) for c in symbol)
        regime_id = symbol_hash % 3
        regime_name = {0: "Trend", 1: "MeanReversion", 2: "Chaotic"}[regime_id]
        symbol_regimes[symbol] = regime_name

    # 3. Performance matrix: {regime: {strategy: [returns]}}
    performance = {
        "Trend": {},
        "MeanReversion": {},
        "Chaotic": {}
    }

    # Initialize Engines
    engine = EnhancedStrategyEngine()
    bt_engine = ProBacktester()
    
    # Sampling strategies to avoid memory/time blowup
    all_strats_info = engine.strategies
    if len(all_strats_info) > 100:
        import random
        test_strats_info = random.sample(all_strats_info, 100)
    else:
        test_strats_info = all_strats_info
    
    test_strategy_names = [s['name'] for s in test_strats_info]
    
    print(f"🧪 Testing {len(test_strategy_names)} representative strategies across {len(symbol_regimes)} symbols...")

    for symbol in symbol_regimes:
        regime = symbol_regimes[symbol]
        df = feeder.get_ohlcv(symbol)
        if df is None: continue
        
        # Wrap single symbol in a dict to satisfy ProBacktester
        symbol_data = {symbol: df}
        
        for strat_name in test_strategy_names:
            try:
                # Run backtest for this specific strategy on this symbol
                res = bt_engine.run_backtest(symbol_data, engine, strat_name)
                ret = res['total_return']
                
                if strat_name not in performance[regime]:
                    performance[regime][strat_name] = []
                performance[regime][strat_name].append(ret)
            except Exception as e:
                continue

    # 4. Aggregate and Find Winners
    final_report = {}
    for regime, strats in performance.items():
        regime_winners = []
        for strat, rets in strats.items():
            avg_ret = np.mean(rets)
            regime_winners.append({'strategy': strat, 'avg_return': avg_ret})
        
        # Sort by return descending
        regime_winners = sorted(regime_winners, key=lambda x: x['avg_return'], reverse=True)
        final_report[regime] = regime_winners[:10] # Top 10 winners per regime

    return final_report

if __name__ == "__main__":
    report = analyze_regimes()
    
    print("\n" + "="*50)
    print("🏆 STRATEGY-REGIME GENE MAP")
    print("="*50)
    
    for regime, winners in report.items():
        print(f"\n🚀 [ {regime} Regime ] Winners:")
        for i, w in enumerate(winners, 1):
            print(f"  {i}. {w['strategy']:<20} | Avg Return: {w['avg_return']:+.4%}")
    
    print("\n" + "="*50)
    print("💡 CONCLUSION: Match these winners to the specific contracts!")
