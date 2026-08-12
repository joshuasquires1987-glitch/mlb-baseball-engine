import json
from pathlib import Path

from live_slate_freezer import (
    all_required_green,
    eligible_preview_games,
    load_secondary_map,
    run_full_slate_freeze,
)


def game(pk, start, state="Preview"):
    return {
        "game_pk": str(pk),
        "game_date": "2026-08-13",
        "game_time_utc": start,
        "status_abstract": state,
        "home_team_name": f"H{pk}",
        "away_team_name": f"A{pk}",
    }


def evidence(pk, lights):
    return {
        "manifest": {
            "game_pk": str(pk),
            "lights": lights,
        }
    }


def test_eligible_preview_games_excludes_started_and_non_preview():
    games = [
        game(1, "2026-08-13T22:00:00Z", "Preview"),
        game(2, "2026-08-13T19:00:00Z", "Preview"),
        game(3, "2026-08-13T23:00:00Z", "Live"),
    ]
    out = eligible_preview_games(games, "2026-08-13T20:00:00Z")
    assert [g["game_pk"] for g in out] == ["1"]


def test_load_secondary_map_is_keyed_by_string_gamepk(tmp_path):
    p = tmp_path / "map.json"
    p.write_text(json.dumps({123: {"source": "x"}}))
    out = load_secondary_map(p)
    assert "123" in out


def test_all_required_green_ignores_optional_umpire():
    lights = {
        "starter": "green",
        "lineup": "green",
        "bullpen": "green",
        "weather": "green",
        "roster_news": "green",
        "umpire": "yellow",
    }
    assert all_required_green(evidence("1", lights)) is True


def test_full_slate_reconstructs_history_once_for_multiple_green_games(tmp_path):
    games = [
        game(1, "2026-08-13T22:00:00Z"),
        game(2, "2026-08-13T23:00:00Z"),
    ]

    lights = {
        "starter": "green",
        "lineup": "green",
        "bullpen": "green",
        "weather": "green",
        "roster_news": "green",
        "umpire": "yellow",
    }

    history_calls = []

    def history_fetcher(d):
        history_calls.append(d)
        return {
            "start_date": "2025-03-15",
            "end_date": "2026-08-12",
            "parsed_games": 4000,
            "pitching_rows": 30000,
        }

    def evidence_builder(d, pk, secondary_starter=None):
        return evidence(pk, lights)

    def freeze_builder(d, pk, manifest, history_fetcher):
        h = history_fetcher(d)
        assert h["parsed_games"] == 4000
        return {
            "probability_freeze": {
                "production": {
                    "model_version": "v1.1",
                    "home_win_probability": 0.55,
                    "away_win_probability": 0.45,
                    "confidence": 0.10,
                }
            }
        }

    report = run_full_slate_freeze(
        "2026-08-13",
        output_dir=tmp_path,
        slate_fetcher=lambda d: games,
        evidence_builder=evidence_builder,
        history_fetcher=history_fetcher,
        freeze_builder=freeze_builder,
        observed_at_utc="2026-08-13T20:00:00Z",
    )

    assert history_calls == ["2026-08-13"]
    assert report["frozen_games"] == 2
    assert report["history_reconstructed_once"] is True


def test_non_green_game_is_skipped_without_history_fetch(tmp_path):
    games = [game(1, "2026-08-13T22:00:00Z")]
    lights = {
        "starter": "yellow",
        "lineup": "green",
        "bullpen": "green",
        "weather": "green",
        "roster_news": "green",
    }

    called = {"history": 0}

    def history_fetcher(d):
        called["history"] += 1
        raise AssertionError("history should not be fetched")

    report = run_full_slate_freeze(
        "2026-08-13",
        output_dir=tmp_path,
        slate_fetcher=lambda d: games,
        evidence_builder=lambda d, pk, secondary_starter=None: evidence(pk, lights),
        history_fetcher=history_fetcher,
        observed_at_utc="2026-08-13T20:00:00Z",
    )

    assert report["frozen_games"] == 0
    assert called["history"] == 0
    assert report["games"][0]["status"] == "skipped"
    assert "starter" in report["games"][0]["reason"]


def test_no_market_fields_in_report(tmp_path):
    report = run_full_slate_freeze(
        "2026-08-13",
        output_dir=tmp_path,
        slate_fetcher=lambda d: [],
        observed_at_utc="2026-08-13T20:00:00Z",
    )
    assert report["prices_seen"] is False
    assert report["sportsbook_fields_present"] is False
    assert report["production_weights_changed"] is False
