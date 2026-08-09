from pregame_inputs import StarterState,TeamState

def build_starter_state(calculator,starts,as_of_date,pitcher_id,confirmed):
    x=calculator.calculate(starts,as_of_date)
    return StarterState(
        pitcher_id=pitcher_id,
        talent_score=x["talent_score"],
        expected_outs=x["expected_outs"],
        confirmed=confirmed,
    )

def build_team_state(team_calc,bullpen_calc,team_games,relief_rows,as_of_date):
    t=team_calc.calculate(team_games,as_of_date)
    b=bullpen_calc.calculate(relief_rows,as_of_date)
    return TeamState(
        team_strength=t["team_strength"],
        offense_score=t["offense_score"],
        defense_score=t["defense_score"],
        bullpen_score=b["bullpen_score"],
    )
