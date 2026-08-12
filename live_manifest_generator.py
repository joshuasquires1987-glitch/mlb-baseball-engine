import argparse
import json
from pathlib import Path

from live_manifest_sources import (
    active_roster_ids,
    closest_hourly_weather,
    feed_venue_coordinates,
    fetch_external_json,
    fetched_at_utc,
    game_feed_url,
    lineup_from_feed,
    open_meteo_url,
    probable_starters_from_feed,
    recent_window,
    roster_url,
    transaction_count,
    transactions_url,
    venue_coordinates,
    venue_url,
)
from live_slate_runtime import live_slate


FROZEN_V11_CONTEXT = {
    "home_field_score": 0.10,
    "park_score": 0.0,
    "weather_score": 0.0,
    "travel_rest_score": 0.0,
    "platoon_score": 0.0,
}


def find_game(game_date, game_pk):
    rows = [g for g in live_slate(game_date) if str(g["game_pk"]) == str(game_pk)]
    if len(rows) != 1:
        raise RuntimeError(
            f"expected one slate game for game_pk={game_pk}; found {len(rows)}"
        )
    return rows[0]


def starter_evidence(schedule_game, feed_starters, secondary=None):
    schedule_home = schedule_game.get("home_probable_starter_id")
    schedule_away = schedule_game.get("away_probable_starter_id")
    feed_home = feed_starters["home"]["id"]
    feed_away = feed_starters["away"]["id"]

    official_complete = all([schedule_home, schedule_away, feed_home, feed_away])
    official_agree = (
        official_complete
        and str(schedule_home) == str(feed_home)
        and str(schedule_away) == str(feed_away)
    )

    secondary = secondary or {}
    secondary_home = secondary.get("home_starter_id")
    secondary_away = secondary.get("away_starter_id")
    secondary_source = secondary.get("source")
    secondary_complete = all([secondary_home, secondary_away, secondary_source])
    secondary_agree = (
        official_agree
        and secondary_complete
        and str(secondary_home) == str(schedule_home)
        and str(secondary_away) == str(schedule_away)
    )

    if secondary_agree:
        light = "green"
        note = (
            "MLB schedule/live-feed probable starters agree and a second reliable "
            "source independently confirms both starters."
        )
    elif official_agree:
        light = "yellow"
        note = (
            "MLB schedule and live feed agree, but no independent second-source "
            "starter confirmation was supplied."
        )
    else:
        light = "red"
        note = "Official MLB starter evidence is incomplete or internally conflicting."

    return {
        "light": light,
        "home_starter_id": str(schedule_home) if schedule_home else None,
        "away_starter_id": str(schedule_away) if schedule_away else None,
        "official_schedule_home": schedule_home,
        "official_schedule_away": schedule_away,
        "official_feed_home": feed_home,
        "official_feed_away": feed_away,
        "secondary": secondary if secondary else None,
        "note": note,
    }


def lineup_evidence(lineup):
    home = lineup.get("home") or []
    away = lineup.get("away") or []
    confirmed = len(home) == 9 and len(away) == 9
    return {
        "light": "green" if confirmed else "yellow",
        "home_batting_order": home,
        "away_batting_order": away,
        "note": (
            "MLB live-feed boxscore contains nine-player batting orders for both teams."
            if confirmed
            else "One or both official batting orders are not yet complete."
        ),
    }


def roster_evidence(home_roster, away_roster, home_tx, away_tx):
    home_ids = active_roster_ids(home_roster)
    away_ids = active_roster_ids(away_roster)
    complete = len(home_ids) >= 20 and len(away_ids) >= 20
    return {
        "light": "green" if complete else "yellow",
        "home_active_roster_count": len(home_ids),
        "away_active_roster_count": len(away_ids),
        "home_recent_transaction_count": transaction_count(home_tx),
        "away_recent_transaction_count": transaction_count(away_tx),
        "note": (
            "Official MLB active rosters loaded for both teams; recent MLB transactions "
            "captured for audit."
            if complete
            else "Official active roster evidence is incomplete."
        ),
    }


