def edge_bucket(edge_pp):
    e=float(edge_pp)
    if e < 3: return "<3pp"
    if e < 5: return "+3-5pp"
    if e < 8: return "+5-8pp"
    return "+8+pp"

def price_band(decimal_odds):
    o=float(decimal_odds)
    if o <= 1.50: return "<=1.50"
    if o <= 1.75: return "1.51-1.75"
    if o <= 2.00: return "1.76-2.00"
    if o <= 2.50: return "2.01-2.50"
    return ">2.50"

def favorite_underdog(decimal_odds):
    return "favorite" if float(decimal_odds)<2.0 else "underdog"

def uncertainty_band(confidence):
    c=float(confidence)
    if c < .10: return "low-confidence"
    if c < .25: return "medium-confidence"
    return "high-confidence"
