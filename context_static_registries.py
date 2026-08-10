import json
from pathlib import Path

class FrozenRegistry:
    def __init__(self,rows=None,key="key"):
        self.key=key
        self.rows={str(r[key]):dict(r) for r in (rows or [])}

    def get(self,k):
        return self.rows.get(str(k))

    @classmethod
    def from_json(cls,path,key="key"):
        p=Path(path)
        if not p.exists():
            return cls([],key=key)
        data=json.loads(p.read_text())
        rows=data if isinstance(data,list) else data.get("rows",[])
        return cls(rows,key=key)
