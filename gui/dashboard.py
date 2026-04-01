"""
=============================================================================
期货量化模拟盘 - 桌面仪表盘
=============================================================================
功能：
  - 实时展示持仓、绩效、策略信号
  - 多维度统计分析图表
  - 可交互的筛选和排序功能
  - 自动刷新数据

作者：OpenClaw 🦞
日期：2026-03-28
=============================================================================
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import warnings
from datetime import datetime
from typing import Dict, List, Any

# 抑制 pandas 性能警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*fragmented.*')
warnings.filterwarnings('ignore', message='.*PerformanceWarning.*')

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONTRACTS, TRADING_CONFIG, TIMEFRAMES
from market.feeder import MarketDataFeeder
from strategy.signals import StrategyGenerator
from strategy.indicators import IndicatorEngine
from trading.executor import OrderExecutor
from trading.portfolio import Portfolio
from analysis.evaluator import PerformanceEvaluator
from analysis.ranker import StrategyRanker


class FuturesDashboard:
    """期货量化仪表盘主窗口"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🦞 期货量化模拟盘 - 桌面仪表盘")
        self.root.geometry("1600x1000")
        
        # 初始化数据
        self.portfolio = None
        self.market = None
        self.executor = None
        self.evaluator = None
        self.ranker = None
        self.results = {}
        self.rankings = {}
        self.positions_data = []
        self.strategies_data = []
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_menu()
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # 绑定刷新事件
        self.root.bind("<F5>", lambda e: self.refresh_data())
        
        # 自动刷新定时器（每 30 秒）
        self.auto_refresh_interval = 30000  # 毫秒
        self.after_id = None
        
    def setup_styles(self):
        """设置 GUI 样式"""
        style = ttk.Style()
        
        # 尝试使用现代主题
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 定义颜色
        colors = {
            'bg': '#1a1a2e',
            'card_bg': '#16213e',
            'text': '#eaeaea',
            'accent': '#0f3460',
            'green': '#00ff88',
            'red': '#ff4757',
            'yellow': '#ffa502',
            'blue': '#3498db',
        }
        
        # 配置样式
        style.configure('Title.TLabel', 
                       font=('Helvetica', 16, 'bold'),
                       background=colors['bg'],
                       foreground=colors['text'])
        
        style.configure('Card.TFrame',
                       background=colors['card_bg'])
        
        style.configure('Positive.TLabel',
                       foreground=colors['green'])
        
        style.configure('Negative.TLabel',
                       foreground=colors['red'])
        
        style.configure('Header.TLabel',
                       font=('Helvetica', 14, 'bold'),
                       background=colors['accent'],
                       foreground=colors['text'])
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="刷新数据 (F5)", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="导出报告", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="刷新", command=self.refresh_data)
        view_menu.add_command(label="全屏", command=self.toggle_fullscreen)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_header(self):
        """创建顶部标题栏"""
        header_frame = tk.Frame(self.root, bg='#0f3460', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(
            header_frame,
            text="🦞 期货量化模拟盘系统",
            font=('Helvetica', 20, 'bold'),
            bg='#0f3460',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 时间显示
        self.time_label = tk.Label(
            header_frame,
            text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            font=('Helvetica', 12),
            bg='#0f3460',
            fg='#aaa'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 刷新",
            command=self.refresh_data,
            bg='#00ff88',
            fg='#000',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
    def create_main_content(self):
        """创建主内容区域"""
        # 主容器
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 使用 PanedWindow 实现可调整大小的分区
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板（70%）
        left_frame = tk.Frame(paned, bg='#16213e')
        paned.add(left_frame, weight=70)
        
        # 右侧面板（30%）
        right_frame = tk.Frame(paned, bg='#16213e')
        paned.add(right_frame, weight=30)
        
        # ========== 左侧面板 ==========
        self.create_performance_cards(left_frame)
        self.create_positions_table(left_frame)
        
        # ========== 右侧面板 ==========
        self.create_strategy_list(right_frame)
        self.create_statistics_panel(right_frame)
        
    def create_performance_cards(self, parent):
        """创建绩效卡片"""
        # 卡片容器
        card_frame = tk.LabelFrame(
            parent,
            text="📊 绩效概览",
            font=('Helvetica', 12, 'bold'),
            bg='#16213e',
            fg='white',
            padx=10,
            pady=10
        )
        card_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 创建 4 个绩效卡片
        cards_frame = tk.Frame(card_frame, bg='#16213e')
        cards_frame.pack(fill=tk.X)
        
        # 卡片配置
        self.performance_cards = {}
        card_configs = [
            ('总收益率', 'total_return', '%', True),
            ('夏普比率', 'sharpe_ratio', '', False),
            ('最大回撤', 'max_drawdown', '%', False),
            ('胜率', 'win_rate', '%', True),
        ]
        
        for i, (title, key, suffix, is_percent) in enumerate(card_configs):
            card = tk.Frame(cards_frame, bg='#0f3460', relief=tk.RAISED, bd=2)
            card.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
            
            # 标题
            tk.Label(
                card,
                text=title,
                font=('Helvetica', 10),
                bg='#0f3460',
                fg='#aaa'
            ).pack(pady=(10, 5))
            
            # 数值
            value_label = tk.Label(
                card,
                text="--",
                font=('Helvetica', 18, 'bold'),
                bg='#0f3460',
                fg='white'
            )
            value_label.pack(pady=5)
            
            self.performance_cards[key] = {
                'label': value_label,
                'suffix': suffix,
                'is_percent': is_percent
            }
        
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
    def create_positions_table(self, parent):
        """创建持仓表格"""
        # 表格容器
        table_frame = tk.LabelFrame(
            parent,
            text="📋 持仓明细",
            font=('Helvetica', 12, 'bold'),
            bg='#16213e',
            fg='white',
            padx=10,
            pady=10
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 筛选框
        filter_frame = tk.Frame(table_frame, bg='#16213e')
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(filter_frame, text="筛选:", bg='#16213e', fg='white').pack(side=tk.LEFT)
        
        # 品种筛选
        self.category_filter = ttk.Combobox(
            filter_frame,
            values=["全部"] + list(set(c.get("category", "其他") for c in CONTRACTS.values())),
            state="readonly",
            width=12
        )
        self.category_filter.set("全部")
        self.category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter.bind("<<ComboboxSelected>>", self.filter_positions)
        
        # 排序选项
        tk.Label(filter_frame, text="排序:", bg='#16213e', fg='white').pack(side=tk.LEFT, padx=(10, 0))
        
        self.sort_var = tk.StringVar(value="pnl")
        sort_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=[
                ("pnl", "盈亏"),
                ("pnl_pct", "盈亏%"),
                ("symbol", "合约"),
                ("quantity", "数量"),
            ],
            state="readonly",
            width=10
        )
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", self.sort_positions)
        
        # 创建 Treeview
        columns = ("symbol", "name", "direction", "quantity", "entry_price", 
                   "current_price", "pnl", "pnl_pct", "category")
        
        self.positions_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # 设置列标题
        headers = {
            "symbol": "合约",
            "name": "名称",
            "direction": "方向",
            "quantity": "数量",
            "entry_price": "开仓价",
            "current_price": "现价",
            "pnl": "盈亏",
            "pnl_pct": "盈亏%",
            "category": "分类",
        }
        
        for col in columns:
            self.positions_tree.heading(col, text=headers[col], 
                                       command=lambda c=col: self.sort_treeview(c))
            self.positions_tree.column(col, width=80 if col not in ['name', 'symbol'] else 100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                 command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_strategy_list(self, parent):
        """创建策略列表"""
        # 策略容器
        strategy_frame = tk.LabelFrame(
            parent,
            text="🎯 活跃策略",
            font=('Helvetica', 12, 'bold'),
            bg='#16213e',
            fg='white',
            padx=10,
            pady=10
        )
        strategy_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建 Treeview
        columns = ("name", "signal", "strength", "category")
        
        self.strategy_tree = ttk.Treeview(
            strategy_frame,
            columns=columns,
            show="headings",
            height=12
        )
        
        # 设置列
        self.strategy_tree.heading("name", text="策略")
        self.strategy_tree.heading("signal", text="信号")
        self.strategy_tree.heading("strength", text="强度")
        self.strategy_tree.heading("category", text="分类")
        
        self.strategy_tree.column("name", width=120)
        self.strategy_tree.column("signal", width=60)
        self.strategy_tree.column("strength", width=60)
        self.strategy_tree.column("category", width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(strategy_frame, orient=tk.VERTICAL,
                                 command=self.strategy_tree.yview)
        self.strategy_tree.configure(yscrollcommand=scrollbar.set)
        
        self.strategy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_statistics_panel(self, parent):
        """创建统计面板"""
        # 统计容器
        stats_frame = tk.LabelFrame(
            parent,
            text="📈 统计分析",
            font=('Helvetica', 12, 'bold'),
            bg='#16213e',
            fg='white',
            padx=10,
            pady=10
        )
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 统计项
        self.stats_labels = {}
        stats_items = [
            ("总交易次数", "total_trades"),
            ("已实现盈亏", "closed_pnl"),
            ("当前权益", "current_equity"),
            ("持仓数量", "open_positions"),
            ("可用资金", "available_cash"),
            ("保证金占用", "margin_used"),
        ]
        
        for i, (label, key) in enumerate(stats_items):
            row_frame = tk.Frame(stats_frame, bg='#16213e')
            row_frame.pack(fill=tk.X, pady=3)
            
            tk.Label(
                row_frame,
                text=label + ":",
                font=('Helvetica', 10),
                bg='#16213e',
                fg='#aaa',
                width=12,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row_frame,
                text="--",
                font=('Helvetica', 10, 'bold'),
                bg='#16213e',
                fg='white',
                anchor='w'
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.stats_labels[key] = value_label
        
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = tk.Frame(self.root, bg='#0f3460', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="就绪",
            font=('Helvetica', 9),
            bg='#0f3460',
            fg='#aaa'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 自动刷新状态
        self.refresh_status = tk.Label(
            status_frame,
            text="自动刷新：开启",
            font=('Helvetica', 9),
            bg='#0f3460',
            fg='#00ff88'
        )
        self.refresh_status.pack(side=tk.RIGHT, padx=10)
        
    def refresh_data(self, show_error=True):
        """刷新所有数据"""
        self.update_status("正在刷新数据...")
        self.root.update_idletasks()  # 立即更新状态显示
        
        try:
            # 重新初始化系统
            self.initialize_system()
            
            # 更新绩效卡片
            self.update_performance_cards()
            
            # 更新持仓表格
            self.update_positions_table()
            
            # 更新策略列表
            self.update_strategy_list()
            
            # 更新统计面板
            self.update_statistics()
            
            # 更新时间
            self.time_label.config(text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            self.update_status("数据已更新")
            
        except Exception as e:
            error_msg = f"刷新失败：{str(e)}"
            self.update_status(error_msg)
            if show_error:
                import traceback
                error_detail = traceback.format_exc()
                print(f"❌ GUI 刷新错误:\n{error_detail}", file=sys.stderr)
                messagebox.showerror("刷新失败", f"{error_msg}\n\n详细信息请查看控制台")
        
    def initialize_system(self):
        """初始化量化系统"""
        try:
            # 初始化组件
            self.portfolio = Portfolio(TRADING_CONFIG["initial_capital"])
            self.market = MarketDataFeeder("data/")
            self.executor = OrderExecutor(self.portfolio)
            self.evaluator = PerformanceEvaluator()
            self.ranker = StrategyRanker()
            
            # 加载数据
            market_data = self.market.load_data()
            symbols = self.market.get_all_symbols()
            
            if not symbols:
                raise Exception("未找到任何合约数据，请先运行 python main.py 生成数据")
            
            # 生成策略
            generator = StrategyGenerator()
            engine = IndicatorEngine()
            
            all_signals = {}
            for symbol in symbols:
                df = self.market.get_ohlcv(symbol)
                if df is not None and len(df) > 50:
                    df_indicators = engine.calculate_all(df)
                    sigs = generator.generate_for_symbol(symbol, df_indicators)
                    all_signals.update({f"{s['name']}": s for s in sigs})
            
            # 执行交易
            prices = self.market.get_price_dict()
            self.executor.execute_signals(all_signals, prices, market_data=market_data)
            
            # 更新盈亏
            for symbol, pos in self.portfolio.positions.items():
                if symbol in prices:
                    pos.update_pnl(prices[symbol])
            
            # 评估绩效
            self.results = self.evaluator.evaluate(self.portfolio)
            self.rankings = self.ranker.rank(self.results)
            
            # 准备持仓数据 (传入当前价格)
            self.positions_data = self.executor.get_positions_summary(current_prices=prices)
            
            # 准备策略数据
            self.strategies_data = list(all_signals.values())[:50]  # 只显示前 50 个
            
        except FileNotFoundError as e:
            raise Exception(f"数据文件缺失：{str(e)}\n请先运行：python main.py")
        except Exception as e:
            raise Exception(f"初始化失败：{str(e)}")
        
    def update_performance_cards(self):
        """更新绩效卡片"""
        for key, config in self.performance_cards.items():
            value = self.results.get(key, 0)
            
            if config['is_percent']:
                text = f"{value:.2f}{config['suffix']}"
            else:
                text = f"{value:.2f}{config['suffix']}"
            
            label = config['label']
            label.config(text=text)
            
            # 根据正负设置颜色
            if key in ['total_return', 'sharpe_ratio', 'win_rate']:
                color = '#00ff88' if value > 0 else '#ff4757'
            elif key == 'max_drawdown':
                color = '#ff4757' if value > 0.1 else '#ffa502'
            else:
                color = 'white'
            
            label.config(fg=color)
        
    def update_positions_table(self):
        """更新持仓表格"""
        # 清空现有数据
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        # 插入新数据
        for pos in self.positions_data:
            contract = CONTRACTS.get(pos['symbol'], {})
            values = (
                pos['symbol'],
                contract.get('name', ''),
                pos['direction'],
                pos['quantity'],
                f"{pos['entry_price']:.2f}",
                f"{pos['current_price']:.2f}",
                f"{pos['pnl']:.2f}",
                f"{pos['pnl_pct']:.2%}",
                contract.get('category', '')
            )
            
            # 根据盈亏设置颜色标签
            tags = ()
            if pos['pnl'] > 0:
                tags = ('positive',)
            elif pos['pnl'] < 0:
                tags = ('negative',)
            
            self.positions_tree.insert('', 'end', values=values, tags=tags)
        
        # 配置颜色标签
        self.positions_tree.tag_configure('positive', foreground='#00ff88')
        self.positions_tree.tag_configure('negative', foreground='#ff4757')
        
    def update_strategy_list(self):
        """更新策略列表"""
        # 清空
        for item in self.strategy_tree.get_children():
            self.strategy_tree.delete(item)
        
        # 插入数据
        for strategy in self.strategies_data:
            signal = strategy.get('signal', 'HOLD')
            strength = strategy.get('strength', 0)
            
            # 信号图标
            signal_icon = {
                'BUY': '🟢',
                'SELL': '🔴',
                'HOLD': '⚪'
            }.get(signal, '⚪')
            
            values = (
                strategy.get('name', ''),
                signal_icon,
                f"{strength:.2f}",
                strategy.get('category', '')
            )
            
            self.strategy_tree.insert('', 'end', values=values)
        
    def update_statistics(self):
        """更新统计面板"""
        stats = self.portfolio.get_stats()
        
        # 映射键名
        key_mapping = {
            'total_trades': 'total_trades',
            'closed_pnl': 'closed_pnl',
            'current_equity': 'current_equity',
            'open_positions': 'open_positions',
            'available_cash': 'available_cash',
            'margin_used': 'margin_used',
        }
        
        for stat_key, label_key in key_mapping.items():
            if label_key in self.stats_labels:
                value = stats.get(stat_key, 0)
                
                if stat_key in ['closed_pnl', 'current_equity', 'available_cash', 'margin_used']:
                    text = f"¥{value:,.2f}"
                else:
                    text = str(value)
                
                self.stats_labels[label_key].config(text=text)
        
    def filter_positions(self, event=None):
        """筛选持仓"""
        category = self.category_filter.get()
        
        for item in self.positions_tree.get_children():
            values = self.positions_tree.item(item, 'values')
            item_category = values[8] if len(values) > 8 else ''
            
            if category == "全部" or item_category == category:
                self.positions_tree.reattach(item, '', 'end')
            else:
                self.positions_tree.detach(item)
        
    def sort_positions(self, event=None):
        """排序持仓"""
        self.sort_treeview(self.sort_var.get())
        
    def sort_treeview(self, col):
        """Treeview 排序"""
        items = [(self.positions_tree.set(item, col), item) 
                 for item in self.positions_tree.get_children('')]
        
        # 尝试数字排序
        try:
            items.sort(key=lambda x: float(x[0].replace('%', '').replace('¥', '').replace(',', '')))
        except:
            items.sort()
        
        for index, (val, item) in enumerate(items):
            self.positions_tree.move(item, '', index)
        
    def toggle_fullscreen(self):
        """切换全屏"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
        
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "🦞 期货量化模拟盘系统\n\n"
            "版本：2.0\n"
            "作者：OpenClaw\n"
            "日期：2026-03-28\n\n"
            "功能：\n"
            "- 53 个期货合约\n"
            "- 232 个交易策略\n"
            "- 实时绩效监控\n"
            "- 多维度统计分析"
        )
        
    def export_report(self):
        """导出报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/dashboard_report_{timestamp}.txt"
        
        try:
            os.makedirs("reports", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("🦞 期货量化模拟盘 - 仪表盘报告\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("【绩效评估】\n")
                for key, value in self.results.items():
                    f.write(f"  {key}: {value:.4f}\n")
                
                f.write("\n【持仓明细】\n")
                for pos in self.positions_data:
                    f.write(f"  {pos['symbol']}: {pos['direction']} x{pos['quantity']} "
                           f"盈亏：{pos['pnl']:.2f}\n")
            
            messagebox.showinfo("成功", f"报告已导出:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败:\n{str(e)}")
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        
    def start_auto_refresh(self):
        """启动自动刷新"""
        self.auto_refresh()
        
    def auto_refresh(self):
        """自动刷新回调"""
        self.refresh_data()
        self.after_id = self.root.after(self.auto_refresh_interval, self.auto_refresh)
        
    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None


def run_dashboard():
    """启动仪表盘"""
    root = tk.Tk()
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = FuturesDashboard(root)
    
    # 延迟启动自动刷新
    root.after(1000, app.start_auto_refresh)
    
    root.mainloop()


if __name__ == "__main__":
    run_dashboard()
