import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from odds_tool.cache_store import JsonCacheStore
from odds_tool.diff_checker import diff_odds
from odds_tool.lark_notifier import LarkNotifier
from odds_tool.message_renderer import render_diff_message, render_snapshot_message
from odds_tool.odds_parser import parse_fixed_bonus_payload, parse_football_match_list_payload
from odds_tool.sporttery_client import NoMatchSaleError, SportteryClient


SCHEDULED_SEND_HOURS_BEIJING = [8, 21]
SCHEDULED_SEND_STATE_PATH = "cache/scheduled_send_state.json"
BEIJING_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _build_match_result(matches: list[dict[str, Any]]) -> dict[str, Any]:
    if not matches:
        return {"status": "not_found", "match": None}
    if len(matches) == 1:
        return {"status": "unique", "match": matches[0]}
    return {"status": "ambiguous", "matches": matches}


def _normalize_match_num(match_num: str) -> str:
    return re.sub(r"\s+", "", match_num or "")


def _normalize_query_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _render_match_block(match: dict[str, Any]) -> str:
    return "\n".join([
        f"场次：{match.get('match_num', match['match_id'])}",
        f"比赛：{match['home_team']} vs {match['away_team']}",
        f"联赛：{match['league']}",
        f"开赛：{match['match_date']} {match['match_time']}",
        f"胜平负：胜 {match['had']['win']}，平 {match['had']['draw']}，负 {match['had']['lose']}",
        (
            f"让球胜平负：让球 {match['hhad']['goal_line']}，胜 {match['hhad']['win']}，"
            f"平 {match['hhad']['draw']}，负 {match['hhad']['lose']}"
        ),
    ])


def render_multi_match_message(matches: list[dict[str, Any]], keyword: str, lookup_label: str) -> str:
    lines = [
        "【竞彩足球当前赔率】",
        f"查询关键词：{lookup_label} {keyword}",
        f"共匹配到 {len(matches)} 场比赛",
        "",
    ]
    for index, match in enumerate(matches, start=1):
        lines.append(f"[{index}]")
        lines.append(_render_match_block(match))
        if index != len(matches):
            lines.append("")
    return "\n".join(lines)


def parse_feishu_query_text(text: str) -> dict[str, str]:
    normalized_text = _normalize_query_text(text)
    if not normalized_text.startswith("查询"):
        return {"status": "ignored"}

    keyword = normalized_text[2:].strip()
    if not keyword:
        return {"status": "invalid", "error": "查询格式错误：请输入查询关键词"}

    if re.fullmatch(r"周[一二三四五六日天]\d{3}", keyword):
        return {"status": "ok", "lookup_type": "match_num", "lookup_value": keyword}

    return {"status": "ok", "lookup_type": "team", "lookup_value": keyword}


def find_match_by_team(matches: list[dict[str, Any]], team_keyword: str) -> dict[str, Any]:
    exact_matches = [
        match
        for match in matches
        if match.get("home_team") == team_keyword or match.get("away_team") == team_keyword
    ]
    if exact_matches:
        return _build_match_result(exact_matches)

    fuzzy_matches = [
        match
        for match in matches
        if team_keyword in (match.get("home_team") or "") or team_keyword in (match.get("away_team") or "")
    ]
    return _build_match_result(fuzzy_matches)


def find_match_by_match_num(matches: list[dict[str, Any]], match_num: str) -> dict[str, Any]:
    normalized_match_num = _normalize_match_num(match_num)
    matched = [
        match
        for match in matches
        if _normalize_match_num(str(match.get("match_num", ""))) == normalized_match_num
    ]
    return _build_match_result(matched)


def fetch_snapshot(match_id: int, client: SportteryClient | None = None) -> dict[str, Any]:
    actual_client = client or SportteryClient()
    payload = actual_client.fetch_fixed_bonus(match_id)
    return parse_fixed_bonus_payload(payload)


def fetch_today_matches(client: SportteryClient | None = None) -> list[dict[str, Any]]:
    actual_client = client or SportteryClient()
    payload = actual_client.fetch_football_match_list()
    return parse_football_match_list_payload(payload)


def _resolve_match(result: dict[str, Any], lookup_value: str, lookup_label: str) -> dict[str, Any]:
    status = result["status"]
    if status == "unique":
        return result["match"]
    if status == "ambiguous":
        match_nums = ", ".join(match.get("match_num", "") for match in result["matches"])
        raise ValueError(f"按{lookup_label} {lookup_value} 匹配到多场比赛：{match_nums}")
    raise ValueError(f"未找到{lookup_label}为 {lookup_value} 的比赛")


