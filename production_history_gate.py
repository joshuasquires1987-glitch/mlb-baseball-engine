def exact_history_status(rows):
    if not rows:
        return {"ready":False,"reason":"no history rows"}
    bad=[r.date for r in rows if not r.production_ready]
    return {
        "ready":not bad,
        "non_exact_dates":bad,
        "reason":"ok" if not bad else "one or more required fields are derived/estimated",
    }

def starter_history_to_calculator_rows(rows):
    status=exact_history_status(rows)
    if not status["ready"]:
        raise ValueError("Starter history is not exact enough for production.")
    return [{
        "date":r.date,
        "outs":r.innings_outs.value,
        "runs_allowed":r.runs_allowed.value,
        "batters_faced":r.batters_faced.value,
    } for r in rows]
