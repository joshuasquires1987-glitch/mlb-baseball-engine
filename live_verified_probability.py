import argparse
import json
from pathlib import Path

import pandas as pd

from assembler_pipeline import AssemblerPipeline
from live_history_adapter import fetch_live_history
from live_probability_freeze import freeze_probability
from live_slate_runtime import live_slate
from live_verified_manifest import (
    assert_manifest_matches_slate,
    parse_verified_manifest,
)
from matchup_definition import MatchupDefinition


def _find_game(game_date, game_pk):
    games = live_slate(game_date)
    matches = [g for g in games if str(g["game_pk"]) == str(game_pk)]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one live slate game for game_pk={game_pk}; "
            f"found {len(matches)}"
        )
    return matches[0]


def build_live_probability_freeze(
    game_date,
    game_pk,
    manifest_payload,
    repo_root=".",
    history_fetcher=fetch_live_history,
):
    game = _find_game(game_date, game_pk)
    manifest = parse_verified_manifest(manifest_payload)
    assert_manifest_matches_slate(manifest, game)

    history = history_fetcher(game_date)
    pitching_df = history["pitching_df"]
    games_df = history["games_df"]

    c = manifest.context
    matchup = MatchupDefinition(
        game_id=str(game["game_pk"]),
        game_date=pd.Timestamp(game["game_time_utc"]),
        home_team=str(game["home_team_id"]),
        away_team=str(game["away_team_id"]),
        home_starter_id=manifest.home_starter_id,
        away_starter_id=manifest.away_starter_id,
        home_starter_confirmed=True,
        away_starter_confirmed=True,
        lineup_confirmed=True,
        bullpen_current=True,
        weather_current=True,
        roster_news_clear=True,
        home_field_score=c["home_field_score"],
        park_score=c["park_score"],
        weather_score=c["weather_score"],
        travel_rest_score=c["travel_rest_score"],
        platoon_score=c["platoon_score"],
        umpire_known=manifest.lights.get("umpire", "yellow") == "green",
    )

    facts, model_inputs = AssemblerPipeline().build_inputs(
        matchup, pitching_df, games_df
    )

    if model_inputs.integrity.unresolved_red():
        raise RuntimeError("model inputs contain unresolved RED integrity")
    required_lights = (
        model_inputs.integrity.starter,
        model_inputs.integrity.lineup,
        model_inputs.integrity.bullpen,
        model_inputs.integrity.weather,
        model_inputs.integrity.roster_news,
    )
    if any(str(x).lower() != "green" for x in required_lights):
        raise RuntimeError("model input integrity is not fully GREEN")

    frozen = freeze_probability(model_inputs, repo_root=repo_root)

    return {
        "schema": "BT-0092",
        "game": game,
        "manifest": {
            "game_pk": manifest.game_pk,
            "verified_at_utc": manifest.verified_at_utc,
            "home_starter_id": manifest.home_starter_id,
            "away_starter_id": manifest.away_starter_id,
            "lights": manifest.lights,
            "evidence": manifest.evidence,
            "context": manifest.context,
        },
        "history": {
            "start_date": history["start_date"],
            "end_date": history["end_date"],
            "parsed_games": history["parsed_games"],
            "pitching_rows": history["pitching_rows"],
            "same_day_results_used": False,
        },
        "model_inputs": {
            "game_id": model_inputs.game_id,
            "game_date": model_inputs.game_date,
            "home_team": model_inputs.home_team,
            "away_team": model_inputs.away_team,
            "features": model_inputs.features,
            "integrity": model_inputs.integrity.__dict__,
        },
        "probability_freeze": frozen,
        "prices_seen": False,
        "sportsbook_fields_present": False,
        "production_weights_changed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--game-pk", required=True)
    parser.add_argument(
        "--manifest-json",
        required=True,
        help="Path to verified live integrity/context manifest JSON.",
    )
    parser.add_argument(
        "--output",
        default="live_probability_freeze.json",
    )
    args = parser.parse_args()

    manifest_payload = json.loads(Path(args.manifest_json).read_text())
    report = build_live_probability_freeze(
        args.date,
        args.game_pk,
        manifest_payload,
    )
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(json.dumps({
        "schema": report["schema"],
        "game_pk": report["game"]["game_pk"],
        "production": report["probability_freeze"]["production"],
        "probabilities_frozen": report["probability_freeze"]["probabilities_frozen"],
        "prices_seen": report["prices_seen"],
        "history": report["history"],
    }, indent=2))


if __name__ == "__main__":
    main()
