"""Exact one-sided face upper bounds from positive dual support.
SymPy required. Lower bounds come from explicitly supplied NS points satisfying
all CHSH inequalities on a designated 2x3 restriction.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
from pathlib import Path
from itertools import product,combinations
import json
import sympy as s
p=Path(__file__).parent;c=json.loads((p/'facet_certificate.json').read_text())

def rows(side,pair):
 r=[]
 for x,y,a,b in product(range(3),range(3),[-1,1],[-1,1]):
  q=[0]*16;q[0]=1;q[1+x]=a;q[4+y]=b;q[7+3*x+y]=a*b;r.append(q)
 for other in combinations(range(3),2):
  ix=list(product(pair,other)) if side=='A' else list(product(other,pair))
  for signs in product([-1,1],repeat=4):
   if s.prod(signs)==-1:
    q=[0]*16;q[0]=2
    for sign,(x,y) in zip(signs,ix):q[7+3*x+y]=-sign
    r.append(q)
 return r
spaces={k:[] for k in ['A','B']}
for d in c['partial_hull_duals']:
 rr=rows(d['side'],d['pair']);weights=list(map(s.Rational,d['weights']))
 assert min(weights)>=0
 assert list((s.Matrix([weights])*s.Matrix(rr)))==[7]+[-x for x in c['w']]
 active=s.Matrix([r for r,w in zip(rr,weights) if w>0])
 spaces[d['side']]+=active.nullspace()
# Nullspace is homogeneous span of (1,v) allowed by necessary face equalities.
# Combining these spaces gives an upper bound, even without feasibility.
upper={k:s.Matrix.hstack(*v).rank()-1 for k,v in spaces.items()}
points=json.loads((p/'face_dimension_points.json').read_text())
for side in ['A','B']:
 vv=[]
 for e in points[side]:
  v=[s.Rational(z) for z in e['v']];assert len(v)==15
  assert sum(a*b for a,b in zip(c['w'],v))==7
  assert tuple(e['pair']) in list(combinations(range(3),2))
  assert min(s.Matrix(rows(side,e['pair']))*s.Matrix([1]+v))>=0
  vv.append([1]+v)
 lower=s.Matrix(vv).rank()-1
 assert lower==upper[side]==13
 print('PASS',side,'face dimension = 13: exact dual-support upper bound and explicit-point lower bound')
assert s.Matrix.hstack(*(spaces['A']+spaces['B'])).rank()-1==14
print('PASS two-sided face upper bound = 14; verify_facet.py proves matching lower bound')
