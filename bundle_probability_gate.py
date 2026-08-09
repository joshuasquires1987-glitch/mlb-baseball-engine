def assert_bundle_ready(bundle):
    r=bundle.get("readiness")
    if not isinstance(r,dict) or r.get("ready") is not True:
        raise RuntimeError("Exact historical bundle is not fully green.")
    if not bundle.get("pitching_rows"):
        raise RuntimeError("Exact historical bundle has no pitching rows.")
    if not bundle.get("team_games"):
        raise RuntimeError("Exact historical bundle has no team-game rows.")
    return True

def assert_probability_integrity(model_inputs):
    integrity=getattr(model_inputs,"integrity",None)
    if integrity is None: raise RuntimeError("Model inputs have no integrity state.")
    if hasattr(integrity,"unresolved_red") and integrity.unresolved_red():
        raise RuntimeError("Unresolved red integrity item blocks probability.")
    return True
