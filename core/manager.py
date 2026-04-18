"""
=============================================================================
期货量化系统 - 核心管理器
=============================================================================
功能:
  - 统一初始化所有组件
  - 管理执行流程
  - 提供单一入口点
  - 错误处理与日志记录
  - 配置管理与验证
=============================================================================
"""
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    TRADING_CONFIG,
    BACKTEST_CONFIG,
    PATHS,
    CONTRACTS,
    TIMEFRAMES
)
from market.feeder import MarketDataFeeder
from strategy.indicators import IndicatorEngine
from strategy.signals import StrategyGenerator
from trading.executor import OrderExecutor
from trading.portfolio import Portfolio
from analysis import (
    PerformanceEvaluator,
    FairEvaluationSystem,
    AnalyticsEngine,
    StrategyRanker,
    ReportGenerator
)


class FuturesQuantManager:
    """
    期货量化系统核心管理器
    
    统一管理所有组件，提供简洁的 API 接口
    """
    
    def __init__(self, initial_capital: float = 1_000_000, log_level: str = 'INFO'):
        """
        初始化系统管理器
        
        参数:
            initial_capital: 初始资金
            log_level: 日志级别
        """
        self.initial_capital = initial_capital
        self.start_time = None
        self.end_time = None
        
        # 设置日志
        self._setup_logging(log_level)
        
        # 核心组件 (延迟初始化)
        self.portfolio = None
        self.market = None
        self.executor = None
        self.generator = None
        self.engine = None
        self.evaluator = None
        self.fair_eval = None
        self.analytics = None
        self.ranker = None
        self.report_gen = None
        
        # 数据缓存
        self.market_data = None
        self.signals = None
        self.results = None
        
        self.logger.info("🦞 期货量化系统管理器已创建")
        self.logger.info(f"   初始资金：¥{initial_capital:,.2f}")
        self.logger.info(f"   支持合约：{len(CONTRACTS)} 个")
        self.logger.info(f"   支持周期：{len(TIMEFRAMES)} 个")
    
    def _setup_logging(self, level: str):
        """设置日志系统"""
        log_dir = PATHS.get('logs', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'system_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('FuturesQuantManager')
    
    def initialize(self) -> bool:
        """
        初始化所有组件
        
        返回:
            bool: 初始化是否成功
        """
        self.start_time = datetime.now()
        self.logger.info("\n📦 初始化交易组件...")
        
        try:
            # 初始化所有组件
            self.portfolio = Portfolio(self.initial_capital)
            self.market = MarketDataFeeder(PATHS.get('data', 'data'))
            self.executor = OrderExecutor(self.portfolio)
            self.generator = StrategyGenerator()
            self.engine = IndicatorEngine()
            self.evaluator = PerformanceEvaluator()
            self.fair_eval = FairEvaluationSystem()
            self.analytics = AnalyticsEngine()
            self.ranker = StrategyRanker()
            self.report_gen = ReportGenerator()
            
            self.logger.info("   ✅ 所有组件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"   ❌ 初始化失败：{e}")
            return False
    
    def load_market_data(self, use_cache: bool = True) -> Dict:
        """
        加载市场数据
        
        参数:
            use_cache: 是否使用缓存数据
        
        返回:
            Dict: 市场数据字典
        """
        self.logger.info("\n📊 加载市场数据...")
        
        try:
            self.market_data = self.market.load_data()
            symbols = self.market.get_all_symbols()
            
            self.logger.info(f"   ✅ 成功加载 {len(symbols)} 个合约数据")
            return self.market_data
            
        except Exception as e:
            self.logger.error(f"   ❌ 数据加载失败：{e}")
            raise
    
    def generate_signals(self) -> Dict:
        """
        生成交易信号
        
        返回:
            Dict: 信号字典
        """
        self.logger.info("\n🎯 生成交易信号...")
        
        try:
            # 获取所有合约
            symbols = self.market.get_all_symbols()
            all_signals = {}
            signal_count = 0
            
            for symbol in symbols:
                df = self.market.get_ohlcv(symbol)
                if df is not None and len(df) > 50:
                    # 计算指标
                    df_indicators = self.engine.calculate_all(df)
                    # 生成信号
                    sigs = self.generator.generate_for_symbol(symbol, df_indicators)
                    all_signals.update({s['name']: s for s in sigs})
                    signal_count += len(sigs)
            
            self.signals = all_signals
            self.logger.info(f"   ✅ 生成 {signal_count} 个交易信号")
            return all_signals
            
        except Exception as e:
            self.logger.error(f"   ❌ 信号生成失败：{e}")
            raise
    
    def execute_trades(self) -> List:
        """
        执行交易
        
        返回:
            List: 已执行的订单列表
        """
        self.logger.info("\n💰 执行交易订单...")
        
        try:
            prices = self.market.get_price_dict()
            self.executor.execute_signals(self.signals, prices, market_data=self.market_data)
            
            # 更新持仓盈亏
            for symbol, pos in self.portfolio.positions.items():
                if symbol in prices:
                    pos.update_pnl(prices[symbol])
            
            self.logger.info(f"   ✅ 执行完成，当前持仓 {len(self.portfolio.positions)} 个")
            return self.executor.executed_orders
            
        except Exception as e:
            self.logger.error(f"   ❌ 交易执行失败：{e}")
            raise
    
    def evaluate_performance(self) -> Dict:
        """
        评估绩效
        
        返回:
            Dict: 绩效评估结果
        """
        self.logger.info("\n📉 评估绩效...")
        
        try:
            # 基础评估
            base_results = self.evaluator.evaluate(self.portfolio)
            
            # 公平公正评估
            trades = self.executor.executed_orders
            equity_curve = self.portfolio.equity_curve
            
            fair_results = {}
            if equity_curve and len(equity_curve) > 1:
                fair_results = self.fair_eval.evaluate_strategy(equity_curve, trades)
            
            # 合并结果
            self.results = {
                **base_results,
                **fair_results,
                'base_metrics': base_results,
                'fair_metrics': fair_results
            }
            
            self.logger.info(f"   ✅ 评估完成，综合评分：{fair_results.get('composite_score', 0):.1f}/100")
            return self.results
            
        except Exception as e:
            self.logger.error(f"   ❌ 绩效评估失败：{e}")
            raise
    
    def analyze(self) -> Dict:
        """
        深度分析
        
        返回:
            Dict: 分析结果
        """
        self.logger.info("\n🔍 深度分析...")
        
        try:
            trades = self.executor.executed_orders
            
            # 绩效归因
            attribution = self.analytics.performance_attribution(self.portfolio, trades)
            
            # 策略诊断
            diagnosis = {}
            if self.results:
                diagnosis = self.analytics.strategy_diagnosis("主策略", self.results)
            
            analysis_results = {
                'attribution': attribution,
                'diagnosis': diagnosis
            }
            
            self.logger.info("   ✅ 分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"   ❌ 分析失败：{e}")
            raise
    
    def generate_report(self, report_type: str = 'daily') -> str:
        """
        生成报告
        
        参数:
            report_type: 报告类型 (daily/weekly/monthly)
        
        返回:
            str: 报告文件路径
        """
        self.logger.info(f"\n📄 生成{report_type}报告...")
        
        try:
            if report_type == 'daily':
                report = self.report_gen.generate_daily_report(
                    self.portfolio,
                    self.executor,
                    self.results
                )
            else:
                raise ValueError(f"不支持的报告类型：{report_type}")
            
            self.logger.info(f"   ✅ 报告已生成：{report_type}")
            return report
            
        except Exception as e:
            self.logger.error(f"   ❌ 报告生成失败：{e}")
            raise
    
    def run_full_pipeline(self, generate_report: bool = False) -> Dict:
        """
        运行完整流程
        
        参数:
            generate_report: 是否生成报告
        
        返回:
            Dict: 完整结果
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"🦞 期货量化系统 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)
        
        try:
            # 1. 初始化
            if not self.initialize():
                raise RuntimeError("初始化失败")
            
            # 2. 加载数据
            self.load_market_data()
            
            # 3. 生成信号
            self.generate_signals()
            
            # 4. 执行交易
            self.execute_trades()
            
            # 5. 评估绩效
            self.evaluate_performance()
            
            # 6. 深度分析
            analysis = self.analyze()
            
            # 7. 生成报告 (可选)
            if generate_report:
                self.generate_report('daily')
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            self.logger.info(f"\n✅ 流程完成，耗时：{duration:.2f}秒")
            self.logger.info("=" * 60)
            
            return {
                'success': True,
                'results': self.results,
                'analysis': analysis,
                'duration_seconds': duration,
                'portfolio_stats': self.portfolio.get_stats()
            }
            
        except Exception as e:
            self.logger.error(f"\n❌ 流程执行失败：{e}")
            self.end_time = datetime.now()
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.start_time else 0
            }
    
    def get_status(self) -> Dict:
        """
        获取系统状态
        
        返回:
            Dict: 状态信息
        """
        return {
            'initialized': self.portfolio is not None,
            'data_loaded': self.market_data is not None,
            'signals_generated': self.signals is not None,
            'results_available': self.results is not None,
            'portfolio_stats': self.portfolio.get_stats() if self.portfolio else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def shutdown(self):
        """关闭系统，清理资源"""
        self.logger.info("\n🔒 关闭系统...")
        self.portfolio = None
        self.market = None
        self.executor = None
        self.logger.info("   ✅ 系统已关闭")


# 便捷函数
def run_quant_system(initial_capital: float = 1_000_000, generate_report: bool = False) -> Dict:
    """
    一键运行量化系统
    
    参数:
        initial_capital: 初始资金
        generate_report: 是否生成报告
    
    返回:
        Dict: 运行结果
    """
    manager = FuturesQuantManager(initial_capital)
    return manager.run_full_pipeline(generate_report)


# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='🦞 期货量化系统管理器')
    parser.add_argument('--capital', type=float, default=1_000_000, help='初始资金')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--log-level', type=str, default='INFO', help='日志级别')
    
    args = parser.parse_args()
    
    manager = FuturesQuantManager(args.capital, args.log_level)
    result = manager.run_full_pipeline(generate_report=args.report)
    
    if result['success']:
        print(f"\n✅ 系统运行成功!")
        print(f"   总收益率：{result['results'].get('total_return', 0):.2%}")
        print(f"   综合评分：{result['results'].get('composite_score', 0):.1f}/100")
        print(f"   耗时：{result['duration_seconds']:.2f}秒")
    else:
        print(f"\n❌ 系统运行失败：{result.get('error', '未知错误')}")
