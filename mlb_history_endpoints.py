BASE="https://statsapi.mlb.com/api/v1"
def player_game_log_url(player_id,season,group="pitching"):
    return f"{BASE}/people/{player_id}/stats?stats=gameLog&group={group}&season={season}"
def schedule_url(start_date,end_date=None):
    end_date=end_date or start_date
    return f"{BASE}/schedule?sportId=1&startDate={start_date}&endDate={end_date}&hydrate=probablePitcher,team,venue"
def game_boxscore_url(game_pk): return f"{BASE}/game/{game_pk}/boxscore"
