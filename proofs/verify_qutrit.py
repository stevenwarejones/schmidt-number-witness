"""The exact qutrit realization: Born probabilities from Gaussian-integer data, and F > 7.

Standalone; Python standard library only.

This verifier does one thing: it rebuilds all 36 probabilities of the supplied behavior from
the state and measurement vectors in exact rational arithmetic, checks they are a valid
nonsignaling behavior, and evaluates F on them.  It does NOT re-check the partial-local dual
certificates -- those live in proofs/verify_facet.py, and this file used to carry a duplicate
copy of the same six records.  run_checks.py cross-checks that the coefficient vectors agree
across the certificates.

The historical routing/record calculation this certificate originated from is not part of any
current claim and is kept, unchanged, under research/legacy/.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
p=Path(__file__).parent;c=json.loads((p/'qutrit_certificate.json').read_text())
idx=list(product(range(3),range(3),range(2),range(2)))

def cmul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def cc(a):return a[0],-a[1]
def csum(xs):
 xs=list(xs);return sum(z[0] for z in xs),sum(z[1] for z in xs)
def nsq(z):return z[0]**2+z[1]**2
state=c['state'];assert len(state)==9;norm_state=sum(map(nsq,state));assert norm_state>0
Q={}
for x,y in product(range(3),repeat=2):
 ax,by=c['Alice'][x],c['Bob'][y];u,v=ax['vector'],by['vector'];nu=sum(map(nsq,u));nv=sum(map(nsq,v));assert nu>0 and nv>0
 assert ax['rank_one_outcome'] in (0,1) and by['rank_one_outcome'] in (0,1)
 pa=F(sum(nsq(csum(cmul(cc(u[i]),state[3*i+j]) for i in range(3))) for j in range(3)),nu*norm_state)
 pb=F(sum(nsq(csum(cmul(cc(v[j]),state[3*i+j]) for j in range(3))) for i in range(3)),nv*norm_state)
 pab=F(nsq(csum(cmul(cmul(cc(u[i]),cc(v[j])),state[3*i+j]) for i,j in product(range(3),repeat=2))),nu*nv*norm_state)
 for a,b in product(range(2),repeat=2):
  ha=a==ax['rank_one_outcome'];hb=b==by['rank_one_outcome'];Q[x,y,a,b]=pab if ha and hb else pa-pab if ha else pb-pab if hb else 1-pa-pb+pab
q=[Q[i] for i in idx];assert q==list(map(F,c['Q'])) and min(q)>=0
for x,y in product(range(3),repeat=2):
 assert sum(Q[x,y,a,b] for a,b in product(range(2),repeat=2))==1
 for a in range(2):assert sum(Q[x,y,a,b] for b in range(2))==sum(Q[x,0,a,b] for b in range(2))
 for b in range(2):assert sum(Q[x,y,a,b] for a in range(2))==sum(Q[0,y,a,b] for a in range(2))
w=c['coefficients'];wp=[F((-1)**a*w[x]+(-1)**b*w[3+y],3)+(-1)**(a+b)*w[6+3*x+y] for x,y,a,b in idx]
score=sum(a*b for a,b in zip(wp,q));assert score==F(c['score'])>F(c['bound'])==7
print('PASS exact qutrit Born probabilities; F =',float(score),'>',c['bound'])
