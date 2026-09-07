"""Build a rational SOS upper certificate from the level-2 numerical Gram dual."""
from pathlib import Path
from functools import lru_cache
from itertools import product
from fractions import Fraction as F
import numpy as np,json
p=Path(__file__).resolve().parent
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build';OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

pairs={(0,1):0,(0,2):1,(1,2):2};zero=(0,)*6
@lru_cache(None)
def normal(word,side):
 for i in range(len(word)-1):
  a,b=word[i:i+2]
  if a==b:return normal(word[:i]+word[i+2:],side)
  if a>b:
   out={}
   for (g,w),z in normal(word[:i]+(b,a)+word[i+2:],side).items():out[g,w]=out.get((g,w),0)-z
   for (g,w),z in normal(word[:i]+word[i+2:],side).items():
    gg=list(g);gg[pairs[b,a]+3*side]+=1;gg=tuple(gg);out[gg,w]=out.get((gg,w),0)+2*z
   return {k:v for k,v in out.items() if v}
 return {(zero,word):1}
def normpair(a,b):
 out={}
 for (g,u),r in normal(a,0).items():
  for (h,v),s in normal(b,1).items():out[tuple(x+y for x,y in zip(g,h)),u,v]=r*s
 return out
@lru_cache(None)
def realpair(a,b):
 out={}
 for aa,bb in [(a,b),(a[::-1],b[::-1])]:
  for k,v in normpair(aa,bb).items():out[k]=out.get(k,F(0))+F(v,2)
 return {k:v for k,v in out.items() if v}
def ldl_positive(M):
 n=len(M);L=[[F(0) for j in range(n)] for i in range(n)];D=[]
 for i in range(n):
  d=M[i][i]-sum(L[i][k]**2*D[k] for k in range(i));assert d>0,(i,float(d));D.append(d);L[i][i]=F(1)
  for j in range(i+1,n):L[j][i]=(M[j][i]-sum(L[j][k]*L[i][k]*D[k] for k in range(i)))/d
 return D
words={((),())}
for length in range(1,3):
 for raw in product(range(6),repeat=length):
  a=tuple(x for x in raw if x<3);b=tuple(x-3 for x in raw if x>=3)
  if any(x==y for w in [a,b] for x,y in zip(w,w[1:])):continue
  words.add((a,b))
words=sorted(words,key=lambda w:(sum(map(len,w)),w));n=len(words)
Z=np.load(p/'inputs'/'clifford_level2.npz')['psd_dual'];assert Z.shape==(n,n)
D=10**9
M=[[F(round(float((Z[i,j]+Z[j,i])/2)*D),D)+(F(1,10**7) if i==j else 0) for j in range(n)] for i in range(n)]
pivots=ldl_positive(M)
Q={}
for i,(a,b) in enumerate(words):
 for j,(c,d) in enumerate(words):
  for k,v in realpair(a[::-1]+c,b[::-1]+d).items():Q[k]=Q.get(k,F(0))+M[i][j]*v
ident=(zero,(),());beta=Q.pop(ident,F(0));aa=[1,-1,1];bb=[-1,-1,1];E=[[-1,-1,-1],[-1,-1,1],[1,-1,-1]]
for i in range(3):
 k=(zero,(i,),());Q[k]=Q.get(k,F(0))+aa[i]
 k=(zero,(),(i,));Q[k]=Q.get(k,F(0))+bb[i]
for i,j in product(range(3),repeat=2):
 k=(zero,(i,),(j,));Q[k]=Q.get(k,F(0))+E[i][j]
radius=sum(abs(z) for z in Q.values());upper=beta+radius
print('constant',float(beta),'residual norm budget',float(radius),'upper',float(upper),'min LDL pivot',float(min(pivots)),flush=True)
assert upper<F(70021,10000)
cert={'bound':str(upper),'simple_bound':'70021/10000','constant':str(beta),'residual_budget':str(radius),'gram_matrix':[[str(x) for x in r] for r in M],'words':words,'coefficients':aa+bb+sum(E,[]),'construction':'rationalized positive Gram plus exact residual operator-norm budget; valid for traceless qubit projective observables'}
(OUTPUT_DIR/'qubit_upper_certificate.json').write_text(json.dumps(cert,indent=2))
