import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def _load(name):
    return json.loads((ROOT / name).read_text())

def test_weights_sum_to_one():
    for fn in ["v1_1.json", "v1_2_rc1.json"]:
        c = _load(fn)
        assert abs(sum(c["weights"].values()) - 1) < 1e-12

def test_rc1_shadow_only():
    c = _load("v1_2_rc1.json")
    assert c["status_rules"]["shadow_only"]
    assert not c["status_rules"]["controls_bets"]
    assert not c["status_rules"]["controls_stakes"]

def test_no_price_leakage():
    for fn in ["v1_1.json", "v1_2_rc1.json"]:
        c = _load(fn)
        assert c["prices_allowed_in_probability_model"] is False
