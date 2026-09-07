"""Independent check of the sum-of-squares operator identity.

Builds every 4x4 operator directly from random unit Bloch vectors.  It does NOT import or
reuse the repository's word-reduction code, so it is a genuine second opinion on
    7I - B_F = sum_jk X_jk J_j^dagger J_k,
which, together with X > 0, is what proves F <= 7 for Schmidt number at most two."""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
import json, os, numpy as np
from fractions import Fraction as Fr
HERE=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'proofs')
d=json.load(open(os.path.join(HERE,'sharp_qubit_certificate.json')))
words=d['words']; P=np.array(d['basis_map'],dtype=float)
X=np.array([[float(Fr(s)) for s in row] for row in d['reduced_gram']])
co=d['coefficients']
I2=np.eye(2); SX=np.array([[0,1],[1,0]],complex)
SY=np.array([[0,-1j],[1j,0]]); SZ=np.diag([1,-1]).astype(complex)
bl=lambda u: u[0]*SX+u[1]*SY+u[2]*SZ
a=co[0:3]; b=co[3:6]; E=np.array(co[6:15]).reshape(3,3)
assert np.allclose(X,X.T) and np.linalg.eigvalsh(X).min()>0, "Gram not positive definite"
rng=np.random.default_rng(11); worst=0.0
for _ in range(200):
    A=[bl(v/np.linalg.norm(v)) for v in rng.normal(size=(3,3))]
    B=[bl(v/np.linalg.norm(v)) for v in rng.normal(size=(3,3))]
    W=[]
    for wa,wb in words:
        ma=np.eye(2,dtype=complex)
        for i in wa: ma=ma@A[i]
        mb=np.eye(2,dtype=complex)
        for j in wb: mb=mb@B[j]
        W.append(np.kron(ma,mb))
    J=np.einsum('ij,ikl->jkl',P,np.array(W))
    RHS=np.einsum('jk,jlm,kmn->ln',X,J.conj().transpose(0,2,1),J)
    BF=sum(a[x]*np.kron(A[x],I2) for x in range(3))
    BF=BF+sum(b[y]*np.kron(I2,B[y]) for y in range(3))
    BF=BF+sum(E[x,y]*np.kron(A[x],B[y]) for x in range(3) for y in range(3))
    worst=max(worst,np.abs(7*np.eye(4)-BF-RHS).max())
print(f"Gram least eigenvalue: {np.linalg.eigvalsh(X).min():.6e}")
print(f"max |7I - B_F - sum X_jk J_j^dag J_k| over 200 random Bloch configs: {worst:.3e}")
assert worst<1e-9, "OPERATOR IDENTITY FAILS"
print("PASS independent reconstruction of the sum-of-squares identity")
