"""Counterexample search, NOT a certified upper bound. Includes binary POVM extremes.
Pure states in Schmidt form suffice for the global optimization. At a maximum,
every binary observable may be chosen projective: a Bloch unit vector or +/-I.
Optimize Bob analytically; enumerate Alice's 3^3 rank patterns. All-rank-one
Alice uses an azimuth gauge to remove one redundant angle. SciPy required.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

from itertools import product
import json
import numpy as np
from scipy.optimize import differential_evolution
AC=np.array([1.,-1.,1.]);BC=np.array([-1.,-1.,1.])
E=np.array([[-1.,-1.,-1.],[-1.,-1.,1.],[1.,-1.,-1.]])

def decode(z,pattern):
 theta=z[0];v=np.zeros((3,3));alpha=np.array(pattern,dtype=float);j=1
 for x,p in enumerate(pattern):
  if p==0:
   polar=z[j];az=z[j+1];j+=2
   v[x]=[np.sin(polar)*np.cos(az),np.sin(polar)*np.sin(az),np.cos(polar)]
 return theta,alpha,v

def evaluate(z,pattern,details=False):
 theta,alpha,v=decode(z,pattern);c=np.cos(2*theta);s=np.sin(2*theta)
 # A=alpha I+v.sigma; reduced local z polarization c, T=diag(s,-s,1).
 alice=alpha+c*v[:,2]
 const=AC@alice
 bob_scalar=BC+E.T@alpha
 bob_vector=E.T@v
 identity=c*bob_vector[:,2]+bob_scalar
 vector=bob_vector*np.array([s,-s,1.]);vector[:,2]+=c*bob_scalar
 norm=np.linalg.norm(vector,axis=1)
 score=float(const+np.maximum(np.abs(identity),norm).sum())
 if not details:return score
 b=[]
 for t,h,n in zip(identity,vector,norm):
  b.append({'alpha':float(np.sign(t) or 1),'vector':[0.,0.,0.]} if abs(t)>=n else {'alpha':0.,'vector':(h/n).tolist()})
 return {'score':score,'theta':float(theta),'Alice':[{'alpha':float(a),'vector':r.tolist()} for a,r in zip(alpha,v)],'Bob':b}

def independent_score(d):
 I=np.eye(2);P=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])
 def obs(o):return o['alpha']*I+np.einsum('i,ijk->jk',o['vector'],P)
 A=list(map(obs,d['Alice']));B=list(map(obs,d['Bob']));psi=np.array([np.cos(d['theta']),0,0,np.sin(d['theta'])])
 H=sum(AC[x]*np.kron(A[x],I) for x in range(3))+sum(BC[y]*np.kron(I,B[y]) for y in range(3))+sum(E[x,y]*np.kron(A[x],B[y]) for x,y in product(range(3),repeat=2))
 return float(np.vdot(psi,H@psi).real)

if __name__=='__main__':
 results=[]
 for pattern in product([-1,0,1],repeat=3):
  count=pattern.count(0);bounds=[(0,np.pi/4)]+[(0,np.pi),(0,2*np.pi)]*count
  if count:bounds[2]=(0,0) # common z rotation is immaterial in Schmidt form
  for seed in range(4 if count==3 else 1):
   r=differential_evolution(lambda z:-evaluate(z,pattern),bounds,seed=9100+seed,popsize=18,maxiter=700,tol=1e-10,polish=True)
   d=evaluate(r.x,pattern,True);d.update(pattern=list(pattern),seed=seed,success=bool(r.success),evaluations=r.nfev)
   d['independent_score']=independent_score(d);assert abs(d['score']-d['independent_score'])<1e-10
   results.append(d);print(pattern,seed,d['score'],flush=True)
 out={'status':'Numerical lower bounds only; no certified qubit upper bound','maximum':max(r['score'] for r in results),'runs':results}
 (OUTPUT_DIR/'qubit_search_results.json').write_text(json.dumps(out,indent=2))
