def lineup_readiness(away_confirmed,home_confirmed):
    if away_confirmed and home_confirmed:
        return {"lineup_integrity":"green","both_confirmed":True}
    return {"lineup_integrity":"yellow","both_confirmed":False}
