import itertools, json, math
import numpy as np
from rc2_context_calibration import FEATURES, sigmoid, log_loss, brier

GROUPS={
 "park":("park_factor_delta",),
 "weather":("temperature_delta_f","wind_out_mph","wind_in_mph"),
 "travel_rest":("travel_timezone_delta_hours","rest_days_delta"),
 "platoon":("platoon_lineup_delta",),
}

def fit_subset(train,features,l2=1.0):
 X=np.array([[float(r[k]) for k in features] for r in train],float)
 y=np.array([float(r["home_win"]) for r in train],float)
 mu=X.mean(0); sd=X.std(0); sd=np.where(sd<1e-12,1.0,sd)
 A=np.c_[np.ones(len(X)),(X-mu)/sd]; beta=np.zeros(A.shape[1])
 for _ in range(100):
  p=sigmoid(A@beta); w=np.clip(p*(1-p),1e-8,None)
  g=A.T@(p-y); g[1:]+=l2*beta[1:]
  H=A.T@(A*w[:,None]); H[1:,1:]+=l2*np.eye(A.shape[1]-1)
  step=np.linalg.solve(H,g); beta-=step
  if np.max(np.abs(step))<1e-9: break
 raw=beta[1:]/sd
 return float(beta[0]-np.dot(beta[1:],mu/sd)),{k:float(v) for k,v in zip(features,raw)}

def score(train,test,features):
 intercept,c=fit_subset(train,features)
 y=np.array([float(r["home_win"]) for r in test])
 X=np.array([[float(r[k]) for k in features] for r in test])
 p=sigmoid(intercept+X@np.array([c[k] for k in features]))
 p0=np.full(len(y),float(sigmoid(intercept)))
 return {"features":list(features),"coefficients":c,"log_loss":log_loss(y,p),
 "baseline_log_loss":log_loss(y,p0),"logloss_delta":log_loss(y,p)-log_loss(y,p0),
 "brier":brier(y,p),"baseline_brier":brier(y,p0)}

def expanding_folds(rows,folds=4,min_train=700):
 o=sorted(rows,key=lambda r:(str(r["game_date"]),str(r["game_id"])))
 remaining=len(o)-min_train; size=remaining//folds; out=[]
 for i in range(folds):
  end=min_train+i*size; test_end=len(o) if i==folds-1 else end+size
  out.append((o[:end],o[end:test_end]))
 return out

def diagnostics(rows):
 specs=[("all",FEATURES)]
 specs += [(f"only_{k}",v) for k,v in GROUPS.items()]
 specs += [(f"drop_{k}",tuple(x for x in FEATURES if x not in v)) for k,v in GROUPS.items()]
 results=[]
 for name,features in specs:
  folds=[]
  for i,(tr,te) in enumerate(expanding_folds(rows),1):
   x=score(tr,te,features); x["fold"]=i; x["train_n"]=len(tr); x["test_n"]=len(te); folds.append(x)
  results.append({"spec":name,"features":list(features),"folds":folds,
   "mean_logloss_delta":float(np.mean([x["logloss_delta"] for x in folds])),
   "improving_folds":sum(x["logloss_delta"]<0 for x in folds)})
 return results
