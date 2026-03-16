"""
=============================================================================
期货量化模拟盘 - 配置文件
=============================================================================
作者：OpenClaw 🦞
版本：2.0
更新日期：2026-03-12
=============================================================================
"""

# =============================================================================
# 期货合约配置 - 全品种覆盖（共53个合约）
# =============================================================================
# 配置字段说明：
#   - name: 合约中文名称
#   - multiplier: 合约乘数（每点价值）
#   - margin: 保证金比例
#   - tick: 最小变动价位
#   - category: 品种分类（股指/能化/黑色/有色/农产品）
# =============================================================================

CONTRACTS = {
    # ===================== 股指期货 (4个) =====================
    # 股指期货以股票指数为标的，风险较高，保证金比例12%
    "IF": {"name": "沪深300股指", "multiplier": 300, "margin": 0.12, "tick": 0.2, "category": "股指"},
    "IC": {"name": "中证500股指", "multiplier": 200, "margin": 0.12, "tick": 0.2, "category": "股指"},
    "IH": {"name": "上证50股指", "multiplier": 300, "margin": 0.12, "tick": 0.2, "category": "股指"},
    "IM": {"name": "中证1000股指", "multiplier": 200, "margin": 0.12, "tick": 0.2, "category": "股指"},
    
    # ===================== 能化期货 (14个) =====================
    # 能化类期货以能源和化工产品为标的
    "SC": {"name": "原油", "multiplier": 1000, "margin": 0.10, "tick": 0.1, "category": "能化"},
    "LU": {"name": "低硫燃油", "multiplier": 10, "margin": 0.10, "tick": 1, "category": "能化"},
    "FU": {"name": "燃料油", "multiplier": 10, "margin": 0.10, "tick": 1, "category": "能化"},
    "TA": {"name": "PTA", "multiplier": 5, "margin": 0.08, "tick": 2, "category": "能化"},
    "MA": {"name": "甲醇", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "能化"},
    "EG": {"name": "乙二醇", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "能化"},
    "PF": {"name": "短纤", "multiplier": 5, "margin": 0.08, "tick": 2, "category": "能化"},
    "RU": {"name": "橡胶", "multiplier": 10, "margin": 0.10, "tick": 5, "category": "能化"},
    "NR": {"name": "20号胶", "multiplier": 10, "margin": 0.10, "tick": 5, "category": "能化"},
    "BU": {"name": "沥青", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "能化"},
    "V": {"name": "PVC", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "能化"},
    "PP": {"name": "聚丙烯", "multiplier": 5, "margin": 0.08, "tick": 1, "category": "能化"},
    "L": {"name": "聚乙烯", "multiplier": 5, "margin": 0.08, "tick": 1, "category": "能化"},
    "EB": {"name": "苯乙烯", "multiplier": 5, "margin": 0.08, "tick": 1, "category": "能化"},
    
    # ===================== 黑色期货 (9个) =====================
    # 黑色系期货以钢材、煤炭、铁矿石等为标的
    "RB": {"name": "螺纹钢", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "黑色"},
    "HC": {"name": "热卷", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "黑色"},
    "J": {"name": "焦炭", "multiplier": 100, "margin": 0.10, "tick": 0.5, "category": "黑色"},
    "JM": {"name": "焦煤", "multiplier": 60, "margin": 0.10, "tick": 0.5, "category": "黑色"},
    "ZC": {"name": "动力煤", "multiplier": 100, "margin": 0.10, "tick": 0.4, "category": "黑色"},
    "I": {"name": "铁矿石", "multiplier": 100, "margin": 0.10, "tick": 0.5, "category": "黑色"},
    "SS": {"name": "不锈钢", "multiplier": 10, "margin": 0.08, "tick": 5, "category": "黑色"},
    "FG": {"name": "玻璃", "multiplier": 20, "margin": 0.08, "tick": 2, "category": "黑色"},
    "SF": {"name": "硅铁", "multiplier": 5, "margin": 0.08, "tick": 2, "category": "黑色"},
    
    # ===================== 有色金属 (9个) =====================
    # 有色金属期货以铜、铝、锌等贵金属和基础金属为标的
    "CU": {"name": "铜", "multiplier": 5, "margin": 0.10, "tick": 10, "category": "有色"},
    "AL": {"name": "铝", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "有色"},
    "ZN": {"name": "锌", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "有色"},
    "PB": {"name": "铅", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "有色"},
    "NI": {"name": "镍", "multiplier": 1, "margin": 0.10, "tick": 10, "category": "有色"},
    "SN": {"name": "锡", "multiplier": 1, "margin": 0.10, "tick": 10, "category": "有色"},
    "AU": {"name": "黄金", "multiplier": 1000, "margin": 0.10, "tick": 0.05, "category": "有色"},
    "AG": {"name": "白银", "multiplier": 15, "margin": 0.10, "tick": 1, "category": "有色"},
    "RC": {"name": "螺纹钢", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "有色"},
    
    # ===================== 农产品 (17个) =====================
    # 农产品期货以粮食、油脂、棉花等农产品为标的
    "M": {"name": "豆粕", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "Y": {"name": "豆油", "multiplier": 10, "margin": 0.08, "tick": 2, "category": "农产品"},
    "P": {"name": "棕榈油", "multiplier": 10, "margin": 0.08, "tick": 2, "category": "农产品"},
    "A": {"name": "豆一", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "B": {"name": "豆二", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "C": {"name": "玉米", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "CS": {"name": "玉米淀粉", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "SR": {"name": "白糖", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "CF": {"name": "棉花", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "农产品"},
    "SM": {"name": "棉纱", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "农产品"},
    "AP": {"name": "苹果", "multiplier": 10, "margin": 0.08, "tick": 10, "category": "农产品"},
    "CJ": {"name": "红枣", "multiplier": 5, "margin": 0.08, "tick": 5, "category": "农产品"},
    "JR": {"name": "粳米", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "LR": {"name": "晚籼稻", "multiplier": 20, "margin": 0.08, "tick": 1, "category": "农产品"},
    "OI": {"name": "菜油", "multiplier": 10, "margin": 0.08, "tick": 2, "category": "农产品"},
    "RS": {"name": "菜籽", "multiplier": 10, "margin": 0.08, "tick": 1, "category": "农产品"},
    "SP": {"name": "纸浆", "multiplier": 10, "margin": 0.08, "tick": 2, "category": "农产品"},
}

# =============================================================================
# 时间周期配置（共10个周期）
# =============================================================================
# 用途：支持多时间周期分析，满足不同交易策略需求
# =============================================================================
TIMEFRAMES = {
    "1m": {"name": "1分钟", "minutes": 1, "desc": "超短线交易"},
    "5m": {"name": "5分钟", "minutes": 5, "desc": "日内短线"},
    "15m": {"name": "15分钟", "minutes": 15, "desc": "日内波段"},
    "30m": {"name": "30分钟", "minutes": 30, "desc": "短线交易"},
    "1h": {"name": "1小时", "minutes": 60, "desc": "日内到隔夜"},
    "2h": {"name": "2小时", "minutes": 120, "desc": "短期波段"},
    "4h": {"name": "4小时", "minutes": 240, "desc": "波段交易"},
    "1d": {"name": "日线", "minutes": 1440, "desc": "趋势交易"},
    "1w": {"name": "周线", "minutes": 10080, "desc": "中长线"},
    "1M": {"name": "月线", "minutes": 43200, "desc": "长线投资"},
}

# =============================================================================
# 交易配置
# =============================================================================
TRADING_CONFIG = {
    "initial_capital": 1_000_000,  # 初始资金：100万元人民币
    "commission_rate": 0.0003,     # 手续费率：万分之3
    "commission_min": 20,         # 最低手续费：20元/手
    "slippage": 0.0001,           # 滑点：万分之1
    "margin_rate": 0.12,          # 默认保证金比例：12%
}

# =============================================================================
# 回测配置
# =============================================================================
BACKTEST_CONFIG = {
    "start_date": "2024-01-01",  # 回测开始日期
    "end_date": "2024-12-31",    # 回测结束日期
    "warm_up_period": 30,        # 预热期（天），用于计算指标
}

# =============================================================================
# 策略排名权重配置
# =============================================================================
# 用于综合评估策略表现
RANKING_WEIGHTS = {
    "return": 0.30,       # 收益率权重：30%
    "risk": 0.30,         # 风险控制权重：30%
    "efficiency": 0.15,   # 效率权重：15%
    "robustness": 0.25,   # 稳健性权重：25%
}

# =============================================================================
# 文件路径配置
# =============================================================================
PATHS = {
    "data": "data/",      # 行情数据目录
    "logs": "logs/",      # 日志文件目录
    "reports": "reports/", # 报告输出目录
    "cache": "cache/",    # 缓存文件目录
}
