import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_weights_sum_to_one():
    for fn in ['v1_1.json','v1_2_rc1.json']:
        c=json.loads((ROOT/'config'/fn).read_text()); assert abs(sum(c['weights'].values())-1)<1e-12
def test_rc1_shadow_only():
    c=json.loads((ROOT/'config'/'v1_2_rc1.json').read_text()); assert c['status_rules']['shadow_only'] and not c['status_rules']['controls_bets'] and not c['status_rules']['controls_stakes']
def test_no_price_leakage():
    for fn in ['v1_1.json','v1_2_rc1.json']:
        c=json.loads((ROOT/'config'/fn).read_text()); assert c['prices_allowed_in_probability_model'] is False
