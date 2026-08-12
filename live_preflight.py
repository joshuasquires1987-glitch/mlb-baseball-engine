import json
from pathlib import Path

from live_integrity import LiveIntegritySnapshot, assert_production_ready
from live_slate_runtime import live_slate


def build_preflight_report(game_date, integrity_by_game=None):
    integrity_by_game = integrity_by_game or {}
    games = live_slate(game_date)
    rows = []

    for game in games:
        game_pk = game["game_pk"]
        supplied = integrity_by_game.get(game_pk)

        if supplied is None:
            # Unknown live inputs are YELLOW, never silently assumed current.
            snapshot = LiveIntegritySnapshot(
                game_pk=game_pk,
                starter=(
                    "yellow"
                    if not (
                        game.get("home_probable_starter_id")
                        and game.get("away_probable_starter_id")
                    )
                    else "yellow"
                ),
                lineup="yellow",
                bullpen="yellow",
                weather="yellow",
                roster_news="yellow",
                umpire="yellow",
            )
        else:
            snapshot = LiveIntegritySnapshot(game_pk=game_pk, **supplied)

        rows.append({
            **game,
            "integrity": snapshot.required_components(),
            "production_ready": snapshot.production_ready(),
            "blockers": snapshot.blockers(),
        })

    return {
        "schema": "BT-0091",
        "game_date": str(game_date),
        "games": rows,
        "production_ready_games": sum(r["production_ready"] for r in rows),
        "total_games": len(rows),
        "probability_generation_attempted": False,
        "prices_seen": False,
        "note": (
            "Preflight only. A game must receive explicit GREEN values for "
            "starter, lineup, bullpen, weather, and roster_news before the "
            "production probability boundary may be called."
        ),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument(
        "--integrity-json",
        help="Optional JSON file keyed by game_pk with integrity light values.",
    )
    parser.add_argument(
        "--output",
        default="live_preflight_report.json",
    )
    args = parser.parse_args()

    integrity = {}
    if args.integrity_json:
        integrity = json.loads(Path(args.integrity_json).read_text())

    report = build_preflight_report(args.date, integrity)
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
