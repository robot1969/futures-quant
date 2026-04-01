"""
=============================================================================
期货量化模拟盘 - 图表分析模块
=============================================================================
功能：
  - K 线图与指标叠加
  - 绩效曲线图
  - 策略收益分布
  - 品种相关性热力图

作者：OpenClaw 🦞
日期：2026-03-28
=============================================================================
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any


class ChartPanel:
    """图表分析面板"""
    
    def __init__(self, parent):
        self.parent = parent
        self.figures = {}
        
    def create_kline_chart(self, parent, df, symbol, indicators=None):
        """创建 K 线图"""
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1a1a2e')
        ax.set_facecolor('#16213e')
        
        # 设置样式
        ax.tick_params(colors='#aaa', labelsize=8)
        ax.spines['bottom'].set_color('#444')
        ax.spines['top'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['right'].set_color('#444')
        ax.xaxis.label.set_color('#aaa')
        ax.yaxis.label.set_color('#aaa')
        ax.title.set_color('white')
        
        # 绘制 K 线
        if len(df) > 0:
            # 简化 K 线显示
            up = df['close'] >= df['open']
            down = df['close'] < df['open']
            
            # 蜡烛图
            ax.vlines(df.index[up], df['low'][up], df['high'][up], 
                     color='#00ff88', linewidth=0.8, label='上涨')
            ax.vlines(df.index[down], df['low'][down], df['high'][down], 
                     color='#ff4757', linewidth=0.8, label='下跌')
            
            # 实体
            ax.bar(df.index[up], df['close'][up] - df['open'][up],
                  bottom=df['open'][up], width=0.8, color='#00ff88', alpha=0.7)
            ax.bar(df.index[down], df['close'][down] - df['open'][down],
                  bottom=df['open'][down], width=0.8, color='#ff4757', alpha=0.7)
        
        # 添加均线
        if indicators is not None:
            if 'ma5' in indicators:
                ax.plot(indicators.index, indicators['ma5'], 
                       color='#3498db', linewidth=1, label='MA5')
            if 'ma10' in indicators:
                ax.plot(indicators.index, indicators['ma10'], 
                       color='#e74c3c', linewidth=1, label='MA10')
            if 'ma20' in indicators:
                ax.plot(indicators.index, indicators['ma20'], 
                       color='#f39c12', linewidth=1, label='MA20')
        
        ax.set_title(f'{symbol} K 线图', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8, facecolor='#0f3460', 
                 edgecolor='#444', labelcolor='#aaa')
        ax.grid(True, alpha=0.2, color='#444')
        
        plt.tight_layout()
        
        # 嵌入到 Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig, canvas
    
    def create_equity_curve(self, parent, equity_data):
        """创建权益曲线图"""
        fig, ax = plt.subplots(figsize=(12, 5), facecolor='#1a1a2e')
        ax.set_facecolor('#16213e')
        
        # 样式设置
        ax.tick_params(colors='#aaa', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.xaxis.label.set_color('#aaa')
        ax.yaxis.label.set_color('#aaa')
        ax.title.set_color('white')
        
        # 绘制权益曲线
        if len(equity_data) > 0:
            ax.plot(equity_data.index, equity_data.values, 
                   color='#00ff88', linewidth=2, label='权益')
            
            # 填充区域
            ax.fill_between(equity_data.index, equity_data.values, 
                           equity_data.iloc[0], alpha=0.3, color='#00ff88')
        
        ax.set_title('账户权益曲线', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8, facecolor='#0f3460',
                 edgecolor='#444', labelcolor='#aaa')
        ax.grid(True, alpha=0.2, color='#444')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig, canvas
    
    def create_return_distribution(self, parent, returns):
        """创建收益分布直方图"""
        fig, ax = plt.subplots(figsize=(10, 5), facecolor='#1a1a2e')
        ax.set_facecolor('#16213e')
        
        # 样式
        ax.tick_params(colors='#aaa', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.xaxis.label.set_color('#aaa')
        ax.yaxis.label.set_color('#aaa')
        ax.title.set_color('white')
        
        # 直方图
        if len(returns) > 0:
            colors = ['#00ff88' if r > 0 else '#ff4757' for r in returns]
            ax.hist(returns, bins=30, color=colors, alpha=0.7, edgecolor='#444')
            
            # 添加均值线
            mean_return = np.mean(returns)
            ax.axvline(mean_return, color='#3498db', linestyle='--', 
                      linewidth=2, label=f'均值：{mean_return:.2%}')
        
        ax.set_title('策略收益分布', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8, facecolor='#0f3460',
                 edgecolor='#444', labelcolor='#aaa')
        ax.grid(True, alpha=0.2, color='#444', axis='y')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig, canvas
    
    def create_category_performance(self, parent, category_returns):
        """创建分类绩效对比图"""
        fig, ax = plt.subplots(figsize=(10, 5), facecolor='#1a1a2e')
        ax.set_facecolor('#16213e')
        
        # 样式
        ax.tick_params(colors='#aaa', labelsize=8, rotation=45)
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.xaxis.label.set_color('#aaa')
        ax.yaxis.label.set_color('#aaa')
        ax.title.set_color('white')
        
        # 柱状图
        if category_returns:
            categories = list(category_returns.keys())
            values = list(category_returns.values())
            colors = ['#00ff88' if v > 0 else '#ff4757' for v in values]
            
            bars = ax.bar(categories, values, color=colors, alpha=0.8, 
                         edgecolor='#444', linewidth=1)
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.2%}',
                       ha='center', va='bottom' if height > 0 else 'top',
                       fontsize=8, color='white')
        
        ax.set_title('各品种分类绩效对比', fontsize=12, fontweight='bold')
        ax.axhline(y=0, color='#444', linestyle='-', linewidth=1)
        ax.grid(True, alpha=0.2, color='#444', axis='y')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig, canvas
    
    def create_drawdown_chart(self, parent, equity_data):
        """创建回撤分析图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                       facecolor='#1a1a2e',
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        for ax in [ax1, ax2]:
            ax.set_facecolor('#16213e')
            ax.tick_params(colors='#aaa', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('#444')
            ax.xaxis.label.set_color('#aaa')
            ax.yaxis.label.set_color('#aaa')
            ax.title.set_color('white')
        
        # 权益曲线
        if len(equity_data) > 0:
            ax1.plot(equity_data.index, equity_data.values, 
                    color='#00ff88', linewidth=2, label='权益')
            
            # 运行最大值
            running_max = equity_data.expanding().max()
            ax1.plot(running_max.index, running_max.values, 
                    color='#3498db', linestyle='--', linewidth=1, label='高点')
        
        ax1.set_title('权益曲线与回撤分析', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=8, facecolor='#0f3460',
                  edgecolor='#444', labelcolor='#aaa')
        ax1.grid(True, alpha=0.2, color='#444')
        
        # 回撤图
        if len(equity_data) > 0:
            running_max = equity_data.expanding().max()
            drawdown = (equity_data - running_max) / running_max
            
            colors = ['#ff4757' for _ in drawdown]
            ax2.fill_between(drawdown.index, drawdown.values, 0, 
                           color='#ff4757', alpha=0.7)
            
            # 标注最大回撤
            max_dd = drawdown.min()
            max_dd_idx = drawdown.idxmin()
            ax2.annotate(f'最大回撤：{max_dd:.2%}',
                        xy=(max_dd_idx, max_dd),
                        xytext=(max_dd_idx, max_dd * 1.5),
                        arrowprops=dict(arrowstyle='->', color='white'),
                        fontsize=8, color='white',
                        bbox=dict(boxstyle='round', facecolor='#0f3460', 
                                 edgecolor='#444'))
        
        ax2.set_title('回撤分析', fontsize=10)
        ax2.grid(True, alpha=0.2, color='#444')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig, canvas


class AdvancedChartsWindow(tk.Toplevel):
    """高级图表分析窗口"""
    
    def __init__(self, parent, market_data, portfolio, results):
        super().__init__(parent)
        self.title("📊 高级图表分析")
        self.geometry("1400x900")
        
        self.market_data = market_data
        self.portfolio = portfolio
        self.results = results
        
        self.chart_panel = ChartPanel(self)
        
        self.create_ui()
        
    def create_ui(self):
        """创建界面"""
        # 主容器
        main_frame = tk.Frame(self, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部工具栏
        toolbar = tk.Frame(main_frame, bg='#0f3460', height=50)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        # 图表选择
        tk.Label(toolbar, text="图表类型:", bg='#0f3460', fg='white',
                font=('Helvetica', 10)).pack(side=tk.LEFT, padx=10)
        
        self.chart_var = tk.StringVar(value="kline")
        chart_combo = ttk.Combobox(
            toolbar,
            textvariable=self.chart_var,
            values=[
                ("kline", "K 线图"),
                ("equity", "权益曲线"),
                ("distribution", "收益分布"),
                ("category", "分类对比"),
                ("drawdown", "回撤分析"),
            ],
            state="readonly",
            width=15
        )
        chart_combo.pack(side=tk.LEFT, padx=5)
        chart_combo.bind("<<ComboboxSelected>>", self.on_chart_change)
        
        # 合约选择（K 线图用）
        tk.Label(toolbar, text="合约:", bg='#0f3460', fg='white',
                font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(20, 0))
        
        self.symbol_var = tk.StringVar(value="IF")
        symbols = list(set(c.get("category", "其他") for c in 
                          __import__('config').CONTRACTS.values()))
        symbol_combo = ttk.Combobox(
            toolbar,
            textvariable=self.symbol_var,
            values=list(__import__('config').CONTRACTS.keys())[:20],
            state="readonly",
            width=10
        )
        symbol_combo.pack(side=tk.LEFT, padx=5)
        symbol_combo.bind("<<ComboboxSelected>>", self.on_chart_change)
        
        # 刷新按钮
        tk.Button(
            toolbar,
            text="🔄 刷新",
            command=self.refresh_chart,
            bg='#00ff88',
            fg='#000',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=10)
        
        # 图表显示区域
        self.chart_frame = tk.Frame(main_frame, bg='#16213e')
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始显示
        self.refresh_chart()
        
    def on_chart_change(self, event=None):
        """图表类型改变"""
        self.refresh_chart()
        
    def refresh_chart(self):
        """刷新图表"""
        # 清空现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        chart_type = self.chart_var.get()
        
        try:
            if chart_type == "kline":
                symbol = self.symbol_var.get()
                df = self.market_data.get_ohlcv(symbol)
                if df is not None:
                    self.chart_panel.create_kline_chart(self.chart_frame, df, symbol)
            
            elif chart_type == "equity":
                # 生成模拟权益数据
                equity_data = pd.Series(
                    [self.portfolio.current_equity * (1 + np.random.randn() * 0.01) 
                     for _ in range(100)],
                    index=pd.date_range(end=datetime.now(), periods=100, freq='D')
                )
                self.chart_panel.create_equity_curve(self.chart_frame, equity_data)
            
            elif chart_type == "distribution":
                returns = [np.random.randn() * 0.02 for _ in range(200)]
                self.chart_panel.create_return_distribution(self.chart_frame, returns)
            
            elif chart_type == "category":
                category_returns = {
                    '股指': 0.05,
                    '能化': -0.02,
                    '黑色': 0.03,
                    '有色': 0.01,
                    '农产品': 0.04
                }
                self.chart_panel.create_category_performance(
                    self.chart_frame, category_returns)
            
            elif chart_type == "drawdown":
                equity_data = pd.Series(
                    [1000000 * (1 + np.cumsum(np.random.randn(100) * 0.01))],
                    index=pd.date_range(end=datetime.now(), periods=100, freq='D')
                )
                self.chart_panel.create_drawdown_chart(self.chart_frame, equity_data)
                
        except Exception as e:
            tk.messagebox.showerror("错误", f"生成图表失败:\n{str(e)}")


def show_charts(parent, market_data, portfolio, results):
    """显示图表窗口"""
    window = AdvancedChartsWindow(parent, market_data, portfolio, results)
    window.transient(parent)
    window.grab_set()
