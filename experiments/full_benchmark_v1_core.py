"""Core generators and two realization engines for full benchmark v1."""
from __future__ import annotations
from dataclasses import dataclass
import time
import numpy as np
from sklearn.isotonic import IsotonicRegression

PRIMITIVES=("direction","curvature","inflection","turning","regime","bound","asymptote")

def ridge(X,y,lam=1e-5):
    gram=np.einsum("ni,nj->ij",X,X); rhs=np.einsum("ni,n->i",X,y)
    return np.linalg.solve(gram+lam*np.eye(X.shape[1]),rhs)
def linear_predict(X,coef): return np.sum(X*coef[None,:],axis=1)

class SplineEngine:
    name="constrained_spline"
    def design(self,x,knots):
        return np.column_stack([np.ones(len(x)),x,x*x,x*x*x]+[np.maximum(x-k,0)**3 for k in knots])
    def fit_predict(self,x,y,xq):
        t=time.perf_counter(); knots=np.linspace(float(x.min()),float(x.max()),5)[1:-1]
        X=self.design(x,knots); Xq=self.design(xq,knots); best=None
        # Three fixed regularization initializations; closed-form solves stay below budget.
        for lam in (1e-6,1e-4,1e-2):
            coef=ridge(X,y,lam); loss=float(np.mean((linear_predict(X,coef)-y)**2))
            if best is None or loss<best[0]: best=(loss,coef,lam)
        pred=linear_predict(Xq,best[1])
        return pred,{"engine":self.name,"parameter_count":X.shape[1],"solver_evaluations":3,
                     "initializations":3,"converged":True,"solver_failure":False,
                     "wall_time":time.perf_counter()-t,"regularization":best[2]}

class NeuralBasisEngine:
    name="constrained_neural_basis_8"
    def design(self,x,shift):
        centers=np.linspace(float(x.min()),float(x.max()),8)+shift
        width=max(float(np.ptp(x))/5,1e-4)
        return np.column_stack([np.ones(len(x)),x]+[np.tanh((x-c)/width) for c in centers])
    def fit_predict(self,x,y,xq):
        t=time.perf_counter(); scale=max(float(np.ptp(x)),1e-4); best=None
        for shift in (-.015*scale,0,.015*scale):
            X=self.design(x,shift); Xq=self.design(xq,shift); coef=ridge(X,y,1e-4)
            loss=float(np.mean((linear_predict(X,coef)-y)**2))
            if best is None or loss<best[0]: best=(loss,coef,shift,Xq,X.shape[1])
        pred=linear_predict(best[3],best[1])
        return pred,{"engine":self.name,"parameter_count":best[4],"solver_evaluations":3,
                     "initializations":3,"converged":True,"solver_failure":False,
                     "wall_time":time.perf_counter()-t,"center_shift":best[2]}

ENGINES={"spline":SplineEngine(),"neural":NeuralBasisEngine()}

def _normalize(y):
    return (y-y[0])/max(float(np.ptp(y)),1e-8)

def generate_truth(composition,generator,x,rng,effect=1.0,heterogeneity=0.0):
    """Generate a clean trajectory and latent realization metadata.

    Formula varies by generator while the requested structural composition is
    preserved by the registered dominant mechanism.
    """
    p=set(composition); tau=float(rng.uniform(.30,.55)); sign=float(rng.choice([-1,1]));
    amp=float(rng.uniform(.8,1.2)*(1+rng.normal(0,heterogeneity))); k=float(rng.uniform(3.5,6.5)*effect)
    meta={"tau":tau,"sign":sign,"bound":0.0,"limit":0.0,"rate":k,"effect":effect}
    mult={"spline":1.0,"basis":1.08,"ode":.92}.get(generator,1.0)
    if "regime" in p:
        k1=max(.2,k*.25); k2=max(.4,k*1.15)
        if "asymptote" in p or "bound" in p:
            y=np.where(x<tau,amp*np.exp(-k1*x),amp*np.exp(-k1*tau)*np.exp(-k2*(x-tau)))
            meta["sign"]=-1.0
        else: y=.2*x+sign*amp*np.maximum(x-tau,0)**1.3
    elif "turning" in p:
        if "asymptote" in p: y=amp*np.exp(-k*mult*(x-tau)**2)
        else: y=sign*amp*(x-tau)**2
    elif "inflection" in p:
        if "asymptote" in p or "bound" in p:
            y=amp/(1+np.exp(k*mult*(x-tau))); meta["sign"]=-1.0
        else: y=sign*amp*(x-tau)**3
    elif "asymptote" in p:
        y=sign*amp*np.exp(-k*mult*x); meta["sign"]=-sign
    elif "curvature" in p:
        y=sign*amp*(x+.6*effect*x*x); meta["curvature_sign"]=sign
    elif "direction" in p:
        y=sign*amp*(x+.08*generator.count("s")*x*x)
    elif "bound" in p:
        y=.55+.35*np.sin(2*np.pi*(1.1+effect*.2)*x+rng.uniform(0,2*np.pi))
    else:
        y=np.sin(2*np.pi*(7*x+2*x*x)+rng.uniform(0,2*np.pi))
    if "bound" in p:
        y=y-float(np.min(y))+.05; meta["bound"]=0.0
    return y,meta

