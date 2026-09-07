"""Endpoint behavior of the (pre-certificate) qubit objective.

Numerical endpoint searches are consistent with a cubic deficit in the OPTIMIZED objective
max_U G(theta,U) over the sampled range.  That is an observation on a sampled range, not an
asymptotic law, and it does not assert that the derivative vanishes for every fixed
measurement configuration -- norm terms can be degenerate.  The exact sharp-bound
certificate is independent of this numerical observation and supersedes it.

Retained only as the record of what the conjecture looked like before the certificate.
Shipped workload: seven positive theta values, 160 Nelder-Mead restarts each, plus a
least-squares fit of the deficit exponent over the five smallest values.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
import numpy as np
from scipy.optimize import minimize
a=np.array([1.,-1,1]); b=np.array([-1.,-1,1])
E=np.array([[-1,-1,-1],[-1,-1,1],[1,-1,-1]],float)
def G1(th,U):
    c=np.cos(2*th); s=np.sin(2*th)
    w=np.einsum('xy,xi->yi',E,U)
    t=np.sqrt(s*s*(w[:,0]**2+w[:,1]**2)+(w[:,2]+c*b)**2)
    return c*(a*U[:,2]).sum()+t.sum()
def U_of(q):
    q=q.reshape(3,2)
    return np.stack([np.array([np.sin(t)*np.cos(f),np.sin(t)*np.sin(f),np.cos(t)])
                     for t,f in q])
if __name__=='__main__':
    rng=np.random.default_rng(7)
    rec=[]
    print(f"{'theta/pi':>10} {'max_U G':>18} {'7 - max':>14}")
    for frac in (0.0005,0.001,0.002,0.004,0.008,0.015,0.03):
        th=frac*np.pi; best=-9
        for _ in range(160):
            q=rng.uniform(0,np.pi,6); q[1::2]=rng.uniform(0,2*np.pi,3)
            r=minimize(lambda z:-G1(th,U_of(z)),q,method='Nelder-Mead',
                       options={'maxiter':20000,'maxfev':20000,'fatol':1e-15,'xatol':1e-13})
            best=max(best,-r.fun)
        print(f"{frac:10.4f} {best:18.12f} {7-best:14.3e}")
        rec.append((th,7-best))
    # Only fit where the deficit is positive and comfortably above optimizer noise: a tiny
    # negative or rounding-level deficit would make the logarithm meaningless.
    FLOOR = 1e-12
    usable = [(t, d) for t, d in rec[:5] if d > FLOOR]
    if len(usable) < 3:
        print(f"\nnot fitting: only {len(usable)} deficits exceed {FLOOR:g}; "
              "the remainder are at or below optimizer noise")
    else:
        x = np.log([t for t, _ in usable]); y = np.log([d for _, d in usable])
        print(f"\nfitted deficit exponent over {len(usable)} points with deficit > {FLOOR:g}: "
              f"{np.polyfit(x, y, 1)[0]:.4f}")
        print("(a fit to an optimizer envelope over a sampled range, not an asymptotic law)")
