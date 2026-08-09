from records import FrozenPredictionRecord
from wager_ledger import WagerLedger
from settlement import settle_wager
from shadow_evaluation import evaluate_predictions

def pred(version="v1.1"):
    return FrozenPredictionRecord("P","T","G","2026-08-09","H","A",version,.60,.40,.2,
        "green","green","green","green","green","yellow",True)

def test_no_wager_without_confirmation():
    l=WagerLedger()
    try: l.confirm(pred(),"home",2.0,50,False); assert False
    except PermissionError: pass

def test_shadow_cannot_create_wager():
    l=WagerLedger()
    try: l.confirm(pred("v1.2-RC1"),"home",2.0,50,True); assert False
    except ValueError: pass

def test_original_probability_preserved():
    l=WagerLedger()
    w=l.confirm(pred(),"home",2.0,50,True)
    assert w.original_model_probability==.60

def test_win_settlement():
    l=WagerLedger()
    w=l.confirm(pred(),"home",2.10,50,True)
    s=settle_wager(w,"win")
    assert s.profit_loss_cad==55.0

def test_loss_settlement():
    l=WagerLedger()
    w=l.confirm(pred(),"away",1.80,40,True)
    s=settle_wager(w,"loss")
    assert s.profit_loss_cad==-40.0

def test_shadow_scoring_independent():
    a=pred("v1.1"); b=pred("v1.2-RC1")
    x=evaluate_predictions(a,b,True)
    assert x["production_brier"]==x["shadow_brier"]

def test_promotion_separate():
    l=WagerLedger()
    w=l.confirm(pred(),"home",2.0,20,True)
    s=settle_wager(w,"win",promotion_early_payout=True)
    assert "separately" in s.promotion_note.lower()
