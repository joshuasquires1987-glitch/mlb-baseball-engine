import json
from pathlib import Path
from historical_platoon_probe import enrich_snapshot

INPUT = "pregame_lineup_snapshots_raw.jsonl"
SAMPLE_SIZE = 120


def load_rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def sample(rows, n=SAMPLE_SIZE):
    if len(rows) <= n:
        return rows
    step = len(rows) / float(n)
    return [rows[min(int(i * step), len(rows) - 1)] for i in range(n)]


def main():
    rows = load_rows(INPUT)
    chosen = sample(rows)
    good, failures = [], []
    for i, row in enumerate(chosen, 1):
        try:
            enriched, err = enrich_snapshot(row)
        except Exception as e:
            enriched = None
            err = {"game_pk": row["game_pk"], "reason": f"request-error:{type(e).__name__}", "detail": str(e)[:300]}
        (good if enriched is not None else failures).append(enriched if enriched is not None else err)
        print(f"[{i}/{len(chosen)}] {row['game_pk']} {'PASS' if enriched else err['reason']}", flush=True)

    summary = {
        "version": "BT-0081",
        "games_probed": len(chosen),
        "fully_derivable": len(good),
        "derivable_rate": len(good) / len(chosen) if chosen else 0.0,
        "failures": failures,
        "feature_definition": "home advantageous-hitter share vs away pregame probable SP minus away advantageous-hitter share vs home pregame probable SP",
        "future_performance_stats_used": False,
    }
    Path("historical_platoon_delta_probe.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "failures"}, indent=2))
    return summary


if __name__ == "__main__":
    main()
