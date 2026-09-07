"""Exact Gram kernel forced by product-state equality families."""
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

import sys
src=(Path(__file__).resolve().parent/'clifford_bound.py').read_text().split('problem=cp.Problem')[0]
sys.argv=[sys.argv[0],'3'];exec(src)
from itertools import combinations
sat=[]
for aa,bb in product(product([-1,1],repeat=3),repeat=2):
 if sum(a[i]*aa[i]+b[i]*bb[i] for i in range(3))+sum(E[i][j]*aa[i]*bb[j] for i,j in product(range(3),repeat=2))==7:sat.append(aa+bb)
edges=[(x,y) for x,y in combinations(sat,2) if sum(a!=b for a,b in zip(x,y))==1]
polars=[(sp.Integer(0),sp.Integer(0),sp.Integer(-1))]
for u,v in product(range(-2,3),repeat=2):
 d=1+u*u+v*v;polars.append((sp.Rational(2*u,d),sp.Rational(2*v,d),sp.Rational(1-u*u-v*v,d)))
# Matrix products acting on |0>, expanded after every step.
Zp=sp.diag(1,-1);Ip=sp.eye(2)
rows=[]
for aa,bb in edges:
 free=next(i for i,(x,y) in enumerate(zip(aa,bb)) if x!=y)
 for x,y,z in polars:
  obs=[v*Zp for v in aa];obs[free]=sp.Matrix([[z,x-sp.I*y],[x+sp.I*y,-z]])
  def action(word,offset):
   v=sp.Matrix([1,0])
   for j in word[::-1]:v=(obs[offset+j]*v).applyfunc(sp.expand)
   return v
  columns=[sp.kronecker_product(action(u,0),action(v,3)) for u,v in words]
  W=sp.Matrix.hstack(*columns)
  rows.extend([list(W.row(i).applyfunc(sp.re)) for i in range(4)])
  rows.extend([list(W.row(i).applyfunc(sp.im)) for i in range(4)])
K=sp.Matrix(rows);K,_=K.rref();K=K[:K.rank(),:]
P=sp.Matrix.hstack(*K.nullspace())
print('edges',len(edges),'kernel rank',K.rows,'remaining',P.cols,flush=True)
(OUTPUT_DIR/'equality_kernel.json').write_text(json.dumps({'words':words,'K':[[str(x) for x in K.row(i)] for i in range(K.rows)],'P':[[str(x) for x in P.row(i)] for i in range(P.rows)]}))