def fit_engine(engine,x,y,xq): return ENGINES[engine].fit_predict(np.asarray(x),np.asarray(y),np.asarray(xq))

def _project_direction(y,increasing):
    ir=IsotonicRegression(increasing=increasing,out_of_bounds="clip")
    return ir.fit_transform(np.arange(len(y)),y)

def _project_curvature(y,convex):
    slope=np.diff(y); ir=IsotonicRegression(increasing=convex,out_of_bounds="clip")
    s=ir.fit_transform(np.arange(len(slope)),slope); return np.r_[y[0],y[0]+np.cumsum(s)]

def apply_prior(base,x,train_max,primitives,params):
    """Apply an AND-conjunction continuation constraint to an engine curve."""
    y=np.asarray(base,float).copy(); p=set(primitives); future=x>train_max
    if not np.any(future): return y
    idx=int(np.searchsorted(x,train_max,side="right")-1); idx=max(idx,1)
    xb=x[idx]; yb=y[idx]; slope=(y[idx]-y[idx-1])/max(x[idx]-x[idx-1],1e-8)
    if "regime" in p:
        tau=float(params.get("tau",train_max)); rate=float(params.get("rate",abs(slope)*2+1e-3)); z=np.maximum(x-tau,0)
        y[future]=yb+slope*(x[future]-xb)-np.sign(max(slope,1e-8))*rate*z[future]**1.3
    if "turning" in p:
        tau=float(params.get("tau",train_max+.2)); scale=float(params.get("rate",max(abs(slope),.2)))
        center=yb+slope*(tau-xb); y[future]=center+np.sign(params.get("sign",1))*scale*(x[future]-tau)**2
    if "inflection" in p:
        tau=float(params.get("tau",train_max+.2)); scale=float(params.get("rate",.5))
        y[future]=yb+slope*(x[future]-xb)+params.get("sign",1)*scale*(x[future]-tau)**3
    if "asymptote" in p:
        L=float(params.get("limit",params.get("bound",0))); rate=max(float(params.get("rate",2)),.05)
        y[future]=L+(yb-L)*np.exp(-rate*(x[future]-xb))
    if "direction" in p:
        y[idx:]=_project_direction(y[idx:],params.get("sign",-1)>0)
    if "curvature" in p:
        y[idx:]=_project_curvature(y[idx:],params.get("curvature_sign",params.get("sign",1))>0)
    if "bound" in p:
        L=float(params.get("bound",0)); side=params.get("bound_side","lower")
        y[future]=np.maximum(y[future],L) if side=="lower" else np.minimum(y[future],L)
    return y

def realized_prediction(engine,xobs,yobs,xq,primitives,params,residual_weight=.25):
    base,diag=fit_engine(engine,xobs,yobs,xq); prior=apply_prior(base,xq,float(xobs.max()),primitives,params)
    pobs=np.interp(xobs,xq,prior); residual=yobs-pobs
    rpred,rdiag=fit_engine(engine,xobs,residual,xq)
    out=prior+residual_weight*rpred
    diag={**diag,"residual_parameter_count":rdiag["parameter_count"],"residual_solver_failure":rdiag["solver_failure"]}
    return out,diag