def weather_evidence(weather):
    if not weather:
        return {
            "light": "yellow",
            "forecast": None,
            "note": "Open-Meteo forecast unavailable.",
        }
    required = (
        weather.get("temperature_2m_c"),
        weather.get("relative_humidity_2m_pct"),
        weather.get("wind_speed_10m_kmh"),
        weather.get("wind_direction_10m_deg"),
    )
    complete = all(v is not None for v in required)
    return {
        "light": "green" if complete else "yellow",
        "forecast": weather,
        "note": (
            "Open-Meteo hourly forecast matched to scheduled first-pitch hour."
            if complete
            else "Open-Meteo forecast returned but material hourly fields are missing."
        ),
    }


def bullpen_evidence(home_roster, away_roster):
    home_ids = active_roster_ids(home_roster)
    away_ids = active_roster_ids(away_roster)
    complete = len(home_ids) >= 20 and len(away_ids) >= 20
    return {
        "light": "green" if complete else "yellow",
        "note": (
            "Official active-roster context is present; BT-0092 separately reconstructs "
            "bullpen performance/workload from prior completed MLB games."
            if complete
            else "Active-roster context is incomplete, so bullpen availability cannot be certified."
        ),
    }


def resolve_venue_coordinates(game, feed, venue_payload, venue_hydrated_payload=None):
    attempts = [
        ("mlb_venue", venue_coordinates(venue_payload)),
        ("mlb_live_feed", feed_venue_coordinates(feed)),
    ]
    if venue_hydrated_payload is not None:
        attempts.append(("mlb_venue_hydrated", venue_coordinates(venue_hydrated_payload)))

    for source, coords in attempts:
        if coords:
            return coords, source
    return None, None


