#!/bin/bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "用法：./run_watch.sh <team> <interval_seconds> <chat_id> [cache_path]"
  echo "示例：./run_watch.sh 日本 60 oc_xxx"
  exit 1
fi

TEAM="$1"
INTERVAL="$2"
CHAT_ID="$3"
CACHE_PATH="${4:-cache/odds_cache.json}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p "$(dirname "$CACHE_PATH")"

exec python -m odds_tool.main watch-team \
  --team "$TEAM" \
  --interval "$INTERVAL" \
  --target "$CHAT_ID" \
  --cache "$CACHE_PATH"
