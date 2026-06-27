"""持仓管理"""
from datetime import datetime
from config import CONTRACTS, TRADING_CONFIG

class Position:
    """单个持仓"""
    
    def __init__(self, symbol, direction, quantity, entry_price, stop_loss=0, take_profit=0):
        self.symbol = symbol
        self.direction = direction
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_time = datetime.now()
        self.pnl = 0
        self.pnl_pct = 0
        self.stop_loss = stop_loss  # 止损价
        self.take_profit = take_profit  # 止盈价
    
    def update_pnl(self, current_price):
        """更新盈亏并更新追踪止损"""
        mult = CONTRACTS[self.symbol]["multiplier"]
        if self.direction == "long":
            self.pnl = (current_price - self.entry_price) * mult * self.quantity
            # 追踪止损：价格创新高时，止损线向上移动 (保持 2*ATR 或固定比例)
            if current_price > self.entry_price and self.stop_loss > 0:
                new_stop = current_price * 0.97 # 简单实现：维持在价格 3% 处
                self.stop_loss = max(self.stop_loss, new_stop)
        else:
            self.pnl = (self.entry_price - current_price) * mult * self.quantity
            if current_price < self.entry_price and self.stop_loss > 0:
                new_stop = current_price * 1.03
                self.stop_loss = min(self.stop_loss, new_stop)
        cost = self.entry_price * mult * self.quantity
        self.pnl_pct = self.pnl / cost if cost > 0 else 0
    
    def should_stop(self, current_price):
        """检查是否触发止损/止盈"""
        if self.direction == "long":
            if self.stop_loss > 0 and current_price <= self.stop_loss:
                return "stop_loss"
            if self.take_profit > 0 and current_price >= self.take_profit:
                return "take_profit"
        else:  # short
            if self.stop_loss > 0 and current_price >= self.stop_loss:
                return "stop_loss"
            if self.take_profit > 0 and current_price <= self.take_profit:
                return "take_profit"
        return None


