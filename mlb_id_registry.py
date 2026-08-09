import json
from pathlib import Path
def normalize_name(name): return " ".join(str(name).replace("’","'").strip().lower().split())
class MLBPlayerIDRegistry:
    def __init__(self,mapping): self.mapping={normalize_name(k):(str(v) if v is not None else None) for k,v in mapping.items()}
    @classmethod
    def from_json(cls,path): return cls(json.loads(Path(path).read_text()))
    def resolve(self,name): return None if name is None else self.mapping.get(normalize_name(name))
