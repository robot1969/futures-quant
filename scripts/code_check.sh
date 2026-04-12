#!/bin/bash
# =============================================================================
# 代码检查脚本 - 定期检查代码质量
# 用法：./scripts/code_check.sh [daily|weekly|monthly]
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
REPORT_DIR="$PROJECT_ROOT/reports"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建目录
mkdir -p "$LOG_DIR" "$REPORT_DIR"

# 检查类型
CHECK_TYPE=${1:-daily}

log_info "开始代码检查 - $CHECK_TYPE"
log_info "项目目录：$PROJECT_ROOT"
log_info "日志目录：$LOG_DIR"

# =============================================================================
# 每日检查
# =============================================================================
if [ "$CHECK_TYPE" = "daily" ]; then
    log_info "=== 每日检查 ==="
    
    # 1. Python 语法检查
    log_info "1. Python 语法检查..."
    cd "$PROJECT_ROOT"
    python -m py_compile main_enhanced.py iteration.py \
        strategy/factors_enhanced.py \
        strategy/strategies_enhanced.py \
        analysis/backtester_pro.py \
        analysis/report_generator.py \
        web/app_pro.py 2>&1 | tee "$LOG_DIR/syntax_check.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_info "✅ 语法检查通过"
    else
        log_error "❌ 语法检查失败"
        exit 1
    fi
    
    # 2. 导入检查
    log_info "2. 模块导入检查..."
    python -c "
import sys
sys.path.insert(0, '.')
try:
    from strategy.factors_enhanced import EnhancedFactorEngine
    from strategy.strategies_enhanced import EnhancedStrategyEngine
    from analysis.backtester_pro import ProBacktester
    from analysis.report_generator import ReportGenerator
    from iteration import IterationSystem
    print('✅ 导入检查通过')
except Exception as e:
    print(f'❌ 导入失败：{e}')
    sys.exit(1)
" 2>&1 | tee "$LOG_DIR/import_check.log"
    
    # 3. 日志文件检查
    log_info "3. 日志文件检查..."
    if [ -d "$LOG_DIR" ]; then
        ERROR_COUNT=$(grep -i "error" "$LOG_DIR"/*.log 2>/dev/null | wc -l || echo "0")
        if [ "$ERROR_COUNT" -gt 0 ]; then
            log_warn "⚠️ 发现 $ERROR_COUNT 个错误日志，请检查"
        else
            log_info "✅ 日志检查通过"
        fi
    fi
    
    log_info "=== 每日检查完成 ==="
fi

# =============================================================================
# 每周检查
# =============================================================================
if [ "$CHECK_TYPE" = "weekly" ]; then
    log_info "=== 每周检查 ==="
    
    # 执行每日检查
    "$SCRIPT_DIR/code_check.sh" daily
    
    # 4. 安装检查工具
    log_info "4. 安装检查工具..."
    pip install -q pylint flake8 2>&1 | tee "$LOG_DIR/pip_install.log"
    
    # 5. Flake8 风格检查
    log_info "5. Flake8 风格检查..."
    cd "$PROJECT_ROOT"
    flake8 strategy/ analysis/ trading/ web/ \
        --max-line-length=120 \
        --ignore=E501,W503 \
        --exclude=venv,__pycache__ \
        2>&1 | tee "$LOG_DIR/flake8_check.log" || true
    
    # 6. 运行回测检查
    log_info "6. 回测检查..."
    python main_enhanced.py --backtest 2>&1 | tee "$LOG_DIR/backtest_check.log"
    
    log_info "=== 每周检查完成 ==="
fi

# =============================================================================
# 每月检查
# =============================================================================
if [ "$CHECK_TYPE" = "monthly" ]; then
    log_info "=== 每月检查 ==="
    
    # 执行每周检查
    "$SCRIPT_DIR/code_check.sh" weekly
    
    # 7. Pylint 代码质量检查
    log_info "7. Pylint 代码质量检查..."
    cd "$PROJECT_ROOT"
    pylint strategy/factors_enhanced.py \
           strategy/strategies_enhanced.py \
           analysis/backtester_pro.py \
           analysis/report_generator.py \
           --max-line-length=120 \
           --disable=C0114,C0115,C0116 \
           2>&1 | tee "$LOG_DIR/pylint_check.log" || true
    
    # 8. 安全扫描
    log_info "8. 安全扫描..."
    pip install -q bandit safety
    bandit -r strategy/ analysis/ trading/ -f json -o "$REPORT_DIR/bandit_report.json" 2>&1 | tee "$LOG_DIR/bandit_check.log" || true
    safety check --json > "$REPORT_DIR/safety_report.json" 2>&1 || true
    
    # 9. 生成检查报告
    log_info "9. 生成检查报告..."
    cat > "$REPORT_DIR/monthly_check_$(date +%Y%m).md" << EOF
# 月度代码检查报告

**检查日期**: $(date +%Y-%m-%d)
**检查类型**: 月度全面检查

## 检查结果

### 语法检查
$(cat "$LOG_DIR/syntax_check.log" | tail -5)

### Flake8 检查
$(cat "$LOG_DIR/flake8_check.log" | tail -10)

### Pylint 评分
$(cat "$LOG_DIR/pylint_check.log" | grep "Rated" | head -5)

### 安全扫描
- Bandit 报告：$REPORT_DIR/bandit_report.json
- Safety 报告：$REPORT_DIR/safety_report.json

## 需要关注的问题

$(grep -i "warning\|error" "$LOG_DIR"/*.log 2>/dev/null | tail -20)

## 下月改进计划

- [ ] 修复高优先级问题
- [ ] 优化性能瓶颈
- [ ] 完善文档

EOF
    
    log_info "✅ 月度报告已生成：$REPORT_DIR/monthly_check_$(date +%Y%m).md"
    
    log_info "=== 每月检查完成 ==="
fi

log_info "代码检查完成！"
