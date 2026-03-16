"""订单执行器 - Day 5"""
import pandas as pd
from config import CONTRACTS, TRADING_CONFIG
from datetime import datetime

class OrderExecutor:
    """订单执行"""
    
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.pending_orders = []
        self.executed_orders = []
        self.max_position_per_symbol = 0.3  # 单品种最大仓位30%
    
    def execute_signals(self, signals, market_prices):
        """执行策略信号"""
        print("⚡ 执行交易信号...")
        
        for name, sig in signals.items():
            # 兼容新旧格式
            signal_type = sig.get("direction", sig.get("signal", 0))
            if signal_type == 0 or signal_type == "neutral":
                continue
            
            # 从信号名提取合约代码
            parts = name.split("_")
            symbol = parts[0] if parts else name[:2]
            
            # 尝试多种方式获取合约代码
            if symbol not in CONTRACTS:
                # 尝试前两个字符
                symbol = name[:2] if len(name) >= 2 else symbol
            if symbol not in CONTRACTS:
                # 尝试在配置中查找
                for contract_code in CONTRACTS.keys():
                    if contract_code in name:
                        symbol = contract_code
                        break
            
            if symbol not in CONTRACTS:
                continue
            
            direction = signal_type
            print(f"   📌 {name}: {direction} {symbol}")
            
            # 执行交易
            if direction == "buy":
                self._buy(symbol, market_prices)
            elif direction == "sell":
                self._sell(symbol, market_prices)
    
    def _buy(self, symbol, prices):
        """买入开多"""
        if symbol not in prices:
            return False
        if symbol in self.portfolio.positions:
            return False  # 已有持仓
            
        price = prices[symbol]
        max_qty = self._calculate_max_quantity(symbol, price)
        
        if max_qty > 0:
            success = self.portfolio.open_position(symbol, "long", max_qty, price)
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
                "price": price
            })
            print(f"      ✅ 平仓 {symbol} @ {price:.2f}")
        return success
    
    def _calculate_max_quantity(self, symbol, price):
        """计算最大开仓数量"""
        mult = CONTRACTS[symbol]["multiplier"]
        margin_per_lot = price * mult * TRADING_CONFIG["margin_rate"]
        
        available_capital = self.portfolio.cash * self.max_position_per_symbol
        max_qty = int(available_capital / margin_per_lot)
        
        return max(0, min(max_qty, 10))  # 最多10手
    
    def get_positions_summary(self):
        """持仓汇总"""
        summary = []
        for symbol, pos in self.portfolio.positions.items():
            summary.append({
                "symbol": symbol,
                "direction": pos.direction,
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
                "pnl": pos.pnl,
                "pnl_pct": pos.pnl_pct
            })
        return summary
    
    def get_orders_summary(self):
        """订单汇总"""
        return {
            "pending": len(self.pending_orders),
            "executed": len(self.executed_orders)
        }
