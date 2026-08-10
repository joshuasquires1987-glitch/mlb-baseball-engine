from mlb_historical_timecode_runtime import fetch_json, timecoded_feed_url
from platoon_lineup_delta import platoon_lineup_delta
from timecoded_platoon_evidence import probable_starter_ids, player_map, lineup_bat_sides, starter_hand


def enrich_snapshot(snapshot, fetcher=fetch_json):
    state = fetcher(timecoded_feed_url(snapshot["game_pk"], snapshot["timecode"]))
    starters = probable_starter_ids(state)
    players = player_map(state)
    away_bats = lineup_bat_sides(snapshot["away_batting_order"], players)
    home_bats = lineup_bat_sides(snapshot["home_batting_order"], players)
    away_sp = starter_hand(starters["away"], players)
    home_sp = starter_hand(starters["home"], players)

    missing = []
    if starters["away"] is None: missing.append("away-probable-starter")
    if starters["home"] is None: missing.append("home-probable-starter")
    if away_sp is None: missing.append("away-starter-hand")
    if home_sp is None: missing.append("home-starter-hand")
    if away_bats is None: missing.append("away-lineup-bat-sides")
    if home_bats is None: missing.append("home-lineup-bat-sides")
    if missing:
        return None, {"game_pk": snapshot["game_pk"], "reason": "missing-timecoded-platoon-evidence", "missing": missing}

    delta = platoon_lineup_delta(home_bats, away_bats, home_sp, away_sp)
    return {
        **snapshot,
        "away_probable_starter_id": starters["away"],
        "home_probable_starter_id": starters["home"],
        "away_probable_starter_hand": away_sp,
        "home_probable_starter_hand": home_sp,
        "away_bat_sides": away_bats,
        "home_bat_sides": home_bats,
        "platoon_lineup_delta": delta,
        "platoon_feature_definition": "home advantageous-hitter share vs away SP minus away advantageous-hitter share vs home SP",
        "feature_status": "derived-from-certified-timecoded-pregame-evidence",
    }, None
