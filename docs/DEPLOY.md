# 部署说明

本文档说明如何把 `sporttery-odds-feishu` 部署为长期运行的本地工具。

## 一、手动运行

### 1. 单次查询

```bash
python -m odds_tool.main fetch --team 加拿大
```

### 2. 监控指定球队赔率变化

```bash
python -m odds_tool.main watch-team --team 加拿大 --interval 60 --target oc_xxx
```

### 3. 定时推送

```bash
python -m odds_tool.main scheduled-send --team 日本 --target oc_demo
```

说明：
- 默认只在北京时间 `08:00` 和 `21:00` 发送
- 由 `SCHEDULED_SEND_HOURS_BEIJING` 控制
- 仅支持整点小时
- 使用 24 小时制

## 二、macOS launchctl 部署

推荐让 `launchctl` 每小时触发一次，由程序内部判断是否到点发送。

### 1. 生成 LaunchAgent 文件

```bash
./install_launch_agent.sh 加拿大 oc_xxx
```

自定义缓存与状态文件：

```bash
./install_launch_agent.sh 加拿大 oc_xxx cache/odds_cache.json cache/scheduled_send_state.json
```

### 2. 加载服务

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

### 3. 立即触发一次

```bash
launchctl kickstart -k gui/$(id -u)/com.herry.sporttery-football-odds
```

### 4. 查看状态

```bash
launchctl print gui/$(id -u)/com.herry.sporttery-football-odds
```

### 5. 查看日志

```bash
tail -f logs/sporttery-football-odds.out.log logs/sporttery-football-odds.err.log
log stream --predicate 'process == "python" OR eventMessage CONTAINS "com.herry.sporttery-football-odds"' --style compact
```

### 6. 卸载

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

## 三、修改定时推送时间

修改文件：

```text
odds_tool/main.py
```

修改常量：

```python
SCHEDULED_SEND_HOURS_BEIJING = [8, 21]
```

例如改成：

```python
SCHEDULED_SEND_HOURS_BEIJING = [9, 18, 22]
```
