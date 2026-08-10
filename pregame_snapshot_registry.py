import json
from pathlib import Path

class PregameSnapshotRegistry:
    def __init__(self,rows=None):
        self._by_game={}
        for r in rows or []:
            self.add(r)

    def add(self,row):
        if row.get("captured_before_first_pitch") is not True:
            raise ValueError("snapshot must certify captured_before_first_pitch")
        if row.get("game_pk") is None:
            raise ValueError("snapshot missing game_pk")
        self._by_game[str(row["game_pk"])]=dict(row)

    def get(self,game_pk):
        return self._by_game.get(str(game_pk))

    @classmethod
    def from_jsonl(cls,path):
        rows=[]
        p=Path(path)
        if not p.exists():
            return cls()
        for line in p.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return cls(rows)
