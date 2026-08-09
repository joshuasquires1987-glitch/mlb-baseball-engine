from .types import ExecutionDecision
def implied_probability(odds):
    if odds<=1: raise ValueError('Decimal odds must be > 1')
    return 1/odds
def half_kelly(prob,odds):
    b=odds-1; q=1-prob; return max(0,((b*prob-q)/b)/2)
def production_decision(prediction,prices,min_edge_pp=3.0):
    he=(prediction.home_win_probability-implied_probability(prices.home_decimal))*100
    ae=(prediction.away_win_probability-implied_probability(prices.away_decimal))*100
    if he>=ae: side,edge,prob,odds='home',he,prediction.home_win_probability,prices.home_decimal
    else: side,edge,prob,odds='away',ae,prediction.away_win_probability,prices.away_decimal
    eligible=edge>=min_edge_pp and not prediction.integrity.unresolved_red()
    return ExecutionDecision(prediction.model_version,side if eligible else None,edge,eligible,half_kelly(prob,odds) if eligible else 0.0,'Production decision uses production model only.')
