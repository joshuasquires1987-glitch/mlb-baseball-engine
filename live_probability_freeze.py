import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone

from probability_only_runner import ProbabilityOnlyRunner


def _jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def fingerprint_model_inputs(model_inputs):
    payload = _jsonable(model_inputs)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def freeze_probability(model_inputs, repo_root="."):
    result = ProbabilityOnlyRunner(repo_root).predict(model_inputs)
    prod = result["production"]
    shadow = result["shadow"]

    return {
        "freeze_schema": "BT-0091",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "game_id": prod.game_id,
        "production": {
            "model_version": prod.model_version,
            "home_win_probability": prod.home_win_probability,
            "away_win_probability": prod.away_win_probability,
            "confidence": prod.confidence,
            "frozen": prod.frozen,
        },
        "shadow": {
            "model_version": shadow.model_version,
            "home_win_probability": shadow.home_win_probability,
            "away_win_probability": shadow.away_win_probability,
            "confidence": shadow.confidence,
            "frozen": shadow.frozen,
            "controls_bets": False,
            "controls_stakes": False,
        },
        "integrity": _jsonable(prod.integrity),
        "model_inputs_sha256": fingerprint_model_inputs(model_inputs),
        "probabilities_frozen": True,
        "prices_seen": False,
        "sportsbook_fields_present": False,
        "production_weights_changed": False,
    }
