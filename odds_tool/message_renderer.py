from typing import Any


def _format_change(label: str, values: dict[str, Any]) -> str:
    return f"{label} {values['old']} → {values['new']}"


def render_diff_message(snapshot: dict[str, Any], diff: dict[str, Any]) -> str:
    if "had" in snapshot or "hhad" in snapshot:
        lines = [
            "【竞彩足球赔率变动】",
            f"比赛：{snapshot['home_team']} vs {snapshot['away_team']}",
            f"场次：{snapshot.get('match_num', snapshot['match_id'])}",
            f"开赛：{snapshot['match_date']} {snapshot['match_time']}",
            "",
        ]

        if "had" in diff:
            lines.append("胜平负：")
            if "win" in diff["had"]:
                lines.append(_format_change("胜", diff["had"]["win"]))
            if "draw" in diff["had"]:
                lines.append(_format_change("平", diff["had"]["draw"]))
            if "lose" in diff["had"]:
                lines.append(_format_change("负", diff["had"]["lose"]))
            lines.append("")

        if "hhad" in diff:
            lines.append("让球胜平负：")
            if "goal_line" in diff["hhad"]:
                lines.append(f"让球 {diff['hhad']['goal_line']['old']} → {diff['hhad']['goal_line']['new']}")
            elif snapshot.get("hhad"):
                lines.append(f"让球 {snapshot['hhad']['goal_line']}")
            if "win" in diff["hhad"]:
                lines.append(_format_change("胜", diff["hhad"]["win"]))
            if "draw" in diff["hhad"]:
                lines.append(_format_change("平", diff["hhad"]["draw"]))
            if "lose" in diff["hhad"]:
                lines.append(_format_change("负", diff["hhad"]["lose"]))
            lines.append("")

        return "\n".join(line for line in lines).rstrip()

    lines = [
        "【竞彩篮球赔率变动】",
        f"比赛：{snapshot['away_team']} vs {snapshot['home_team']}",
        f"场次：{snapshot['match_id']}",
        f"开赛：{snapshot['match_time']}",
        "",
    ]

    if "mnl" in diff:
        lines.append("胜负：")
        if "home" in diff["mnl"]:
            lines.append(_format_change("主胜", diff["mnl"]["home"]))
        if "away" in diff["mnl"]:
            lines.append(_format_change("客胜", diff["mnl"]["away"]))
        lines.append("")

    if "hdc" in diff:
        lines.append("让分胜负：")
        if "goal_line" in diff["hdc"]:
            lines.append(f"让分 {diff['hdc']['goal_line']['old']} → {diff['hdc']['goal_line']['new']}")
        elif snapshot.get("hdc"):
            lines.append(f"让分 {snapshot['hdc']['goal_line']}")
        if "home" in diff["hdc"]:
            lines.append(_format_change("主胜", diff["hdc"]["home"]))
        if "away" in diff["hdc"]:
            lines.append(_format_change("客胜", diff["hdc"]["away"]))
        lines.append("")

    if "hilo" in diff:
        lines.append("大小分：")
        if "goal_line" in diff["hilo"]:
            lines.append(f"分数线 {diff['hilo']['goal_line']['old']} → {diff['hilo']['goal_line']['new']}")
        elif snapshot.get("hilo"):
            lines.append(str(snapshot["hilo"]["goal_line"]))
        if "high" in diff["hilo"]:
            lines.append(_format_change("大分", diff["hilo"]["high"]))
        if "low" in diff["hilo"]:
            lines.append(_format_change("小分", diff["hilo"]["low"]))
        lines.append("")

    return "\n".join(line for line in lines).rstrip()


def render_snapshot_message(snapshot: dict[str, Any]) -> str:
    if "had" in snapshot or "hhad" in snapshot:
        return "\n".join([
            "【竞彩足球当前赔率】",
            f"比赛：{snapshot['home_team']} vs {snapshot['away_team']}",
            f"场次：{snapshot.get('match_num', snapshot['match_id'])}",
            f"联赛：{snapshot['league']}",
            f"开赛：{snapshot['match_date']} {snapshot['match_time']}",
            "",
            f"胜平负：胜 {snapshot['had']['win']}，平 {snapshot['had']['draw']}，负 {snapshot['had']['lose']}",
            f"让球胜平负：让球 {snapshot['hhad']['goal_line']}，胜 {snapshot['hhad']['win']}，平 {snapshot['hhad']['draw']}，负 {snapshot['hhad']['lose']}",
        ])

    return "\n".join([
        "【竞彩篮球当前赔率】",
        f"比赛：{snapshot['away_team']} vs {snapshot['home_team']}",
        f"场次：{snapshot['match_id']}",
        f"开赛：{snapshot['match_time']}",
        "",
        f"胜负：主胜 {snapshot['mnl']['home']}，客胜 {snapshot['mnl']['away']}",
        f"让分胜负：让分 {snapshot['hdc']['goal_line']}，主胜 {snapshot['hdc']['home']}，客胜 {snapshot['hdc']['away']}",
        f"大小分：{snapshot['hilo']['goal_line']}，大分 {snapshot['hilo']['high']}，小分 {snapshot['hilo']['low']}",
    ])
