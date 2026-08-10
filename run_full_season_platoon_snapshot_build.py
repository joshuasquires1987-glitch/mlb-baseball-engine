import json
from pathlib import Path
from full_season_platoon_snapshot_builder import load_jsonl,write_jsonl,build_all

INPUT="pregame_lineup_snapshots_raw.jsonl"
OUTPUT="pregame_lineup_snapshots.jsonl"
REPORT="pregame_lineup_snapshots_build_report.json"
MAX_WORKERS=16
MIN_EXPECTED_FINAL=2300

def main():
    raw=load_jsonl(INPUT)

    if len(raw) < 2400:
        raise RuntimeError(
            f"raw lineup sanity check failed: only {len(raw)} rows found"
        )

    final_rows,failures=build_all(raw,max_workers=MAX_WORKERS)

    if len(final_rows) < MIN_EXPECTED_FINAL:
        raise RuntimeError(
            f"final snapshot sanity check failed: only {len(final_rows)} rows enriched"
        )

    write_jsonl(final_rows,OUTPUT)

    reasons={}
    for x in failures:
        k=x["reason"]
        reasons[k]=reasons.get(k,0)+1

    deltas=[float(r["platoon_lineup_delta"]) for r in final_rows]

    report={
        "version":"BT-0082",
        "raw_rows":len(raw),
        "final_rows":len(final_rows),
        "failed_rows":len(failures),
        "success_rate":len(final_rows)/len(raw) if raw else 0.0,
        "failure_reasons":reasons,
        "delta_min":min(deltas) if deltas else None,
        "delta_max":max(deltas) if deltas else None,
        "delta_mean":sum(deltas)/len(deltas) if deltas else None,
        "policy":"same-timecoded-pregame-state-only",
        "future_performance_stats_used":False,
        "output_file":OUTPUT,
        "failures":failures,
    }

    Path(REPORT).write_text(json.dumps(report,indent=2))

    print(json.dumps({k:v for k,v in report.items() if k!="failures"},indent=2))
    return report

if __name__=="__main__":
    main()
