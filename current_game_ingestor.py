from datetime import datetime,timezone
from current_game_sources import StarterInfo,LineupInfo,WeatherInfo,RosterNewsInfo,ParkInfo,CurrentGameRecord
from matchup_definition import MatchupDefinition
from ingestion_freshness import is_fresh

class CurrentGameIngestor:
    def __init__(self,starter_max_age_minutes=180,lineup_max_age_minutes=90,weather_max_age_minutes=120,roster_max_age_minutes=240):
        self.starter_max_age_minutes=starter_max_age_minutes
        self.lineup_max_age_minutes=lineup_max_age_minutes
        self.weather_max_age_minutes=weather_max_age_minutes
        self.roster_max_age_minutes=roster_max_age_minutes

    def build_record(self,row,lineup_confirmed,lineup_source,weather_score,weather_source,roster_clear,roster_source,
                     park_score=0.0,now_utc=None,bullpen_current=True,home_field_score=.10,
                     travel_rest_score=0.0,platoon_score=0.0,umpire_known=False):
        now_utc=now_utc or datetime.now(timezone.utc)
        ss=row["starter_source"]
        sf=is_fresh(ss.fetched_at_utc,now_utc,self.starter_max_age_minutes)
        lf=is_fresh(lineup_source.fetched_at_utc,now_utc,self.lineup_max_age_minutes)
        wf=is_fresh(weather_source.fetched_at_utc,now_utc,self.weather_max_age_minutes)
        rf=is_fresh(roster_source.fetched_at_utc,now_utc,self.roster_max_age_minutes)
        hp=row.get("home_starter_id"); ap=row.get("away_starter_id")
        return CurrentGameRecord(
            row["game_id"],row["game_date"],row["home_team"],row["away_team"],
            StarterInfo(hp or "",row.get("home_starter_name") or "",bool(hp) and sf,ss),
            StarterInfo(ap or "",row.get("away_starter_name") or "",bool(ap) and sf,ss),
            LineupInfo(bool(lineup_confirmed) and lf,lineup_source),
            WeatherInfo(wf,float(weather_score),weather_source),
            RosterNewsInfo(bool(roster_clear) and rf,roster_source),
            ParkInfo(row.get("venue_name","unknown"),float(park_score)),
            bool(bullpen_current),float(home_field_score),float(travel_rest_score),float(platoon_score),bool(umpire_known)
        )

    def to_matchup_definition(self,r):
        return MatchupDefinition(
            r.game_id,r.game_date,r.home_team,r.away_team,
            r.home_starter.pitcher_id,r.away_starter.pitcher_id,
            r.home_starter.confirmed,r.away_starter.confirmed,
            r.lineup.confirmed,r.bullpen_current,r.weather.current,r.roster_news.clear,
            r.home_field_score,r.park.park_score,r.weather.weather_score,
            r.travel_rest_score,r.platoon_score,r.umpire_known
        )
