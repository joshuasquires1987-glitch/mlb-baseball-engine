def clip(x,lo=-3.0,hi=3.0):
    return max(lo,min(hi,float(x)))

def advantage(home,away,scale=1.0):
    return clip((float(home)-float(away))/float(scale))

def centered(value,center=0.0,scale=1.0):
    return clip((float(value)-float(center))/float(scale))

def expected_bullpen_outs(expected_starter_outs):
    return max(0.0,min(27.0,27.0-float(expected_starter_outs)))

def bullpen_exposure_quality(home_expected_outs,away_expected_outs,home_bp,away_bp,scale=1.0):
    home_exp=expected_bullpen_outs(home_expected_outs)
    away_exp=expected_bullpen_outs(away_expected_outs)
    # Higher bullpen_score is assumed better. Positive output favors home.
    return clip((home_exp*float(home_bp)-away_exp*float(away_bp))/float(scale))
