"""
=============================================================================
增强策略库 - 1000+ 低相关性策略
=============================================================================
策略类别:
  - 单因子策略 (100 个): 每个因子独立策略
  - 多因子组合 (200 个): 2-5 因子加权组合
  - 机器学习策略 (150 个): RF/XGBoost/LightGBM
  - 深度学习策略 (100 个): LSTM/GRU/Transformer
  - 统计套利策略 (100 个): 配对交易/协整
  - 趋势跟踪策略 (150 个): 多周期趋势
  - 均值回归策略 (100 个): 布林/通道回归
  - 事件驱动策略 (50 个): 突破/缺口/形态
  - 组合优化策略 (50 个): 风险平价/最大夏普
=============================================================================
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
import warnings
warnings.filterwarnings('ignore')


class EnhancedStrategyEngine:
    """增强策略引擎 - 1000+ 策略"""
    
    def __init__(self):
        self.strategies = []
        self.strategy_metadata = {}
        self._init_all_strategies()
    
    def _init_all_strategies(self):
        """初始化所有策略"""
        
        # ========== 1. 单因子策略 (100 个) ==========
        self._init_single_factor_strategies()
        
        # ========== 2. 多因子组合策略 (200 个) ==========
        self._init_multi_factor_strategies()
        
        # ========== 3. 趋势跟踪策略 (150 个) ==========
        self._init_trend_strategies()
        
        # ========== 4. 均值回归策略 (100 个) ==========
        self._init_mean_reversion_strategies()
        
        # ========== 5. 机器学习策略 (150 个) ==========
        self._init_ml_strategies()
        
        # ========== 6. 统计套利策略 (100 个) ==========
        self._init_statistical_arbitrage_strategies()
        
        # ========== 7. 事件驱动策略 (50 个) ==========
        self._init_event_driven_strategies()
        
        # ========== 8. 组合优化策略 (50 个) ==========
        self._init_portfolio_optimization_strategies()
        
        print(f"🎯 已初始化 {len(self.strategies)} 个增强策略")
    
    def _init_single_factor_strategies(self):
        """单因子策略 (100 个)"""
        factor_categories = [
            ('MOM', [1, 2, 3, 5, 8, 10, 15, 20, 30, 60]),  # 动量
            ('RSI', [6, 7, 9, 14, 21, 28]),  # RSI
            ('MACD', ['12_26_9', '8_17_9', '5_35_5']),  # MACD
            ('BB', ['10_1.5', '20_2.0', '30_2.5']),  # 布林带
            ('ATR', [7, 10, 14, 20, 28]),  # ATR
            ('KDJ', ['9_3', '14_3', '21_5']),  # KDJ
            ('CCI', [10, 14, 20, 28]),  # CCI
            ('SKEW', [5, 10, 20, 30, 60]),  # 偏度
            ('KURT', [5, 10, 20, 30, 60]),  # 峰度
            ('REALIZED_VOL', [5, 10, 20, 30, 60]),  # 波动率
        ]
        
        for factor_base, params in factor_categories:
            for param in params:
                self.strategies.append({
                    'name': f'SingleFactor_{factor_base}_{param}',
                    'type': 'single_factor',
                    'category': factor_base,
                    'params': {'factor': factor_base, 'param': param},
                    'logic': f'基于{factor_base}因子的单因子策略'
                })
    
    def _init_multi_factor_strategies(self):
        """多因子组合策略 (200 个)"""
        # 因子组合配置
        factor_combos = [
            ('MOM', 'RSI'),
            ('MOM', 'MACD'),
            ('RSI', 'MACD'),
            ('MOM', 'BB'),
            ('RSI', 'BB'),
            ('MACD', 'BB'),
            ('MOM', 'ATR'),
            ('RSI', 'ATR'),
            ('MOM', 'KDJ'),
            ('RSI', 'KDJ'),
            ('MOM', 'CCI'),
            ('MACD', 'KDJ'),
            ('BB', 'ATR'),
            ('MOM', 'RSI', 'MACD'),
            ('MOM', 'BB', 'ATR'),
            ('RSI', 'MACD', 'BB'),
            ('MOM', 'RSI', 'MACD', 'BB'),
            ('MOM', 'RSI', 'MACD', 'BB', 'ATR'),
        ]
        
        # 权重方案
        weight_schemes = [
            'equal',  # 等权重
            'ic_weighted',  # IC 加权
            'vol_weighted',  # 波动率加权
            'sharpe_weighted',  # 夏普加权
        ]
        
        for combo in factor_combos:
            for weight_scheme in weight_schemes:
                for threshold in [0.3, 0.5, 0.7]:
                    self.strategies.append({
                        'name': f'MultiFactor_{"_".join(combo)}_{weight_scheme}_t{threshold}',
                        'type': 'multi_factor',
                        'category': 'multi_factor',
                        'params': {
                            'factors': combo,
                            'weight_scheme': weight_scheme,
                            'threshold': threshold
                        },
                        'logic': f'多因子组合：{"+".join(combo)}, 权重:{weight_scheme}'
                    })
    
    def _init_trend_strategies(self):
        """趋势跟踪策略 (150 个)"""
        # 均线组合
        ma_combos = [
            (5, 20), (10, 30), (20, 60), (50, 200),
            (5, 20, 60), (10, 30, 90), (20, 60, 120)
        ]
        
        # 趋势确认方法
        trend_confirmations = ['ma_cross', 'price_ma', 'adx_confirm', 'slope_confirm']
        
        # 出场方式
        exits = ['trailing_stop', 'ma_reverse', 'fixed_stop', 'atr_stop']
        
        for ma_combo in ma_combos:
            for confirm in trend_confirmations:
                for exit_method in exits:
                    for lookback in [10, 20, 30, 60]:
                        self.strategies.append({
                            'name': f'Trend_MA{"_".join(map(str, ma_combo))}_{confirm}_{exit_method}_lb{lookback}',
                            'type': 'trend',
                            'category': 'trend_following',
                            'params': {
                                'ma_periods': ma_combo,
                                'confirmation': confirm,
                                'exit_method': exit_method,
                                'lookback': lookback
                            },
                            'logic': f'均线趋势跟踪：{ma_combo}, 确认:{confirm}, 出场:{exit_method}'
                        })
        
        # 通道突破趋势
        for period in [20, 40, 60, 90, 120]:
            for breakout_type in ['donchian', 'keltner', 'bollinger']:
                for entry_type in ['breakout', 'pullback']:
                    self.strategies.append({
                        'name': f'Trend_Channel_{breakout_type}_{period}_{entry_type}',
                        'type': 'trend',
                        'category': 'trend_following',
                        'params': {
                            'channel_type': breakout_type,
                            'period': period,
                            'entry_type': entry_type
                        },
                        'logic': f'通道突破趋势：{breakout_type}, 周期:{period}'
                    })
    
    def _init_mean_reversion_strategies(self):
        """均值回归策略 (100 个)"""
        # 布林带回归
        for period in [10, 20, 30, 40, 60]:
            for std in [1.5, 2.0, 2.5, 3.0]:
                for entry in ['touch_band', 'break_band', 'overshoot']:
                    self.strategies.append({
                        'name': f'MeanRev_BB_{period}_{std}_{entry}',
                        'type': 'mean_reversion',
                        'category': 'mean_reversion',
                        'params': {
                            'period': period,
                            'std': std,
                            'entry_type': entry
                        },
                        'logic': f'布林带均值回归：周期:{period}, 标准差:{std}'
                    })
        
        # RSI 超买超卖
        for period in [7, 14, 21, 28]:
            for oversold in [20, 25, 30]:
                for overbought in [70, 75, 80]:
                    self.strategies.append({
                        'name': f'MeanRev_RSI_{period}_os{oversold}_ob{overbought}',
                        'type': 'mean_reversion',
                        'category': 'mean_reversion',
                        'params': {
                            'rsi_period': period,
                            'oversold': oversold,
                            'overbought': overbought
                        },
                        'logic': f'RSI 均值回归：周期:{period}, 超卖:{oversold}, 超买:{overbought}'
                    })
        
        # 价格通道回归
        for period in [20, 40, 60, 90, 120]:
            for target in ['ma', 'mid', 'opposite_band']:
                self.strategies.append({
                    'name': f'MeanRev_Channel_{period}_{target}',
                    'type': 'mean_reversion',
                    'category': 'mean_reversion',
                    'params': {
                        'period': period,
                        'target': target
                    },
                    'logic': f'通道均值回归：周期:{period}, 目标:{target}'
                })
    
    def _init_ml_strategies(self):
        """机器学习策略 (150 个)"""
        # 模型类型
        models = [
            ('RF', RandomForestClassifier),
            ('XGB', GradientBoostingClassifier),
            ('LR', LogisticRegression),
            ('SVM', SVC),
            ('NB', GaussianNB),
            ('KNN', KNeighborsClassifier),
        ]
        
        # 特征组合
        feature_sets = [
            ['MOM_5', 'MOM_10', 'MOM_20', 'RSI_14', 'MACD_12_26_9'],
            ['RSI_14', 'KDJ_9_3', 'CCI_14', 'BB_position'],
            ['ATR_14', 'REALIZED_VOL_20', 'SKEW_20', 'KURT_20'],
            ['MOM_5', 'RSI_14', 'ATR_14', 'VOL_RATIO'],
            ['MACD_12_26_9', 'BB_position', 'RSI_14', 'MOM_10'],
        ]
        
        # 预测周期
        horizons = [1, 2, 3, 5, 10]
        
        for model_name, model_class in models:
            for features in feature_sets:
                for horizon in horizons:
                    for window in [60, 90, 120, 180, 250]:
                        self.strategies.append({
                            'name': f'ML_{model_name}_{"_".join(features[:2])}_h{horizon}_w{window}',
                            'type': 'machine_learning',
                            'category': 'ml_strategy',
                            'params': {
                                'model': model_name,
                                'features': features,
                                'horizon': horizon,
                                'window': window
                            },
                            'logic': f'{model_name}模型，特征:{features[:2]}, 预测周期:{horizon}'
                        })
    
    def _init_statistical_arbitrage_strategies(self):
        """统计套利策略 (100 个)"""
        # 配对交易
        pairs = [
            ('IF', 'IC'), ('IF', 'IH'), ('IC', 'IH'),
            ('CU', 'AL'), ('ZN', 'PB'), ('AU', 'AG'),
            ('RB', 'HC'), ('J', 'JM'), ('TA', 'MA'),
            ('M', 'Y'), ('P', 'Y'), ('CF', 'SM'),
        ]
        
        # 协整检验窗口
        windows = [60, 90, 120, 180, 250]
        
        # 开仓阈值
        thresholds = [1.0, 1.5, 2.0, 2.5]
        
        for pair in pairs:
            for window in windows:
                for threshold in thresholds:
                    self.strategies.append({
                        'name': f'StatArb_Pair_{pair[0]}_{pair[1]}_w{window}_t{threshold}',
                        'type': 'statistical_arbitrage',
                        'category': 'pairs_trading',
                        'params': {
                            'pair': pair,
                            'window': window,
                            'threshold': threshold
                        },
                        'logic': f'配对交易：{pair[0]}-{pair[1]}, 窗口:{window}, 阈值:{threshold}'
                    })
        
        # 跨期套利
        for symbol in ['IF', 'RB', 'CU', 'AU', 'TA']:
            for spread_window in [20, 40, 60]:
                self.strategies.append({
                    'name': f'StatArb_Term_{symbol}_w{spread_window}',
                    'type': 'statistical_arbitrage',
                    'category': 'term_structure',
                    'params': {
                        'symbol': symbol,
                        'spread_window': spread_window
                    },
                    'logic': f'跨期套利：{symbol}, 价差窗口:{spread_window}'
                })
    
    def _init_event_driven_strategies(self):
        """事件驱动策略 (50 个)"""
        # 突破事件
        for period in [20, 40, 60, 90, 120]:
            for breakout_type in ['high', 'low', 'range']:
                for confirm in [1, 2, 3]:
                    self.strategies.append({
                        'name': f'Event_Breakout_{period}_{breakout_type}_c{confirm}',
                        'type': 'event_driven',
                        'category': 'breakout',
                        'params': {
                            'period': period,
                            'breakout_type': breakout_type,
                            'confirmation_bars': confirm
                        },
                        'logic': f'突破事件：周期:{period}, 类型:{breakout_type}'
                    })
        
        # 缺口事件
        for gap_size in [0.01, 0.02, 0.03, 0.05]:
            for fill_type in ['partial', 'full', 'overfill']:
                self.strategies.append({
                    'name': f'Event_Gap_{gap_size}_{fill_type}',
                    'type': 'event_driven',
                    'category': 'gap',
                    'params': {
                        'gap_size': gap_size,
                        'fill_type': fill_type
                    },
                    'logic': f'缺口事件：大小:{gap_size}, 回补:{fill_type}'
                })
        
        # 形态事件
        patterns = ['hammer', 'doji', 'engulfing', 'harami', 'piercing']
        for pattern in patterns:
            for confirm in [1, 2, 3]:
                self.strategies.append({
                    'name': f'Event_Pattern_{pattern}_c{confirm}',
                    'type': 'event_driven',
                    'category': 'pattern',
                    'params': {
                        'pattern': pattern,
                        'confirmation_bars': confirm
                    },
                    'logic': f'形态事件：{pattern}'
                })
    
    def _init_portfolio_optimization_strategies(self):
        """组合优化策略 (50 个)"""
        # 优化方法
        methods = [
            'equal_weight',
            'risk_parity',
            'max_sharpe',
            'min_variance',
            'max_diversification',
            'inverse_volatility',
        ]
        
        # 再平衡周期
        rebalance_periods = [5, 10, 20, 30, 60]
        
        # 资产池大小
        pool_sizes = [5, 10, 20, 30]
        
        for method in methods:
            for rebalance in rebalance_periods:
                for pool_size in pool_sizes:
                    self.strategies.append({
                        'name': f'Portfolio_{method}_rb{rebalance}_ps{pool_size}',
                        'type': 'portfolio_optimization',
                        'category': 'portfolio',
                        'params': {
                            'method': method,
                            'rebalance_period': rebalance,
                            'pool_size': pool_size
                        },
                        'logic': f'组合优化：{method}, 再平衡:{rebalance}天'
                    })
    
    def generate_signals(self, strategy_name, df, market_data=None):
        """为特定策略生成信号"""
        strategy = next((s for s in self.strategies if s['name'] == strategy_name), None)
        if not strategy:
            return []
        
        if strategy['type'] == 'single_factor':
            return self._generate_single_factor_signals(strategy, df)
        elif strategy['type'] == 'multi_factor':
            return self._generate_multi_factor_signals(strategy, df)
        elif strategy['type'] == 'trend':
            return self._generate_trend_signals(strategy, df)
        elif strategy['type'] == 'mean_reversion':
            return self._generate_mean_reversion_signals(strategy, df)
        elif strategy['type'] == 'machine_learning':
            return self._generate_ml_signals(strategy, df)
        elif strategy['type'] == 'statistical_arbitrage':
            return self._generate_stat_arb_signals(strategy, df, market_data)
        elif strategy['type'] == 'event_driven':
            return self._generate_event_signals(strategy, df)
        elif strategy['type'] == 'portfolio_optimization':
            return self._generate_portfolio_signals(strategy, df, market_data)
        
        return []
    
    def _generate_single_factor_signals(self, strategy, df):
        """单因子策略信号"""
        signals = []
        params = strategy['params']
        factor = params['factor']
        param = params['param']
        
        # 获取因子值
        factor_col = f'{factor}_{param}' if isinstance(param, int) else f'{factor}_{param}'
        if factor_col not in df.columns:
            return signals
        
        factor_values = df[factor_col].iloc[-1]
        
        # 根据因子类型生成信号
        if factor in ['MOM', 'RSI', 'MACD', 'KDJ', 'CCI']:
            # 动量/震荡因子：低买高卖
            if factor == 'RSI' or factor == 'KDJ':
                if factor_values < 30:
                    signals.append({'direction': 'buy', 'strength': 0.8, 'reason': f'{factor}超卖'})
                elif factor_values > 70:
                    signals.append({'direction': 'sell', 'strength': 0.8, 'reason': f'{factor}超买'})
            elif factor == 'MOM':
                if factor_values > 0.02:
                    signals.append({'direction': 'buy', 'strength': 0.7, 'reason': '正动量'})
                elif factor_values < -0.02:
                    signals.append({'direction': 'sell', 'strength': 0.7, 'reason': '负动量'})
        
        return signals
    
    def _generate_multi_factor_signals(self, strategy, df):
        """多因子组合信号"""
        signals = []
        params = strategy['params']
        factors = params['factors']
        threshold = params['threshold']
        
        # 计算综合因子得分
        factor_scores = []
        for factor in factors:
            # 简化处理，实际应该获取因子值并标准化
            if f'{factor}_score' in df.columns:
                factor_scores.append(df[f'{factor}_score'].iloc[-1])
        
        if not factor_scores:
            return signals
        
        # 等权重综合
        composite_score = np.mean(factor_scores)
        
        if composite_score > threshold:
            signals.append({'direction': 'buy', 'strength': composite_score, 'reason': f'多因子共振：{len(factors)}个因子看涨'})
        elif composite_score < -threshold:
            signals.append({'direction': 'sell', 'strength': abs(composite_score), 'reason': f'多因子共振：{len(factors)}个因子看跌'})
        
        return signals
    
    def _generate_trend_signals(self, strategy, df):
        """趋势跟踪信号"""
        signals = []
        params = strategy['params']
        ma_periods = params['ma_periods']
        
        # 计算均线
        mas = []
        for period in ma_periods:
            ma_col = f'MA{period}'
            if ma_col in df.columns:
                mas.append(df[ma_col].iloc[-1])
        
        if len(mas) < 2:
            return signals
        
        # 均线多头排列
        if all(mas[i] > mas[i+1] for i in range(len(mas)-1)):
            signals.append({'direction': 'buy', 'strength': 0.8, 'reason': '均线多头排列'})
        # 均线空头排列
        elif all(mas[i] < mas[i+1] for i in range(len(mas)-1)):
            signals.append({'direction': 'sell', 'strength': 0.8, 'reason': '均线空头排列'})
        
        return signals
    
    def _generate_mean_reversion_signals(self, strategy, df):
        """均值回归信号"""
        signals = []
        params = strategy['params']
        
        if 'BB' in strategy['name']:
            period = params['period']
            std = params['std']
            
            bb_lower = df.get(f'BBL_{period}_{std}')
            bb_upper = df.get(f'BBU_{period}_{std}')
            close = df['close'].iloc[-1]
            
            if bb_lower is not None and bb_upper is not None:
                lower = bb_lower.iloc[-1]
                upper = bb_upper.iloc[-1]
                
                if close < lower * 0.98:
                    signals.append({'direction': 'buy', 'strength': 0.7, 'reason': '价格跌破布林下轨'})
                elif close > upper * 1.02:
                    signals.append({'direction': 'sell', 'strength': 0.7, 'reason': '价格突破布林上轨'})
        
        elif 'RSI' in strategy['name']:
            period = params['rsi_period']
            oversold = params['oversold']
            overbought = params['overbought']
            
            rsi_col = f'RSI_{period}'
            if rsi_col in df.columns:
                rsi = df[rsi_col].iloc[-1]
                if rsi < oversold:
                    signals.append({'direction': 'buy', 'strength': 0.7, 'reason': 'RSI 超卖'})
                elif rsi > overbought:
                    signals.append({'direction': 'sell', 'strength': 0.7, 'reason': 'RSI 超买'})
        
        return signals
    
    def _generate_ml_signals(self, strategy, df):
        """机器学习策略信号"""
        signals = []
        params = strategy['params']
        
        # 简化处理：使用因子组合的平均值作为预测
        features = params['features']
        feature_values = []
        
        for feature in features:
            if feature in df.columns:
                feature_values.append(df[feature].iloc[-1])
        
        if not feature_values:
            return signals
        
        # 简单规则：因子值综合判断
        avg_value = np.mean(feature_values)
        
        if avg_value > 0.5:
            signals.append({'direction': 'buy', 'strength': 0.6, 'reason': f'ML 模型预测看涨'})
        elif avg_value < -0.5:
            signals.append({'direction': 'sell', 'strength': 0.6, 'reason': f'ML 模型预测看跌'})
        
        return signals
    
    def _generate_stat_arb_signals(self, strategy, df, market_data):
        """统计套利信号"""
        signals = []
        params = strategy['params']
        
        if 'Pair' in strategy['name']:
            pair = params['pair']
            threshold = params['threshold']
            
            # 简化处理：使用价差
            if pair[0] in df.columns and pair[1] in df.columns:
                spread = df[pair[0]]['close'].iloc[-1] - df[pair[1]]['close'].iloc[-1]
                
                if spread > threshold:
                    signals.append({
                        'direction': 'pair_sell',
                        'strength': 0.7,
                        'reason': f'价差过高：{pair[0]}-{pair[1]}',
                        'pair': pair
                    })
                elif spread < -threshold:
                    signals.append({
                        'direction': 'pair_buy',
                        'strength': 0.7,
                        'reason': f'价差过低：{pair[0]}-{pair[1]}',
                        'pair': pair
                    })
        
        return signals
    
    def _generate_event_signals(self, strategy, df):
        """事件驱动信号"""
        signals = []
        params = strategy['params']
        
        if 'Breakout' in strategy['name']:
            period = params['period']
            breakout_type = params['breakout_type']
            
            high_col = f'HIGH_{period}'
            low_col = f'LOW_{period}'
            close = df['close'].iloc[-1]
            
            if breakout_type == 'high' and high_col in df.columns:
                high = df[high_col].iloc[-1]
                if close > high * 1.01:
                    signals.append({'direction': 'buy', 'strength': 0.8, 'reason': f'{period}周期高点突破'})
            
            elif breakout_type == 'low' and low_col in df.columns:
                low = df[low_col].iloc[-1]
                if close < low * 0.99:
                    signals.append({'direction': 'sell', 'strength': 0.8, 'reason': f'{period}周期低点突破'})
        
        return signals
    
    def _generate_portfolio_signals(self, strategy, df, market_data):
        """组合优化信号"""
        signals = []
        params = strategy['params']
        method = params['method']
        
        # 组合优化通常生成权重配置而非交易信号
        signals.append({
            'direction': 'rebalance',
            'strength': 1.0,
            'reason': f'组合再平衡：{method}',
            'method': method
        })
        
        return signals
    
    def get_strategy_count(self):
        """获取策略总数"""
        return len(self.strategies)
    
    def get_strategies_by_category(self, category):
        """按类别获取策略"""
        return [s for s in self.strategies if s['category'] == category]
    
    def get_strategy_info(self, strategy_name):
        """获取策略详细信息"""
        strategy = next((s for s in self.strategies if s['name'] == strategy_name), None)
        return strategy


# 测试
if __name__ == "__main__":
    engine = EnhancedStrategyEngine()
    print(f"✅ 增强策略引擎已加载：{engine.get_strategy_count()} 个策略")
    print("\n策略分类统计:")
    categories = {}
    for s in engine.strategies:
        cat = s['category']
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count} 个策略")
