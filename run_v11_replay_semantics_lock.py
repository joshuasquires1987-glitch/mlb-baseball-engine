import json
from pathlib import Path
from v11_replay_semantics import report

x=report()
Path("v11_replay_semantics_report.json").write_text(json.dumps(x,indent=2))
print(json.dumps(x,indent=2))
