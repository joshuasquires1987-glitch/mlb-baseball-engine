from mlb_pregame_evidence import extract_pregame_evidence
from context_evidence_bridge import qualification_context_from_evidence
from evidence_integrity import apply_evidence_to_matchup_flags

def payload():
    away_order = list(range(1, 10))
    home_order = list(range(11, 20))
    players_a = {f"ID{x}": {"person": {"id": x}, "stats": {}} for x in away_order}
    players_h = {f"ID{x}": {"person": {"id": x}, "stats": {}} for x in home_order}
    players_a["ID640455"] = {"person": {"id": 640455}, "stats": {"pitching": {"gamesStarted": 1}}}
    players_h["ID683003"] = {"person": {"id": 683003}, "stats": {"pitching": {"gamesStarted": 1}}}
    return {
        "gameData": {
            "teams": {"away": {"abbreviation": "NYM"}, "home": {"abbreviation": "PIT"}},
            "venue": {"name": "PNC Park"},
            "weather": {"condition": "Partly Cloudy", "temp": 78, "wind": "8 mph, Out To RF"},
        },
        "liveData": {"boxscore": {"teams": {
            "away": {"battingOrder": away_order, "players": players_a, "pitchers": [640455]},
            "home": {"battingOrder": home_order, "players": players_h, "pitchers": [683003]},
        }}},
    }

def test_exact_evidence():
    e = extract_pregame_evidence(payload(), "123")
    assert e["lineup_confirmed"]
    assert e["venue_name"] == "PNC Park"
    assert e["away_starter_id"] == "640455"
    assert e["home_starter_id"] == "683003"

def test_integrity_flags_turn_green_for_matching_starters_and_lineups():
    e = extract_pregame_evidence(payload(), "123")
    f = apply_evidence_to_matchup_flags(e, "640455", "683003")
    assert f["away_starter_confirmed"]
    assert f["home_starter_confirmed"]
    assert f["lineup_confirmed"]
    assert f["weather_observation_available"]

def test_raw_evidence_does_not_verify_model_scores():
    e = extract_pregame_evidence(payload(), "123")
    c = qualification_context_from_evidence(e)
    assert c["park_score"] is None
    assert c["weather_score"] is None
    assert c["provenance"]["park_score"] == "unverified"
    assert c["provenance"]["weather_score"] == "unverified"
