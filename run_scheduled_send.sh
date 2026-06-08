#!/bin/bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "用法：./run_scheduled_send.sh <team> <chat_id> [cache_path] [state_path]"
  echo "示例：./run_scheduled_send.sh 日本 oc_xxx"
  exit 1
fi

TEAM="$1"
CHAT_ID="$2"
CACHE_PATH="${3:-cache/odds_cache.json}"
STATE_PATH="${4:-cache/scheduled_send_state.json}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p "$(dirname "$CACHE_PATH")"
mkdir -p "$(dirname "$STATE_PATH")"

exec /usr/bin/env python3 -m odds_tool.main scheduled-send \
  --team "$TEAM" \
  --target "$CHAT_ID" \
  --cache "$CACHE_PATH" \
  --state "$STATE_PATH"
