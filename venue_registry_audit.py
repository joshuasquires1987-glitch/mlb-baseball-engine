def audit_registry(games, registry):
    used = {str(g["venue_id"]) for g in games if g.get("venue_id") is not None}
    rows = registry.get("rows", [])
    by_id = {str(r["venue_id"]): r for r in rows}

    missing = sorted(used - set(by_id))
    malformed = []
    for vid in sorted(used & set(by_id)):
        if by_id[vid].get("utc_offset_hours") is None:
            malformed.append(vid)

    return {
        "venues_used": len(used),
        "venues_registered": len(used & set(by_id)),
        "missing_venue_ids": missing,
        "malformed_venue_ids": malformed,
        "complete": not missing and not malformed,
    }
