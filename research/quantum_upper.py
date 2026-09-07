"""Numerical dimension-unrestricted moment bound; no qubit identities."""
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

from itertools import product
from functools import lru_cache
import numpy as np,cvxpy as cp,json
from scipy.sparse import coo_matrix
@lru_cache(None)
def reduce_word(w):
 out=[]
 for i in w:
  if out and out[-1]==i:out.pop()
  else:out.append(i)
 return tuple(out)
words={((),())}
for n in range(1,3):
 for w in product(range(6),repeat=n):words.add((reduce_word(tuple(i for i in w if i<3)),reduce_word(tuple(i-3 for i in w if i>=3))))
words=sorted(words,key=lambda w:(sum(map(len,w)),w));n=len(words)
entries=[(reduce_word(a[::-1]+c),reduce_word(b[::-1]+d)) for a,b in words for c,d in words]
keys=sorted(set(entries));lookup={k:i for i,k in enumerate(keys)}
R=coo_matrix((np.ones(n*n),(np.arange(n*n),[lookup[e] for e in entries])),shape=(n*n,len(keys))).tocsr()
y=cp.Variable(len(keys));M=cp.Variable((n,n),symmetric=True)
constraints=[M>>0,y[lookup[(),()]]==1,cp.reshape(M,(n*n,),order='C')==R@y]
w=[1,-1,1,-1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1]
f=sum(w[i]*y[lookup[(i,),()]]+w[3+i]*y[lookup[(),(i,)]] for i in range(3))+sum(w[6+3*i+j]*y[lookup[(i,),(j,)]] for i,j in product(range(3),repeat=2))
problem=cp.Problem(cp.Maximize(f),constraints);problem.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9)
print('unrestricted quantum numerical upper',problem.value,problem.status,flush=True)
np.savez_compressed((OUTPUT_DIR/'quantum_upper.npz'),Z=constraints[0].dual_value)
# Rationalize and bound the full residual, explicitly averaging adjoints.
from fractions import Fraction as F
D=10**9;ZZ=constraints[0].dual_value
Z=[[F(round(float((ZZ[i,j]+ZZ[j,i])/2)*D),D)+(F(1,10**7) if i==j else 0) for j in range(n)] for i in range(n)]
L=[[F(0) for _ in range(n)] for _ in range(n)];diag=[]
for i in range(n):
 d=Z[i][i]-sum(L[i][k]**2*diag[k] for k in range(i));assert d>0;diag.append(d);L[i][i]=F(1)
 for j in range(i+1,n):L[j][i]=(Z[j][i]-sum(L[j][k]*L[i][k]*diag[k] for k in range(i)))/d
poly={}
for i,(a,b) in enumerate(words):
 for j,(c,d) in enumerate(words):
  u,v=reduce_word(a[::-1]+c),reduce_word(b[::-1]+d)
  # Use the same label for a word and its adjoint: expectations of their
  # Hermitian parts are equal; each Hermitian part has norm at most 1.
  key=min((u,v),(u[::-1],v[::-1]));poly[key]=poly.get(key,F(0))+Z[i][j]
beta=poly.pop(((),()),F(0))
for i in range(3):
 for key,z in [(((i,),()),w[i]),(((),(i,)),w[3+i])]:poly[key]=poly.get(key,F(0))+z
for i,j in product(range(3),repeat=2):key=((i,),(j,));poly[key]=poly.get(key,F(0))+w[6+3*i+j]
r=sum(abs(z) for z in poly.values());bound=beta+r
print('exact quantum upper',str(bound),float(bound),'residual',float(r),flush=True)
(OUTPUT_DIR/'quantum_upper_certificate.json').write_text(json.dumps({'bound':str(bound),'constant':str(beta),'residual':str(r),'gram':[[str(x) for x in r] for r in Z],'words':words,'coefficients':w},indent=2))
