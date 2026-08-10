from dataclasses import dataclass

V11_FEATURE_SEMANTICS = {
    "starting_pitcher": {
        "source": "PregameFeatureBuilder",
        "derivation": "advantage(home starter talent_score, away starter talent_score)",
        "historically_replayable_from_repo_calculators": True,
    },
    "underlying_team_strength": {
        "source": "PregameFeatureBuilder",
        "derivation": "advantage(home team_strength, away team_strength)",
        "historically_replayable_from_repo_calculators": True,
    },
    "bullpen": {
        "source": "PregameFeatureBuilder",
        "derivation": "advantage(home bullpen_score, away bullpen_score)",
        "historically_replayable_from_repo_calculators": True,
    },
    "confirmed_lineup_offense": {
        "source": "PregameFeatureBuilder",
        "derivation": "advantage(home TeamState.offense_score, away TeamState.offense_score)",
        "historically_replayable_from_repo_calculators": True,
        "note": "Despite its name, frozen code does not use a separate player-lineup talent calculation.",
    },
    "defense": {
        "source": "PregameFeatureBuilder",
        "derivation": "advantage(home defense_score, away defense_score)",
        "historically_replayable_from_repo_calculators": True,
    },
    "home_field": {
        "source": "MatchupDefinition/RealGameStateAssembler",
        "derivation": "externally supplied normalized score",
        "default_value": 0.10,
        "exact_historical_value_recoverable_from_repo": False,
    },
    "park": {
        "source": "MatchupDefinition/RealGameStateAssembler",
        "derivation": "externally supplied normalized score",
        "default_value": 0.0,
        "exact_historical_value_recoverable_from_repo": False,
    },
    "weather": {
        "source": "MatchupDefinition/RealGameStateAssembler",
        "derivation": "externally supplied normalized score",
        "default_value": 0.0,
        "exact_historical_value_recoverable_from_repo": False,
    },
    "travel_rest_circadian": {
        "source": "MatchupDefinition/RealGameStateAssembler",
        "derivation": "externally supplied normalized score",
        "default_value": 0.0,
        "exact_historical_value_recoverable_from_repo": False,
    },
    "platoon_matchup_fit": {
        "source": "MatchupDefinition/RealGameStateAssembler",
        "derivation": "externally supplied normalized score",
        "default_value": 0.0,
        "exact_historical_value_recoverable_from_repo": False,
    },
}

def exact_replay_possible():
    return all(
        x.get("historically_replayable_from_repo_calculators")
        or x.get("exact_historical_value_recoverable_from_repo")
        for x in V11_FEATURE_SEMANTICS.values()
    )

def structural_default_replay_possible():
    return all(
        x.get("historically_replayable_from_repo_calculators")
        or "default_value" in x
        for x in V11_FEATURE_SEMANTICS.values()
    )

def report():
    unrecoverable=[
        k for k,v in V11_FEATURE_SEMANTICS.items()
        if not (
            v.get("historically_replayable_from_repo_calculators")
            or v.get("exact_historical_value_recoverable_from_repo")
        )
    ]
    return {
        "version":"BT-0086",
        "exact_historical_v11_replay_certified":exact_replay_possible(),
        "structural_default_replay_possible":structural_default_replay_possible(),
        "unrecoverable_exact_external_scores":unrecoverable,
        "allowed_next_baseline":"v1.1 structural-default replay",
        "forbidden_claim":"Do not label structural-default replay as the exact historical v1.1 probability ledger.",
        "feature_semantics":V11_FEATURE_SEMANTICS,
    }
