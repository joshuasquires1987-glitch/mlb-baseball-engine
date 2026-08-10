import json
from pathlib import Path
from mlb_bulk_schedule_runtime import completed_games
from historical_pregame_lineup_builder import build_all,write_jsonl

START="2025-03-27"
END="2025-09-28"
MAX_WORKERS=16
MIN_EXPECTED_RECOVERED=2000

def main():
    games=completed_games(START,END)
    if len(games) < 2400:
        raise RuntimeError(f"schedule sanity check failed: only {len(games)} games retrieved")
    rows,failures=build_all(games,max_workers=MAX_WORKERS,safety_seconds=60)
    if len(rows) < MIN_EXPECTED_RECOVERED:
        raise RuntimeError(f"lineup recovery sanity check failed: only {len(rows)} games recovered")
    write_jsonl(rows,"pregame_lineup_snapshots_raw.jsonl")
    summary={
        "version":"BT-0080",
        "games_considered":len(games),
        "recovered_lineups":len(rows),
        "failed_games":len(failures),
        "recovery_rate":len(rows)/len(games) if games else 0.0,
        "max_workers":MAX_WORKERS,
        "policy":"historical-MLB-timecode-only; no completed-lineup fallback",
        "feature_status":"raw-certified-lineups; platoon_lineup_delta not yet derived",
        "failure_reasons":{},
        "failures":failures,
    }
    for x in failures:
        k=x["reason"]; summary["failure_reasons"][k]=summary["failure_reasons"].get(k,0)+1
    Path("pregame_lineup_snapshot_build_report.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!="failures"},indent=2))
    return summary

if __name__=="__main__":
    main()
