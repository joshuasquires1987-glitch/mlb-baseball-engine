class PriorScheduleTracker:
    def __init__(self):
        self.last={}

    def state_for(self,home_team_id,away_team_id):
        h=self.last.get(str(home_team_id))
        a=self.last.get(str(away_team_id))
        if h is None or a is None:
            return None
        return {"home":dict(h),"away":dict(a)}

    def update_after_game(self,game,venue_utc_offset_hours):
        stamp={
            "previous_game_time_utc":game.get("game_time_utc"),
            "previous_venue_utc_offset_hours":venue_utc_offset_hours,
        }
        self.last[str(game["home_team_id"])]=dict(stamp)
        self.last[str(game["away_team_id"])]=dict(stamp)
