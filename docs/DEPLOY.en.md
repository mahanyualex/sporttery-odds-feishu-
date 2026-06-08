# Deployment Guide

> For users who want to run `sporttery-odds-feishu` long-term.

[Back to English README](../README.en.md) · [Install Guide](./INSTALL.en.md) · [中文部署文档](./DEPLOY.md)

## Deployment Options

This project supports two common run modes:
- run commands manually for ad-hoc query or debugging
- use macOS `launchctl` for long-running scheduled delivery

## 1. Run Manually

### One-off query

```bash
python -m odds_tool.main fetch --team Canada
```

### Watch odds changes for a team

```bash
python -m odds_tool.main watch-team --team Canada --interval 60 --target oc_xxx
```

### Scheduled send

```bash
python -m odds_tool.main scheduled-send --team Japan --target oc_demo
```

Notes:
- the default send windows are Beijing time `08:00` and `21:00`
- the schedule is controlled by `SCHEDULED_SEND_HOURS_BEIJING`
- only whole-hour windows are supported
- the tool uses a 24-hour clock

## 2. Deploy with macOS launchctl

Recommended pattern: let `launchctl` trigger once every hour, and let the program decide whether the current hour is a valid send slot.

### Generate the LaunchAgent file

```bash
./install_launch_agent.sh Canada oc_xxx
```

Custom cache and state paths:

```bash
./install_launch_agent.sh Canada oc_xxx cache/odds_cache.json cache/scheduled_send_state.json
```

### Load the service

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

### Trigger it immediately

```bash
launchctl kickstart -k gui/$(id -u)/com.herry.sporttery-football-odds
```

### Check status

```bash
launchctl print gui/$(id -u)/com.herry.sporttery-football-odds
```

### View logs

```bash
tail -f logs/sporttery-football-odds.out.log logs/sporttery-football-odds.err.log
log stream --predicate 'process == "python" OR eventMessage CONTAINS "com.herry.sporttery-football-odds"' --style compact
```

### Unload the service

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

## Change Scheduled Send Times

Modify this file:

```text
odds_tool/main.py
```

Edit this constant:

```python
SCHEDULED_SEND_HOURS_BEIJING = [8, 21]
```

Example:

```python
SCHEDULED_SEND_HOURS_BEIJING = [9, 18, 22]
```
