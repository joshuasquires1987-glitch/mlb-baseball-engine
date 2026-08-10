import csv, json
from pathlib import Path
from context_calibration_schema import REQUIRED_FEATURES

FIELDNAMES=["game_id","game_date","home_win",*REQUIRED_FEATURES]

def write_jsonl(rows,path):
    p=Path(path)
    with p.open("w") as f:
        for r in rows:
            f.write(json.dumps(r,sort_keys=True)+"\n")
    return p

def write_csv(rows,path):
    p=Path(path)
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDNAMES)
        w.writeheader()
        for r in rows:
            w.writerow({k:r[k] for k in FIELDNAMES})
    return p
