import json
from pathlib import Path
from game_log_importer import import_pitching_row

def load_snapshot(path):
    raw=json.loads(Path(path).read_text())
    return {
        pitcher:[
            import_pitching_row(
                x["date"],x["ip"],x["runs_allowed"],x.get("batters_faced"),
                x["source"]
            ) for x in rows
        ]
        for pitcher,rows in raw.items()
    }
