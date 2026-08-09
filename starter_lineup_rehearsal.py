import json
from pathlib import Path
from live_probable_sources import LiveProbable
from probable_resolution import resolve_probable_ids
from lineup_readiness import lineup_readiness

def load_probables(path):
    return [LiveProbable(**x) for x in json.loads(Path(path).read_text())]

def audit_probables(path,name_to_id=None,lineup_status=None):
    name_to_id=name_to_id or {}
    lineup_status=lineup_status or {}
    rows=[]
    for p in load_probables(path):
        resolved=resolve_probable_ids(p,name_to_id)
        l=lineup_status.get(p.game_key,(False,False))
        ready=lineup_readiness(*l)
        rows.append({
            "game_key":p.game_key,
            "both_probables_named":p.both_named,
            "starter_ids_resolved":resolved["resolution_complete"],
            "starter_integrity":resolved["starter_integrity"],
            "lineup_integrity":ready["lineup_integrity"],
            "model_ready":resolved["resolution_complete"],
            "bet_ready":resolved["resolution_complete"] and ready["both_confirmed"],
            "notes":p.notes,
        })
    return rows
