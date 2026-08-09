REQUIRED_HISTORY_KEYS=("starter_history","team_history","bullpen_history")

def history_readiness(bundle):
    missing=[k for k in REQUIRED_HISTORY_KEYS if not bundle.get(k)]
    return {
        "ready":not missing,
        "missing":missing,
        "integrity":"green" if not missing else "red",
    }

def probability_allowed(role_ready,history_bundle):
    h=history_readiness(history_bundle)
    return bool(role_ready and h["ready"])
