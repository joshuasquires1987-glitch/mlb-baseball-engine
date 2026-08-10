from context_availability_audit import audit_game,summarize_audit
from historical_context_dataset import build_training_row
from historical_context_manifest import manifest

class BulkContextDatasetRunner:
    def __init__(self,weather_provider,park_registry,venue_registry,snapshot_registry):
        self.weather_provider=weather_provider
        self.park_registry=park_registry
        self.venue_registry=venue_registry
        self.snapshot_registry=snapshot_registry

    def run(self,games):
        rows=[]
        audit=[]
        skipped=[]
        prior={}

        for g in sorted(games,key=lambda x:(x.get("game_time_utc") or "",x["game_pk"])):
            if hasattr(self.venue_registry,"get_for_game_time"):
                venue=self.venue_registry.get_for_game_time(
                    g.get("venue_id"),g.get("game_time_utc")
                )
            else:
                venue=self.venue_registry.get(g.get("venue_id"))

            if hasattr(self.park_registry,"get_for_game"):
                park=self.park_registry.get_for_game(
                    g["game_pk"],g.get("venue_id")
                )
            else:
                park=self.park_registry.get(g.get("venue_id"))

            snap=self.snapshot_registry.get(g["game_pk"])
            weather=self.weather_provider(g["game_pk"])

            home_prior=prior.get(str(g["home_team_id"]))
            away_prior=prior.get(str(g["away_team_id"]))
            prior_state=None
            if home_prior is not None and away_prior is not None:
                prior_state={"home":home_prior,"away":away_prior}

            ar=audit_game(g,weather,park,venue,prior_state,snap)
            audit.append({"game_pk":g["game_pk"],**ar})

            if ar["usable"]:
                try:
                    game={
                        "game_id":g["game_pk"],
                        "game_date":g["game_date"],
                        "game_time_utc":g["game_time_utc"],
                        "home_team":str(g["home_team_id"]),
                        "away_team":str(g["away_team_id"]),
                        "home_runs":g["home_runs"],
                        "away_runs":g["away_runs"],
                        "home_venue_utc_offset_hours":venue["utc_offset_hours"],
                        "pregame_weather":weather,
                    }
                    ps={
                        str(g["home_team_id"]):home_prior,
                        str(g["away_team_id"]):away_prior,
                    }
                    rows.append(build_training_row(
                        game,ps,park["park_factor"],snap
                    ))
                except Exception as e:
                    skipped.append({
                        "game_pk":g["game_pk"],
                        "reason":f"build-error:{type(e).__name__}",
                    })
            else:
                skipped.append({
                    "game_pk":g["game_pk"],
                    "reason":"|".join(ar["missing"]),
                })

            if (
                venue is not None
                and venue.get("utc_offset_hours") is not None
                and g.get("game_time_utc") is not None
            ):
                stamp={
                    "previous_game_time_utc":g["game_time_utc"],
                    "previous_venue_utc_offset_hours":venue["utc_offset_hours"],
                }
                prior[str(g["home_team_id"])]=dict(stamp)
                prior[str(g["away_team_id"])]=dict(stamp)

        return {
            "rows":rows,
            "audit":audit,
            "availability":summarize_audit(audit),
            "manifest":manifest(rows,skipped),
        }
