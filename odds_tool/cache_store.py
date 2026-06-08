import json
from pathlib import Path
from typing import Any


class JsonCacheStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get_snapshot(self, match_id: str) -> dict[str, Any] | None:
        return self.load_all().get(str(match_id))

    def save_snapshot(self, match_id: str, snapshot: dict[str, Any]) -> None:
        data = self.load_all()
        data[str(match_id)] = snapshot
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self.path)
