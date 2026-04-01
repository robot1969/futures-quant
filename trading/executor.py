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
    
    def execute_signals(self, signals, market_prices, market_data=None):
        """执行策略信号
        
        Args:
            market_data: 市场数据字典 {symbol: df}，用于计算动态止损
        """
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
                # 传入 K 线数据用于动态止损
                df = market_data.get(symbol) if market_data else None
                self._buy(symbol, market_prices, df=df)
            elif direction == "sell":
                self._sell(symbol, market_prices)
    
    def _buy(self, symbol, prices, df=None):
        """买入开多
        
        Args:
            df: K 线数据（用于动态止损）
        """
        if symbol not in prices:
            return False
        if symbol in self.portfolio.positions:
            return False  # 已有持仓
            
        price = prices[symbol]
        max_qty = self._calculate_max_quantity(symbol, price)
        
        if max_qty > 0:
            # 传入 df 用于计算动态止损止盈
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
    
    def get_positions_summary(self, current_prices=None):
        """持仓汇总
        
        Args:
            current_prices: 当前价格字典 {symbol: price}
        """
        summary = []
        for symbol, pos in self.portfolio.positions.items():
            # 获取当前价格
            current_price = current_prices.get(symbol, pos.entry_price) if current_prices else pos.entry_price
            
            # 获取合约信息
            contract = CONTRACTS.get(symbol, {})
            category = contract.get('category', '其他')
            
            # 计算保证金
            margin = pos.entry_price * pos.quantity * contract.get('multiplier', 1) * TRADING_CONFIG.get('margin_rate', 0.12)
            
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
                "margin": margin
            })
        return summary
    
    def get_orders_summary(self):
        """订单汇总"""
        return {
            "pending": len(self.pending_orders),
            "executed": len(self.executed_orders)
        }
