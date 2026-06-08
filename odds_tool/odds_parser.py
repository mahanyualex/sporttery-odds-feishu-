import datetime as dt
from typing import Any

from odds_tool.models import FootballMatch


def _to_float(value: Any) -> float:
    return float(value)


def _combine_datetime(date_text: str, time_text: str) -> dt.datetime:
    return dt.datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M:%S")


def _extract_goal_line(market: dict[str, Any]) -> float:
    goal_line = market.get("goalLine")
    if goal_line is None:
        goal_line = market.get("goalLineValue")
    if goal_line is None:
        goal_line = market["fixedGoal"]
    return _to_float(goal_line)


def _build_odds_lookup(match: dict[str, Any]) -> dict[str, dict[str, Any]]:
    odds_lookup: dict[str, dict[str, Any]] = {}
    for odds in match.get("oddsList", []):
        pool_code = str(odds.get("poolCode", "")).upper()
        if pool_code:
            odds_lookup[pool_code] = odds
    return odds_lookup


def _resolve_market(match: dict[str, Any], market_key: str, pool_code: str) -> dict[str, Any]:
    market = match.get(market_key) or {}
    if market.get("h") is not None:
        return market
    odds_lookup = _build_odds_lookup(match)
    fallback = odds_lookup.get(pool_code, {})
    return fallback


def _pick_latest_market_entry(grouped_history: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    latest_entry: dict[str, Any] | None = None
    latest_dt: dt.datetime | None = None
    latest_goal_line: float | None = None
    for goal_line, entries in grouped_history.items():
        if not entries:
            continue
        candidate = entries[-1]
        candidate_dt = _combine_datetime(candidate["updateDate"], candidate["updateTime"])
        candidate_goal_line = _to_float(candidate["goalLine"])
        if latest_dt is None or candidate_dt > latest_dt:
            latest_entry = candidate
            latest_dt = candidate_dt
            latest_goal_line = candidate_goal_line
    if latest_entry is None or latest_goal_line is None:
        raise ValueError("盘口历史为空，无法提取最新赔率")
    return {"entry": latest_entry, "goal_line": latest_goal_line, "updated_at": latest_dt.strftime("%Y-%m-%d %H:%M:%S")}


def parse_fixed_bonus_payload(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload["value"]
    match_info = value["matchInfo"]
    odds_history = value["oddsHistory"]

    mnl_entry = odds_history["mnlList"][0]
    hdc_latest = _pick_latest_market_entry(odds_history["hdcList"])
    hilo_latest = _pick_latest_market_entry(odds_history["hiloList"])

    return {
        "match_id": int(match_info["matchId"]),
        "league": match_info["leagueAllName"],
        "match_time": match_info["matchDateTime"],
        "home_team": match_info["homeTeamAllName"],
        "away_team": match_info["awayTeamAllName"],
        "pool_status": match_info["poolStatus"],
        "mnl": {
            "home": _to_float(mnl_entry["h"]),
            "away": _to_float(mnl_entry["a"]),
            "updated_at": _combine_datetime(mnl_entry["updateDate"], mnl_entry["updateTime"]).strftime("%Y-%m-%d %H:%M:%S"),
        },
        "hdc": {
            "goal_line": hdc_latest["goal_line"],
            "home": _to_float(hdc_latest["entry"]["h"]),
            "away": _to_float(hdc_latest["entry"]["a"]),
            "updated_at": hdc_latest["updated_at"],
        },
        "hilo": {
            "goal_line": hilo_latest["goal_line"],
            "high": _to_float(hilo_latest["entry"]["h"]),
            "low": _to_float(hilo_latest["entry"]["l"]),
            "updated_at": hilo_latest["updated_at"],
        },
    }


def parse_football_match_list_payload(payload: dict[str, Any]) -> list[FootballMatch]:
    matches: list[FootballMatch] = []
    for day_group in payload["value"]["matchInfoList"]:
        business_date = day_group["businessDate"]
        for match in day_group["subMatchList"]:
            had = _resolve_market(match, "had", "HAD")
            hhad = _resolve_market(match, "hhad", "HHAD")
            if had.get("h") is None or hhad.get("h") is None:
                continue
            matches.append(
                {
                    "business_date": business_date,
                    "match_id": int(match["matchId"]),
                    "match_num": match["matchNumStr"],
                    "league": match["leagueAllName"],
                    "home_team": match["homeTeamAllName"],
                    "away_team": match["awayTeamAllName"],
                    "match_date": match["matchDate"],
                    "match_time": match["matchTime"],
                    "match_status": match["matchStatus"],
                    "had": {
                        "win": _to_float(had["h"]),
                        "draw": _to_float(had["d"]),
                        "lose": _to_float(had["a"]),
                        "updated_at": _combine_datetime(had["updateDate"], had["updateTime"]).strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    "hhad": {
                        "goal_line": _extract_goal_line(hhad),
                        "win": _to_float(hhad["h"]),
                        "draw": _to_float(hhad["d"]),
                        "lose": _to_float(hhad["a"]),
                        "updated_at": _combine_datetime(hhad["updateDate"], hhad["updateTime"]).strftime("%Y-%m-%d %H:%M:%S"),
                    },
                }
            )
    return matches
