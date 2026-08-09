from math import exp, log

def half_life_weight(age_days,half_life_days):
    return 0.5 ** (float(age_days)/float(half_life_days))

def shrunk_rate(numerator,denominator,prior_rate,prior_weight):
    denominator=float(denominator)
    return (float(numerator)+float(prior_rate)*float(prior_weight))/(denominator+float(prior_weight))

def bounded_score(x,center,scale,lo=-3.0,hi=3.0,invert=False):
    if scale<=0:
        raise ValueError("scale must be positive")
    z=(float(x)-float(center))/float(scale)
    if invert: z=-z
    return max(lo,min(hi,z))
