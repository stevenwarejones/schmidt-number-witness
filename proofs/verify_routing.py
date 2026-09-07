"""Standalone exact verifier. Python standard library only."""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import json
p=Path(__file__).parent;c=json.loads((p/'routing_certificate.json').read_text())
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
score=sum(a*b for a,b in zip(wp,q));assert score==F(c['score'])>7
print('PASS exact qutrit Born probabilities; F =',float(score),'> 7')

def ineq(side,pair):
 rows=[]
 for x,y,a,b in product(range(3),range(3),[-1,1],[-1,1]):
  r=[0]*16;r[0]=1;r[1+x]=a;r[4+y]=b;r[7+3*x+y]=a*b;rows.append(r)
 for other in combinations(range(3),2):
  inds=list(product(pair,other)) if side=='A' else list(product(other,pair))
  for ss in product([-1,1],repeat=4):
   if ss[0]*ss[1]*ss[2]*ss[3]==-1:
    r=[0]*16;r[0]=2
    for z,(x,y) in zip(ss,inds):r[7+3*x+y]=-z
    rows.append(r)
 return rows
assert {(d['side'],tuple(d['pair'])) for d in c['duals']}==set(product(['A','B'],combinations(range(3),2)))
for d in c['duals']:
 rows=ineq(d['side'],d['pair']);ww=list(map(F,d['weights']));assert len(ww)==len(rows) and min(ww)>=0
 assert [sum(z*r[j] for z,r in zip(ww,rows)) for j in range(16)]==[7]+[-z for z in w]
print('PASS all six exact positivity/CHSH certificates for partial-local bound F <= 7')
patterns=[(0,0,1),(0,1,0),(0,1,1)]

def outcomes(s):
 msg=s['message'];aa=s['sender_outputs'];bb=s['receiver_outputs'];reverse=s['reverse']
 assert tuple(msg) in patterns and len(aa)==3 and len(bb)==6
 assert all(t in (0,1) for t in list(msg)+list(aa)+list(bb))
 return [((bb[2*x+msg[y]],aa[y]) if reverse else (aa[x],bb[2*y+msg[x]])) for x,y in product(range(3),repeat=2)]
def differences(outs,reverse,msg,recipient_settings):
 high=msg.index(1);ds=[]
 for r in recipient_settings:
  a0,b0=outs[3*r] if reverse else outs[r]
  a1,b1=outs[3*r+high] if reverse else outs[3*high+r]
  z0,z1=(a0,a1) if reverse else (b0,b1)
  ds.append(int(z0==0)-int(z1==0))
 return ds
# The qutrit realization above is the part this repository's theorem uses.  Everything
# below is the legacy routing/record calculation this certificate originated from; it
# is not part of the current physical claim, so it runs only under --legacy-routing.
if '--legacy-routing' not in _sys.argv:
    print('(legacy routing/record checks skipped; rerun with --legacy-routing)')
    raise SystemExit(0)

for anchored,name in [(True,'optimal_routing'),(False,'ordinary_optimal_routing')]:
 cert=c[name];settings=[1,2] if anchored else [0,1,2];nrows=2*len(settings)
 out={i:F(0) for i in idx};signals=[[F(0)]*len(settings) for _ in range(6)];mass=F(0)
 for e in cert['completion']:
  z=F(e['weight']);assert z>0;mass+=z;s=e['strategy'];oo=outcomes(s)
  if anchored:assert s['receiver_outputs'][0]==s['receiver_outputs'][1]
  group=3*int(s['reverse'])+patterns.index(tuple(s['message']))
  for (x,y),(a,b) in zip(product(range(3),repeat=2),oo):out[x,y,a,b]+=z
  for j,t in enumerate(differences(oo,s['reverse'],s['message'],settings)):signals[group][j]+=z*t
 assert mass==1 and out==Q
 actual=sum(max(map(abs,row)) for row in signals);t=list(map(F,cert['t']));value=F(cert['value'])
 assert len(t)==6 and sum(t)==actual==value
 assert all(max(map(abs,row))<=z for row,z in zip(signals,t))
 dy=list(map(F,cert['dual_y']));mu=list(map(F,cert['dual_mu']));assert len(dy)==36 and len(mu)==6*nrows and max(mu)<=0
 for group,(reverse,msg) in enumerate(product([False,True],patterns)):
  local_mu=mu[group*nrows:(group+1)*nrows];assert -sum(local_mu)<=1
  for aa in product(range(2),repeat=3):
   for raw in product(range(2),repeat=5 if anchored else 6):
    bb=(raw[0],raw[0])+raw[1:] if anchored else raw
    s={'reverse':reverse,'message':msg,'sender_outputs':aa,'receiver_outputs':bb};oo=outcomes(s)
    lhs=sum(dy[4*(3*x+y)+2*a+b] for (x,y),(a,b) in zip(product(range(3),repeat=2),oo))
    ds=differences(oo,reverse,msg,settings)
    lhs+=sum(local_mu[2*j]*d-local_mu[2*j+1]*d for j,d in enumerate(ds))
    assert lhs<=0
 assert sum(a*b for a,b in zip(q,dy))==value
 # Collapse the dual objective on the nonsignaling slice.
 constant=sum(dy)/4;A=[F(0)]*3;B=[F(0)]*3;E=[F(0)]*9
 for z,(x,y,a,b) in zip(dy,idx):A[x]+=z*(-1)**a/4;B[y]+=z*(-1)**b/4;E[3*x+y]+=z*(-1)**(a+b)/4
 assert constant==F(-21,4) and A+B+E==[F(3,4)*z for z in w]
 assert value==F(3,4)*(score-7)
 print('PASS exact optimal T and universal dual bound; anchored=',anchored,'T=',float(value))
assert c['optimal_routing']['value']==c['ordinary_optimal_routing']['value']
print('ALL EXACT CHECKS PASSED: no record-specific penalty in this example')
