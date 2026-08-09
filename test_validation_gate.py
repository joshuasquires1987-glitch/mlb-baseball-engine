from validation_metrics import brier,log_loss,predicted_edge_pp,clv_pp
from segmentation import edge_bucket,price_band,favorite_underdog
from validation_tracker import ValidationTracker
from promotion_gate import review_status

def test_metrics():
    assert abs(brier(.6,1)-.16) < 1e-12
    assert log_loss(.6,1)>0
    assert abs(predicted_edge_pp(.55,2.0)-5.0) < 1e-12

def test_segments():
    assert edge_bucket(3.1)=="+3-5pp"
    assert edge_bucket(5.1)=="+5-8pp"
    assert edge_bucket(9)=="+8+pp"
    assert favorite_underdog(1.8)=="favorite"
    assert favorite_underdog(2.2)=="underdog"
    assert price_band(1.5)=="<=1.50"

def test_tracker_summary():
    t=ValidationTracker()
    t.add_game("G1","v1.1",.6,1,2.0,confidence=.2)
    t.add_game("G2","v1.1",.4,0,2.2,confidence=.3)
    s=t.summary("v1.1")
    assert s["n"]==2 and s["wins"]==1

def test_gate_not_before_500():
    x=review_status(499,0,.24,.25,True,False,False)
    assert not x["review_eligible"] and not x["promoted"]

def test_gate_review_eligible_but_not_promoted():
    x=review_status(500,0,.24,.25,True,False,False)
    assert x["review_eligible"] and not x["promoted"]
    assert x["status"]=="ELIGIBLE_FOR_REVIEW"

def test_requires_human_approval():
    x=review_status(500,0,.24,.25,True,False,True)
    assert x["promoted"] and x["automatic_promotion"] is False

def test_bad_brier_blocks():
    x=review_status(600,0,.26,.25,True,False,True)
    assert not x["review_eligible"] and not x["promoted"]

def test_integrity_failure_blocks():
    x=review_status(600,1,.24,.25,True,False,True)
    assert not x["review_eligible"]

def test_clv_direction():
    assert clv_pp(2.0,1.9)>0
