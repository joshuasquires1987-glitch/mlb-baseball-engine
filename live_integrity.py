from dataclasses import dataclass

from engine_types import IntegrityState


@dataclass(frozen=True)
class LiveIntegritySnapshot:
    game_pk: str
    starter: str
    lineup: str
    bullpen: str
    weather: str
    roster_news: str
    umpire: str = "yellow"

    def to_engine_state(self):
        return IntegrityState(
            starter=self.starter,
            lineup=self.lineup,
            bullpen=self.bullpen,
            weather=self.weather,
            roster_news=self.roster_news,
            umpire=self.umpire,
        )

    def required_components(self):
        return {
            "starter": self.starter.lower(),
            "lineup": self.lineup.lower(),
            "bullpen": self.bullpen.lower(),
            "weather": self.weather.lower(),
            "roster_news": self.roster_news.lower(),
        }

    def production_ready(self):
        # BT-0060 requires a fully green exact-history bundle before
        # the independent probability is generated.
        return all(v == "green" for v in self.required_components().values())

    def blockers(self):
        return [
            name
            for name, value in self.required_components().items()
            if value != "green"
        ]


def assert_production_ready(snapshot):
    if not snapshot.production_ready():
        raise RuntimeError(
            "live probability blocked; non-green integrity components: "
            + ",".join(snapshot.blockers())
        )
    return True
