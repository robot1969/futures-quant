"""订单执行器 - 增强版
=============================================================================
功能:
  - 执行策略信号
  - 动态止损止盈
  - 时间止损 (持仓超过 N 天强制平仓)
  - 仓位管理
  - 信号过滤 (多指标共振)
=============================================================================
"""
import pandas as pd
from config import CONTRACTS, TRADING_CONFIG
from datetime import datetime, timedelta

class OrderExecutor:
    """订单执行"""
    
    def __init__(self, portfolio, config=None):
        self.portfolio = portfolio
        self.pending_orders = []
        self.executed_orders = []
        self.max_position_per_symbol = 0.3  # 单品种最大仓位 30%
        
        # 增强配置
        self.config = config or {}
        self.time_stop_loss_days = self.config.get('time_stop_loss_days', 1)  # 时间止损 1 天
        self.enable_signal_filter = self.config.get('enable_signal_filter', False)  # 关闭信号过滤
        self.min_confidence = self.config.get('min_confidence', 0.3)  # 降低置信度门槛
    
    def execute_signals(self, signals, market_prices, market_data=None):
        """执行策略信号
        
        Args:
            market_data: 市场数据字典 {symbol: df}，用于计算动态止损
        """
        print("⚡ 执行交易信号...")
        
        # 1. 先检查现有持仓的止损止盈和时间止损
        self._check_stop_loss(market_prices, market_data)
        
        # 2. 执行新信号
        for name, sig in signals.items():
            # 兼容新旧格式
            signal_type = sig.get("direction", sig.get("signal", 0))
            if signal_type == 0 or signal_type == "neutral":
                continue
            
            # 信号过滤 (多指标共振检查)
            if self.enable_signal_filter:
                confidence = sig.get("confidence", 1.0)
                if confidence < self.min_confidence:
                    continue
            
            # 从信号名提取合约代码
            parts = name.split("_")
            symbol = parts[0] if parts else name[:2]
            
            # 尝试多种方式获取合约代码
            if symbol not in CONTRACTS:
                symbol = name[:2] if len(name) >= 2 else symbol
            if symbol not in CONTRACTS:
                for contract_code in CONTRACTS.keys():
                    if contract_code in name:
                        symbol = contract_code
                        break
            
            if symbol not in CONTRACTS:
                continue
            
            direction = signal_type
            
            # 执行交易
            if direction == "buy":
                df = market_data.get(symbol) if market_data else None
                self._buy(symbol, market_prices, df=df)
            elif direction == "sell":
                self._sell(symbol, market_prices)
    
    def _check_stop_loss(self, prices, market_data=None):
        """检查止损止盈和时间止损"""
        symbols_to_close = []
        
        for symbol, pos in self.portfolio.positions.items():
            if symbol not in prices:
                continue
            
            current_price = prices[symbol]
            
            # 1. 检查止损止盈
            stop_reason = pos.should_stop(current_price)
            if stop_reason:
                symbols_to_close.append((symbol, current_price, stop_reason))
                continue
            
            # 2. 检查时间止损
            if self.time_stop_loss_days > 0:
                holding_days = (datetime.now() - pos.entry_time).days
                if holding_days >= self.time_stop_loss_days:
                    symbols_to_close.append((symbol, current_price, 'time_stop'))
        
        # 执行平仓
        for symbol, price, reason in symbols_to_close:
            self._close_with_reason(symbol, price, reason)
    
    def _close_with_reason(self, symbol, price, reason):
        """平仓并记录原因"""
        if symbol not in self.portfolio.positions:
            return
        
        pos = self.portfolio.positions[symbol]
        reason_map = {
            'stop_loss': '止损',
            'take_profit': '止盈',
            'time_stop': '时间止损'
        }
        
        reason_text = reason_map.get(reason, reason)
        
        success = self.portfolio.close_position(symbol, price)
        if success:
            self.executed_orders.append({
                "time": datetime.now(),
                "symbol": symbol,
                "action": "sell",
                "price": price,
                "reason": reason,
                "reason_text": reason_text
            })
            print(f"      🚫 平仓 {symbol} @ {price:.2f} ({reason_text})")
    
    def _buy(self, symbol, prices, df=None):
        """买入开多
        
        Args:
            df: K 线数据 (用于动态止损)
        """
        if symbol not in prices:
            return False
        if symbol in self.portfolio.positions:
            return False  # 已有持仓
            
        price = prices[symbol]
        max_qty = self._calculate_max_quantity(symbol, price)
        
        if max_qty > 0:
            success = self.portfolio.open_position(symbol, "long", max_qty, price, df=df)
            if success:
                self.executed_orders.append({
                    "time": datetime.now(),
                    "symbol": symbol,
                    "action": "buy",
                    "quantity": max_qty,
                    "price": price
                })
                print(f"      ✅ 开多 {symbol} x{max_qty} @ {price:.2f}")
            return success
        return False
    
    def _sell(self, symbol, prices):
        """卖出平仓"""
        if symbol not in prices:
            return False
        if symbol not in self.portfolio.positions:
            return False
            
        price = prices[symbol]
        success = self.portfolio.close_position(symbol, price)
        
        if success:
            self.executed_orders.append({
                "time": datetime.now(),
                "symbol": symbol,
                "action": "sell",
                "price": price,
                "reason": "manual",
                "reason_text": "手动平仓"
            })
            print(f"      ✅ 平仓 {symbol} @ {price:.2f}")
        return success
    
    def _calculate_max_quantity(self, symbol, price):
        """计算最大开仓数量"""
        mult = CONTRACTS[symbol]["multiplier"]
        margin_per_lot = price * mult * TRADING_CONFIG["margin_rate"]
        
        available_capital = self.portfolio.cash * self.max_position_per_symbol
        max_qty = int(available_capital / margin_per_lot)
        
        return max(0, min(max_qty, 10))  # 最多 10 手
    
    def get_positions_summary(self, current_prices=None):
        """持仓汇总
        
        Args:
            current_prices: 当前价格字典 {symbol: price}
        """
        summary = []
        for symbol, pos in self.portfolio.positions.items():
            current_price = current_prices.get(symbol, pos.entry_price) if current_prices else pos.entry_price
            contract = CONTRACTS.get(symbol, {})
            category = contract.get('category', '其他')
            margin = pos.entry_price * pos.quantity * contract.get('multiplier', 1) * TRADING_CONFIG.get('margin_rate', 0.12)
            
            # 计算持仓天数
            holding_days = (datetime.now() - pos.entry_time).days
            
            summary.append({
                "symbol": symbol,
                "name": contract.get('name', symbol),
                "category": category,
                "direction": pos.direction,
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
                "current_price": current_price,
                "pnl": pos.pnl,
                "pnl_pct": pos.pnl_pct,
                "margin": margin,
                "holding_days": holding_days,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit
            })
        return summary
    
    def get_orders_summary(self):
        """订单汇总"""
        return {
            "pending": len(self.pending_orders),
            "executed": len(self.executed_orders)
        }
