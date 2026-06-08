from typing import Any


def _record_change(section_diff: dict[str, dict[str, Any]], field: str, old_value: Any, new_value: Any) -> None:
    if old_value != new_value:
        section_diff[field] = {"old": old_value, "new": new_value}


def diff_odds(old_snapshot: dict[str, Any] | None, new_snapshot: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    if old_snapshot is None:
        return False, {"reason": "initial_baseline"}

    diff: dict[str, Any] = {}
    section_fields = {
        "had": ["win", "draw", "lose"],
        "hhad": ["goal_line", "win", "draw", "lose"],
        "mnl": ["home", "away"],
        "hdc": ["goal_line", "home", "away"],
        "hilo": ["goal_line", "high", "low"],
    }
    for section, fields in section_fields.items():
        old_section = old_snapshot.get(section)
        new_section = new_snapshot.get(section)
        if old_section is None or new_section is None:
            continue
        section_diff: dict[str, Any] = {}
        for field in fields:
            if field not in old_section or field not in new_section:
                continue
            _record_change(section_diff, field, old_section[field], new_section[field])
        if section_diff:
            diff[section] = section_diff

    return bool(diff), diff
