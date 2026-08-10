def _person_id(obj):
    if not isinstance(obj, dict):
        return None
    v = obj.get("id")
    return str(v) if v is not None else None


def probable_starter_ids(state):
    gd = (state or {}).get("gameData") or {}
    pp = gd.get("probablePitchers") or {}
    return {"away": _person_id(pp.get("away")), "home": _person_id(pp.get("home"))}


def player_map(state):
    gd = (state or {}).get("gameData") or {}
    players = gd.get("players") or {}
    out = {}
    for p in players.values():
        pid = p.get("id")
        if pid is None:
            continue
        out[str(pid)] = {
            "bat_side": (p.get("batSide") or {}).get("code"),
            "pitch_hand": (p.get("pitchHand") or {}).get("code"),
        }
    return out


def lineup_bat_sides(order, players):
    out = []
    for pid in order:
        row = players.get(str(pid))
        if not row or row.get("bat_side") not in {"L", "R", "S"}:
            return None
        out.append(row["bat_side"])
    return out


def starter_hand(starter_id, players):
    if starter_id is None:
        return None
    row = players.get(str(starter_id))
    if not row:
        return None
    hand = row.get("pitch_hand")
    return hand if hand in {"L", "R"} else None
