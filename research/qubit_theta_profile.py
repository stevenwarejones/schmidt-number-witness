"""theta-profile of max_U G for the (pre-certificate) qubit conjecture G <= 7.
Retained as the record of what the conjecture looked like before the exact Gram
certificate resolved it.  Closed-form objective, so millions of evaluations are cheap."""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
import numpy as np
from scipy.optimize import minimize
a=np.array([1.,-1,1]); b=np.array([-1.,-1,1])
E=np.array([[-1,-1,-1],[-1,-1,1],[1,-1,-1]],float)
def Gvec(theta,U):
    c=np.cos(2*theta); s=np.sin(2*theta)
    w=np.einsum('xy,nxi->nyi',E,U)
    t=np.sqrt(s*s*(w[...,0]**2+w[...,1]**2)+(w[...,2]+c*b)**2)
    return c*np.einsum('x,nx->n',a,U[:,:,2])+t.sum(axis=1)
def rand_U(n,rng):
    v=rng.normal(size=(n,3,3)); return v/np.linalg.norm(v,axis=2,keepdims=True)
def unpack(p):
    ang=p[1:].reshape(3,2)
    return p[0],np.stack([np.array([np.sin(t)*np.cos(f),np.sin(t)*np.sin(f),np.cos(t)])
                          for t,f in ang])
if __name__=='__main__':
    rng=np.random.default_rng(20260906)
    print(f"{'theta/pi':>9} {'random max':>13} {'after polish':>14}")
    for frac in np.linspace(0,0.25,26):
        th=frac*np.pi
        v=np.concatenate([Gvec(th,rand_U(40000,rng)) for _ in range(12)])
        U0=rand_U(400000,rng); g=Gvec(th,U0); pol=v.max()
        for i in np.argsort(g)[-12:]:
            u=U0[i]
            ang=np.array([[np.arccos(np.clip(u[k,2],-1,1)),np.arctan2(u[k,1],u[k,0])]
                          for k in range(3)]).ravel()
            r=minimize(lambda q:-Gvec(th,unpack(np.concatenate([[th],q]))[1][None,...])[0],
                       ang,method='Nelder-Mead',
                       options={'maxiter':4000,'fatol':1e-13,'xatol':1e-11})
            pol=max(pol,-r.fun)
        print(f"{frac:9.3f} {v.max():13.9f} {pol:14.9f}")
