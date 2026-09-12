"""Exact continuation of the reviewed Gram certificate; no SDP optimization.

Usage: python research/derive_penalty_boundary.py
Requires python-flint for rational solves. Original certificate validity and
the original equality theorem are dependencies, not reproved by this script.
Writes build/penalty_boundary_certificate.json; does not overwrite shipped data.
"""
import hashlib
import json
import sys
from pathlib import Path
from flint import fmpq, fmpq_mat

if sys.flags.optimize:
    raise SystemExit('Run without -O: assertions check exact identities.')
ROOT = Path(__file__).resolve().parent.parent
PROOFS = ROOT / 'proofs'
OUTPUT_DIR = ROOT / 'build'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
c = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
s = json.loads((PROOFS / 'sharp_qubit_certificate.json').read_text())
X = fmpq_mat([[fmpq(x) for x in row] for row in c['gram']])
assert X.nrows() == X.ncols() == 70 and X == X.transpose()
words = [(tuple(a), tuple(b)) for a, b in s['words']]
P = s['basis_map']
for j, by in [(8, 0), (9, 1)]:
    want = {((), ()): 1, ((1,), ()): 1, ((), (by,)): 1,
            ((1,), (by,)): 1}
    got = {words[i]: row[j] for i, row in enumerate(P) if row[j]}
    assert got == want, 'J8/J9 projector identity incorrect'

e = fmpq_mat(70, 1)
e[8, 0] = 1
v = X.solve(e)
assert X*v == e and v[8, 0] > 0
delta = 16/v[8, 0]
alpha = fmpq(c['alpha']) - delta
epsilon = 4-alpha
Y = fmpq_mat(X)
Y[8, 8] -= delta/16
assert Y*v == fmpq_mat(70, 1)
# X positive definite implies Y positive semidefinite, corank exactly one,
# by the rank-one downdate lemma proved in the accompanying note.
r = v[9, 0]/v[8, 0]
assert r < 0

# An exact witness for Y >= c0*a*a^T. Solve on a nonsingular principal block;
# this is equivalent to a pseudoinverse solve because a is orthogonal to v.
a = fmpq_mat(70, 1)
a[9, 0] = 1
a[8, 0] = -r
assert (a.transpose()*v)[0, 0] == 0
ids = [i for i in range(70) if i != 8]
Z = fmpq_mat([[Y[i,j] for j in ids] for i in ids])
b = fmpq_mat([[a[i,0]] for i in ids])
small_z = Z.solve(b)
z = fmpq_mat(70, 1)
for j, i in enumerate(ids):
    z[i, 0] = small_z[j, 0]
assert Y*z == a
c0 = 1/(a.transpose()*z)[0, 0]
C = 16*c0*r*r
assert 0 < C < alpha < fmpq(c['alpha'])
simple = fmpq(16310672, 100000000)
assert alpha < simple < fmpq(c['alpha'])

out = {
    'status': 'exact rational continuation; inherits base SOS and equality theorem',
    'base_sha256': hashlib.sha256((PROOFS/'penalty_endpoint_certificate.json').read_bytes()).hexdigest(),
    'sharp_sha256': hashlib.sha256((PROOFS/'sharp_qubit_certificate.json').read_bytes()).hexdigest(),
    'delta': str(delta), 'alpha_boundary': str(alpha), 'epsilon_boundary': str(epsilon),
    'v': [str(v[i,0]) for i in range(70)],
    'r': str(r), 'a': [str(a[i,0]) for i in range(70)],
    'z': [str(z[i,0]) for i in range(70)], 'c0': str(c0), 'C': str(C),
    'simple_PD_alpha': str(simple),
    'interpretation': 'certificate boundary, NOT the true optimal alpha_star',
}
(OUTPUT_DIR / 'penalty_boundary_certificate.json').write_text(json.dumps(out, indent=2)+'\n')
print('PASS exact projector identities, Xv=e8, Yv=0, a^Tv=0, Yz=a, and rational signs')
print('alpha_boundary ~',float(alpha),'; simpler PD bound alpha =',float(simple))
print('r ~',float(r),'; quadratic coefficient C ~',float(C))
print('The original certificate chain and prose lemmas remain required dependencies.')
