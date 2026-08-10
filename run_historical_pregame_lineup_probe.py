import json
from pathlib import Path

from mlb_bulk_schedule_runtime import completed_games
from mlb_historical_timecode_runtime import fetch_pregame_state
from historical_pregame_lineup_probe import probe_result,summarize

START="2025-03-27"
END="2025-09-28"
SAMPLE_SIZE=120

def stratified_sample(games,n=SAMPLE_SIZE):
    ordered=sorted(
        games,
        key=lambda g:(g.get("game_time_utc") or "",str(g["game_pk"])),
    )
    if len(ordered)<=n:
        return ordered
    step=len(ordered)/float(n)
    out=[]
    used=set()
    for i in range(n):
        idx=min(int(i*step),len(ordered)-1)
        g=ordered[idx]
        if g["game_pk"] not in used:
            used.add(g["game_pk"])
            out.append(g)
    return out

def main():
    games=completed_games(START,END)
    sample=stratified_sample(games)

    results=[]
    for i,g in enumerate(sample,1):
        try:
            payload=fetch_pregame_state(
                g["game_pk"],
                g["game_time_utc"],
                safety_seconds=60,
            )
            r=probe_result(g,payload)
        except Exception as e:
            r={
                "game_pk":str(g["game_pk"]),
                "game_date":g.get("game_date"),
                "recoverable":False,
                "reason":f"request-error:{type(e).__name__}",
            }
        results.append(r)
        print(f"[{i}/{len(sample)}] {g['game_pk']} {'PASS' if r['recoverable'] else r['reason']}")

    summary=summarize(results)
    Path("historical_pregame_lineup_probe.json").write_text(
        json.dumps({
            "version":"BT-0079",
            "sample_start":START,
            "sample_end":END,
            "sample_size":len(sample),
            "policy":"timecoded-state-before-scheduled-first-pitch-only",
            "summary":summary,
            "results":results,
        },indent=2)
    )
    print(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    main()
