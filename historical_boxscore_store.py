from mlb_boxscore_exact_adapter import exact_pitching_rows

class HistoricalBoxscoreStore:
    def __init__(self):
        self.pitching_rows=[]

    def ingest(self,game_pk,game_date,boxscore_payload):
        seen={(r.get("game_pk"),r["id"],r["team"]) for r in self.pitching_rows}
        for side in ("away","home"):
            team=boxscore_payload.get("teams",{}).get(side,{}).get("team",{}).get("abbreviation")
            if not team:
                continue
            for row in exact_pitching_rows(boxscore_payload,game_date,team):
                key=(str(game_pk),row["id"],row["team"])
                if key in seen:
                    continue
                self.pitching_rows.append({"game_pk":str(game_pk),**row})
                seen.add(key)

    def pitcher_history(self,pitcher_id,before_date):
        return sorted(
            [r for r in self.pitching_rows if r["id"]==str(pitcher_id) and r["date"] < before_date],
            key=lambda x:x["date"]
        )

    def bullpen_history(self,team,before_date):
        return sorted(
            [r for r in self.pitching_rows if r["team"]==team and r["p_gs"]==0 and r["date"] < before_date],
            key=lambda x:x["date"]
        )
