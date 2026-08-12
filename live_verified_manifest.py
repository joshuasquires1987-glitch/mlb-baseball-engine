from dataclasses import dataclass
from typing import Dict

from live_integrity import LiveIntegritySnapshot, assert_production_ready

REQUIRED_COMPONENTS = (
    "starter",
    "lineup",
    "bullpen",
    "weather",
    "roster_news",
)


@dataclass(frozen=True)
class VerifiedLiveManifest:
    game_pk: str
    verified_at_utc: str
    home_starter_id: str
    away_starter_id: str
    lights: Dict[str, str]
    evidence: Dict[str, str]
    context: Dict[str, float]

    def integrity_snapshot(self):
        return LiveIntegritySnapshot(
            game_pk=self.game_pk,
            starter=self.lights["starter"],
            lineup=self.lights["lineup"],
            bullpen=self.lights["bullpen"],
            weather=self.lights["weather"],
            roster_news=self.lights["roster_news"],
            umpire=self.lights.get("umpire", "yellow"),
        )


def parse_verified_manifest(payload):
    required = (
        "game_pk",
        "verified_at_utc",
        "home_starter_id",
        "away_starter_id",
        "lights",
        "evidence",
        "context",
    )
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError("manifest missing: " + ",".join(missing))

    lights = {str(k): str(v).lower() for k, v in dict(payload["lights"]).items()}
    evidence = {str(k): str(v).strip() for k, v in dict(payload["evidence"]).items()}
    context = {str(k): float(v) for k, v in dict(payload["context"]).items()}

    for component in REQUIRED_COMPONENTS:
        if component not in lights:
            raise ValueError(f"manifest lights missing {component}")
        if not evidence.get(component):
            raise ValueError(f"manifest evidence missing {component}")

    required_context = (
        "home_field_score",
        "park_score",
        "weather_score",
        "travel_rest_score",
        "platoon_score",
    )
    missing_context = [k for k in required_context if k not in context]
    if missing_context:
        raise ValueError("manifest context missing: " + ",".join(missing_context))

    manifest = VerifiedLiveManifest(
        game_pk=str(payload["game_pk"]),
        verified_at_utc=str(payload["verified_at_utc"]),
        home_starter_id=str(payload["home_starter_id"]),
        away_starter_id=str(payload["away_starter_id"]),
        lights=lights,
        evidence=evidence,
        context=context,
    )
    assert_production_ready(manifest.integrity_snapshot())
    return manifest


def assert_manifest_matches_slate(manifest, game):
    if str(game["game_pk"]) != manifest.game_pk:
        raise RuntimeError("manifest game_pk does not match live slate")
    if not game.get("home_probable_starter_id") or not game.get("away_probable_starter_id"):
        raise RuntimeError("live slate does not currently expose both probable starters")
    if str(game["home_probable_starter_id"]) != manifest.home_starter_id:
        raise RuntimeError("home starter changed; complete rerun required")
    if str(game["away_probable_starter_id"]) != manifest.away_starter_id:
        raise RuntimeError("away starter changed; complete rerun required")
    return True
