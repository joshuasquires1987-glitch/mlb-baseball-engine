import pandas as pd
from game_state_assembler import RealGameStateAssembler
from matchup_definition import MatchupDefinition
from assembler_pipeline import AssemblerPipeline

D=pd.Timestamp("2026-08-09")

def pitching():
    return pd.DataFrame([
        {"id":"HSP","team":"H","date":"2026-08-01","p_gs":1,"p_bfp":24,"p_r":1,"p_ipouts":18},
        {"id":"ASP","team":"A","date":"2026-08-02","p_gs":1,"p_bfp":24,"p_r":5,"p_ipouts":15},
        {"id":"HR","team":"H","date":"2026-08-08","p_gs":0,"p_bfp":15,"p_r":0,"p_ipouts":9},
        {"id":"AR","team":"A","date":"2026-08-08","p_gs":0,"p_bfp":15,"p_r":4,"p_ipouts":9},
        {"id":"HSP","team":"H","date":"2026-08-10","p_gs":1,"p_bfp":25,"p_r":20,"p_ipouts":3},
    ])

def games():
    return pd.DataFrame([
        {"date":"2026-08-07","hometeam":"H","visteam":"X","hruns":7,"vruns":2},
        {"date":"2026-08-07","hometeam":"A","visteam":"X","hruns":2,"vruns":6},
        {"date":"2026-08-10","hometeam":"A","visteam":"Y","hruns":20,"vruns":0},
    ])

def test_assembler_and_pipeline():
    m=MatchupDefinition("G",D,"H","A","HSP","ASP",True,True)
    facts,inputs=AssemblerPipeline().build_inputs(m,pitching(),games())
    assert facts.home_starter.talent_score > facts.away_starter.talent_score
    assert facts.home_team_state.team_strength > facts.away_team_state.team_strength
    assert "starting_pitcher" in inputs.features
    assert "bullpen_exposure_quality" in inputs.features

def test_unconfirmed_starter_propagates():
    f=RealGameStateAssembler().assemble("G",D,"H","A","HSP","ASP",pitching(),games(),False,True,False,True,True,True)
    assert f.home_starter.confirmed is False
