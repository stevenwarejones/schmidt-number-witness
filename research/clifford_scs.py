"""Numerical moment upper relaxation for three traceless qubit observables/party.
Uses central anticommutators {Ai,Aj}=2 gij I. No sampled span.
Only real parts of moments are retained, giving a valid outer relaxation.
Outputs are numerical SDP estimates, not exact certificates.
"""
from functools import lru_cache
from itertools import product
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

import numpy as np, cvxpy as cp,json,time,sys
level=int(sys.argv[1]) if len(sys.argv)>1 else 3
pairs={(0,1):0,(0,2):1,(1,2):2};zero=(0,)*6
@lru_cache(None)
def norm(word,side):
 for i in range(len(word)-1):
  a,b=word[i:i+2]
  if a==b:return norm(word[:i]+word[i+2:],side)
  if a>b:
   out={}
   for (g,w),z in norm(word[:i]+(b,a)+word[i+2:],side).items():out[g,w]=out.get((g,w),0)-z
   for (g,w),z in norm(word[:i]+word[i+2:],side).items():
    gg=list(g);gg[pairs[b,a]+3*side]+=1;gg=tuple(gg);out[gg,w]=out.get((gg,w),0)+2*z
   return {k:v for k,v in out.items() if v}
 return {(zero,word):1}
@lru_cache(None)
def multiply(a,b):
 aa,ab=a;ba,bb=b;out={}
 for (g,u),r in norm(aa[::-1]+ba,0).items():
  for (h,v),s in norm(ab[::-1]+bb,1).items():
   key=(tuple(x+y for x,y in zip(g,h)),u,v);out[key]=out.get(key,0)+r*s
 return out
words={((),())}
for length in range(1,level+1):
 for raw in product(range(6),repeat=length):
  a=tuple(x for x in raw if x<3);b=tuple(x-3 for x in raw if x>=3)
  if any(x==y for w in [a,b] for x,y in zip(w,w[1:])):continue
  words.add((a,b))
words=sorted(words,key=lambda w:(sum(map(len,w)),w))
# Remove universal linear dependencies among the word vectors exactly.
import sympy as sp
normal=[multiply(((),()),w) for w in words]
normalkeys=sorted(set(k for r in normal for k in r))
_,pivots=sp.Matrix([[r.get(k,0) for r in normal] for k in normalkeys]).rref()
words=[words[i] for i in pivots];n=len(words)
entries=[[multiply(a,b) for b in words] for a in words]
keys=set(k for row in entries for e in row for k in e);keys=sorted(keys);lookup={k:i for i,k in enumerate(keys)}
y=cp.Variable(len(keys));M=cp.Variable((n,n),symmetric=True)
constraints=[M>>0,y[lookup[zero,(),()]]==1]
# All ordered entries constrained: enforces real-moment adjoint consistency.
from scipy.sparse import coo_matrix
rr=[];cc=[];vv=[]
for i in range(n):
 for j in range(n):
  for k,v in entries[i][j].items():rr.append(i*n+j);cc.append(lookup[k]);vv.append(v)
R=coo_matrix((vv,(rr,cc)),shape=(n*n,len(keys))).tocsr()
constraints+=[cp.reshape(M,(n*n,),order='C')==R@y]
a=[1,-1,1];b=[-1,-1,1];E=[[-1,-1,-1],[-1,-1,1],[1,-1,-1]]
objective=sum(a[i]*y[lookup[zero,(i,),()]]+b[i]*y[lookup[zero,(),(i,)]] for i in range(3))+sum(E[i][j]*y[lookup[zero,(i,),(j,)]] for i,j in product(range(3),repeat=2))
problem=cp.Problem(cp.Maximize(objective),constraints)
print('level',level,'matrix',n,'moments',len(keys),flush=True);t=time.time()
problem.solve(solver='SCS',eps=1e-10,max_iters=60000,acceleration_lookback=20)
print('status',problem.status,'value',problem.value,'seconds',time.time()-t,flush=True)
out={'level':level,'matrix_size':n,'moments':len(keys),'status':problem.status,'numerical_value':problem.value,'seconds':time.time()-t,'warning':'No exact PSD or dual certificate; do not claim proved bound'}
(OUTPUT_DIR/f'clifford_scs_level{level}.json').write_text(json.dumps(out,indent=2))
if y.value is not None:np.savez((OUTPUT_DIR/f'clifford_scs_level{level}.npz'),moments=y.value,psd_dual=constraints[0].dual_value,normalization_dual=constraints[1].dual_value,equality_dual=constraints[2].dual_value,R=R.toarray())