class Portfolio:
    """投资组合管理"""
    
    def __init__(self, initial_capital=1_000_000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.closed_pnl = 0
        self.trades = []
        self.equity_curve = [initial_capital]
    
    def can_open(self, symbol, quantity, price):
        margin = price * CONTRACTS[symbol]["multiplier"] * quantity * TRADING_CONFIG["margin_rate"]
        return self.cash >= margin
    
    def open_position(self, symbol, direction, quantity, price, stop_loss_pct=0.05, take_profit_pct=0.10, df=None):
        """开仓（支持动态止损止盈）
        
        Args:
            df: K 线数据（用于计算 ATR 动态止损）
        """
        if not self.can_open(symbol, quantity, price):
            return False
        mult = CONTRACTS[symbol]["multiplier"]
        commission = price * mult * quantity * TRADING_CONFIG["commission_rate"]
        commission = max(commission, TRADING_CONFIG["commission_min"])
        slippage = price * TRADING_CONFIG["slippage"] * mult * quantity
        margin = price * mult * quantity * TRADING_CONFIG["margin_rate"]
        self.cash -= (margin + commission + slippage)
        exec_price = price * (1 + TRADING_CONFIG["slippage"]) if direction == "long" else price * (1 - TRADING_CONFIG["slippage"])
        
        # 计算止损止盈价格（支持动态计算）
        if df is not None and "ATR_14" in df.columns:
            # 使用动态止损止盈
            stop_loss, take_profit = self._calculate_dynamic_stop_profit(
                symbol, direction, exec_price, df
            )
        else:
            # 使用固定比例止损止盈
            stop_loss = exec_price * (1 - stop_loss_pct) if direction == "long" else exec_price * (1 + stop_loss_pct)
            take_profit = exec_price * (1 + take_profit_pct) if direction == "long" else exec_price * (1 - take_profit_pct)
        
        self.positions[symbol] = Position(symbol, direction, quantity, exec_price, stop_loss, take_profit)
        self.trades.append({
            "time": datetime.now(), 
            "symbol": symbol, 
            "direction": direction, 
            "quantity": quantity, 
            "price": exec_price, 
            "type": "open", 
            "commission": commission, 
            "stop_loss": stop_loss, 
            "take_profit": take_profit
        })
        return True
    
    def _calculate_dynamic_stop_profit(self, symbol, direction, entry_price, df):
        """基于 ATR 动态计算止损止盈价格
        
        止损：2 倍 ATR
        止盈：3 倍 ATR
        """
        atr = df["ATR_14"].iloc[-1]
        if not pd.notna(atr):
            # ATR 无效时使用固定比例
            if direction == "long":
                return entry_price * 0.95, entry_price * 1.10
            else:
                return entry_price * 1.05, entry_price * 0.90
        
        # 动态计算
        if direction == "long":
            stop_loss = max(entry_price - (2 * atr), entry_price * 0.90)  # 最多不超过 10%
            take_profit = min(entry_price + (3 * atr), entry_price * 1.20)  # 最多不超过 20%
        else:  # short
            stop_loss = min(entry_price + (2 * atr), entry_price * 1.10)
            take_profit = max(entry_price - (3 * atr), entry_price * 0.80)
        
        return stop_loss, take_profit
    
    def close_position(self, symbol, price):
        if symbol not in self.positions:
            return False
        pos = self.positions[symbol]
        mult = CONTRACTS[symbol]["multiplier"]
        commission = price * mult * pos.quantity * TRADING_CONFIG["commission_rate"]
        commission = max(commission, TRADING_CONFIG["commission_min"])
        pos.update_pnl(price)
        self.closed_pnl += pos.pnl - commission
        margin = pos.entry_price * mult * pos.quantity * TRADING_CONFIG["margin_rate"]
        self.cash += margin
        self.trades.append({"time": datetime.now(), "symbol": symbol, "direction": pos.direction, "quantity": pos.quantity, "price": price, "pnl": pos.pnl - commission, "type": "close", "commission": commission})
        del self.positions[symbol]
        return True
    
    def get_equity(self, prices=None):
        """计算总权益（包含保证金）"""
        # 当前现金 + 已实现盈亏
        equity = self.cash + self.closed_pnl
        
        # 加上持仓的保证金（因为保证金仍然是我们的资产）
        for symbol, pos in self.positions.items():
            mult = CONTRACTS[symbol]["multiplier"]
            margin = pos.entry_price * mult * pos.quantity * TRADING_CONFIG["margin_rate"]
            equity += margin  # 保证金仍然是权益的一部分
        
        # 加上持仓的浮动盈亏
        if prices:
            for symbol, pos in self.positions.items():
                if symbol in prices:
                    pos.update_pnl(prices[symbol])
                    equity += pos.pnl
        
        self.equity_curve.append(equity)
        return equity
    
    def get_stats(self):
        return {"initial_capital": self.initial_capital, "current_equity": self.get_equity(), "cash": self.cash, "closed_pnl": self.closed_pnl, "open_positions": len(self.positions), "total_trades": len(self.trades)}
    
    # ========== 风险管理模块 ==========
    
    def set_risk_params(self, stop_loss_pct=0.05, take_profit_pct=0.10):
        """设置风控参数"""
        self.stop_loss_pct = stop_loss_pct  # 止损比例
        self.take_profit_pct = take_profit_pct  # 止盈比例
    
    def calculate_position_size(self, symbol, price, risk_pct=0.02):
        """计算开仓数量（基于风险）"""
        equity = self.get_equity()
        risk_amount = equity * risk_pct
        mult = CONTRACTS[symbol]["multiplier"]
        price_risk = price * self.stop_loss_pct
        return int(risk_amount / (price_risk * mult))
    
    def check_risk_limits(self, symbol, direction, quantity, price):
        """检查风控限制"""
        # 1. 单品种仓位限制
        if symbol in self.positions:
            existing = self.positions[symbol]
            total_qty = existing.quantity + quantity
            if total_qty > TRADING_CONFIG.get("max_position_size", 50):
                return False, "超过单品种仓位上限"
        
        # 2. 总仓位限制
        total_margin = 0
        for sym, pos in self.positions.items():
            mult = CONTRACTS[sym]["multiplier"]
            total_margin += pos.entry_price * mult * pos.quantity
        new_margin = price * CONTRACTS[symbol]["multiplier"] * quantity * TRADING_CONFIG["margin_rate"]
        if total_margin + new_margin > self.initial_capital * TRADING_CONFIG.get("max_leverage", 0.5):
            return False, "超过总仓位杠杆限制"
        
        # 3. 单日亏损限制
        if self.closed_pnl < -self.initial_capital * 0.03:
            return False, "单日亏损超过3%上限"
        
        return True, "ok"
    
    def get_open_positions_info(self):
        """获取持仓信息（含风控状态）"""
        positions = []
        for symbol, pos in self.positions.items():
            positions.append({
                "symbol": symbol,
                "direction": pos.direction,
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
                "pnl": pos.pnl,
                "pnl_pct": pos.pnl_pct,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit
            })
        return positions