def fetch_by_team(team: str, client: SportteryClient | None = None) -> str:
    matches = fetch_today_matches(client)
    result = find_match_by_team(matches, team)
    if result["status"] == "ambiguous":
        return render_multi_match_message(result["matches"], team, "球队")
    match = _resolve_match(result, team, "球队")
    return render_snapshot_message(match)


def fetch_by_match_num(match_num: str, client: SportteryClient | None = None) -> str:
    matches = fetch_today_matches(client)
    result = find_match_by_match_num(matches, match_num)
    if result["status"] == "ambiguous":
        return render_multi_match_message(result["matches"], match_num, "场次")
    match = _resolve_match(result, match_num, "场次")
    return render_snapshot_message(match)


def handle_feishu_query_text(text: str) -> str | None:
    parsed = parse_feishu_query_text(text)
    status = parsed["status"]

    if status == "ignored":
        return None
    if status == "invalid":
        return parsed["error"]

    try:
        if parsed["lookup_type"] == "match_num":
            return fetch_by_match_num(parsed["lookup_value"])
        return fetch_by_team(parsed["lookup_value"])
    except NoMatchSaleError as exc:
        return str(exc)
    except ValueError as exc:
        return str(exc)
    except Exception:
        return "查询失败，请稍后重试"


def fetch_command(
    match_id: int | None = None,
    notify: bool = False,
    target: str | None = None,
    team: str | None = None,
    match_num: str | None = None,
) -> str:
    if team:
        message = fetch_by_team(team)
    elif match_num:
        message = fetch_by_match_num(match_num)
    elif match_id is not None:
        snapshot = fetch_snapshot(match_id)
        message = render_snapshot_message(snapshot)
    else:
        raise ValueError("fetch 命令至少需要提供 --team、--match-num 或 --match-id")
    if notify:
        if not target:
            raise ValueError("启用通知时必须提供 target")
        LarkNotifier().send_text(target, message)
    return message


def watch_once(
    match_id: int,
    target: str,
    store: JsonCacheStore,
    notifier: LarkNotifier,
    fetch_snapshot: Callable[[int], dict[str, Any]],
) -> bool:
    new_snapshot = fetch_snapshot(match_id)
    old_snapshot = store.get_snapshot(str(match_id))
    changed, diff = diff_odds(old_snapshot, new_snapshot)

    if old_snapshot is None:
        store.save_snapshot(str(match_id), new_snapshot)
        return False

    if changed:
        message = render_diff_message(new_snapshot, diff)
        notifier.send_text(target, message)
        store.save_snapshot(str(match_id), new_snapshot)
        return True

    return False


def watch_team_once(
    team: str,
    target: str,
    store: JsonCacheStore,
    notifier: LarkNotifier,
    fetch_today_matches: Callable[[], list[dict[str, Any]]],
) -> dict[str, Any]:
    matches = fetch_today_matches()
    result = find_match_by_team(matches, team)
    status = result["status"]
    if status == "not_found":
        return {"status": "not_found"}
    if status == "ambiguous":
        return {"status": "ambiguous", "matches": result["matches"]}

    cache_key = f"team::{team}"
    new_snapshot = result["match"]
    old_snapshot = store.get_snapshot(cache_key)
    changed, diff = diff_odds(old_snapshot, new_snapshot)

    if old_snapshot is None:
        store.save_snapshot(cache_key, new_snapshot)
        return {"status": "baseline_saved", "match": new_snapshot}

    if changed:
        notifier.send_text(target, render_diff_message(new_snapshot, diff))
        store.save_snapshot(cache_key, new_snapshot)
        return {"status": "changed", "match": new_snapshot, "diff": diff}

    return {"status": "unchanged", "match": new_snapshot}


def watch_team_loop(
    team: str,
    interval: int,
    target: str,
    cache_path: str,
    fetch_matches_func: Callable[[], list[dict[str, Any]]] | None = None,
) -> None:
    store = JsonCacheStore(Path(cache_path))
    notifier = LarkNotifier()
    actual_fetch_matches = fetch_matches_func or fetch_today_matches

    while True:
        watch_team_once(
            team=team,
            target=target,
            store=store,
            notifier=notifier,
            fetch_today_matches=actual_fetch_matches,
        )
        time.sleep(interval)


def notify_test(target: str) -> None:
    LarkNotifier().send_text(target, "【体彩赔率工具】飞书通知链路测试成功")


