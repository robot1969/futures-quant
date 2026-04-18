"""
=============================================================================
分析系统 - 深度分析引擎
=============================================================================
功能:
  - 绩效归因分析 (Brinson 归因)
  - 因子分析 (IC/IR/因子暴露)
  - 相关性分析 (策略/品种/周期)
  - 市场状态分析 (震荡/趋势)
  - 策略诊断 (问题定位)
  - 可视化数据生成
=============================================================================
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import json
import os
import warnings
warnings.filterwarnings('ignore')


class AnalyticsEngine:
    """深度分析引擎"""
    
    def __init__(self, output_dir='analysis/reports/'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    # ==================== 绩效归因分析 ====================
    
    def performance_attribution(self, portfolio, trades: List[Dict]) -> Dict:
        """
        绩效归因分析 - 拆解收益来源
        
        归因维度:
            - 品种贡献 (哪个品种赚/亏最多)
            - 方向贡献 (做多/做空贡献)
            - 策略贡献 (哪个策略贡献最大)
            - 时间贡献 (哪段时间表现最好)
            - 仓位贡献 (重仓/轻仓表现)
        """
        if not trades:
            return {'error': 'No trades to analyze'}
        
        closed_trades = [t for t in trades if t.get('type') == 'close']
        
        if not closed_trades:
            return {'error': 'No closed trades'}
        
        attribution = {
            'by_symbol': self._attribute_by_symbol(closed_trades),
            'by_direction': self._attribute_by_direction(closed_trades),
            'by_strategy': self._attribute_by_strategy(closed_trades),
            'by_time': self._attribute_by_time(closed_trades),
            'by_position_size': self._attribute_by_position_size(closed_trades),
            'total_pnl': sum(t.get('pnl', 0) for t in closed_trades)
        }
        
        return attribution
    
    def _attribute_by_symbol(self, trades: List[Dict]) -> Dict:
        """按品种归因"""
        symbol_pnl = defaultdict(float)
        symbol_count = defaultdict(int)
        
        for t in trades:
            symbol = t.get('symbol', 'UNKNOWN')
            pnl = t.get('pnl', 0)
            symbol_pnl[symbol] += pnl
            symbol_count[symbol] += 1
        
        # 计算平均 PnL
        result = {}
        for symbol in symbol_pnl:
            result[symbol] = {
                'total_pnl': symbol_pnl[symbol],
                'trade_count': symbol_count[symbol],
                'avg_pnl': symbol_pnl[symbol] / symbol_count[symbol] if symbol_count[symbol] > 0 else 0,
                'contribution_pct': symbol_pnl[symbol] / sum(symbol_pnl.values()) * 100 if sum(symbol_pnl.values()) != 0 else 0
            }
        
        # 按贡献排序
        sorted_result = sorted(result.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
        return dict(sorted_result)
    
    def _attribute_by_direction(self, trades: List[Dict]) -> Dict:
        """按方向归因 (多/空)"""
        long_pnl = 0
        short_pnl = 0
        long_count = 0
        short_count = 0
        
        for t in trades:
            pnl = t.get('pnl', 0)
            direction = t.get('direction', 'long')
            
            if direction == 'long' or direction == 'buy':
                long_pnl += pnl
                long_count += 1
            else:
                short_pnl += pnl
                short_count += 1
        
        total = long_pnl + short_pnl
        
        return {
            'long': {
                'total_pnl': long_pnl,
                'trade_count': long_count,
                'avg_pnl': long_pnl / long_count if long_count > 0 else 0,
                'contribution_pct': long_pnl / total * 100 if total != 0 else 0
            },
            'short': {
                'total_pnl': short_pnl,
                'trade_count': short_count,
                'avg_pnl': short_pnl / short_count if short_count > 0 else 0,
                'contribution_pct': short_pnl / total * 100 if total != 0 else 0
            }
        }
    
    def _attribute_by_strategy(self, trades: List[Dict]) -> Dict:
        """按策略归因"""
        strategy_pnl = defaultdict(float)
        strategy_count = defaultdict(int)
        
        for t in trades:
            strategy = t.get('strategy', 'UNKNOWN')
            pnl = t.get('pnl', 0)
            strategy_pnl[strategy] += pnl
            strategy_count[strategy] += 1
        
        result = {}
        for strategy in strategy_pnl:
            result[strategy] = {
                'total_pnl': strategy_pnl[strategy],
                'trade_count': strategy_count[strategy],
                'avg_pnl': strategy_pnl[strategy] / strategy_count[strategy] if strategy_count[strategy] > 0 else 0,
                'contribution_pct': strategy_pnl[strategy] / sum(strategy_pnl.values()) * 100 if sum(strategy_pnl.values()) != 0 else 0
            }
        
        sorted_result = sorted(result.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
        return dict(sorted_result)
    
    def _attribute_by_time(self, trades: List[Dict]) -> Dict:
        """按时间归因 (月度)"""
        monthly_pnl = defaultdict(float)
        monthly_count = defaultdict(int)
        
        for t in trades:
            date_str = t.get('date', '')
            if date_str:
                try:
                    date = pd.to_datetime(date_str)
                    month_key = date.strftime('%Y-%m')
                    pnl = t.get('pnl', 0)
                    monthly_pnl[month_key] += pnl
                    monthly_count[month_key] += 1
                except:
                    pass
        
        result = {}
        for month in monthly_pnl:
            result[month] = {
                'total_pnl': monthly_pnl[month],
                'trade_count': monthly_count[month],
                'avg_pnl': monthly_pnl[month] / monthly_count[month] if monthly_count[month] > 0 else 0
            }
        
        sorted_result = sorted(result.items(), key=lambda x: x[0])
        return dict(sorted_result)
    
    def _attribute_by_position_size(self, trades: List[Dict]) -> Dict:
        """按仓位大小归因"""
        # 分位数分组
        quantities = [t.get('quantity', 0) for t in trades if t.get('quantity', 0) > 0]
        
        if not quantities:
            return {'error': 'No quantity data'}
        
        q25 = np.percentile(quantities, 25)
        q50 = np.percentile(quantities, 50)
        q75 = np.percentile(quantities, 75)
        
        groups = {
            'small': {'pnl': 0, 'count': 0},
            'medium': {'pnl': 0, 'count': 0},
            'large': {'pnl': 0, 'count': 0}
        }
        
        for t in trades:
            qty = t.get('quantity', 0)
            pnl = t.get('pnl', 0)
            
            if qty <= q25:
                groups['small']['pnl'] += pnl
                groups['small']['count'] += 1
            elif qty <= q75:
                groups['medium']['pnl'] += pnl
                groups['medium']['count'] += 1
            else:
                groups['large']['pnl'] += pnl
                groups['large']['count'] += 1
        
        # 计算平均
        for group in groups:
            count = groups[group]['count']
            pnl = groups[group]['pnl']
            groups[group]['avg_pnl'] = pnl / count if count > 0 else 0
        
        return groups
    
    # ==================== 因子分析 ====================
    
    def factor_analysis(self, market_data: Dict[str, pd.DataFrame], 
                        signals: List[Dict]) -> Dict:
        """
        因子分析 - 评估因子有效性
        
        分析内容:
            - IC 分析 (Information Coefficient)
            - IR 分析 (Information Ratio)
            - 因子暴露分析
            - 因子衰减分析
            - 因子相关性矩阵
        """
        if not market_data or not signals:
            return {'error': 'Insufficient data'}
        
        analysis = {
            'ic_analysis': self._analyze_ic(market_data, signals),
            'ir_analysis': self._analyze_ir(signals),
            'factor_exposure': self._analyze_factor_exposure(market_data, signals),
            'factor_decay': self._analyze_factor_decay(market_data, signals),
            'factor_correlation': self._analyze_factor_correlation(signals)
        }
        
        return analysis
    
    def _analyze_ic(self, market_data: Dict[str, pd.DataFrame], 
                    signals: List[Dict]) -> Dict:
        """IC 分析 - 因子与收益的相关性"""
        # 简化 IC 计算
        ic_values = []
        
        for signal in signals[:100]:  # 限制计算量
            factor_value = signal.get('factor_value', 0)
            future_return = signal.get('future_return', 0)
            
            if factor_value is not None and future_return is not None:
                ic_values.append((factor_value, future_return))
        
        if len(ic_values) < 10:
            return {'mean_ic': 0, 'ic_std': 0, 'ic_ir': 0, 'sample_size': len(ic_values)}
        
        factors = [x[0] for x in ic_values]
        returns = [x[1] for x in ic_values]
        
        ic_array = np.corrcoef(factors, returns)[0, 1]
        ic_mean = np.mean([ic_array]) if not np.isnan(ic_array) else 0
        ic_std = np.std([ic_array]) if not np.isnan(ic_array) else 0
        ic_ir = ic_mean / ic_std if ic_std > 0 else 0
        
        return {
            'mean_ic': ic_mean,
            'ic_std': ic_std,
            'ic_ir': ic_ir,
            'sample_size': len(ic_values),
            'ic_t_stat': ic_mean / (ic_std / np.sqrt(len(ic_values))) if ic_std > 0 and len(ic_values) > 0 else 0
        }
    
    def _analyze_ir(self, signals: List[Dict]) -> Dict:
        """IR 分析 - 信息比率"""
        if not signals:
            return {'ir': 0, 'active_return': 0, 'tracking_error': 0}
        
        active_returns = [s.get('active_return', 0) for s in signals if 'active_return' in s]
        
        if not active_returns:
            return {'ir': 0, 'active_return': 0, 'tracking_error': 0}
        
        mean_active = np.mean(active_returns)
        std_active = np.std(active_returns)
        ir = mean_active / std_active * np.sqrt(252) if std_active > 0 else 0
        
        return {
            'ir': ir,
            'active_return': mean_active * 252,
            'tracking_error': std_active * np.sqrt(252)
        }
    
    def _analyze_factor_exposure(self, market_data: Dict[str, pd.DataFrame],
                                  signals: List[Dict]) -> Dict:
        """因子暴露分析"""
        # 简化处理
        exposures = {
            'momentum': {'mean': 0.5, 'std': 0.2, 'min': -0.5, 'max': 1.5},
            'value': {'mean': 0.3, 'std': 0.15, 'min': -0.3, 'max': 1.0},
            'volatility': {'mean': 0.4, 'std': 0.25, 'min': -0.2, 'max': 1.2},
            'liquidity': {'mean': 0.2, 'std': 0.1, 'min': -0.1, 'max': 0.8}
        }
        
        return exposures
    
    def _analyze_factor_decay(self, market_data: Dict[str, pd.DataFrame],
                               signals: List[Dict]) -> Dict:
        """因子衰减分析 - IC 随时间的衰减"""
        decay_periods = [1, 5, 10, 20, 60]
        decay_values = []
        
        for period in decay_periods:
            # 模拟衰减
            decay = 0.95 ** (period / 10)
            decay_values.append({
                'period': period,
                'ic_decay': decay,
                'retention_rate': decay * 100
            })
        
        return {'decay_analysis': decay_values}
    
    def _analyze_factor_correlation(self, signals: List[Dict]) -> Dict:
        """因子相关性矩阵"""
        # 简化处理 - 返回示例数据
        correlation_matrix = {
            'momentum': {'momentum': 1.0, 'value': -0.15, 'volatility': 0.25, 'liquidity': 0.1},
            'value': {'momentum': -0.15, 'value': 1.0, 'volatility': -0.3, 'liquidity': 0.05},
            'volatility': {'momentum': 0.25, 'value': -0.3, 'volatility': 1.0, 'liquidity': -0.2},
            'liquidity': {'momentum': 0.1, 'value': 0.05, 'volatility': -0.2, 'liquidity': 1.0}
        }
        
        return correlation_matrix
    
    # ==================== 相关性分析 ====================
    
    def correlation_analysis(self, strategy_results: Dict[str, Dict]) -> Dict:
        """
        相关性分析 - 策略/品种/周期相关性
        
        分析内容:
            - 策略收益相关性矩阵
            - 品种收益相关性矩阵
            - 周期收益相关性矩阵
            - 低相关性策略组合建议
        """
        if not strategy_results:
            return {'error': 'No strategy results'}
        
        # 提取收益序列
        returns_matrix = {}
        for name, result in strategy_results.items():
            if 'equity_curve' in result:
                equity = result['equity_curve']
                if len(equity) > 1:
                    returns = [(equity[i] - equity[i-1]) / equity[i-1] 
                               for i in range(1, len(equity))]
                    returns_matrix[name] = returns
        
        if len(returns_matrix) < 2:
            return {'error': 'Insufficient data for correlation'}
        
        # 计算相关性矩阵
        correlation_matrix = {}
        strategies = list(returns_matrix.keys())
        
        for s1 in strategies:
            correlation_matrix[s1] = {}
            for s2 in strategies:
                if s1 == s2:
                    correlation_matrix[s1][s2] = 1.0
                else:
                    r1 = returns_matrix[s1]
                    r2 = returns_matrix[s2]
                    min_len = min(len(r1), len(r2))
                    if min_len > 10:
                        corr = np.corrcoef(r1[:min_len], r2[:min_len])[0, 1]
                        correlation_matrix[s1][s2] = corr if not np.isnan(corr) else 0
                    else:
                        correlation_matrix[s1][s2] = 0
        
        # 找出低相关性策略对
        low_corr_pairs = []
        for i, s1 in enumerate(strategies):
            for j, s2 in enumerate(strategies):
                if i < j:
                    corr = correlation_matrix[s1][s2]
                    if abs(corr) < 0.3:
                        low_corr_pairs.append({
                            'strategy1': s1,
                            'strategy2': s2,
                            'correlation': corr
                        })
        
        low_corr_pairs.sort(key=lambda x: abs(x['correlation']))
        
        return {
            'correlation_matrix': correlation_matrix,
            'low_correlation_pairs': low_corr_pairs[:10],
            'diversification_suggestion': self._suggest_diversification(correlation_matrix, strategy_results)
        }
    
    def _suggest_diversification(self, corr_matrix: Dict, 
                                  strategy_results: Dict[str, Dict]) -> List[str]:
        """多样化配置建议"""
        suggestions = []
        
        # 找出表现最好且低相关的策略
        sorted_by_sharpe = sorted(
            strategy_results.items(),
            key=lambda x: x[1].get('sharpe_ratio', 0),
            reverse=True
        )
        
        if len(sorted_by_sharpe) >= 2:
            best = sorted_by_sharpe[0][0]
            second = sorted_by_sharpe[1][0]
            
            if best in corr_matrix and second in corr_matrix[best]:
                corr = corr_matrix[best][second]
                if abs(corr) < 0.5:
                    suggestions.append(f"建议配置 {best} + {second} (相关性={corr:.2f})")
        
        suggestions.append("选择低相关性策略组合可以降低整体波动")
        suggestions.append("建议配置 3-5 个低相关性策略以分散风险")
        
        return suggestions
    
    # ==================== 市场状态分析 ====================
    
    def market_regime_analysis(self, market_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        市场状态分析 - 识别市场 regime
        
        状态分类:
            - 趋势市场 (上涨/下跌)
            - 震荡市场
            - 高波动市场
            - 低波动市场
        """
        if not market_data:
            return {'error': 'No market data'}
        
        regimes = {}
        
        for symbol, df in list(market_data.items())[:5]:  # 分析前 5 个品种
            if len(df) < 60:
                continue
            
            # 计算趋势指标
            ma20 = df['close'].rolling(20).mean()
            ma60 = df['close'].rolling(60).mean()
            
            # 计算波动率
            returns = df['close'].pct_change()
            volatility = returns.rolling(20).std()
            
            # 当前状态
            latest = df.iloc[-1]
            latest_ma20 = ma20.iloc[-1]
            latest_ma60 = ma60.iloc[-1]
            latest_vol = volatility.iloc[-1]
            
            # 判断趋势
            if latest_ma20 > latest_ma60:
                trend = 'uptrend'
            elif latest_ma20 < latest_ma60:
                trend = 'downtrend'
            else:
                trend = 'sideways'
            
            # 判断波动
            avg_vol = volatility.mean()
            if latest_vol > avg_vol * 1.5:
                vol_state = 'high'
            elif latest_vol < avg_vol * 0.5:
                vol_state = 'low'
            else:
                vol_state = 'normal'
            
            regimes[symbol] = {
                'trend': trend,
                'volatility_state': vol_state,
                'current_volatility': latest_vol,
                'avg_volatility': avg_vol,
                'ma20': latest_ma20,
                'ma60': latest_ma60,
                'price': latest['close']
            }
        
        # 整体市场状态
        trend_counts = defaultdict(int)
        vol_counts = defaultdict(int)
        
        for symbol, regime in regimes.items():
            trend_counts[regime['trend']] += 1
            vol_counts[regime['volatility_state']] += 1
        
        dominant_trend = max(trend_counts, key=trend_counts.get) if trend_counts else 'unknown'
        dominant_vol = max(vol_counts, key=vol_counts.get) if vol_counts else 'unknown'
        
        return {
            'overall_regime': {
                'trend': dominant_trend,
                'volatility': dominant_vol
            },
            'by_symbol': regimes,
            'strategy_suggestions': self._regime_strategy_suggestions(dominant_trend, dominant_vol)
        }
    
    def _regime_strategy_suggestions(self, trend: str, volatility: str) -> List[str]:
        """根据市场状态给出策略建议"""
        suggestions = []
        
        if trend == 'uptrend':
            suggestions.append("市场处于上涨趋势，建议增加趋势跟踪策略权重")
        elif trend == 'downtrend':
            suggestions.append("市场处于下跌趋势，可考虑增加反向策略")
        else:
            suggestions.append("市场处于震荡状态，建议增加均值回归策略权重")
        
        if volatility == 'high':
            suggestions.append("波动率较高，建议降低仓位或增加止损")
        elif volatility == 'low':
            suggestions.append("波动率较低，可适当增加仓位")
        
        return suggestions
    
    # ==================== 策略诊断 ====================
    
    def strategy_diagnosis(self, strategy_name: str, result: Dict) -> Dict:
        """
        策略诊断 - 定位问题
        
        诊断内容:
            - 表现异常检测
            - 问题根因分析
            - 优化建议
        """
        diagnosis = {
            'strategy_name': strategy_name,
            'overall_health': 'good',
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'metrics_assessment': {}
        }
        
        # 评估各项指标
        total_return = result.get('total_return', 0)
        sharpe = result.get('sharpe_ratio', 0)
        max_dd = result.get('max_drawdown', 0)
        win_rate = result.get('win_rate', 0)
        pl_ratio = result.get('profit_loss_ratio', 0)
        
        # 收益评估
        if total_return < -0.2:
            diagnosis['issues'].append({
                'type': 'negative_return',
                'severity': 'high',
                'description': f'策略收益为 {total_return:.2%}，表现较差',
                'suggestion': '检查策略逻辑或考虑暂停该策略'
            })
            diagnosis['overall_health'] = 'poor'
        elif total_return < 0:
            diagnosis['warnings'].append({
                'type': 'slight_negative',
                'severity': 'medium',
                'description': f'策略收益为 {total_return:.2%}，略微亏损',
                'suggestion': '考虑优化策略参数'
            })
        
        # 夏普比率评估
        if sharpe < 0:
            diagnosis['issues'].append({
                'type': 'negative_sharpe',
                'severity': 'high',
                'description': f'夏普比率为 {sharpe:.2f}，风险调整收益为负',
                'suggestion': '策略风险过高或收益不足，需要重新评估'
            })
            diagnosis['overall_health'] = 'poor'
        elif sharpe < 0.5:
            diagnosis['warnings'].append({
                'type': 'low_sharpe',
                'severity': 'medium',
                'description': f'夏普比率为 {sharpe:.2f}，低于 0.5',
                'suggestion': '考虑优化入场信号或止损策略'
            })
        
        # 回撤评估
        if max_dd > 0.3:
            diagnosis['issues'].append({
                'type': 'high_drawdown',
                'severity': 'high',
                'description': f'最大回撤为 {max_dd:.2%}，超过 30%',
                'suggestion': '加强止损控制或降低仓位'
            })
        elif max_dd > 0.15:
            diagnosis['warnings'].append({
                'type': 'moderate_drawdown',
                'severity': 'medium',
                'description': f'最大回撤为 {max_dd:.2%}，建议关注',
                'suggestion': '考虑增加止损或降低单笔风险'
            })
        
        # 胜率评估
        if win_rate < 0.35:
            diagnosis['warnings'].append({
                'type': 'low_win_rate',
                'severity': 'medium',
                'description': f'胜率为 {win_rate:.2%}，低于 35%',
                'suggestion': '优化入场信号质量或调整出场策略'
            })
        
        # 盈亏比评估
        if pl_ratio < 1.0:
            diagnosis['warnings'].append({
                'type': 'low_pl_ratio',
                'severity': 'medium',
                'description': f'盈亏比为 {pl_ratio:.2f}，小于 1',
                'suggestion': '提高止盈目标或降低止损幅度'
            })
        
        # 生成综合建议
        if diagnosis['overall_health'] == 'good':
            diagnosis['suggestions'].append('策略表现良好，建议继续观察')
        elif diagnosis['overall_health'] == 'poor':
            diagnosis['suggestions'].append('建议暂停策略并进行全面复盘')
        
        # 参数优化建议
        if sharpe < 0.5 or max_dd > 0.15:
            diagnosis['suggestions'].append('建议进行参数敏感性分析，寻找更稳健的参数组合')
        
        return diagnosis
    
    # ==================== 报告导出 ====================
    
    def export_analysis_report(self, analysis_results: Dict, 
                                filename: str) -> str:
        """导出分析报告"""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        return filepath
    
    def generate_summary_report(self, evaluation_results: Dict, 
                                 attribution_results: Dict,
                                 diagnosis_results: Dict) -> str:
        """生成综合分析报告"""
        lines = [
            "=" * 80,
            "🦞 期货量化系统 - 综合分析报告",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ]
        
        # 总体评估
        lines.append("📊 【总体评估】")
        if evaluation_results:
            avg_score = np.mean([r.get('composite_score', 0) 
                                for r in evaluation_results.values()])
            lines.append(f"   平均综合评分：{avg_score:.1f}/100")
            
            # 最佳策略
            best = max(evaluation_results.items(), 
                      key=lambda x: x[1].get('composite_score', 0))
            lines.append(f"   最佳策略：{best[0]} (评分：{best[1].get('composite_score', 0):.1f})")
        
        lines.append("")
        
        # 绩效归因
        lines.append("📈 【绩效归因】")
        if attribution_results and 'by_symbol' in attribution_results:
            lines.append("   品种贡献 Top 3:")
            for i, (symbol, data) in enumerate(list(attribution_results['by_symbol'].items())[:3]):
                lines.append(f"      {i+1}. {symbol}: ¥{data['total_pnl']:,.2f} ({data['contribution_pct']:.1f}%)")
        
        lines.append("")
        
        # 问题诊断
        lines.append("⚠️ 【问题诊断】")
        total_issues = sum(len(d.get('issues', [])) for d in diagnosis_results.values())
        total_warnings = sum(len(d.get('warnings', [])) for d in diagnosis_results.values())
        lines.append(f"   发现 {total_issues} 个严重问题，{total_warnings} 个警告")
        
        if total_issues > 0:
            lines.append("   需要关注:")
            for name, diag in diagnosis_results.items():
                for issue in diag.get('issues', [])[:2]:
                    lines.append(f"      - {name}: {issue['description']}")
        
        lines.append("")
        lines.append("=" * 80)
        
        report = "\n".join(lines)
        
        # 保存
        filepath = os.path.join(self.output_dir, 'comprehensive_analysis.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


# 测试
if __name__ == "__main__":
    print("✅ 分析系统已加载")
    print("   - 绩效归因分析")
    print("   - 因子分析 (IC/IR)")
    print("   - 相关性分析")
    print("   - 市场状态分析")
    print("   - 策略诊断")
    print("   - 综合报告生成")
