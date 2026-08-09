from bundle_probability_gate import assert_bundle_ready,assert_probability_integrity

class Integrity:
    def __init__(self,red=False): self.red=red
    def unresolved_red(self): return self.red
class Inputs:
    def __init__(self,red=False): self.integrity=Integrity(red)

def test_bundle_must_be_green():
    try:
        assert_bundle_ready({"readiness":{"ready":False},"pitching_rows":[1],"team_games":[1]})
        assert False
    except RuntimeError: pass

def test_bundle_needs_rows():
    try:
        assert_bundle_ready({"readiness":{"ready":True},"pitching_rows":[],"team_games":[1]})
        assert False
    except RuntimeError: pass

def test_green_bundle_passes():
    assert assert_bundle_ready({"readiness":{"ready":True},"pitching_rows":[1],"team_games":[1]})

def test_red_integrity_blocks():
    try:
        assert_probability_integrity(Inputs(True))
        assert False
    except RuntimeError: pass

def test_clean_integrity_passes():
    assert assert_probability_integrity(Inputs(False))
