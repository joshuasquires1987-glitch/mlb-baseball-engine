def _code(value):
    if isinstance(value, dict):
        value = value.get("code")
    return str(value or "").upper()


def hitter_has_platoon_advantage(bat_side, pitcher_hand):
    b = _code(bat_side)
    p = _code(pitcher_hand)
    if b not in {"L", "R", "S"} or p not in {"L", "R"}:
        raise ValueError("valid hitter bat side and pitcher hand required")
    if b == "S":
        return 1.0
    return 1.0 if b != p else 0.0


def lineup_advantage_share(bat_sides, pitcher_hand):
    if len(bat_sides) != 9:
        raise ValueError("exactly nine hitter bat sides required")
    vals = [hitter_has_platoon_advantage(x, pitcher_hand) for x in bat_sides]
    return sum(vals) / 9.0


def platoon_lineup_delta(home_bat_sides, away_bat_sides, home_sp_hand, away_sp_hand):
    home = lineup_advantage_share(home_bat_sides, away_sp_hand)
    away = lineup_advantage_share(away_bat_sides, home_sp_hand)
    return home - away
