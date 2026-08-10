import json
from pathlib import Path
from venue_time_at_game import venue_offset_record

class FrozenRegistry:
    def __init__(self, rows=None, key="key"):
        self.key = key
        self.rows = {str(r[key]): dict(r) for r in (rows or [])}

    def get(self, k):
        return self.rows.get(str(k))

    def get_for_game_time(self, k, game_time_utc):
        row = self.get(k)
        if row is None:
            return None
        if row.get("timezone_id"):
            return venue_offset_record(row, game_time_utc)
        return row

    @classmethod
    def from_json(cls, path, key="key"):
        p = Path(path)
        if not p.exists():
            return cls([], key=key)
        data = json.loads(p.read_text())
        rows = data if isinstance(data, list) else data.get("rows", [])
        return cls(rows, key=key)
