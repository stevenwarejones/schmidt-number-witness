"""Exact facet and membership verification; standard library only."""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
from pathlib import Path
from fractions import Fraction as F
from itertools import product,combinations
import json
p=Path(__file__).parent;c=json.loads((p/'facet_certificate.json').read_text());w=c['w']
def rank(rows):
 a=[list(map(F,r)) for r in rows];n=len(a[0]);r=0
 for j in range(n):
  k=next((k for k in range(r,len(a)) if a[k][j]),None)
  if k is None:continue
  a[r],a[k]=a[k],a[r];z=a[r][j];a[r]=[v/z for v in a[r]]
  for i in range(r+1,len(a)):
   z=a[i][j]
   if z:a[i]=[v-z*t for v,t in zip(a[i],a[r])]
  r+=1
  if r==len(a):break
 return r
local=[list(a)+list(b)+[x*y for x in a for y in b] for a,b in product(product([-1,1],repeat=3),repeat=2)]
assert rank([[1]+v for v in local])==16
local_tight=[v for v in local if sum(a*b for a,b in zip(v,w))==7]
assert len(local_tight)==5 and rank([[1]+v for v in local_tight])==5
points=[]
for e in c['saturating_points']:
 v=list(map(F,e['v']));assert len(v)==15 and sum(a*b for a,b in zip(v,w))==7
 P={(x,y,a,b):(1+(-1)**a*v[x]+(-1)**b*v[3+y]+(-1)**(a+b)*v[6+3*x+y])/4 for x,y,a,b in product(range(3),range(3),range(2),range(2))}
 assert min(P.values())>=0,'[E-NEGATIVE-PROB] a supplied point has a negative probability'
 pair=e['pair'];side=e['side'];assert side in ['A','B'] and tuple(pair) in list(combinations(range(3),2))
 assert sum(F(m['weight']) for m in e['local_model'])==1
 for m in e['local_model']:
  assert F(m['weight'])>0 and len(m['small'])==2 and len(m['large'])==3 and all(a in [0,1] for a in m['small']+m['large'])
 inds=list(product(pair,range(3),range(2),range(2))) if side=='A' else list(product(range(3),pair,range(2),range(2)))
 for x,y,a,b in inds:
  expected=sum(F(m['weight'])*int(((m['small'][pair.index(x)],m['large'][y]) if side=='A' else (m['large'][x],m['small'][pair.index(y)]))==(a,b)) for m in e['local_model'])
  assert expected==P[x,y,a,b]
 points.append(v)
assert len(points)==15 and rank([[1]+v for v in points])==15
# Validity on all six partial-local classes, using exact positivity and CHSH certificates.
assert {(d['side'],tuple(d['pair'])) for d in c['partial_hull_duals']}==set(product(['A','B'],combinations(range(3),2)))
for d in c['partial_hull_duals']:
 rows=[]
 for x,y,a,b in product(range(3),range(3),[-1,1],[-1,1]):
  row=[0]*16;row[0]=1;row[1+x]=a;row[4+y]=b;row[7+3*x+y]=a*b;rows.append(row)
 for other in combinations(range(3),2):
  inds=list(product(d['pair'],other)) if d['side']=='A' else list(product(other,d['pair']))
  for ss in product([-1,1],repeat=4):
   if ss[0]*ss[1]*ss[2]*ss[3]==-1:
    row=[0]*16;row[0]=2
    for z,(x,y) in zip(ss,inds):row[7+3*x+y]=-z
    rows.append(row)
 weights=list(map(F,d['weights']));assert len(weights)==len(rows) and min(weights)>=0
 assert [sum(z*r[j] for z,r in zip(weights,rows)) for j in range(16)]==[7]+[-z for z in w]
print('PASS: local dimension 15, local saturating face dimension 4 (5 vertices)')
print('PASS: 15 affinely independent saturating points in H, each with an exact partial-local model')
print('PASS: exact validity on all six partial-local sets')
print('CONCLUSION: F <= 7 IS A FACET OF H, although not a facet of the local polytope')
