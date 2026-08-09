def team_game_rows_from_game(game_payload,game_date):
    teams=game_payload.get("teams",{})
    away=teams.get("away",{})
    home=teams.get("home",{})
    aa=away.get("team",{}).get("abbreviation")
    ha=home.get("team",{}).get("abbreviation")
    ar=away.get("score")
    hr=home.get("score")
    if None in (aa,ha,ar,hr):
        raise ValueError("Missing exact team/score fields")
    canonical={
        "date":str(game_date),
        "hometeam":ha,
        "visteam":aa,
        "hruns":float(hr),
        "vruns":float(ar),
        "source_exact":True,
    }
    perspectives=[
        {"date":str(game_date),"team":aa,"opponent":ha,"runs_for":float(ar),"runs_against":float(hr),
         "venue":"away","source_exact":True},
        {"date":str(game_date),"team":ha,"opponent":aa,"runs_for":float(hr),"runs_against":float(ar),
         "venue":"home","source_exact":True},
    ]
    return canonical,perspectives
