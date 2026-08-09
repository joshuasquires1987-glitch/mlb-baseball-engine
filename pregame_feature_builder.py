from engine_types import BaseballInputs,IntegrityState
from feature_normalization import advantage,bullpen_exposure_quality
from pregame_inputs import PregameFacts

class PregameFeatureBuilder:
    def __init__(self):
        self._starter_fingerprints={}

    def starter_fingerprint(self,facts:PregameFacts):
        return f"{facts.away_starter.pitcher_id}|{facts.home_starter.pitcher_id}"

    def starter_changed(self,facts:PregameFacts):
        fp=self.starter_fingerprint(facts)
        old=self._starter_fingerprints.get(facts.game_id)
        return old is not None and old!=fp

    def _integrity(self,facts:PregameFacts):
        starter="green" if facts.home_starter.confirmed and facts.away_starter.confirmed else "red"
        lineup="green" if facts.lineup_confirmed else "yellow"
        bullpen="green" if facts.bullpen_current else "yellow"
        weather="green" if facts.weather_current else "yellow"
        roster="green" if facts.roster_news_clear else "yellow"
        umpire="green" if facts.umpire_known else "yellow"
        return IntegrityState(starter,lineup,bullpen,weather,roster,umpire)

    def build(self,facts:PregameFacts):
        integrity=self._integrity(facts)

        hts=facts.home_team_state
        ats=facts.away_team_state
        hs=facts.home_starter
        aws=facts.away_starter
        c=facts.context

        # Directional convention: positive favors home, negative favors away.
        features={
            # v1.1
            "starting_pitcher":advantage(hs.talent_score,aws.talent_score),
            "underlying_team_strength":advantage(hts.team_strength,ats.team_strength),
            "bullpen":advantage(hts.bullpen_score,ats.bullpen_score),
            "confirmed_lineup_offense":advantage(hts.offense_score,ats.offense_score),
            "platoon_matchup_fit":float(c.platoon_score),
            "defense":advantage(hts.defense_score,ats.defense_score),
            "home_field":float(c.home_field_score),
            "park":float(c.park_score),
            "weather":float(c.weather_score),
            "travel_rest_circadian":float(c.travel_rest_score),

            # v1.2-RC1
            "starting_pitcher_talent_state":advantage(hs.talent_score,aws.talent_score),
            "bullpen_talent_state":advantage(hts.bullpen_score,ats.bullpen_score),
            "expected_starter_depth":advantage(hs.expected_outs,aws.expected_outs,scale=6.0),
            "bullpen_exposure_quality":bullpen_exposure_quality(
                hs.expected_outs,aws.expected_outs,hts.bullpen_score,ats.bullpen_score,scale=12.0
            ),
        }

        self._starter_fingerprints[facts.game_id]=self.starter_fingerprint(facts)
        return BaseballInputs(
            game_id=facts.game_id,
            game_date=facts.game_date,
            home_team=facts.home_team,
            away_team=facts.away_team,
            features=features,
            integrity=integrity,
        )
