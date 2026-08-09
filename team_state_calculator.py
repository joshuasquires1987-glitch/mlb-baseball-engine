from state_utils import half_life_weight,shrunk_rate,bounded_score

class TeamStateCalculator:
    def __init__(self,half_life_days=90,prior_games=20,league_runs_per_team_game=4.5):
        self.half_life_days=half_life_days
        self.prior_games=prior_games
        self.league_runs_per_team_game=league_runs_per_team_game

    def calculate(self,games,as_of_date):
        prior=[r for r in games if r["date"] < as_of_date]
        if not prior:
            return {
                "team_strength":0.0,
                "offense_score":0.0,
                "defense_score":0.0,
                "games_prior":0,
                "data_quality":"prior-only-default",
            }

        rw=raw=gw=0.0
        for r in prior:
            age=(as_of_date-r["date"]).days
            w=half_life_weight(age,self.half_life_days)
            rw += float(r["runs_for"])*w
            raw += float(r["runs_against"])*w
            gw += w

        rf=(rw+self.prior_games*self.league_runs_per_team_game)/(gw+self.prior_games)
        ra=(raw+self.prior_games*self.league_runs_per_team_game)/(gw+self.prior_games)
        scale=max(self.league_runs_per_team_game*0.18,1e-6)

        offense=bounded_score(rf,self.league_runs_per_team_game,scale)
        defense=bounded_score(ra,self.league_runs_per_team_game,scale,invert=True)
        strength=max(-3.0,min(3.0,(offense+defense)/2.0))

        return {
            "team_strength":strength,
            "offense_score":offense,
            "defense_score":defense,
            "games_prior":len(prior),
            "runs_for_per_game_state":rf,
            "runs_against_per_game_state":ra,
            "data_quality":"pregame-history",
        }
