#!/bin/bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "用法：./install_launch_agent.sh <team> <chat_id> [cache_path] [state_path]"
  echo "示例：./install_launch_agent.sh 日本 oc_xxx"
  exit 1
fi

TEAM="$1"
TARGET="$2"
CACHE_PATH="${3:-cache/odds_cache.json}"
STATE_PATH="${4:-cache/scheduled_send_state.json}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_PATH="$SCRIPT_DIR/launchd/com.herry.sporttery-football-odds.plist.template"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$SCRIPT_DIR/logs"
OUTPUT_PATH="$LAUNCH_AGENTS_DIR/com.herry.sporttery-football-odds.plist"
GUI_DOMAIN="gui/$(id -u)"

mkdir -p "$LAUNCH_AGENTS_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$SCRIPT_DIR/$(dirname "$CACHE_PATH")"
mkdir -p "$SCRIPT_DIR/$(dirname "$STATE_PATH")"

python3 - "$TEMPLATE_PATH" "$OUTPUT_PATH" "$SCRIPT_DIR" "$TEAM" "$TARGET" "$CACHE_PATH" "$STATE_PATH" "$LOG_DIR" <<'PY'
from pathlib import Path
import sys

(
    template_path,
    output_path,
    project_dir,
    team,
    target,
    cache_path,
    state_path,
    log_dir,
) = sys.argv[1:9]

content = Path(template_path).read_text(encoding="utf-8")
replacements = {
    "{{PROJECT_DIR}}": project_dir,
    "{{TEAM}}": team,
    "{{TARGET}}": target,
    "{{CACHE_PATH}}": cache_path,
    "{{STATE_PATH}}": state_path,
    "{{LOG_DIR}}": log_dir,
}
for old, new in replacements.items():
    content = content.replace(old, new)
Path(output_path).write_text(content, encoding="utf-8")
PY

chmod 644 "$OUTPUT_PATH"

echo "已生成 LaunchAgent: $OUTPUT_PATH"
echo "该配置会在每小时整点触发一次 run_scheduled_send.sh，并由程序内部判断是否到点发送。"
echo "安装/重载可执行："
echo "  launchctl bootout gui/$(id -u) $OUTPUT_PATH 2>/dev/null || true"
echo "  launchctl bootstrap gui/$(id -u) $OUTPUT_PATH"
echo "立即触发一次（可选）："
echo "  launchctl kickstart -k $GUI_DOMAIN/com.herry.sporttery-football-odds"
echo "查看状态："
echo "  launchctl print $GUI_DOMAIN/com.herry.sporttery-football-odds"
echo "查看日志："
echo "  tail -f $LOG_DIR/sporttery-football-odds.out.log $LOG_DIR/sporttery-football-odds.err.log"
echo "  log stream --predicate 'process == ""python"" OR eventMessage CONTAINS ""com.herry.sporttery-football-odds""' --style compact"
echo "卸载："
echo "  launchctl bootout $GUI_DOMAIN $OUTPUT_PATH"
