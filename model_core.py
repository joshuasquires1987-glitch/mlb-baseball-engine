from math import exp
from engine_types import ModelPrediction

def sigmoid(x): return 1/(1+exp(-x))

def weighted_probability(inputs,model_version,weights):
    score=sum(float(inputs.features.get(k,0))*float(w) for k,w in weights.items())
    p=sigmoid(score)
    return ModelPrediction(inputs.game_id,model_version,p,1-p,abs(p-.5)*2,inputs.integrity,True)
