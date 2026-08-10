import json
from pathlib import Path

class PointInTimeParkRegistry:
    def __init__(self,records=None):
        self.by_game={}
        for r in records or []:
            self.by_game[str(r["game_pk"])]=dict(r)

    def get_for_game(self,game_pk,venue_id=None):
        r=self.by_game.get(str(game_pk))
        if r is None:
            return None
        if venue_id is not None and str(r.get("venue_id")) != str(venue_id):
            raise ValueError("park-factor venue mismatch")
        return dict(r)

    # Deliberately unsupported: a point-in-time park factor cannot safely
    # be retrieved by venue alone.
    def get(self,venue_id):
        return None

    @classmethod
    def from_json(cls,path):
        p=Path(path)
        if not p.exists():
            return cls()
        payload=json.loads(p.read_text())
        records=payload if isinstance(payload,list) else payload.get("records",[])
        return cls(records)
