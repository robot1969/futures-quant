"""风险管理模块 - 止损/止盈/仓位"""
from config import CONTRACTS, TRADING_CONFIG

class RiskManager:
    """风险管理"""
    
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.max_position_pct = 0.3  # 单品种最大30%
        self.max_total_pct = 0.8      # 总仓位最大80%
        self.stop_loss_pct = 0.05      # 止损5%
        self.take_profit_pct = 0.10    # 止盈10%
    
    def check_open(self, symbol, price, quantity):
        """检查是否允许开仓"""
        mult = CONTRACTS[symbol]["multiplier"]
        margin = price * mult * quantity * TRADING_CONFIG["margin_rate"]
        total_margin = sum(
            p.entry_price * CONTRACTS[p.symbol]["multiplier"] * p.quantity * TRADING_CONFIG["margin_rate"]
            for p in self.portfolio.positions.values()
        )
        
        # 检查总仓位
        equity = self.portfolio.get_equity()
        if (total_margin + margin) / equity > self.max_total_pct:
            return False, "总仓位超限"
        
        # 检查单品种仓位
        if symbol in self.portfolio.positions:
            return False, "已有持仓"
        
        return True, "允许开仓"
    
    def check_close(self, symbol, current_price):
        """检查是否需要止损/止盈"""
        if symbol not in self.portfolio.positions:
            return False, ""
        
        pos = self.portfolio.positions[symbol]
        pos.update_pnl(current_price)
        
        # 止损检查
        if pos.pnl_pct <= -self.stop_loss_pct:
            return True, f"止损 {pos.pnl_pct:.2%}"
        
        # 止盈检查
        if pos.pnl_pct >= self.take_profit_pct:
            return True, f"止盈 {pos.pnl_pct:.2%}"
        
        return False, ""
    
    def get_risk_metrics(self):
        """获取风险指标"""
        equity = self.portfolio.get_equity()
        
        total_margin = sum(
            p.entry_price * CONTRACTS[p.symbol]["multiplier"] * p.quantity * TRADING_CONFIG["margin_rate"]
            for p in self.portfolio.positions.values()
        )
        
        exposure = total_margin / equity if equity > 0 else 0
        positions_count = len(self.portfolio.positions)
        
        return {
            "exposure": exposure,
            "positions_count": positions_count,
            "max_position_pct": self.max_position_pct,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
            "risk_level": "HIGH" if exposure > 0.7 else "MEDIUM" if exposure > 0.4 else "LOW"
        }
