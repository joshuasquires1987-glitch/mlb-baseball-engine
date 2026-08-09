def calibration_bins(rows,bins=None):
    bins=bins or [(0,.4),(.4,.45),(.45,.5),(.5,.55),(.55,.6),(.6,1.0)]
    out=[]
    for lo,hi in bins:
        q=[r for r in rows if lo <= r["model_prob"] < hi or (hi==1.0 and lo <= r["model_prob"] <= hi)]
        if q:
            out.append({
                "low":lo,"high":hi,"n":len(q),
                "mean_pred":sum(r["model_prob"] for r in q)/len(q),
                "actual_rate":sum(r["outcome"] for r in q)/len(q),
            })
    return out

def calibration_gap(rows):
    bins=calibration_bins(rows)
    if not bins: return None
    n=sum(b["n"] for b in bins)
    return sum(abs(b["actual_rate"]-b["mean_pred"])*b["n"] for b in bins)/n
