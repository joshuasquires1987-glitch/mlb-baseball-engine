from dataclasses import dataclass

@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id:str
    name:str
    status:str
    description:str
    production_rule:bool=False

DEFAULT_HYPOTHESES=[
    Hypothesis("H1","Tail calibration","research","Check calibration at extreme probabilities."),
    Hypothesis("H2","Bet timing","research","Study first vs final Bet365 snapshot and CLV."),
    Hypothesis("H3","Pitcher change points","research","Detect meaningful starter skill regime changes."),
    Hypothesis("H4","Rain-delay effects","research","Test delay risk effects on starter/bullpen allocation."),
    Hypothesis("H5","Lesser-known effective starters","research","Test whether public/market underreaction exists."),
    Hypothesis("H6","Starter depth / bullpen exposure","validated_challenger",
               "Expected starter depth and bullpen exposure showed robust forward value."),
]
