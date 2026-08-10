import json
from pathlib import Path

from mlb_bulk_schedule_runtime import completed_games_chunked
from point_in_time_park_factor import build_point_in_time_records

HISTORY_START="2023-03-30"
TARGET_START="2025-03-27"
TARGET_END="2025-09-28"

MIN_EXPECTED_HISTORY_GAMES=4000
MIN_EXPECTED_TARGET_RECORDS=2000

def main():
    games,chunk_stats=completed_games_chunked(
        HISTORY_START,
        TARGET_END,
    )

    if len(games) < MIN_EXPECTED_HISTORY_GAMES:
        raise RuntimeError(
            f"historical schedule sanity check failed: "
            f"only {len(games)} completed games retrieved"
        )

    result=build_point_in_time_records(
        games,
        target_start_date=TARGET_START,
        target_end_date=TARGET_END,
    )

    if len(result["records"]) < MIN_EXPECTED_TARGET_RECORDS:
        raise RuntimeError(
            f"park-factor sanity check failed: "
            f"only {len(result['records'])} target records built"
        )

    payload={
        "version":"BT-0078",
        "status":"research_only",
        "history_start_date":HISTORY_START,
        "target_start_date":TARGET_START,
        "target_end_date":TARGET_END,
        "historical_completed_games":len(games),
        "chunk_stats":chunk_stats,
        "records":result["records"],
        "skipped":result["skipped"],
    }

    Path("park_factor_registry.json").write_text(
        json.dumps(payload,indent=2)
    )

    print(json.dumps({
        "historical_completed_games":len(games),
        "chunks":len(chunk_stats),
        "records":len(result["records"]),
        "skipped":len(result["skipped"]),
        "insufficient_prior":sum(
            1 for x in result["skipped"]
            if x["reason"]=="insufficient-prior-venue-games"
        ),
    },indent=2))

    return payload

if __name__=="__main__":
    main()
