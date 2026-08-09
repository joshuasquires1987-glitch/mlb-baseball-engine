import json, hashlib
from pathlib import Path
from dataclasses import asdict,is_dataclass

def _jsonable(x):
    if is_dataclass(x): return {k:_jsonable(v) for k,v in asdict(x).items()}
    if isinstance(x,dict): return {str(k):_jsonable(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [_jsonable(v) for v in x]
    if hasattr(x,"isoformat"): return x.isoformat()
    if hasattr(x,"item"):
        try: return x.item()
        except Exception: pass
    return x

def write_probability_proof(path,game_key,target_date,result,coverage):
    payload={
        "game_key":game_key,
        "target_date":target_date,
        "coverage":_jsonable(coverage),
        "production":_jsonable(result["production"]),
        "shadow":_jsonable(result["shadow"]),
        "probabilities_frozen":bool(result["probabilities_frozen"]),
        "prices_seen":bool(result["prices_seen"]),
    }
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"))
    payload["sha256"]=hashlib.sha256(raw.encode()).hexdigest()
    Path(path).write_text(json.dumps(payload,indent=2))
    return payload
