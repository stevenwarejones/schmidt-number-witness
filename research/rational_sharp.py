"""Attempt exact affine correction inside a numerically identified Gram face."""
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

import numpy as np, json,time
from scipy.linalg import qr
from flint import fmpq_mat
p=Path(__file__).parent
data=np.load(p/'inputs'/'reduced_face_map.npz');A=data['A'].astype(np.int64);target=data['target'].astype(np.int64);P=data['P'];m=P.shape[1];inds=list(zip(*np.triu_indices(m)))
old=np.load(p/'inputs'/'face_solution.npz');Pold=old['P'];V=np.linalg.lstsq(Pold,P,rcond=None)[0];Vi=np.linalg.pinv(V);X=Vi@old['X']@Vi.T
print('starting min eigenvalue',np.linalg.eigvalsh(X).min(),flush=True)
_,rr,sel=qr(A.T,mode='economic',pivoting=True);rank=np.sum(abs(np.diag(rr))>1e-8);sel=sel[:rank]
_,rr,piv=qr(A[sel],mode='economic',pivoting=True);piv=piv[:rank]
D=10**9;x=np.array([round(X[i,j]*D) for i,j in inds],dtype=np.int64)
rhs=target[sel]*D-A[sel]@x
S=A[np.ix_(sel,piv)]
t=time.time();print('exact solve',rank,flush=True)
z=fmpq_mat(S.tolist()).solve(fmpq_mat([[int(a)] for a in rhs]));print('solve seconds',time.time()-t,flush=True)
from fractions import Fraction as F
xx=[F(int(a),D) for a in x]
for i,col in enumerate(piv):xx[col]+=F(str(z[i,0]))/D
MM=[[F(0) for j in range(m)] for i in range(m)]
for (i,j),a in zip(inds,xx):MM[i][j]=MM[j][i]=a
print('corrected numeric min eigenvalue',np.linalg.eigvalsh(np.array(MM,dtype=float)).min(),flush=True)
# Check every polynomial coefficient, not just selected independent rows.
for row,b in zip(A,target):assert sum(int(a)*xx[i] for i,a in enumerate(row) if a)==int(b)
print('all polynomial coefficients EXACT',flush=True)
# Exact LDL with positive pivots using FLINT rational arithmetic.
M=fmpq_mat([[str(a) for a in row] for row in MM]);L=fmpq_mat(m,m);diag=[]
for i in range(m):
 d=M[i,i]-sum(L[i,k]*L[i,k]*diag[k] for k in range(i))
 assert d>0,('nonpositive pivot',i,float(d))
 diag.append(d);L[i,i]=1
 for j in range(i+1,m):L[j,i]=(M[j,i]-sum(L[j,k]*L[i,k]*diag[k] for k in range(i)))/d
print('EXACT POSITIVE GRAM',m,'smallest pivot',min(map(float,diag)),flush=True)
words=json.loads((p/'inputs'/'equality_kernel.json').read_text())['words']
assert np.max(abs(P-np.rint(P)))<1e-8
cert={'bound':'7','words':words,'basis_map':np.rint(P).astype(int).tolist(),'reduced_gram':[[str(a) for a in row] for row in MM],'coefficients':[1,-1,1,-1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1],'method':'exact positive Gram with identically zero polynomial residual'}
(OUTPUT_DIR/'sharp_qubit_certificate.json').write_text(json.dumps(cert,indent=2))
