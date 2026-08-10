from v11_replay_readiness import REQUIRED_COMPONENTS,audit_repo_contract

def test_all_v11_components_named():
    assert len(REQUIRED_COMPONENTS)==10
    assert "starting_pitcher" in REQUIRED_COMPONENTS
    assert "weather" in REQUIRED_COMPONENTS

def test_report_blocks_uncertified_replay():
    x=audit_repo_contract()
    assert x["historical_replay_status"]=="not_yet_certified"
