"""Exact F <= 7 certificate; standard library only, independent of SDP code.
Uses a separate right-insertion Clifford normalizer and rational LDL positivity.
"""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json,sys
if sys.flags.optimize:raise SystemExit('Run without -O: assertions are exact certificate gates.')
p=Path(__file__).parent
zero=(0,)*6;pairs={(0,1):0,(0,2):1,(1,2):2}
@lru_cache(None)
def insert(sorted_word,j,side):
 """Multiply an ordered Clifford monomial on the right by generator j."""
 if not sorted_word or sorted_word[-1]<j:return {(zero,sorted_word+(j,)):1}
 k=sorted_word[-1];prefix=sorted_word[:-1]
 if k==j:return {(zero,prefix):1}
 # prefix * k * j = -prefix * j * k + 2g_jk * prefix.
 out={}
 for (g,u),a in insert(prefix,j,side).items():out[g,u+(k,)]=-a
 g=list(zero);g[3*side+pairs[j,k]]=1;key=(tuple(g),prefix)
 out[key]=out.get(key,0)+2
 return {key:a for key,a in out.items() if a}
@lru_cache(None)
def normal(word,side):
 out={(zero,()):1}
 for j in word:
  new={}
  for (g,u),a in out.items():
   for (h,v),b in insert(u,j,side).items():
    key=(tuple(x+y for x,y in zip(g,h)),v);new[key]=new.get(key,0)+a*b
  out={key:a for key,a in new.items() if a}
 return out
@lru_cache(None)
def pair_normal(a,b):
 out={}
 for (g,u),x in normal(a,0).items():
  for (h,v),y in normal(b,1).items():
   key=(tuple(i+j for i,j in zip(g,h)),u,v);out[key]=out.get(key,0)+x*y
 return {key:a for key,a in out.items() if a}
def positive_ldl(X):
 m=len(X);L=[[F(0) for _ in range(m)] for _ in range(m)];D=[]
 for i in range(m):
  d=X[i][i]-sum(L[i][k]**2*D[k] for k in range(i))
  assert d>0,('nonpositive LDL pivot',i)
  D.append(d);L[i][i]=F(1)
  for j in range(i+1,m):L[j][i]=(X[j][i]-sum(L[j][k]*L[i][k]*D[k] for k in range(i)))/d
 return D
c=json.loads((p/'sharp_qubit_certificate.json').read_text())
assert c['bound']=='7'
w=[1,-1,1,-1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1]
assert c['coefficients']==w
words=[(tuple(a),tuple(b)) for a,b in c['words']];n=len(words)
assert n==84 and len(set(words))==n
assert all(len(a)+len(b)<=3 and all(type(i)==int and 0<=i<3 for i in a+b) for a,b in words)
P=c['basis_map'];m=70
assert len(P)==n and all(len(r)==m and all(type(a)==int for a in r) for r in P)
raw=c['reduced_gram'];assert len(raw)==m and all(len(r)==m and all(type(a)==str for a in r) for r in raw)
X=[[F(a) for a in r] for r in raw]
assert all(X[i][j]==X[j][i] for i in range(m) for j in range(m))
D=positive_ldl(X)
print('PASS 70x70 rational Gram is positive definite by exact LDL',flush=True)
# Reconstruct the full Gram by sparse basis-map multiplication.
rows=[[(k,a) for k,a in enumerate(r) if a] for r in P]
Z=[[sum(F(a*b)*X[k][l] for k,a in rows[i] for l,b in rows[j]) for j in range(n)] for i in range(n)]
poly={}
for i,(a,b) in enumerate(words):
 for j,(d,e) in enumerate(words):
  for key,v in pair_normal(a[::-1]+d,b[::-1]+e).items():poly[key]=poly.get(key,F(0))+Z[i][j]*v
poly={key:v for key,v in poly.items() if v}
target={(zero,(),()):F(7)}
for i in range(3):target[zero,(i,),()]=F(-w[i]);target[zero,(),(i,)]=F(-w[3+i])
for i,j in product(range(3),repeat=2):target[zero,(i,),(j,)]=F(-w[6+3*i+j])
assert poly==target,'Nonzero polynomial residual'
print('PASS exact identity: sum X[j,k] J[j]^dagger J[k] = 7 I - Bell_F',flush=True)
aa=(1,1,1);bb=(-1,-1,-1)
attainer=list(aa)+list(bb)+[a*b for a in aa for b in bb]
assert sum(a*b for a,b in zip(w,attainer))==7
print('SHARP CERTIFICATE VALID: F <= 7 for traceless projective qubit observables, for every state.',flush=True)
print('The accompanying projective-extreme, deterministic-measurement, and Schmidt-compression arguments extend this to all Schmidt-number-two behaviors.',flush=True)