def build_manifest_evidence(game_date, game_pk, secondary_starter=None):
    game = find_game(game_date, game_pk)
    observed_at = fetched_at_utc()

    feed_url = game_feed_url(game_pk)
    feed = fetch_external_json(feed_url)
    feed_starters = probable_starters_from_feed(feed)
    lineup = lineup_from_feed(feed)

    venue_primary_url = venue_url(game["venue_id"])
    venue_payload = fetch_external_json(venue_primary_url)

    coords, coords_source = resolve_venue_coordinates(game, feed, venue_payload)
    venue_hydrated_url = None
    if not coords:
        venue_hydrated_url = venue_url(game["venue_id"], hydrate=True)
        venue_hydrated_payload = fetch_external_json(venue_hydrated_url)
        coords, coords_source = resolve_venue_coordinates(
            game, feed, venue_payload, venue_hydrated_payload
        )

    weather = None
    weather_url = None
    if coords:
        weather_url = open_meteo_url(coords[0], coords[1], game_date)
        weather_payload = fetch_external_json(weather_url)
        weather = closest_hourly_weather(weather_payload, game["game_time_utc"])

    home_roster_url = roster_url(game["home_team_id"], game_date)
    away_roster_url = roster_url(game["away_team_id"], game_date)
    home_roster = fetch_external_json(home_roster_url)
    away_roster = fetch_external_json(away_roster_url)

    tx_start, tx_end = recent_window(game_date, days=7)
    home_tx_url = transactions_url(game["home_team_id"], tx_start, tx_end)
    away_tx_url = transactions_url(game["away_team_id"], tx_start, tx_end)
    home_tx = fetch_external_json(home_tx_url)
    away_tx = fetch_external_json(away_tx_url)

    starter = starter_evidence(game, feed_starters, secondary_starter)
    lineups = lineup_evidence(lineup)
    roster = roster_evidence(home_roster, away_roster, home_tx, away_tx)
    bullpen = bullpen_evidence(home_roster, away_roster)
    weather_ev = weather_evidence(weather)

    lights = {
        "starter": starter["light"],
        "lineup": lineups["light"],
        "bullpen": bullpen["light"],
        "weather": weather_ev["light"],
        "roster_news": roster["light"],
        "umpire": "yellow",
    }

    evidence_notes = {
        "starter": starter["note"],
        "lineup": lineups["note"],
        "bullpen": bullpen["note"],
        "weather": weather_ev["note"],
        "roster_news": roster["note"],
    }

    manifest = {
        "game_pk": str(game_pk),
        "verified_at_utc": observed_at,
        "home_starter_id": starter["home_starter_id"] or "",
        "away_starter_id": starter["away_starter_id"] or "",
        "lights": lights,
        "evidence": evidence_notes,
        "context": dict(FROZEN_V11_CONTEXT),
    }

    all_green = all(
        lights[k] == "green"
        for k in ("starter", "lineup", "bullpen", "weather", "roster_news")
    )

    return {
        "schema": "BT-0093a",
        "game": game,
        "observed_at_utc": observed_at,
        "integrity": {
            "starter": starter,
            "lineup": lineups,
            "bullpen": bullpen,
            "weather": weather_ev,
            "roster_news": roster,
            "umpire": {
                "light": "yellow",
                "note": "Optional/non-blocking; no umpire source collected.",
            },
        },
        "source_urls": {
            "mlb_live_feed": feed_url,
            "mlb_venue": venue_primary_url,
            "mlb_venue_hydrated": venue_hydrated_url,
            "open_meteo": weather_url,
            "home_active_roster": home_roster_url,
            "away_active_roster": away_roster_url,
            "home_transactions": home_tx_url,
            "away_transactions": away_tx_url,
        },
        "venue_coordinates": (
            {
                "latitude": coords[0],
                "longitude": coords[1],
                "source": coords_source,
            }
            if coords else None
        ),
        "context_raw": {
            "weather": weather,
            "venue_id": game.get("venue_id"),
            "venue_name": game.get("venue_name"),
            "travel_rest": {
                "status": "raw-schedule-reconstruction-deferred",
            },
            "park": {
                "status": "raw-venue-known-production-mapping-not-estimated",
            },
        },
        "production_context_policy": {
            "scores": dict(FROZEN_V11_CONTEXT),
            "reason": (
                "No validated production mapping exists yet for raw park/weather/"
                "travel context, so frozen v1.1 structural defaults are preserved."
            ),
        },
        "manifest": manifest,
        "manifest_ready_for_BT_0092": all_green,
        "prices_seen": False,
        "sportsbook_fields_present": False,
        "production_weights_changed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--game-pk", required=True)
    parser.add_argument("--secondary-starter-json")
    parser.add_argument("--report-output", default="live_evidence_report.json")
    parser.add_argument(
        "--manifest-output",
        default="live_verified_manifest.draft.json",
    )
    args = parser.parse_args()

    secondary = None
    if args.secondary_starter_json:
        secondary = json.loads(Path(args.secondary_starter_json).read_text())

    report = build_manifest_evidence(
        args.date, args.game_pk, secondary_starter=secondary
    )

    Path(args.report_output).write_text(json.dumps(report, indent=2))
    Path(args.manifest_output).write_text(json.dumps(report["manifest"], indent=2))

    verified_path = Path("live_verified_manifest.json")
    if verified_path.exists():
        verified_path.unlink()

    if report["manifest_ready_for_BT_0092"]:
        verified_path.write_text(json.dumps(report["manifest"], indent=2))

    print(json.dumps({
        "schema": report["schema"],
        "game_pk": report["game"]["game_pk"],
        "venue_coordinates": report["venue_coordinates"],
        "integrity_lights": report["manifest"]["lights"],
        "manifest_ready_for_BT_0092": report["manifest_ready_for_BT_0092"],
        "verified_manifest_written": verified_path.exists(),
        "prices_seen": report["prices_seen"],
    }, indent=2))


if __name__ == "__main__":
    main()
