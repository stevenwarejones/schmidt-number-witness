"""Exact dimension-unrestricted quantum upper certificate; standard library only."""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json,sys
if sys.flags.optimize:raise SystemExit('Run without -O: assertions are exact certificate gates.')
p=Path(__file__).parent;c=json.loads((p/'quantum_upper_certificate.json').read_text())
@lru_cache(None)
def reduce_word(w):
 for i in range(len(w)-1):
  if w[i]==w[i+1]:return reduce_word(w[:i]+w[i+2:])
 return w
words=[(tuple(a),tuple(b)) for a,b in c['words']];n=len(words)
assert n==28 and len(set(words))==n
assert all(len(a)+len(b)<=2 and all(type(i)==int and 0<=i<3 for i in a+b) for a,b in words)
assert len(c['gram'])==n and all(len(r)==n and all(type(a)==str for a in r) for r in c['gram'])
Z=[[F(a) for a in r] for r in c['gram']]
assert all(Z[i][j]==Z[j][i] for i in range(n) for j in range(n))
L=[[F(0) for _ in range(n)] for _ in range(n)];D=[]
for i in range(n):
 d=Z[i][i]-sum(L[i][k]**2*D[k] for k in range(i));assert d>0;D.append(d);L[i][i]=F(1)
 for j in range(i+1,n):L[j][i]=(Z[j][i]-sum(L[j][k]*L[i][k]*D[k] for k in range(i)))/d
poly={}
for i,(a,b) in enumerate(words):
 for j,(d,e) in enumerate(words):
  u,v=reduce_word(a[::-1]+d),reduce_word(b[::-1]+e)
  key=min((u,v),(u[::-1],v[::-1]))
  poly[key]=poly.get(key,F(0))+Z[i][j]
beta=poly.pop(((),()),F(0));w=[1,-1,1,-1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1];assert c['coefficients']==w
for i in range(3):
 for key,z in [(((i,),()),w[i]),(((),(i,)),w[3+i])]:poly[key]=poly.get(key,F(0))+z
for i,j in product(range(3),repeat=2):key=((i,),(j,));poly[key]=poly.get(key,F(0))+w[6+3*i+j]
radius=sum(abs(x) for x in poly.values())
assert beta==F(c['constant']) and radius==F(c['residual'])
assert beta+radius==F(c['bound'])==F(7041387041,10**9)
print('UNRESTRICTED QUANTUM CERTIFICATE VALID: F <= 7.041387041; no dimension-specific identities used.')
