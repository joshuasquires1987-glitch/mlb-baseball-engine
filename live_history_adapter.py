from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import pandas as pd

from mlb_bulk_schedule_runtime import completed_games_chunked
from mlb_historical_timecode_runtime import fetch_json
from v11_historical_feed_parser import parse_final_feed

BASE = "https://statsapi.mlb.com/api/v1.1"
MAX_WORKERS = 16


def _final_feed_url(game_pk):
    return f"{BASE}/game/{game_pk}/feed/live"


def _fetch_parse(game):
    return parse_final_feed(game, fetch_json(_final_feed_url(game["game_pk"])))


def history_window(target_date, warmup_season_start=None):
    """
    Strict point-in-time window.

    Conservative live rule: do not use any same-calendar-day completed result,
    even if an earlier game finished before the target game's first pitch.
    """
    target = date.fromisoformat(str(target_date))
    end = target - timedelta(days=1)
    if warmup_season_start is None:
        start = date(target.year - 1, 3, 15)
    else:
        start = date.fromisoformat(str(warmup_season_start))
    if end < start:
        raise ValueError("history window is empty")
    return start.isoformat(), end.isoformat()


def fetch_live_history(target_date, warmup_season_start=None):
    start, end = history_window(target_date, warmup_season_start)
    games, chunks = completed_games_chunked(start, end)

    parsed = []
    failures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_fetch_parse, g): g for g in games}
        for i, fut in enumerate(as_completed(futures), 1):
            game = futures[fut]
            try:
                parsed.append(fut.result())
            except Exception as exc:
                failures.append({
                    "game_pk": str(game["game_pk"]),
                    "reason": f"{type(exc).__name__}:{str(exc)[:250]}",
                })
            if i % 250 == 0 or i == len(futures):
                print(
                    f"live-history feeds={i}/{len(futures)} "
                    f"parsed={len(parsed)} failures={len(failures)}",
                    flush=True,
                )

    if failures:
        raise RuntimeError(
            f"live history feed failures={len(failures)} examples={failures[:5]}"
        )

    pitching_rows = []
    game_rows = []
    for game in parsed:
        game_rows.append({
            "date": game["game_time_utc"],
            "hometeam": str(game["home_team_id"]),
            "visteam": str(game["away_team_id"]),
            "hruns": float(game["home_runs"]),
            "vruns": float(game["away_runs"]),
            "game_pk": str(game["game_pk"]),
        })
        for p in game.get("pitching_rows", []):
            pitching_rows.append({
                "date": game["game_time_utc"],
                "id": str(p["id"]),
                "team": str(p["team"]),
                "p_gs": int(p.get("p_gs", 0)),
                "p_bfp": float(p.get("p_bfp", 0)),
                "p_r": float(p.get("p_r", 0)),
                "p_ipouts": float(p.get("p_ipouts", 0)),
            })

    pitching_df = pd.DataFrame(
        pitching_rows,
        columns=["date", "id", "team", "p_gs", "p_bfp", "p_r", "p_ipouts"],
    )
    games_df = pd.DataFrame(
        game_rows,
        columns=["date", "hometeam", "visteam", "hruns", "vruns", "game_pk"],
    )

    return {
        "start_date": start,
        "end_date": end,
        "parsed_games": len(parsed),
        "pitching_rows": len(pitching_df),
        "schedule_chunks": chunks,
        "pitching_df": pitching_df,
        "games_df": games_df,
    }
