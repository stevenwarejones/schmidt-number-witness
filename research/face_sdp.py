"""Fixed sharp target with exact equality-family facial reduction."""
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

import sys
src=(Path(__file__).resolve().parent/'clifford_bound.py').read_text().split('problem=cp.Problem')[0]
sys.argv=[sys.argv[0],'3'];exec(src)
RESEARCH_DIR=Path(__file__).resolve().parent
KERNEL_PATH=RESEARCH_DIR/'inputs'/'equality_kernel.json'
k=json.loads(KERNEL_PATH.read_text());P=np.array(k['P'],dtype=float)
target=np.zeros(len(keys));target[lookup[zero,(),()]]=7
for i in range(3):target[lookup[zero,(i,),()]]=-a[i];target[lookup[zero,(),(i,)]]=-b[i]
for i,j in product(range(3),repeat=2):target[lookup[zero,(i,),(j,)]]=-E[i][j]
# Build exact-integer map from symmetric reduced Gram coordinates to polynomial.
from scipy.sparse import csr_matrix
m=P.shape[1];inds=list(zip(*np.triu_indices(m)));Amap=np.empty((len(keys),len(inds)))
for k in range(len(keys)):
 S=P.T@R[:,k].toarray().reshape(n,n)@P
 Amap[k]=[S[i,j] if i==j else S[i,j]+S[j,i] for i,j in inds]
assert np.max(np.abs(Amap-np.rint(Amap)))<1e-8
Amap=np.rint(Amap).astype(int)
np.savez_compressed((OUTPUT_DIR/'face_map.npz'),A=Amap,target=target,P=P)
from scipy.linalg import qr,lstsq
_,rr,piv=qr(Amap.T,mode='economic',pivoting=True);rank=np.sum(np.abs(np.diag(rr))>1e-8);sel=piv[:rank]
x,_,_,_=lstsq(Amap[sel],target[sel]);res=np.max(np.abs(Amap@x-target));print('dim',m,'map rank',rank,'linear residual',res,flush=True)
if res>1e-7:raise SystemExit('Exact target appears linearly inconsistent')
X=cp.Variable((m,m),symmetric=True);t=cp.Variable()
coords=cp.hstack([X[i,j] for i,j in inds])
problem=cp.Problem(cp.Maximize(t),[X-t*np.eye(m)>>0,csr_matrix(Amap[sel])@coords==target[sel]])
problem.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=150)
print('status',problem.status,'min eigenvalue',t.value,flush=True)
if X.value is not None:np.savez_compressed((OUTPUT_DIR/'face_solution.npz'),X=X.value,P=P,A=Amap,target=target,selected=sel)
