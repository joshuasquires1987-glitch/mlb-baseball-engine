REQUIRED_GREEN = ("starter","lineup","bullpen","weather","roster_news")

def qualify_probability(proof, context):
    issues=[]

    if proof.get("prices_seen") is not False:
        issues.append("market-independence-failed")
    if proof.get("probabilities_frozen") is not True:
        issues.append("probabilities-not-frozen")

    prod=proof.get("production",{})
    integrity=prod.get("integrity",{})
    for key in REQUIRED_GREEN:
        if integrity.get(key) != "green":
            issues.append(f"integrity-{key}-{integrity.get(key,'missing')}")

    required_context=("park_score","weather_score","travel_rest_score","platoon_score")
    provenance=context.get("provenance",{})
    for key in required_context:
        if key not in context:
            issues.append(f"context-{key}-missing")
        if provenance.get(key) not in ("verified","exact"):
            issues.append(f"context-{key}-unverified")

    return {
        "qualified": not issues,
        "issues": issues,
        "market_evaluation_allowed": not issues,
    }
