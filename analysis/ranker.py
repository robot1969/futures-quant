"""策略排名"""
from config import RANKING_WEIGHTS

class StrategyRanker:
    """策略排名"""
    
    def __init__(self):
        self.weights = RANKING_WEIGHTS
    
    def rank(self, results):
        score = self._calculate_score(results)
        return {"score": score, "results": results, "rank": 1, "grade": self._get_grade(score)}
    
    def _calculate_score(self, results):
        return_score = max(0, results.get("total_return", 0) * 100)
        risk_score = max(0, (1 - results.get("max_drawdown", 0)) * 100)
        efficiency_score = max(0, results.get("sharpe_ratio", 0) * 50)
        robustness_score = results.get("win_rate", 0) * 100
        total = return_score * self.weights["return"] + risk_score * self.weights["risk"] + efficiency_score * self.weights["efficiency"] + robustness_score * self.weights["robustness"]
        return total
    
    def _get_grade(self, score):
        if score >= 80: return "A+"
        elif score >= 70: return "A"
        elif score >= 60: return "B+"
        elif score >= 50: return "B"
        elif score >= 40: return "C"
        else: return "D"
    
    def rank_multiple_strategies(self, strategy_results):
        ranked = []
        for name, result in strategy_results.items():
            score = self._calculate_score(result)
            ranked.append({"name": name, "score": score, "grade": self._get_grade(score), "return": result.get("total_return", 0)})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
