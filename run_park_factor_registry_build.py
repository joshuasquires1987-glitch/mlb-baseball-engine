import json
from pathlib import Path
from mlb_bulk_schedule_runtime import completed_games
from point_in_time_park_factor import build_point_in_time_records

HISTORY_START="2023-03-30"
TARGET_START="2025-03-27"
TARGET_END="2025-09-28"

def main():
    games=completed_games(HISTORY_START,TARGET_END)
    result=build_point_in_time_records(
        games,
        target_start_date=TARGET_START,
        target_end_date=TARGET_END,
    )
    payload={
        "version":"BT-0077",
        "status":"research_only",
        "target_start_date":TARGET_START,
        "target_end_date":TARGET_END,
        "records":result["records"],
        "skipped":result["skipped"],
    }
    Path("park_factor_registry.json").write_text(json.dumps(payload,indent=2))
    print(json.dumps({
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
