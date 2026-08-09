from datetime import datetime,timezone
from uuid import uuid4
from records import FrozenPredictionRecord

class PredictionStore:
    def __init__(self):
        self.records={}
    def freeze(self,game_record,model="production"):
        block=game_record["production"] if model=="production" else game_record["shadow"]
        version=block["version"] if model=="production" else block["model_version"]
        hp=block["home_prob"] if model=="production" else block["home_win_probability"]
        ap=block["away_prob"] if model=="production" else block["away_win_probability"]
        conf=block["confidence"]
        i=game_record["integrity"]
        rec=FrozenPredictionRecord(
            prediction_id=str(uuid4()),
            timestamp_utc=game_record["timestamp_utc"],
            game_id=game_record["game_id"],
            game_date=game_record["game_date"],
            home_team=game_record["home_team"],
            away_team=game_record["away_team"],
            model_version=version,
            home_win_probability=hp,
            away_win_probability=ap,
            confidence=conf,
            starter_light=i["starter"],lineup_light=i["lineup"],bullpen_light=i["bullpen"],
            weather_light=i["weather"],roster_news_light=i["roster_news"],umpire_light=i.get("umpire","yellow"),
            frozen=True,
        )
        self.records[rec.prediction_id]=rec
        return rec
