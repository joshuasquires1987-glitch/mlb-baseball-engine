import math
from collections import defaultdict
from datetime import datetime

from starter_state_calculator import StarterStateCalculator
from team_state_calculator import TeamStateCalculator
from bullpen_state_calculator import BullpenStateCalculator
from feature_normalization import advantage

DEFAULT_CONTEXT = {
    "home_field": 0.10,
    "park": 0.0,
    "weather": 0.0,
    "travel_rest_circadian": 0.0,
    "platoon_matchup_fit": 0.0,
}

def _dt(v):
    return datetime.fromisoformat(str(v).replace("Z", "+00:00"))

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, float(x)))))

def _validated_final_score(g):
    hr = g.get("home_runs")
    ar = g.get("away_runs")
    if hr is None or ar is None:
        raise ValueError(
            f"missing final score: home_runs={hr!r}, away_runs={ar!r}"
        )
    try:
        hr = float(hr)
        ar = float(ar)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"invalid final score: home_runs={hr!r}, away_runs={ar!r}"
        ) from e
    if not math.isfinite(hr) or not math.isfinite(ar):
        raise ValueError(
            f"non-finite final score: home_runs={hr!r}, away_runs={ar!r}"
        )
    return hr, ar

def state_features(target, starter_history, team_history, bullpen_history):
    cutoff = _dt(target["game_time_utc"])
    hs = str(target["home_probable_starter_id"])
    aws = str(target["away_probable_starter_id"])
    ht = str(target["home_team_id"])
    at = str(target["away_team_id"])

    sc = StarterStateCalculator()
    tc = TeamStateCalculator()
    bc = BullpenStateCalculator()

    home_sp = sc.calculate(starter_history.get(hs, []), cutoff)
    away_sp = sc.calculate(starter_history.get(aws, []), cutoff)
    home_tm = tc.calculate(team_history.get(ht, []), cutoff)
    away_tm = tc.calculate(team_history.get(at, []), cutoff)
    home_bp = bc.calculate(bullpen_history.get(ht, []), cutoff)
    away_bp = bc.calculate(bullpen_history.get(at, []), cutoff)

    return {
        "starting_pitcher": advantage(home_sp["talent_score"], away_sp["talent_score"]),
        "underlying_team_strength": advantage(home_tm["team_strength"], away_tm["team_strength"]),
        "bullpen": advantage(home_bp["bullpen_score"], away_bp["bullpen_score"]),
        "confirmed_lineup_offense": advantage(home_tm["offense_score"], away_tm["offense_score"]),
        "platoon_matchup_fit": DEFAULT_CONTEXT["platoon_matchup_fit"],
        "defense": advantage(home_tm["defense_score"], away_tm["defense_score"]),
        "home_field": DEFAULT_CONTEXT["home_field"],
        "park": DEFAULT_CONTEXT["park"],
        "weather": DEFAULT_CONTEXT["weather"],
        "travel_rest_circadian": DEFAULT_CONTEXT["travel_rest_circadian"],
    }

def probability(features, weights):
    score = sum(float(features[k]) * float(weights[k]) for k in weights)
    return sigmoid(score), score

class ReplayState:
    def __init__(self):
        self.starters = defaultdict(list)
        self.teams = defaultdict(list)
        self.bullpens = defaultdict(list)

    def add_completed_game(self, g):
        # Validate before mutating any replay state so malformed historical
        # records cannot partially contaminate team/starter/bullpen histories.
        hr, ar = _validated_final_score(g)
        gt = _dt(g["game_time_utc"])
        ht, at = str(g["home_team_id"]), str(g["away_team_id"])

        self.teams[ht].append({"date": gt, "runs_for": hr, "runs_against": ar})
        self.teams[at].append({"date": gt, "runs_for": ar, "runs_against": hr})

        for p in g.get("pitching_rows", []):
            pid, team = str(p["id"]), str(p["team"])
            if int(p.get("p_gs", 0)) > 0:
                self.starters[pid].append({
                    "date": gt,
                    "batters_faced": float(p.get("p_bfp", 0)),
                    "runs_allowed": float(p.get("p_r", 0)),
                    "outs": float(p.get("p_ipouts", 0)),
                })
            else:
                self.bullpens[team].append({
                    "date": gt,
                    "batters_faced": float(p.get("p_bfp", 0)),
                    "runs_allowed": float(p.get("p_r", 0)),
                })

def replay_2025(parsed_games, target_snapshots, weights):
    state = ReplayState()
    warmup = [g for g in parsed_games if str(g["game_date"]).startswith("2024")]
    finals_2025 = {str(g["game_pk"]): g for g in parsed_games if str(g["game_date"]).startswith("2025")}
    rows, failures = [], []

    def add_state_game(g, phase):
        try:
            state.add_completed_game(g)
            return True
        except Exception as e:
            failures.append({
                "game_pk": str(g.get("game_pk", "")),
                "reason": f"state-ingest-{phase}:{type(e).__name__}",
                "detail": str(e)[:300],
                "home_runs": g.get("home_runs"),
                "away_runs": g.get("away_runs"),
            })
            return False

    for g in sorted(warmup, key=lambda x: x["game_time_utc"]):
        add_state_game(g, "warmup")

    by_date = defaultdict(list)
    for s in target_snapshots:
        by_date[str(s["game_date"])].append(s)

    for day in sorted(by_date):
        targets = sorted(by_date[day], key=lambda x: (x["game_time_utc"], str(x["game_pk"])))

        # Conservative anti-leakage rule: no same-calendar-day results are used.
        for s in targets:
            try:
                f = state_features(s, state.starters, state.teams, state.bullpens)
                p, score = probability(f, weights)
                rows.append({
                    "game_pk": str(s["game_pk"]),
                    "game_date": s["game_date"],
                    "game_time_utc": s["game_time_utc"],
                    "home_team_id": str(s["home_team_id"]),
                    "away_team_id": str(s["away_team_id"]),
                    "home_probable_starter_id": str(s["home_probable_starter_id"]),
                    "away_probable_starter_id": str(s["away_probable_starter_id"]),
                    "baseline_label": "v1.1-structural-default-replay",
                    "exact_historical_v11_probability": False,
                    "context_defaults": dict(DEFAULT_CONTEXT),
                    "features": f,
                    "weighted_score": score,
                    "home_win_probability": p,
                    "away_win_probability": 1.0 - p,
                })
            except Exception as e:
                failures.append({
                    "game_pk": str(s["game_pk"]),
                    "reason": f"replay-error:{type(e).__name__}",
                    "detail": str(e)[:300],
                })

        for s in targets:
            g = finals_2025.get(str(s["game_pk"]))
            if g is not None:
                add_state_game(g, "target-final")

    return rows, failures
