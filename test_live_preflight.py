import live_preflight


def test_preflight_never_assumes_missing_integrity_is_green(monkeypatch):
    monkeypatch.setattr(
        live_preflight,
        "live_slate",
        lambda game_date: [{
            "game_pk": "123",
            "game_date": str(game_date),
            "game_time_utc": "2026-08-12T23:10:00Z",
            "home_probable_starter_id": "10",
            "away_probable_starter_id": "20",
        }],
    )
    report = live_preflight.build_preflight_report("2026-08-12")
    row = report["games"][0]
    assert row["production_ready"] is False
    assert set(row["blockers"]) == {
        "starter", "lineup", "bullpen", "weather", "roster_news"
    }
    assert report["prices_seen"] is False
    assert report["probability_generation_attempted"] is False
