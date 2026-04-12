# ⏰ 定期检查 Cron 任务设置

## 快速设置

### macOS/Linux

```bash
# 编辑 crontab
crontab -e

# 添加以下任务
```

### Windows (任务计划程序)

使用 `schtasks` 命令或任务计划程序 GUI 添加任务。

---

## Cron 任务列表

### 每日检查 (08:00)

```cron
# 每日代码检查 - 08:00
0 8 * * * cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh daily >> logs/cron_daily.log 2>&1
```

**检查内容**:
- ✅ Python 语法检查
- ✅ 模块导入检查
- ✅ 日志文件检查

**输出**: `logs/cron_daily.log`

---

### 每周检查 (周日 20:00)

```cron
# 每周代码检查 - 周日 20:00
0 20 * * 0 cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh weekly >> logs/cron_weekly.log 2>&1
```

**检查内容**:
- ✅ 每日检查所有内容
- ✅ Flake8 风格检查
- ✅ 回测运行检查

**输出**: `logs/cron_weekly.log`

---

### 每月检查 (月末 20:00)

```cron
# 每月代码检查 - 每月最后一天 20:00
0 20 28-31 * * [ "$(date +\%d)" = "$(date -d tomorrow +\%d)" ] && cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh monthly >> logs/cron_monthly.log 2>&1
```

**检查内容**:
- ✅ 每周检查所有内容
- ✅ Pylint 代码质量检查
- ✅ 安全扫描 (Bandit/Safety)
- ✅ 生成月度检查报告

**输出**: `logs/cron_monthly.log` + `reports/monthly_check_YYYYMM.md`

---

### 自动化迭代 (已存在于 iteration.py)

```cron
# 盘前运行 - 工作日 08:00
0 8 * * 1-5 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --morning >> logs/iteration_morning.log 2>&1

# 盘中运行 - 工作日 09:00
0 9 * * 1-5 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --trading >> logs/iteration_trading.log 2>&1

# 盘后运行 - 工作日 15:00
0 15 * * 1-5 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --evening >> logs/iteration_evening.log 2>&1

# 周回测 - 周日 20:00
0 20 * * 0 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --backtest >> logs/iteration_backtest.log 2>&1

# 月优化 - 每月 1 号 20:00
0 20 1 * * cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --optimize >> logs/iteration_optimize.log 2>&1
```

---

## 完整 Crontab 示例

```bash
# 编辑 crontab
crontab -e

# 期货量化系统 - 定期检查任务
# ============================================================

# 每日代码检查 - 08:00
0 8 * * * cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh daily >> logs/cron_daily.log 2>&1

# 每周代码检查 - 周日 20:00
0 20 * * 0 cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh weekly >> logs/cron_weekly.log 2>&1

# 每月代码检查 - 月末 20:00
0 20 28-31 * * [ "$(date +\%d)" = "$(date -d tomorrow +\%d)" ] && cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh monthly >> logs/cron_monthly.log 2>&1

# ============================================================
# 自动化迭代任务

# 盘前运行 - 工作日 08:00
0 8 * * 1-5 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --morning >> logs/iteration_morning.log 2>&1

# 盘中运行 - 工作日 09:00
0 9 * * 1-5 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --trading >> logs/iteration_trading.log 2>&1

# 盘后运行 - 工作日 15:00
0 15 * * 1-5 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --evening >> logs/iteration_evening.log 2>&1

# 周回测 - 周日 20:00
0 20 * * 0 cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --backtest >> logs/iteration_backtest.log 2>&1

# 月优化 - 每月 1 号 20:00
0 20 1 * * cd /Users/zy/futures_quant && source venv/bin/activate && python iteration.py --optimize >> logs/iteration_optimize.log 2>&1

# ============================================================
```

---

## 验证 Cron 任务

### 查看已安装的任务

```bash
crontab -l
```

### 查看 Cron 日志

```bash
# macOS
log show --predicate 'process == "cron"' --last 1h

# Linux
grep CRON /var/log/syslog | tail -20
```

### 手动测试脚本

```bash
cd /Users/zy/futures_quant
source venv/bin/activate

# 测试每日检查
./scripts/code_check.sh daily

# 测试每周检查
./scripts/code_check.sh weekly

# 测试每月检查
./scripts/code_check.sh monthly
```

---

## 通知设置 (可选)

### 邮件通知

```cron
# 检查失败时发送邮件
0 8 * * * cd /Users/zy/futures_quant && source venv/bin/activate && ./scripts/code_check.sh daily || mail -s "代码检查失败" your@email.com
```

### 钉钉通知

```bash
# 添加通知脚本 scripts/notify_dingtalk.sh
curl 'https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN' \
   -H 'Content-Type: application/json' \
   -d '{"msgtype":"text","text":{"content":"代码检查完成"}}'
```

### 微信通知

使用 Server 酱或其他微信推送服务。

---

## 故障排查

### Cron 不执行

1. **检查 Cron 服务状态**
   ```bash
   # macOS
   sudo launchctl load -w /System/Library/LaunchDaemons/com.vix.cron.plist
   
   # Linux
   sudo systemctl status cron
   ```

2. **检查脚本权限**
   ```bash
   chmod +x /Users/zy/futures_quant/scripts/code_check.sh
   ```

3. **检查路径**
   - 使用绝对路径
   - 确保 Python 虚拟环境路径正确

4. **查看 Cron 日志**
   ```bash
   # macOS
   log show --predicate 'process == "cron"' --last 24h
   
   # Linux
   tail -f /var/log/cron
   ```

### 脚本执行失败

1. **手动运行测试**
   ```bash
   cd /Users/zy/futures_quant
   source venv/bin/activate
   ./scripts/code_check.sh daily
   ```

2. **检查依赖**
   ```bash
   pip install pylint flake8 bandit safety
   ```

3. **检查日志**
   ```bash
   tail -100 logs/cron_daily.log
   ```

---

## 检查报告查看

### 每日报告

```bash
tail -50 logs/cron_daily.log
```

### 每周报告

```bash
tail -100 logs/cron_weekly.log
```

### 月度报告

```bash
cat reports/monthly_check_$(date +%Y%m).md
```

---

## 下一步

1. ✅ 设置 Cron 任务
2. ✅ 验证任务执行
3. ✅ 配置通知 (可选)
4. ✅ 定期检查报告

---

**文档**: https://github.com/robot1969/futures-quant/blob/main/CRON_SETUP.md
**问题反馈**: https://github.com/robot1969/futures-quant/issues
