from dataclasses import dataclass
@dataclass(frozen=True)
class HistoryAttachment:
    player_id:str; season:int; rows:list; source_url:str; fetched_at_utc:str
    @property
    def usable(self): return bool(self.player_id and self.rows)

def attach_histories(probable_rows,registry,history_lookup):
    out=[]
    for row in probable_rows:
        aid=registry.resolve(row.get("away_pitcher_name")); hid=registry.resolve(row.get("home_pitcher_name"))
        ah=history_lookup(aid) if aid else None; hh=history_lookup(hid) if hid else None
        out.append({**row,"away_pitcher_id":aid,"home_pitcher_id":hid,
                    "away_history_attached":bool(ah and ah.usable),"home_history_attached":bool(hh and hh.usable),
                    "starter_integrity":"green" if aid and hid and ah and hh and ah.usable and hh.usable else "red"})
    return out
