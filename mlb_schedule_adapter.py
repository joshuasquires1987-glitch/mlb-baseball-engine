def _team_code(team):
    return team.get("abbreviation") or team.get("teamCode") or str(team.get("id")) or team.get("name")
def parse_schedule_games(payload,source_stamp):
    rows=[]
    for d in payload.get("dates",[]):
        for g in d.get("games",[]):
            t=g.get("teams",{})
            h=t.get("home",{}).get("team",{}); a=t.get("away",{}).get("team",{})
            hp=t.get("home",{}).get("probablePitcher"); ap=t.get("away",{}).get("probablePitcher")
            rows.append({
                "game_id":str(g.get("gamePk")),"game_date":g.get("gameDate") or d.get("date"),
                "home_team":_team_code(h),"away_team":_team_code(a),
                "venue_name":g.get("venue",{}).get("name","unknown"),
                "home_starter_id":str(hp.get("id")) if hp else None,
                "home_starter_name":hp.get("fullName") if hp else None,
                "away_starter_id":str(ap.get("id")) if ap else None,
                "away_starter_name":ap.get("fullName") if ap else None,
                "starter_source":source_stamp,
                "status":g.get("status",{}).get("detailedState","unknown")
            })
    return rows