def get_beijing_now() -> datetime:
    return datetime.now(BEIJING_TIMEZONE)


def load_scheduled_send_state(path: str | Path) -> dict[str, Any]:
    state_path = Path(path)
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_scheduled_send_state(path: str | Path, state: dict[str, Any]) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def get_current_send_slot(now: datetime) -> str | None:
    beijing_now = now.astimezone(BEIJING_TIMEZONE)
    if beijing_now.minute != 0:
        return None
    return beijing_now.strftime("%Y-%m-%d-%H")


def should_send_in_current_slot(
    now: datetime,
    scheduled_hours: list[int],
    state: dict[str, Any],
) -> tuple[bool, str | None]:
    slot = get_current_send_slot(now)
    if slot is None:
        return False, None

    beijing_now = now.astimezone(BEIJING_TIMEZONE)
    if beijing_now.hour not in scheduled_hours:
        return False, None

    if state.get("last_sent_slot") == slot:
        return False, slot

    return True, slot


def scheduled_send_once(
    team: str,
    target: str,
    cache_path: str,
    state_path: str = SCHEDULED_SEND_STATE_PATH,
    notifier: LarkNotifier | None = None,
    now: datetime | None = None,
) -> None:
    del cache_path
    current_now = now or get_beijing_now()
    state = load_scheduled_send_state(state_path)
    should_send, slot = should_send_in_current_slot(current_now, SCHEDULED_SEND_HOURS_BEIJING, state)
    if not should_send or slot is None:
        return

    message = fetch_by_team(team)
    actual_notifier = notifier or LarkNotifier()
    actual_notifier.send_text(target, message)
    save_scheduled_send_state(state_path, {"last_sent_slot": slot})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="体彩竞彩足球赔率飞书通知工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("--match-id", type=int)
    fetch_parser.add_argument("--team")
    fetch_parser.add_argument("--match-num")
    fetch_parser.add_argument("--notify", action="store_true")
    fetch_parser.add_argument("--target")

    watch_parser = subparsers.add_parser("watch")
    watch_parser.add_argument("--match-id", type=str, required=True)
    watch_parser.add_argument("--interval", type=int, default=60)
    watch_parser.add_argument("--target", required=True)
    watch_parser.add_argument("--cache", default="cache/odds_cache.json")

    watch_team_parser = subparsers.add_parser("watch-team")
    watch_team_parser.add_argument("--team", required=True)
    watch_team_parser.add_argument("--interval", type=int, default=60)
    watch_team_parser.add_argument("--target", required=True)
    watch_team_parser.add_argument("--cache", default="cache/odds_cache.json")

    notify_parser = subparsers.add_parser("notify-test")
    notify_parser.add_argument("--target", required=True)

    feishu_query_parser = subparsers.add_parser("feishu-query")
    feishu_query_parser.add_argument("--text", required=True)

    scheduled_send_parser = subparsers.add_parser("scheduled-send")
    scheduled_send_parser.add_argument("--team", required=True)
    scheduled_send_parser.add_argument("--target", required=True)
    scheduled_send_parser.add_argument("--cache", default="cache/odds_cache.json")
    scheduled_send_parser.add_argument("--state", default=SCHEDULED_SEND_STATE_PATH)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fetch":
        print(
            fetch_command(
                match_id=args.match_id,
                team=args.team,
                match_num=args.match_num,
                notify=args.notify,
                target=args.target,
            )
        )
        return

    if args.command == "notify-test":
        notify_test(args.target)
        print("通知已发送")
        return

    if args.command == "feishu-query":
        response = handle_feishu_query_text(args.text)
        if response is not None:
            print(response)
        return

    if args.command == "scheduled-send":
        scheduled_send_once(
            team=args.team,
            target=args.target,
            cache_path=args.cache,
            state_path=args.state,
        )
        return

    if args.command == "watch":
        store = JsonCacheStore(Path(args.cache))
        notifier = LarkNotifier()
        match_ids = [int(item.strip()) for item in args.match_id.split(",") if item.strip()]
        while True:
            for match_id in match_ids:
                watch_once(
                    match_id=match_id,
                    target=args.target,
                    store=store,
                    notifier=notifier,
                    fetch_snapshot=lambda current_match_id: fetch_snapshot(current_match_id),
                )
            time.sleep(args.interval)

    if args.command == "watch-team":
        watch_team_loop(
            team=args.team,
            interval=args.interval,
            target=args.target,
            cache_path=args.cache,
        )


if __name__ == "__main__":
    main()
