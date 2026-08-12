import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from mlb_bulk_schedule_runtime import completed_games_chunked
from mlb_historical_timecode_runtime import fetch_json
from v11_historical_feed_parser import parse_final_feed
from v11_structural_replay import replay_2025

BASE = "https://statsapi.mlb.com/api/v1.1"
MAX_WORKERS = 16
MIN_EXPECTED = 2200

def final_feed_url(game_pk):
    return f"{BASE}/game/{game_pk}/feed/live"

def normalize_snapshot(row, line_number=None):
    """
    Adapt certified historical snapshot schema to the replay contract.

    BT-0080/BT-0082 snapshots store the scheduled timestamp as
    `scheduled_game_time_utc`. The structural replay consumes the canonical
    field `game_time_utc`. Preserve the original field and add the canonical
    alias rather than rewriting the historical artifact.
    """
    row = dict(row)
    if not row.get("game_time_utc"):
        scheduled = row.get("scheduled_game_time_utc")
        if scheduled:
            row["game_time_utc"] = scheduled

    required = (
        "game_pk",
        "game_date",
        "game_time_utc",
        "home_team_id",
        "away_team_id",
        "home_probable_starter_id",
        "away_probable_starter_id",
    )
    missing = [k for k in required if row.get(k) in (None, "")]
    if missing:
        where = f" on line {line_number}" if line_number is not None else ""
        raise ValueError(
            f"snapshot schema invalid{where}: missing {','.join(missing)}"
        )
    return row

def load_snapshots(path):
    rows = []
    for i, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            continue
        rows.append(normalize_snapshot(json.loads(line), line_number=i))
    return rows

def fetch_parse(game):
    return parse_final_feed(game, fetch_json(final_feed_url(game["game_pk"])))

def main():
    games, _ = completed_games_chunked("2024-03-20", "2025-09-28")
    snapshots = load_snapshots("pregame_lineup_snapshots.jsonl")
    target_pks = {str(x["game_pk"]) for x in snapshots}

    wanted = [
        g for g in games
        if str(g["game_date"]).startswith("2024") or str(g["game_pk"]) in target_pks
    ]

    parsed, fetch_failures = [], []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_parse, g): g for g in wanted}
        for i, fut in enumerate(as_completed(futures), 1):
            g = futures[fut]
            try:
                parsed.append(fut.result())
            except Exception as e:
                fetch_failures.append({
                    "game_pk": str(g["game_pk"]),
                    "reason": f"feed-error:{type(e).__name__}",
                    "detail": str(e)[:300],
                })
            if i % 100 == 0 or i == len(futures):
                print(
                    f"feeds={i}/{len(futures)} parsed={len(parsed)} "
                    f"failures={len(fetch_failures)}",
                    flush=True,
                )

    cfg = json.loads(Path("v1_1.json").read_text())
    rows, replay_failures = replay_2025(parsed, snapshots, cfg["weights"])

    if len(rows) < MIN_EXPECTED:
        raise RuntimeError(f"structural replay coverage failed: only {len(rows)} rows")

    with open("v11_structural_default_probability_ledger.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")

    report = {
        "version": "BT-0087",
        "baseline_label": "v1.1-structural-default-replay",
        "exact_historical_v11_probability": False,
        "2024_warmup_games": sum(
            str(g["game_date"]).startswith("2024") for g in parsed
        ),
        "target_snapshots": len(snapshots),
        "ledger_rows": len(rows),
        "feed_failures": len(fetch_failures),
        "replay_failures": len(replay_failures),
        "same_day_results_used": False,
        "snapshot_timestamp_contract": (
            "game_time_utc canonical; scheduled_game_time_utc accepted as "
            "certified historical alias"
        ),
        "context_defaults": {
            "home_field": 0.10,
            "park": 0.0,
            "weather": 0.0,
            "travel_rest_circadian": 0.0,
            "platoon_matchup_fit": 0.0,
        },
        "production_weights_changed": False,
        "fetch_failure_examples": fetch_failures[:25],
        "replay_failure_examples": replay_failures[:25],
    }
    Path("v11_structural_default_replay_report.json").write_text(
        json.dumps(report, indent=2)
    )
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
