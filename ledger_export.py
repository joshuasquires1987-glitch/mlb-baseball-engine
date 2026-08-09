import csv
from dataclasses import asdict
from pathlib import Path

def append_dataclass(path,obj):
    path=Path(path)
    row=asdict(obj)
    exists=path.exists() and path.stat().st_size>0
    with path.open("a",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(row.keys()))
        if not exists: w.writeheader()
        w.writerow(row)
