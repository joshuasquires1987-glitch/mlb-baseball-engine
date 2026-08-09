from proof_qualification import qualify_probability

def base():
    return {
      "prices_seen":False,
      "probabilities_frozen":True,
      "production":{"integrity":{
        "starter":"green","lineup":"green","bullpen":"green",
        "weather":"green","roster_news":"green","umpire":"yellow"
      }}
    }

def context():
    return {
      "park_score":0.0,"weather_score":0.0,"travel_rest_score":0.0,"platoon_score":0.0,
      "provenance":{
        "park_score":"verified","weather_score":"verified",
        "travel_rest_score":"verified","platoon_score":"verified"
      }
    }

def test_green_proof_qualifies():
    q=qualify_probability(base(),context())
    assert q["qualified"]
    assert q["market_evaluation_allowed"]

def test_yellow_lineup_blocks():
    p=base()
    p["production"]["integrity"]["lineup"]="yellow"
    q=qualify_probability(p,context())
    assert not q["qualified"]
    assert "integrity-lineup-yellow" in q["issues"]

def test_unverified_neutral_context_blocks():
    c=context()
    c["provenance"]["platoon_score"]="unverified"
    q=qualify_probability(base(),c)
    assert not q["qualified"]
    assert "context-platoon_score-unverified" in q["issues"]

def test_market_leakage_blocks():
    p=base(); p["prices_seen"]=True
    assert not qualify_probability(p,context())["qualified"]
