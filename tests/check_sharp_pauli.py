"""Independent exact matrix checks of the symbolic SOS expansion.
These are cross-checks, not a replacement for the universal algebraic proof.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
import sympy as s
from pathlib import Path
import json,itertools,importlib.util
p=Path(__file__).resolve().parent.parent/'proofs'
spec=importlib.util.spec_from_file_location('verify',p/'verify_sharp_qubit.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
I=s.eye(2);pauli=[s.Matrix([[0,1],[1,0]]),s.Matrix([[0,-s.I],[s.I,0]]),s.diag(1,-1)]
configs=[([(1,0,0),(0,1,0),(0,0,1)],[(s.Rational(3,5),s.Rational(4,5),0),(s.Rational(2,3),s.Rational(1,3),s.Rational(2,3)),(0,0,-1)]), ([(s.Rational(2,3),s.Rational(-2,3),s.Rational(1,3)),(s.Rational(3,5),0,s.Rational(4,5)),(0,1,0)],[(0,0,1),(s.Rational(1,3),s.Rational(2,3),s.Rational(-2,3)),(1,0,0)])]
def prod(ms):
 out=I
 for m in ms:out=(out*m).applyfunc(s.expand)
 return out
for ix,(aa,bb) in enumerate(configs):
 assert all(sum(x*x for x in u)==1 for u in aa+bb)
 A=[sum((u[k]*pauli[k] for k in range(3)),s.zeros(2)) for u in aa];B=[sum((u[k]*pauli[k] for k in range(3)),s.zeros(2)) for u in bb]
 g=[sum(u[k]*w[k] for k in range(3)) for side in [aa,bb] for u,w in itertools.combinations(side,2)]
 W=[s.kronecker_product(prod([A[i] for i in a]),prod([B[i] for i in b])) for a,b in v.words]
 direct=s.zeros(4)
 for i in range(len(W)):
  for j in range(len(W)):
   direct+=s.Rational(v.Z[i][j].numerator,v.Z[i][j].denominator)*(W[i].conjugate().T*W[j]).applyfunc(s.expand)
 # Independently reconstruct Bell operator and the residual monomials.
 bell=sum((v.w[i]*s.kronecker_product(A[i],I)+v.w[3+i]*s.kronecker_product(I,B[i]) for i in range(3)),s.zeros(4))
 bell+=sum((v.w[6+3*i+j]*s.kronecker_product(A[i],B[j]) for i,j in itertools.product(range(3),repeat=2)),s.zeros(4))
 expected=7*s.eye(4)-bell
 assert all(s.simplify(x)==0 for x in direct-expected)
 print('PASS exact complex Pauli reconstruction',ix,flush=True)
