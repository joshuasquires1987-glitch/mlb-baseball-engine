from math import log

def brier(prob,outcome):
    return (float(prob)-float(outcome))**2

def log_loss(prob,outcome,eps=1e-12):
    p=min(max(float(prob),eps),1-eps)
    y=int(outcome)
    return -(y*log(p)+(1-y)*log(1-p))

def intact_implied_probability(decimal_odds):
    if decimal_odds<=1:
        raise ValueError("Decimal odds must be > 1")
    return 1.0/decimal_odds

def predicted_edge_pp(model_prob,decimal_odds):
    return (float(model_prob)-intact_implied_probability(decimal_odds))*100.0

def clv_pp(entry_odds,closing_odds):
    return (intact_implied_probability(closing_odds)-intact_implied_probability(entry_odds))*100.0

def kelly_fraction(prob,decimal_odds):
    b=decimal_odds-1.0
    q=1.0-prob
    return max(0.0,(b*prob-q)/b)

def half_kelly_fraction(prob,decimal_odds):
    return kelly_fraction(prob,decimal_odds)/2.0
