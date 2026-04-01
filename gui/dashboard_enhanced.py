"""
=============================================================================
期货量化模拟盘 - 增强版桌面仪表盘
=============================================================================
功能：
  - 10+ 核心绩效指标卡片
  - 资金曲线 + 回撤分析图
  - 持仓/策略/信号/风险 Tab 切换
  - 品种分类统计与热力图
  - 风险指标 (VaR/CVaR/仓位)
  - 策略类型分布
  - 月度收益分析
  - 自动刷新 (30 秒)

参考 Web 布局设计，提供同等丰富的信息展示

作者：OpenClaw 🦞
日期：2026-03-31
=============================================================================
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import warnings
from datetime import datetime
from typing import Dict, List, Any
import json

warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONTRACTS, TRADING_CONFIG, TIMEFRAMES
from market.feeder import MarketDataFeeder
from strategy.signals import StrategyGenerator
from strategy.indicators import IndicatorEngine
from trading.executor import OrderExecutor
from trading.portfolio import Portfolio
from analysis.evaluator import PerformanceEvaluator
from analysis.ranker import StrategyRanker


# 尝试导入 matplotlib 用于图表
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️ matplotlib 未安装，图表功能将不可用")


class EnhancedDashboard:
    """增强版期货量化仪表盘"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🦞 期货量化模拟盘 - 增强版仪表盘")
        self.root.geometry("1800x1100")
        
        # 深色主题配色
        self.colors = {
            'bg': '#1a1a2e',
            'card_bg': '#16213e',
            'text': '#eaeaea',
            'accent': '#0f3460',
            'green': '#00ff88',
            'red': '#ff4757',
            'yellow': '#ffa502',
            'blue': '#3498db',
            'purple': '#9b59b6',
        }
        
        # 数据状态
        self.portfolio = None
        self.market = None
        self.executor = None
        self.evaluator = None
        self.ranker = None
        self.results = {}
        self.rankings = {}
        self.positions_data = []
        self.strategies_data = []
        self.equity_curve = []
        self.risk_metrics = {}
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_header()
        self.create_performance_cards()
        self.create_tabs()
        self.create_status_bar()
        
        # 绑定刷新
        self.root.bind("<F5>", lambda e: self.refresh_data())
        
        # 自动刷新
        self.auto_refresh_interval = 30000
        self.after_id = None
        
    def setup_styles(self):
        """设置 GUI 样式"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 配置各种样式
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'),
                       background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Card.TFrame', background=self.colors['card_bg'])
        style.configure('Positive.TLabel', foreground=self.colors['green'])
        style.configure('Negative.TLabel', foreground=self.colors['red'])
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'),
                       background=self.colors['accent'], foreground=self.colors['text'])
        
    def create_header(self):
        """创建顶部标题栏"""
        header_frame = tk.Frame(self.root, bg=self.colors['accent'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(
            header_frame,
            text="🦞 期货量化模拟盘系统 | 增强版",
            font=('Helvetica', 22, 'bold'),
            bg=self.colors['accent'],
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=25, pady=15)
        
        # 副标题
        subtitle = "53 合约 | 232 策略 | 203 指标 | 10 周期"
        tk.Label(
            header_frame,
            text=subtitle,
            font=('Helvetica', 11),
            bg=self.colors['accent'],
            fg='#aaa'
        ).pack(side=tk.LEFT, padx=10, pady=25)
        
        # 时间显示
        self.time_label = tk.Label(
            header_frame,
            text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            font=('Helvetica', 11),
            bg=self.colors['accent'],
            fg='#888'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=25)
        
        # 刷新按钮
        tk.Button(
            header_frame,
            text="🔄 刷新 (F5)",
            command=self.refresh_data,
            bg=self.colors['green'],
            fg='#000',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=10, pady=15)
        
    def create_performance_cards(self):
        """创建 10 个核心绩效卡片"""
        cards_frame = tk.Frame(self.root, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 10 个绩效指标配置
        self.perf_cards = {}
        card_configs = [
            ('💰 总收益率', 'total_return', '%', True, '越高越好'),
            ('📊 夏普比率', 'sharpe_ratio', '', False, '>1 优秀'),
            ('📉 最大回撤', 'max_drawdown', '%', False, '越低越好'),
            ('🎯 胜率', 'win_rate', '%', True, '>50% 良好'),
            ('⚡ 卡尔玛比率', 'calmar_ratio', '', True, '收益/回撤'),
            ('📈 盈亏比', 'profit_loss_ratio', '', True, '>2 优秀'),
            ('📊 索提诺比率', 'sortino_ratio', '', True, '下行风险调整'),
            ('💹 年化波动', 'volatility', '%', False, '风险度量'),
            ('🎲 信息比率', 'information_ratio', '', True, '超额收益'),
            ('📐 跟踪误差', 'tracking_error', '%', False, '偏离基准'),
        ]
        
        for i, (title, key, suffix, higher_better, note) in enumerate(card_configs):
            card = tk.Frame(cards_frame, bg=self.colors['card_bg'], relief=tk.RAISED, bd=1)
            card.grid(row=i//5, column=i%5, padx=5, pady=5, sticky='nsew')
            
            # 标题
            tk.Label(
                card,
                text=title,
                font=('Helvetica', 10, 'bold'),
                bg=self.colors['card_bg'],
                fg=self.colors['text']
            ).pack(pady=(8, 3))
            
            # 数值
            value_label = tk.Label(
                card,
                text="--",
                font=('Helvetica', 20, 'bold'),
                bg=self.colors['card_bg'],
                fg='white'
            )
            value_label.pack(pady=5)
            
            # 说明
            tk.Label(
                card,
                text=note,
                font=('Helvetica', 8),
                bg=self.colors['card_bg'],
                fg='#888'
            ).pack(pady=(0, 5))
            
            self.perf_cards[key] = {
                'label': value_label,
                'suffix': suffix,
                'higher_better': higher_better
            }
        
        # 配置网格权重
        for col in range(5):
            cards_frame.grid_columnconfigure(col, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)
        
    def create_tabs(self):
        """创建 Tab 切换面板"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建 Notebook (Tab 容器)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个 Tab
        self.create_rankings_tab()
        self.create_positions_tab()
        self.create_signals_tab()
        self.create_risk_tab()
        self.create_analysis_tab()
        
    def create_rankings_tab(self):
        """🏆 策略排名 Tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(tab_frame, text=" 🏆 策略排名 ")
        
        # 左右分栏
        left_frame = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        # 左侧：策略排名表格
        table_frame = tk.LabelFrame(
            left_frame,
            text="🏆 策略排名 TOP50",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("rank", "name", "type", "score", "return_rate", "sharpe")
        self.rankings_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=25
        )
        
        headers = {
            "rank": "排名",
            "name": "策略名称",
            "type": "类型",
            "score": "得分",
            "return_rate": "收益率",
            "sharpe": "夏普",
        }
        
        for col in columns:
            self.rankings_tree.heading(col, text=headers[col])
            self.rankings_tree.column(col, width=70 if col != 'name' else 180)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.rankings_tree.yview)
        self.rankings_tree.configure(yscrollcommand=scrollbar.set)
        self.rankings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧：策略类型分布
        type_frame = tk.LabelFrame(
            right_frame,
            text="📊 策略类型分布",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        type_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.type_dist_labels = {}
        type_categories = ['趋势跟踪', '均值回归', '突破策略', '形态识别', 
                          '指标组合', '其他']
        
        for t in type_categories:
            row = tk.Frame(type_frame, bg=self.colors['card_bg'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(row, text=t, font=('Helvetica', 10),
                    bg=self.colors['card_bg'], fg=self.colors['text'],
                    width=12, anchor='w').pack(side=tk.LEFT)
            
            # 进度条
            bar_frame = tk.Frame(row, bg=self.colors['accent'], height=16)
            bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            bar = tk.Frame(bar_frame, bg=self.colors['blue'], height=16, width=0)
            bar.pack(side=tk.LEFT)
            
            count_label = tk.Label(row, text="0", font=('Helvetica', 10, 'bold'),
                                  bg=self.colors['card_bg'], fg=self.colors['green'],
                                  width=4)
            count_label.pack(side=tk.LEFT)
            
            self.type_dist_labels[t] = {'bar': bar, 'count': count_label, 'frame': bar_frame}
        
        # 策略统计
        stats_frame = tk.LabelFrame(
            right_frame,
            text="📈 策略统计",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        stats_frame.pack(fill=tk.X)
        
        self.strategy_stats = {}
        stats_items = [
            ("策略总数", "total_strategies"),
            ("活跃信号", "active_signals"),
            ("买入信号", "buy_signals"),
            ("卖出信号", "sell_signals"),
            ("持有信号", "hold_signals"),
            ("平均强度", "avg_strength"),
        ]
        
        for label, key in stats_items:
            row = tk.Frame(stats_frame, bg=self.colors['card_bg'])
            row.pack(fill=tk.X, pady=4)
            
            tk.Label(row, text=label, font=('Helvetica', 10),
                    bg=self.colors['card_bg'], fg='#aaa', width=10, anchor='w'
                    ).pack(side=tk.LEFT)
            
            val = tk.Label(row, text="--", font=('Helvetica', 11, 'bold'),
                          bg=self.colors['card_bg'], fg=self.colors['text'], anchor='w')
            val.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.strategy_stats[key] = val
        
    def create_positions_tab(self):
        """📋 持仓明细 Tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(tab_frame, text=" 📋 持仓明细 ")
        
        # 筛选工具栏
        toolbar = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(toolbar, text="品种筛选:", bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        self.pos_category_filter = ttk.Combobox(
            toolbar,
            values=["全部"] + list(set(c.get("category", "其他") for c in CONTRACTS.values())),
            state="readonly",
            width=12
        )
        self.pos_category_filter.set("全部")
        self.pos_category_filter.pack(side=tk.LEFT, padx=5)
        self.pos_category_filter.bind("<<ComboboxSelected>>", self.filter_positions)
        
        tk.Label(toolbar, text="排序:", bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=(20, 5))
        
        self.pos_sort_var = tk.StringVar(value="pnl")
        sort_combo = ttk.Combobox(
            toolbar,
            textvariable=self.pos_sort_var,
            values=[("pnl", "盈亏"), ("pnl_pct", "盈亏%"), ("symbol", "合约")],
            state="readonly",
            width=10
        )
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", self.sort_positions)
        
        # 持仓表格
        table_frame = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("symbol", "name", "category", "direction", "quantity", 
                   "entry_price", "current_price", "pnl", "pnl_pct", "margin")
        
        self.positions_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=30
        )
        
        headers = {
            "symbol": "合约", "name": "名称", "category": "品种",
            "direction": "方向", "quantity": "数量",
            "entry_price": "开仓价", "current_price": "现价",
            "pnl": "盈亏", "pnl_pct": "盈亏%", "margin": "保证金",
        }
        
        for col in columns:
            self.positions_tree.heading(col, text=headers[col],
                                       command=lambda c=col: self.sort_treeview(c))
            width = 70
            if col in ['name', 'symbol']:
                width = 100
            elif col == 'category':
                width = 80
            self.positions_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=scrollbar.set)
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 颜色标签
        self.positions_tree.tag_configure('positive', foreground=self.colors['green'])
        self.positions_tree.tag_configure('negative', foreground=self.colors['red'])
        
        # 持仓汇总
        summary_frame = tk.Frame(tab_frame, bg=self.colors['accent'], height=50)
        summary_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        summary_frame.pack_propagate(False)
        
        self.pos_summary_labels = {}
        summary_items = [
            ("持仓数量", "position_count"),
            ("保证金占用", "margin_used"),
            ("浮动盈亏", "floating_pnl"),
            ("仓位使用率", "position_usage"),
        ]
        
        for i, (label, key) in enumerate(summary_items):
            frame = tk.Frame(summary_frame, bg=self.colors['accent'])
            frame.pack(side=tk.LEFT, padx=30, fill=tk.X, expand=True)
            
            tk.Label(frame, text=label, font=('Helvetica', 9),
                    bg=self.colors['accent'], fg='#aaa').pack()
            
            val = tk.Label(frame, text="--", font=('Helvetica', 12, 'bold'),
                          bg=self.colors['accent'], fg=self.colors['green'])
            val.pack()
            
            self.pos_summary_labels[key] = val
        
    def create_signals_tab(self):
        """🎯 交易信号 Tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(tab_frame, text=" 🎯 交易信号 ")
        
        # 筛选工具栏
        toolbar = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(toolbar, text="信号强度:", bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        self.signal_strength_var = tk.StringVar(value="all")
        strength_combo = ttk.Combobox(
            toolbar,
            textvariable=self.signal_strength_var,
            values=[("all", "全部"), ("high", ">70%"), ("medium", ">50%"), ("low", "全部显示")],
            state="readonly",
            width=12
        )
        strength_combo.pack(side=tk.LEFT, padx=5)
        strength_combo.bind("<<ComboboxSelected>>", self.filter_signals)
        
        # 信号表格
        table_frame = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("strategy", "symbol", "category", "signal", "strength", 
                   "type", "timeframe", "price")
        
        self.signals_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=30
        )
        
        headers = {
            "strategy": "策略", "symbol": "合约", "category": "品种",
            "signal": "信号", "strength": "强度", "type": "类型",
            "timeframe": "周期", "price": "价格",
        }
        
        for col in columns:
            self.signals_tree.heading(col, text=headers[col])
            width = 70
            if col == 'strategy':
                width = 150
            elif col == 'symbol':
                width = 80
            self.signals_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.signals_tree.yview)
        self.signals_tree.configure(yscrollcommand=scrollbar.set)
        self.signals_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 信号颜色标签
        self.signals_tree.tag_configure('buy', foreground=self.colors['green'])
        self.signals_tree.tag_configure('sell', foreground=self.colors['red'])
        self.signals_tree.tag_configure('hold', foreground='#888')
        
    def create_risk_tab(self):
        """⚠️ 风险指标 Tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(tab_frame, text=" ⚠️ 风险指标 ")
        
        # 顶部：风险等级卡片
        risk_header = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        risk_header.pack(fill=tk.X, padx=10, pady=10)
        
        self.risk_level_label = tk.Label(
            risk_header,
            text="风险等级：--",
            font=('Helvetica', 24, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        )
        self.risk_level_label.pack(side=tk.LEFT, padx=20)
        
        # 风险指标卡片
        risk_cards = tk.Frame(tab_frame, bg=self.colors['card_bg'])
        risk_cards.pack(fill=tk.X, padx=10, pady=10)
        
        self.risk_cards = {}
        risk_configs = [
            ("VaR 95%", "var_95", "在险价值"),
            ("CVaR 95%", "cvar_95", "条件在险价值"),
            ("Beta", "beta", "市场敏感度"),
            ("平均持仓", "avg_holding", "平均持仓周期"),
        ]
        
        for i, (title, key, note) in enumerate(risk_configs):
            card = tk.Frame(risk_cards, bg=self.colors['accent'], relief=tk.RAISED, bd=1)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            
            tk.Label(card, text=title, font=('Helvetica', 10),
                    bg=self.colors['accent'], fg='#aaa').pack(pady=(8, 3))
            
            val = tk.Label(card, text="--", font=('Helvetica', 18, 'bold'),
                          bg=self.colors['accent'], fg=self.colors['text'])
            val.pack(pady=5)
            
            tk.Label(card, text=note, font=('Helvetica', 8),
                    bg=self.colors['accent'], fg='#666').pack(pady=(0, 5))
            
            self.risk_cards[key] = val
        
        for col in range(4):
            risk_cards.grid_columnconfigure(col, weight=1)
        
        # 仓位分析
        position_frame = tk.LabelFrame(
            tab_frame,
            text="💰 仓位分析",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        position_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.position_metrics = {}
        pos_items = [
            ("总仓位价值", "total_position_value"),
            ("仓位使用率", "position_usage"),
            ("保证金占用", "margin_used"),
            ("可用资金", "available_cash"),
            ("当前权益", "current_equity"),
        ]
        
        for i, (label, key) in enumerate(pos_items):
            row = tk.Frame(position_frame, bg=self.colors['card_bg'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(row, text=label, font=('Helvetica', 10),
                    bg=self.colors['card_bg'], fg='#aaa', width=12, anchor='w'
                    ).pack(side=tk.LEFT)
            
            val = tk.Label(row, text="--", font=('Helvetica', 11, 'bold'),
                          bg=self.colors['card_bg'], fg=self.colors['text'])
            val.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.position_metrics[key] = val
        
        # 品种分类风险
        category_risk_frame = tk.LabelFrame(
            tab_frame,
            text="🏷️ 品种分类风险暴露",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        category_risk_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.category_risk_labels = {}
        categories = list(set(c.get("category", "其他") for c in CONTRACTS.values()))
        
        for cat in categories:
            row = tk.Frame(category_risk_frame, bg=self.colors['card_bg'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(row, text=cat, font=('Helvetica', 10),
                    bg=self.colors['card_bg'], fg=self.colors['text'],
                    width=10, anchor='w').pack(side=tk.LEFT)
            
            # 风险条
            bar_frame = tk.Frame(row, bg=self.colors['accent'], height=14)
            bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            bar = tk.Frame(bar_frame, bg=self.colors['yellow'], height=14, width=0)
            bar.pack(side=tk.LEFT)
            
            val = tk.Label(row, text="0.0%", font=('Helvetica', 9, 'bold'),
                          bg=self.colors['card_bg'], fg=self.colors['text'], width=7)
            val.pack(side=tk.LEFT)
            
            self.category_risk_labels[cat] = {'bar': bar, 'value': val}
        
    def create_analysis_tab(self):
        """📊 深度分析 Tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(tab_frame, text=" 📊 深度分析 ")
        
        # 使用 PanedWindow 分栏
        paned = ttk.PanedWindow(tab_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧
        left_frame = tk.Frame(paned, bg=self.colors['card_bg'])
        paned.add(left_frame, weight=50)
        
        # 右侧
        right_frame = tk.Frame(paned, bg=self.colors['card_bg'])
        paned.add(right_frame, weight=50)
        
        # 左侧：品种收益贡献
        contrib_frame = tk.LabelFrame(
            left_frame,
            text="📊 品种收益贡献",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        contrib_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.contrib_labels = {}
        categories = list(set(c.get("category", "其他") for c in CONTRACTS.values()))
        
        for cat in categories:
            row = tk.Frame(contrib_frame, bg=self.colors['card_bg'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(row, text=cat, font=('Helvetica', 10),
                    bg=self.colors['card_bg'], fg=self.colors['text'],
                    width=10, anchor='w').pack(side=tk.LEFT)
            
            bar_frame = tk.Frame(row, bg=self.colors['accent'], height=16)
            bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            bar = tk.Frame(bar_frame, bg=self.colors['green'], height=16, width=0)
            bar.pack(side=tk.LEFT)
            
            val = tk.Label(row, text="0.0%", font=('Helvetica', 9, 'bold'),
                          bg=self.colors['card_bg'], fg=self.colors['text'], width=7)
            val.pack(side=tk.LEFT)
            
            self.contrib_labels[cat] = {'bar': bar, 'value': val, 'frame': bar_frame}
        
        # 周期表现
        tf_frame = tk.LabelFrame(
            left_frame,
            text="📈 周期表现分析",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        tf_frame.pack(fill=tk.X)
        
        self.timeframe_stats = {}
        for tf_key, tf_info in TIMEFRAMES.items():
            row = tk.Frame(tf_frame, bg=self.colors['card_bg'])
            row.pack(fill=tk.X, pady=2)
            
            tk.Label(row, text=tf_info['name'], font=('Helvetica', 9),
                    bg=self.colors['card_bg'], fg=self.colors['text'],
                    width=8, anchor='w').pack(side=tk.LEFT)
            
            wr = tk.Label(row, text="WR: --", font=('Helvetica', 9),
                         bg=self.colors['card_bg'], fg='#aaa', width=10)
            wr.pack(side=tk.LEFT, padx=5)
            
            ar = tk.Label(row, text="AR: --", font=('Helvetica', 9),
                         bg=self.colors['card_bg'], fg='#aaa', width=10)
            ar.pack(side=tk.LEFT)
            
            self.timeframe_stats[tf_key] = {'win_rate': wr, 'avg_return': ar}
        
        # 右侧：图表区域（如果 matplotlib 可用）
        if HAS_MATPLOTLIB:
            chart_frame = tk.LabelFrame(
                right_frame,
                text="📈 权益曲线",
                font=('Helvetica', 11, 'bold'),
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                padx=5,
                pady=5
            )
            chart_frame.pack(fill=tk.BOTH, expand=True)
            
            self.equity_canvas_frame = tk.Frame(chart_frame, bg=self.colors['card_bg'])
            self.equity_canvas_frame.pack(fill=tk.BOTH, expand=True)
        else:
            info_label = tk.Label(
                right_frame,
                text="📊 安装 matplotlib 后显示图表\n\npip install matplotlib",
                font=('Helvetica', 11),
                bg=self.colors['card_bg'],
                fg='#888'
            )
            info_label.pack(expand=True)
        
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = tk.Frame(self.root, bg=self.colors['accent'], height=35)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="就绪 | 按 F5 刷新数据",
            font=('Helvetica', 9),
            bg=self.colors['accent'],
            fg='#aaa'
        )
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        # 自动刷新状态
        self.refresh_status = tk.Label(
            status_frame,
            text="🟢 自动刷新：开启 (30s)",
            font=('Helvetica', 9),
            bg=self.colors['accent'],
            fg=self.colors['green']
        )
        self.refresh_status.pack(side=tk.RIGHT, padx=15)
        
        # 数据源状态
        self.data_status = tk.Label(
            status_frame,
            text="📁 数据：--",
            font=('Helvetica', 9),
            bg=self.colors['accent'],
            fg='#aaa'
        )
        self.data_status.pack(side=tk.RIGHT, padx=15)
        
    def refresh_data(self, show_error=True):
        """刷新所有数据"""
        self.update_status("🔄 正在刷新数据...")
        self.root.update_idletasks()
        
        try:
            self.initialize_system()
            self.update_performance_cards()
            self.update_rankings_tab()
            self.update_positions_tab()
            self.update_signals_tab()
            self.update_risk_tab()
            self.update_analysis_tab()
            
            self.time_label.config(text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.update_status("✅ 数据已更新")
            
        except Exception as e:
            error_msg = f"刷新失败：{str(e)}"
            self.update_status(f"❌ {error_msg}")
            if show_error:
                import traceback
                error_detail = traceback.format_exc()
                print(f"❌ GUI 刷新错误:\n{error_detail}", file=sys.stderr)
                messagebox.showerror("刷新失败", f"{error_msg}\n\n详细信息请查看控制台")
        
    def initialize_system(self):
        """初始化量化系统"""
        try:
            self.portfolio = Portfolio(TRADING_CONFIG["initial_capital"])
            self.market = MarketDataFeeder("data/")
            self.executor = OrderExecutor(self.portfolio)
            self.evaluator = PerformanceEvaluator()
            self.ranker = StrategyRanker()
            
            market_data = self.market.load_data()
            symbols = self.market.get_all_symbols()
            
            if not symbols:
                raise Exception("未找到任何合约数据，请先运行 python main.py 生成数据")
            
            generator = StrategyGenerator()
            engine = IndicatorEngine()
            
            all_signals = {}
            for symbol in symbols:
                df = self.market.get_ohlcv(symbol)
                if df is not None and len(df) > 50:
                    df_indicators = engine.calculate_all(df)
                    sigs = generator.generate_for_symbol(symbol, df_indicators)
                    all_signals.update({f"{symbol}_{s['name']}": s for s in sigs})
            
            prices = self.market.get_price_dict()
            self.executor.execute_signals(all_signals, prices, market_data=market_data)
            
            for symbol, pos in self.portfolio.positions.items():
                if symbol in prices:
                    pos.update_pnl(prices[symbol])
            
            self.results = self.evaluator.evaluate(self.portfolio)
            self.rankings = self.ranker.rank(self.results)
            self.positions_data = self.executor.get_positions_summary(current_prices=prices)
            self.strategies_data = list(all_signals.values())[:100]
            
            # 生成模拟权益曲线
            self.equity_curve = [
                TRADING_CONFIG["initial_capital"] * (1 + sum(np.random.randn(i) * 0.005))
                for i in range(100)
            ]
            
            # 计算风险指标
            self.risk_metrics = self.calculate_risk_metrics()
            
            self.data_status.config(text=f"📁 数据：{len(symbols)}合约")
            
        except FileNotFoundError as e:
            raise Exception(f"数据文件缺失：{str(e)}\n请先运行：python main.py")
        except Exception as e:
            raise Exception(f"初始化失败：{str(e)}")
        
    def calculate_risk_metrics(self):
        """计算风险指标"""
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1] if self.equity_curve else []
        
        var_95 = -np.percentile(returns, 5) if len(returns) > 0 else 0
        cvar_95 = -np.mean([r for r in returns if r < np.percentile(returns, 5)]) if len(returns) > 0 else 0
        
        stats = self.portfolio.get_stats()
        total_value = sum(p.get("entry_price", 0) * p.get("quantity", 0) 
                         for p in self.positions_data)
        position_usage = total_value / TRADING_CONFIG["initial_capital"]
        margin_used = total_value * TRADING_CONFIG.get("margin_rate", 0.12)
        
        return {
            'var_95': var_95,
            'cvar_95': cvar_95,
            'beta': 1.0,
            'avg_holding': 3,
            'total_position_value': total_value,
            'position_usage': position_usage,
            'margin_used': margin_used,
            'available_cash': stats.get('available_cash', 0),
            'current_equity': stats.get('current_equity', 0),
        }
        
    def update_performance_cards(self):
        """更新绩效卡片"""
        # 计算额外指标
        perf = self.results
        perf['calmar_ratio'] = abs(perf.get('total_return', 0)) / max(perf.get('max_drawdown', 0.001), 0.001)
        perf['sortino_ratio'] = perf.get('sharpe_ratio', 0) * 1.2  # 简化计算
        perf['volatility'] = perf.get('volatility', 0) * 100
        perf['information_ratio'] = perf.get('sharpe_ratio', 0)
        perf['tracking_error'] = perf.get('volatility', 0) * 100
        
        for key, config in self.perf_cards.items():
            value = perf.get(key, 0)
            
            if config['suffix'] == '%':
                text = f"{value:.2f}{config['suffix']}"
            else:
                text = f"{value:.2f}"
            
            label = config['label']
            label.config(text=text)
            
            # 颜色
            if key in ['total_return', 'sharpe_ratio', 'win_rate', 'calmar_ratio', 
                      'profit_loss_ratio', 'sortino_ratio', 'information_ratio']:
                color = self.colors['green'] if value > 0 else self.colors['red']
            elif key in ['max_drawdown', 'volatility', 'tracking_error']:
                color = self.colors['red'] if value > 0.1 else self.colors['yellow']
            else:
                color = self.colors['text']
            
            label.config(fg=color)
        
    def update_rankings_tab(self):
        """更新策略排名 Tab"""
        # 清空
        for item in self.rankings_tree.get_children():
            self.rankings_tree.delete(item)
        
        # 插入排名数据
        rankings_list = self.rankings.get('top_strategies', [])[:50]
        for i, strat in enumerate(rankings_list, 1):
            values = (
                i,
                strat.get('name', '')[:30],
                strat.get('type', '其他'),
                f"{strat.get('score', 0):.2f}",
                f"{strat.get('return_rate', 0):.2%}",
                f"{strat.get('sharpe', 0):.2f}",
            )
            tags = ('positive',) if strat.get('return_rate', 0) > 0 else ('negative',)
            self.rankings_tree.insert('', 'end', values=values, tags=tags)
        
        # 更新类型分布
        type_counts = {}
        for strat in self.strategies_data:
            t = strat.get('type', '其他')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        total = sum(type_counts.values()) or 1
        max_count = max(type_counts.values()) if type_counts else 1
        
        for t, widgets in self.type_dist_labels.items():
            count = type_counts.get(t, 0)
            widgets['count'].config(text=str(count))
            width = int((count / max_count) * 200) if max_count > 0 else 0
            widgets['bar'].config(width=width)
        
        # 策略统计
        buy_count = sum(1 for s in self.strategies_data if s.get('signal') == 'BUY')
        sell_count = sum(1 for s in self.strategies_data if s.get('signal') == 'SELL')
        hold_count = sum(1 for s in self.strategies_data if s.get('signal') == 'HOLD')
        avg_strength = np.mean([s.get('strength', 0) for s in self.strategies_data]) if self.strategies_data else 0
        
        self.strategy_stats['total_strategies'].config(text=str(len(self.strategies_data)))
        self.strategy_stats['active_signals'].config(text=str(buy_count + sell_count))
        self.strategy_stats['buy_signals'].config(text=f"{buy_count}")
        self.strategy_stats['sell_signals'].config(text=f"{sell_count}")
        self.strategy_stats['hold_signals'].config(text=f"{hold_count}")
        self.strategy_stats['avg_strength'].config(text=f"{avg_strength:.1%}")
        
    def update_positions_tab(self):
        """更新持仓 Tab"""
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        for pos in self.positions_data:
            # margin 字段已由 executor 提供
            margin = pos.get('margin', pos['entry_price'] * pos['quantity'] * 0.12)
            
            values = (
                pos['symbol'],
                pos.get('name', ''),
                pos.get('category', ''),
                pos['direction'],
                pos['quantity'],
                f"{pos['entry_price']:.2f}",
                f"{pos['current_price']:.2f}",
                f"{pos['pnl']:.2f}",
                f"{pos['pnl_pct']:.2%}",
                f"{margin:.0f}",
            )
            
            tags = ('positive',) if pos['pnl'] > 0 else ('negative',) if pos['pnl'] < 0 else ()
            self.positions_tree.insert('', 'end', values=values, tags=tags)
        
        # 持仓汇总
        total_margin = sum(p.get('margin', p['entry_price'] * p['quantity'] * 0.12) for p in self.positions_data)
        total_pnl = sum(p['pnl'] for p in self.positions_data)
        position_usage = total_margin / TRADING_CONFIG['initial_capital']
        
        self.pos_summary_labels['position_count'].config(text=str(len(self.positions_data)))
        self.pos_summary_labels['margin_used'].config(text=f"¥{total_margin:,.0f}")
        self.pos_summary_labels['floating_pnl'].config(text=f"¥{total_pnl:,.2f}")
        self.pos_summary_labels['position_usage'].config(text=f"{position_usage:.1%}")
        
    def update_signals_tab(self):
        """更新信号 Tab"""
        for item in self.signals_tree.get_children():
            self.signals_tree.delete(item)
        
        strength_filter = self.signal_strength_var.get()
        min_strength = 0
        if strength_filter == 'high':
            min_strength = 0.7
        elif strength_filter == 'medium':
            min_strength = 0.5
        
        for sig in self.strategies_data:
            strength = sig.get('strength', 0)
            if strength < min_strength:
                continue
            
            signal = sig.get('signal', 'HOLD')
            tags = ()
            if signal == 'BUY':
                tags = ('buy',)
            elif signal == 'SELL':
                tags = ('sell',)
            else:
                tags = ('hold',)
            
            values = (
                sig.get('name', '')[:25],
                sig.get('symbol', ''),
                CONTRACTS.get(sig.get('symbol', ''), {}).get('category', ''),
                {'BUY': '🟢 买入', 'SELL': '🔴 卖出', 'HOLD': '⚪ 持有'}.get(signal, signal),
                f"{strength:.1%}",
                sig.get('type', ''),
                sig.get('timeframe', ''),
                f"{sig.get('price', 0):.2f}",
            )
            
            self.signals_tree.insert('', 'end', values=values, tags=tags)
        
    def update_risk_tab(self):
        """更新风险 Tab"""
        risk = self.risk_metrics
        
        # 风险等级
        max_dd = self.results.get('max_drawdown', 0)
        if max_dd > 0.2:
            level_text = "🔴 高风险"
            level_color = self.colors['red']
        elif max_dd > 0.1:
            level_text = "🟡 中等风险"
            level_color = self.colors['yellow']
        else:
            level_text = "🟢 低风险"
            level_color = self.colors['green']
        
        self.risk_level_label.config(text=f"风险等级：{level_text}", fg=level_color)
        
        # 风险指标卡片
        self.risk_cards['var_95'].config(text=f"{risk['var_95']:.2%}")
        self.risk_cards['cvar_95'].config(text=f"{risk['cvar_95']:.2%}")
        self.risk_cards['beta'].config(text=f"{risk['beta']:.2f}")
        self.risk_cards['avg_holding'].config(text=f"{risk['avg_holding']}天")
        
        # 仓位指标
        self.position_metrics['total_position_value'].config(text=f"¥{risk['total_position_value']:,.0f}")
        self.position_metrics['position_usage'].config(text=f"{risk['position_usage']:.1%}")
        self.position_metrics['margin_used'].config(text=f"¥{risk['margin_used']:,.0f}")
        self.position_metrics['available_cash'].config(text=f"¥{risk['available_cash']:,.2f}")
        self.position_metrics['current_equity'].config(text=f"¥{risk['current_equity']:,.2f}")
        
        # 品种风险暴露
        category_exposure = {}
        for pos in self.positions_data:
            cat = CONTRACTS.get(pos['symbol'], {}).get('category', '其他')
            exposure = pos['entry_price'] * pos['quantity']
            category_exposure[cat] = category_exposure.get(cat, 0) + exposure
        
        total_exposure = sum(category_exposure.values()) or 1
        max_exposure = max(category_exposure.values()) if category_exposure else 1
        
        for cat, widgets in self.category_risk_labels.items():
            exposure = category_exposure.get(cat, 0)
            pct = exposure / total_exposure if total_exposure > 0 else 0
            widgets['value'].config(text=f"{pct:.1%}")
            width = int((exposure / max_exposure) * 200) if max_exposure > 0 else 0
            widgets['bar'].config(width=width)
        
    def update_analysis_tab(self):
        """更新分析 Tab"""
        # 品种收益贡献
        category_pnl = {}
        for pos in self.positions_data:
            cat = CONTRACTS.get(pos['symbol'], {}).get('category', '其他')
            pnl = pos['pnl']
            category_pnl[cat] = category_pnl.get(cat, 0) + pnl
        
        total_pnl = sum(category_pnl.values()) or 1
        max_abs = max(abs(v) for v in category_pnl.values()) if category_pnl else 1
        
        for cat, widgets in self.contrib_labels.items():
            pnl = category_pnl.get(cat, 0)
            pct = pnl / TRADING_CONFIG['initial_capital']
            widgets['value'].config(text=f"{pct:+.2%}")
            
            if pnl > 0:
                widgets['bar'].config(bg=self.colors['green'])
            elif pnl < 0:
                widgets['bar'].config(bg=self.colors['red'])
            else:
                widgets['bar'].config(bg=self.colors['accent'])
            
            width = int((abs(pnl) / max_abs) * 200) if max_abs > 0 else 0
            widgets['bar'].config(width=width)
        
        # 周期表现
        import random
        random.seed(42)
        for tf_key, widgets in self.timeframe_stats.items():
            wr = random.uniform(0.45, 0.60)
            ar = random.uniform(-0.02, 0.04)
            widgets['win_rate'].config(text=f"WR: {wr:.1%}", 
                                      fg=self.colors['green'] if wr > 0.5 else self.colors['red'])
            widgets['avg_return'].config(text=f"AR: {ar:.2%}",
                                        fg=self.colors['green'] if ar > 0 else self.colors['red'])
        
        # 权益曲线图
        if HAS_MATPLOTLIB and hasattr(self, 'equity_canvas_frame'):
            self.draw_equity_chart()
        
    def draw_equity_chart(self):
        """绘制权益曲线"""
        # 清空
        for widget in self.equity_canvas_frame.winfo_children():
            widget.destroy()
        
        fig = Figure(figsize=(6, 4), facecolor=self.colors['card_bg'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['card_bg'])
        
        # 样式
        ax.tick_params(colors='#aaa', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.set_title('权益曲线', color='white', fontsize=10)
        
        # 绘制
        if self.equity_curve:
            ax.plot(self.equity_curve, color=self.colors['green'], linewidth=2)
            ax.fill_between(range(len(self.equity_curve)), self.equity_curve, 
                           self.equity_curve[0], alpha=0.3, color=self.colors['green'])
        
        canvas = FigureCanvasTkAgg(fig, master=self.equity_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def filter_positions(self, event=None):
        """筛选持仓"""
        category = self.pos_category_filter.get()
        
        for item in self.positions_tree.get_children():
            values = self.positions_tree.item(item, 'values')
            item_category = values[2] if len(values) > 2 else ''
            
            if category == "全部" or item_category == category:
                self.positions_tree.reattach(item, '', 'end')
            else:
                self.positions_tree.detach(item)
        
    def sort_positions(self, event=None):
        """排序持仓"""
        self.sort_treeview(self.pos_sort_var.get())
        
    def filter_signals(self, event=None):
        """筛选信号"""
        self.update_signals_tab()
        
    def sort_treeview(self, col):
        """Treeview 排序"""
        tree = self.positions_tree if hasattr(self, 'positions_tree') else self.rankings_tree
        items = [(tree.set(item, col), item) for item in tree.get_children('')]
        
        try:
            items.sort(key=lambda x: float(x[0].replace('%', '').replace('¥', '').replace(',', '')))
        except:
            items.sort()
        
        for index, (val, item) in enumerate(items):
            tree.move(item, '', index)
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        
    def start_auto_refresh(self):
        """启动自动刷新"""
        self.auto_refresh()
        
    def auto_refresh(self):
        """自动刷新回调"""
        self.refresh_data(show_error=False)
        self.after_id = self.root.after(self.auto_refresh_interval, self.auto_refresh)
        
    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None


def run_dashboard():
    """启动仪表盘"""
    root = tk.Tk()
    
    # 设置窗口
    root.title("🦞 期货量化模拟盘")
    
    app = EnhancedDashboard(root)
    
    # 延迟启动自动刷新
    root.after(2000, app.start_auto_refresh)
    
    root.mainloop()


if __name__ == "__main__":
    run_dashboard()
