"""
=============================================================================
核心模块 - 系统管理器与统一入口
=============================================================================
"""
from .manager import FuturesQuantManager, run_quant_system

__all__ = [
    'FuturesQuantManager',
    'run_quant_system'
]
