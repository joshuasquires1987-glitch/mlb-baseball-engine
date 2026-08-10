import numpy as np
FEATURES=("park_factor_delta","temperature_delta_f","wind_out_mph","wind_in_mph","travel_timezone_delta_hours","rest_days_delta","platoon_lineup_delta")
def sigmoid(z): return 1/(1+np.exp(-np.clip(z,-35,35)))
def log_loss(y,p):
 p=np.clip(np.asarray(p,float),1e-12,1-1e-12); y=np.asarray(y,float)
 return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
def brier(y,p): return float(np.mean((np.asarray(p,float)-np.asarray(y,float))**2))
def chronological_split(rows,frac=.25):
 o=sorted(rows,key=lambda r:(str(r["game_date"]),str(r["game_id"]))); h=max(150,round(len(o)*frac))
 return o[:-h],o[-h:]
def fit(train,l2=1.0):
 X=np.array([[float(r[k]) for k in FEATURES] for r in train]); y=np.array([r["home_win"] for r in train],float)
 mu=X.mean(0); sd=X.std(0); sd=np.where(sd<1e-12,1,sd); Z=(X-mu)/sd; A=np.c_[np.ones(len(Z)),Z]; b=np.zeros(A.shape[1])
 for _ in range(100):
  p=sigmoid(A@b); w=np.clip(p*(1-p),1e-8,None); g=A.T@(p-y); g[1:]+=l2*b[1:]
  H=A.T@(A*w[:,None]); H[1:,1:]+=l2*np.eye(A.shape[1]-1); step=np.linalg.solve(H,g); b-=step
  if abs(step).max()<1e-9: break
 raw=b[1:]/sd; intercept=float(b[0]-np.dot(b[1:],mu/sd))
 return intercept,{k:float(v) for k,v in zip(FEATURES,raw)}
def evaluate(train,hold):
 intercept,c=fit(train); X=np.array([[float(r[k]) for k in FEATURES] for r in hold]); y=np.array([r["home_win"] for r in hold],float)
 p=sigmoid(intercept+X@np.array([c[k] for k in FEATURES])); p0=np.full(len(y),float(sigmoid(intercept)))
 return intercept,c,log_loss(y,p),log_loss(y,p0),brier(y,p),brier(y,p0)
