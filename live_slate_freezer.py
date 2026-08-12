import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from live_history_adapter import fetch_live_history
from live_manifest_generator import build_manifest_evidence
from live_slate_runtime import live_slate
from live_verified_probability import build_live_probability_freeze

REQUIRED_GREEN = ("starter", "lineup", "bullpen", "weather", "roster_news")


def _dt(value):
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def eligible_preview_games(games, observed_at_utc=None):
    """
    Only future, not-yet-started games may enter the slate freeze.
    No live/in-progress/final game is ever eligible.
    """
    observed = (
        _dt(observed_at_utc)
        if observed_at_utc
        else datetime.now(timezone.utc)
    )
    rows = []
    for game in games:
        if str(game.get("status_abstract") or "").lower() != "preview":
            continue
        start = game.get("game_time_utc")
        if not start:
            continue
        if _dt(start) <= observed:
            continue
        rows.append(game)
    return sorted(rows, key=lambda g: (g["game_time_utc"], g["game_pk"]))


def load_secondary_map(path=None):
    if not path:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("secondary starter confirmation map must be a JSON object")
    return {str(k): v for k, v in payload.items()}


def required_lights(report):
    lights = report["manifest"]["lights"]
    return {name: str(lights.get(name, "yellow")).lower() for name in REQUIRED_GREEN}


def all_required_green(report):
    return all(v == "green" for v in required_lights(report).values())


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def run_full_slate_freeze(
    game_date,
    secondary_map=None,
    output_dir="live_slate_artifacts",
    slate_fetcher=live_slate,
    evidence_builder=build_manifest_evidence,
    history_fetcher=fetch_live_history,
    freeze_builder=build_live_probability_freeze,
    observed_at_utc=None,
):
    secondary_map = secondary_map or {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    observed = (
        observed_at_utc
        or datetime.now(timezone.utc).isoformat()
    )
    full_slate = slate_fetcher(game_date)
    eligible = eligible_preview_games(full_slate, observed)

    rows = []
    green_candidates = []

    for game in eligible:
        game_pk = str(game["game_pk"])
        secondary = secondary_map.get(game_pk)

        try:
            evidence = evidence_builder(
                game_date,
                game_pk,
                secondary_starter=secondary,
            )
        except Exception as exc:
            rows.append({
                "game_pk": game_pk,
                "game_time_utc": game.get("game_time_utc"),
                "home_team": game.get("home_team_name"),
                "away_team": game.get("away_team_name"),
                "stage": "evidence",
                "status": "error",
                "reason": f"{type(exc).__name__}:{str(exc)[:500]}",
                "prices_seen": False,
            })
            continue

        write_json(output_dir / f"evidence_{game_pk}.json", evidence)

        lights = required_lights(evidence)
        row = {
            "game_pk": game_pk,
            "game_time_utc": game.get("game_time_utc"),
            "home_team": game.get("home_team_name"),
            "away_team": game.get("away_team_name"),
            "integrity_lights": lights,
            "secondary_starter_confirmation_present": secondary is not None,
            "prices_seen": False,
        }

        if all_required_green(evidence):
            write_json(
                output_dir / f"manifest_{game_pk}.json",
                evidence["manifest"],
            )
            row.update({
                "stage": "integrity",
                "status": "green_candidate",
                "reason": None,
            })
            green_candidates.append((game, evidence, row))
        else:
            blockers = [k for k, v in lights.items() if v != "green"]
            row.update({
                "stage": "integrity",
                "status": "skipped",
                "reason": "non-green:" + ",".join(blockers),
            })
            rows.append(row)

    history = None
    if green_candidates:
        # One point-in-time reconstruction shared by every GREEN candidate.
        history = history_fetcher(game_date)

    pipeline_errors = []
    frozen_count = 0

    for game, evidence, row in green_candidates:
        game_pk = str(game["game_pk"])
        try:
            frozen = freeze_builder(
                game_date,
                game_pk,
                evidence["manifest"],
                history_fetcher=lambda _: history,
            )
            write_json(output_dir / f"freeze_{game_pk}.json", frozen)
            prod = frozen["probability_freeze"]["production"]
            row.update({
                "stage": "freeze",
                "status": "frozen",
                "reason": None,
                "production_model_version": prod["model_version"],
                "home_win_probability": prod["home_win_probability"],
                "away_win_probability": prod["away_win_probability"],
                "confidence": prod["confidence"],
                "probabilities_frozen": True,
            })
            frozen_count += 1
        except Exception as exc:
            reason = f"{type(exc).__name__}:{str(exc)[:500]}"
            row.update({
                "stage": "freeze",
                "status": "error",
                "reason": reason,
                "probabilities_frozen": False,
            })
            pipeline_errors.append({
                "game_pk": game_pk,
                "reason": reason,
            })
        rows.append(row)

    # Include non-preview slate games in counts, but never model them.
    summary = {
        "schema": "BT-0094",
        "game_date": str(game_date),
        "observed_at_utc": observed,
        "total_slate_games": len(full_slate),
        "eligible_future_preview_games": len(eligible),
        "green_candidates": len(green_candidates),
        "frozen_games": frozen_count,
        "skipped_or_evidence_error_games": len(eligible) - frozen_count,
        "history_reconstructed_once": bool(green_candidates),
        "history": (
            {
                "start_date": history["start_date"],
                "end_date": history["end_date"],
                "parsed_games": history["parsed_games"],
                "pitching_rows": history["pitching_rows"],
                "same_day_results_used": False,
            }
            if history is not None
            else None
        ),
        "pipeline_errors": pipeline_errors,
        "prices_seen": False,
        "sportsbook_fields_present": False,
        "production_weights_changed": False,
        "games": sorted(rows, key=lambda r: (r.get("game_time_utc") or "", r["game_pk"])),
    }
    write_json(output_dir / "live_slate_freeze_report.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument(
        "--secondary-starter-map",
        help=(
            "Optional JSON object keyed by gamePk. Each value contains "
            "home_starter_id, away_starter_id, and independent source note."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="live_slate_artifacts",
    )
    args = parser.parse_args()

    secondary = load_secondary_map(args.secondary_starter_map)
    report = run_full_slate_freeze(
        args.date,
        secondary_map=secondary,
        output_dir=args.output_dir,
    )

    print(json.dumps({
        "schema": report["schema"],
        "game_date": report["game_date"],
        "total_slate_games": report["total_slate_games"],
        "eligible_future_preview_games": report["eligible_future_preview_games"],
        "green_candidates": report["green_candidates"],
        "frozen_games": report["frozen_games"],
        "pipeline_error_count": len(report["pipeline_errors"]),
        "prices_seen": report["prices_seen"],
    }, indent=2))

    # A GREEN game failing the probability boundary is an infrastructure error.
    if report["pipeline_errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
