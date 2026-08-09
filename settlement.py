from records import Settlement

def settle_wager(wager,result,promotion_early_payout=False):
    r=result.lower()
    if r not in ("win","loss","push"):
        raise ValueError("result must be win/loss/push")
    if r=="win":
        pnl=wager.stake_cad*(wager.decimal_odds-1.0)
    elif r=="loss":
        pnl=-wager.stake_cad
    else:
        pnl=0.0
    note="Early payout promotion recorded separately." if promotion_early_payout else None
    return Settlement(wager.wager_id,r,round(pnl,2),"settled",note)
