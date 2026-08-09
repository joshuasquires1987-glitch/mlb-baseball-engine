from datetime import datetime, timezone

def _to_utc_naive(value):
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime):
        raise TypeError(f"Unsupported date value: {value!r}")
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value

from state_utils import half_life_weight,shrunk_rate,bounded_score

class StarterStateCalculator:
    def __init__(self,talent_half_life_days=180,depth_half_life_days=90,
                 talent_prior_bf=350,depth_prior_starts=5,
                 league_runs_per_bf=0.18,league_outs_per_start=16.0):
        self.talent_half_life_days=talent_half_life_days
        self.depth_half_life_days=depth_half_life_days
        self.talent_prior_bf=talent_prior_bf
        self.depth_prior_starts=depth_prior_starts
        self.league_runs_per_bf=league_runs_per_bf
        self.league_outs_per_start=league_outs_per_start

    def calculate(self,starts,as_of_date):
        cutoff=_to_utc_naive(as_of_date)
        normalized=[{**r,"date":_to_utc_naive(r["date"])} for r in starts]
        prior=[r for r in normalized if r["date"] < cutoff]
        if not prior:
            return {"talent_score":0.0,"expected_outs":self.league_outs_per_start,
                    "starts_prior":0,"data_quality":"prior-only-default"}

        bf_w=r_w=0.0
        outs_w=w_depth=0.0
        for r in prior:
            age=(cutoff-r["date"]).days
            wt=half_life_weight(age,self.talent_half_life_days)
            bf_w += float(r.get("batters_faced",0))*wt
            r_w += float(r.get("runs_allowed",0))*wt
            wd=half_life_weight(age,self.depth_half_life_days)
            outs_w += float(r.get("outs",0))*wd
            w_depth += wd

        ra_per_bf=shrunk_rate(r_w,bf_w,self.league_runs_per_bf,self.talent_prior_bf)
        talent_score=bounded_score(
            ra_per_bf,self.league_runs_per_bf,
            max(self.league_runs_per_bf*0.20,1e-6),invert=True)
        expected_outs=(outs_w+self.depth_prior_starts*self.league_outs_per_start)/(w_depth+self.depth_prior_starts)
        return {"talent_score":talent_score,"expected_outs":expected_outs,
                "starts_prior":len(prior),"runs_per_bf":ra_per_bf,
                "data_quality":"pregame-history"}
