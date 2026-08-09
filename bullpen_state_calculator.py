from state_utils import half_life_weight,shrunk_rate,bounded_score

class BullpenStateCalculator:
    def __init__(self,half_life_days=120,prior_bf=250,league_runs_per_bf=0.18):
        self.half_life_days=half_life_days
        self.prior_bf=prior_bf
        self.league_runs_per_bf=league_runs_per_bf

    def calculate(self,relief_rows,as_of_date):
        prior=[r for r in relief_rows if r["date"] < as_of_date]
        if not prior:
            return {
                "bullpen_score":0.0,
                "batters_faced_prior":0.0,
                "data_quality":"prior-only-default",
            }

        bf_w=r_w=0.0
        for r in prior:
            age=(as_of_date-r["date"]).days
            w=half_life_weight(age,self.half_life_days)
            bf_w += float(r.get("batters_faced",0))*w
            r_w += float(r.get("runs_allowed",0))*w

        ra_per_bf=shrunk_rate(r_w,bf_w,self.league_runs_per_bf,self.prior_bf)
        score=bounded_score(
            ra_per_bf,
            self.league_runs_per_bf,
            max(self.league_runs_per_bf*0.18,1e-6),
            invert=True
        )
        return {
            "bullpen_score":score,
            "batters_faced_prior":bf_w,
            "runs_per_bf":ra_per_bf,
            "data_quality":"pregame-history",
        }
