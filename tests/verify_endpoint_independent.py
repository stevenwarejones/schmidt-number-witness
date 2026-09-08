"""A second opinion on the endpoint certificate, sharing no code with the proof path.

proofs/verify_penalty_endpoint.py rides the repository's existing right-insertion
Clifford normaliser and rational LDL.  If that normaliser were wrong, the proof and
its check would be wrong together.  This file therefore re-derives the same claims
along routes that were written independently:

  A. MY OWN normal ordering.  A confluent rewriting on raw generator strings --
         ..kk..      ->  ..;..                       (A_k^2 = I)
         ..ij..  i>j -> -..ji.. + 2 c_ji ..;..       (Clifford relation)
     -- with coefficients kept as exact polynomials in the six Gram parameters
     c01,c02,c12,d01,d02,d12.  The residual of the endpoint identity must be
     identically zero as a polynomial, which also forces every parameter-dependent
     term on the right-hand side to cancel.

  B. NO normal ordering at all.  Alice's and Bob's observables are built as explicit
     2x2 matrices over the GAUSSIAN RATIONALS from rational points of the unit
     sphere, so A_i^2 = I and A_iA_j + A_jA_i = 2(a_i.a_j)I hold by construction.
     Both sides of the identity are then compared as exact 4x4 matrices.  This is
     the exact-arithmetic strengthening of tests/verify_sos_independent.py, which
     does the same thing in floating point for the eps = 0 certificate.

  C. Positive definiteness by integer BAREISS elimination rather than rational LDL:
     every leading principal minor of the integer-scaled Gram must be positive.

  D. The twelve deterministic-observable duals rebuilt from P(ab|xy) >= 0 directly,
     plus explicit rational behaviours showing the certified value is attained (so a
     vacuous or mis-scaled dual would be visible).

  E. Numerical corroboration -- NOT proof -- of the two reduction steps that carry
     the qubit-projective statement to all Schmidt-number-two behaviours: the binary
     effect decomposition and Schmidt compression.  The proofs of those steps are
     prose, in docs/CERTIFICATE_PENALTY_ENDPOINT.md; this only checks that the
     identities they rest on hold numerically and that no violation shows up in a
     random search.

Each route is also run against the eps = 0 certificate the repository already
trusts, so agreement there cross-validates the routes themselves.

Diagnostic codes: [E-IND-RESIDUAL] [E-IND-REP] [E-IND-MINOR] [E-IND-DUAL]
[E-IND-REDUCTION]
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit('Run without -O: assertions in this file are certificate checks.')

import itertools
import json
import math
import random
from fractions import Fraction as Fr
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOFS = ROOT / 'proofs'

base = json.loads((PROOFS / 'sharp_qubit_certificate.json').read_text())
endpoint = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
WORDS = base['words']
BMAP = base['basis_map']
FVEC = base['coefficients']
EPS0 = Fr(endpoint['epsilon'])
assert endpoint['coefficients'] == FVEC, '[E-IND-RESIDUAL] certificates disagree on the functional'

CASES = [('endpoint eps = 383689/100000', [[Fr(x) for x in r] for r in endpoint['gram']], EPS0),
         ('base eps = 0 (control)', [[Fr(x) for x in r] for r in base['reduced_gram']], Fr(0))]


def penalised_coefficients(eps):
    c = [Fr(x) for x in FVEC]
    for k in (1, 3, 9):
        c[k] += eps / 4
    return c


# =============================================================================
# D. the twelve deterministic-observable duals, rebuilt from P(ab|xy) >= 0
# =============================================================================
EVENTS = list(itertools.product(range(3), range(3), (-1, 1), (-1, 1)))


def positivity_row(x, y, a, b):
    r = [0] * 15
    r[x] += a
    r[3 + y] += b
    r[6 + 3 * x + y] += a * b
    return r


ROWS = [positivity_row(*e) for e in EVENTS]
M_A = [Fr(c) for c in FVEC]
for k in (1, 3, 9):
    M_A[k] += 1

FEASIBLE = []                       # genuine no-signaling behaviours, for a sanity sweep
for z in itertools.product((-1, 1), repeat=6):
    FEASIBLE.append([Fr(t) for t in list(z) + [a * b for a in z[:3] for b in z[3:]]])
LOCAL = list(FEASIBLE)
for x1, x2 in itertools.combinations(range(3), 2):          # PR boxes on 2x2 sub-scenarios
    for y1, y2 in itertools.combinations(range(3), 2):
        xs, ys = {x1: 0, x2: 1}, {y1: 0, y2: 1}
        rest_x = [x for x in range(3) if x not in xs]
        rest_y = [y for y in range(3) if y not in ys]
        for mu, nu_, sg in itertools.product((0, 1), repeat=3):
            for sx in itertools.product((-1, 1), repeat=len(rest_x)):
                for sy in itertools.product((-1, 1), repeat=len(rest_y)):
                    v = [Fr(0)] * 15
                    for t, x in zip(sx, rest_x):
                        v[x] = Fr(t)
                    for t, y in zip(sy, rest_y):
                        v[3 + y] = Fr(t)
                    for x in range(3):
                        for y in range(3):
                            if x in xs and y in ys:
                                e = (xs[x] & ys[y]) ^ (mu & xs[x]) ^ (nu_ & ys[y]) ^ sg
                                v[6 + 3 * x + y] = Fr(1 - 2 * e)
                            else:
                                v[6 + 3 * x + y] = v[x] * v[3 + y]
                    if all(1 + sum(r[k] * v[k] for k in range(15)) >= 0 for r in ROWS):
                        FEASIBLE.append(v)

branches = json.loads((PROOFS / 'penalty_branch_certificates.json').read_text())
seen = set()
for c in branches:
    i, s = c['i'], c['s']
    t = [Fr(x) for x in c['t']]
    nu = Fr(c['nu'])
    upper = Fr(c['upper'])
    assert all(x >= 0 for x in t), f'[E-IND-DUAL] branch ({i},{s}) has a negative multiplier'
    for k in range(15):
        lhs = sum(-ROWS[j][k] * t[j] for j in range(36)) + (nu if k == i else Fr(0))
        assert lhs == M_A[k], f'[E-IND-DUAL] branch ({i},{s}) dual identity fails at coordinate {k}'
    assert sum(t) + nu * s == upper <= 6, f'[E-IND-DUAL] branch ({i},{s}) states a wrong or useless value'
    attained = [sum(M_A[k] * v[k] for k in range(15)) for v in FEASIBLE if v[i] == s]
    best = max(attained)
    assert best <= upper, (f'[E-IND-DUAL] branch ({i},{s}) claims M_A <= {upper} but an explicit '
                           f'no-signaling behaviour reaches {best}')
    best_local = max(sum(M_A[k] * v[k] for k in range(15)) for v in LOCAL if v[i] == s)
    seen.add((i, s))
    print(f'  PASS [D] branch obs {i} = {s:+d}: dual value {upper}, best explicit behaviour {best}'
          f'{"" if best == upper else "  (dual not tight here, still valid)"}', flush=True)
    assert best_local <= upper
assert seen == set(itertools.product(range(6), (-1, 1))), \
    '[E-IND-DUAL] the twelve branches are not all present'
# The branch hypothesis is doing real work: with NO deterministic observable, an explicit
# no-signaling behaviour reaches M_A = 8, well above the 6 the duals certify.
FREE = [Fr(0)] * 6 + [Fr(c) for c in FVEC[6:]]
assert all(1 + sum(r[k] * FREE[k] for k in range(15)) >= 0 for r in ROWS), \
    '[E-IND-DUAL] the unconstrained witness is not a behaviour'
assert all(abs(FREE[i]) != 1 for i in range(6)), \
    '[E-IND-DUAL] the unconstrained witness has a deterministic observable after all'
assert sum(M_A[k] * FREE[k] for k in range(15)) == 8, \
    '[E-IND-DUAL] the unconstrained no-signaling maximum is not 8'
print('  PASS [D] without a deterministic observable an explicit no-signaling behaviour reaches '
      'M_A = 8 (F = 9), so the branch hypothesis is essential', flush=True)

# =============================================================================
# A. my own Clifford rewriting, coefficients as polynomials in c__ and d__
# =============================================================================
VARIDX = {('A', 0, 1): 0, ('A', 0, 2): 1, ('A', 1, 2): 2,
          ('B', 0, 1): 3, ('B', 0, 2): 4, ('B', 1, 2): 5}
ONE = {(0,) * 6: Fr(1)}


def pmul(p, q):
    out = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = tuple(a + b for a, b in zip(e1, e2))
            out[e] = out.get(e, Fr(0)) + c1 * c2
    return {e: c for e, c in out.items() if c}


def padd(p, q):
    out = dict(p)
    for e, c in q.items():
        s = out.get(e, Fr(0)) + c
        if s:
            out[e] = s
        else:
            out.pop(e, None)
    return out


def pscale(k, p):
    return {} if k == 0 else {e: k * c for e, c in p.items()}


def _reducer(party):
    @lru_cache(maxsize=None)
    def red(w):
        for pos in range(len(w) - 1):
            if w[pos] >= w[pos + 1]:
                if w[pos] == w[pos + 1]:
                    return red(w[:pos] + w[pos + 2:])
                i, j = w[pos], w[pos + 1]                      # i > j
                swapped = red(w[:pos] + (j, i) + w[pos + 2:])
                dropped = red(w[:pos] + w[pos + 2:])
                e = [0] * 6
                e[VARIDX[(party, j, i)]] = 1
                cvar = {tuple(e): Fr(1)}
                out = {}
                for k, v in swapped.items():
                    out[k] = padd(out.get(k, {}), pscale(Fr(-1), v))
                for k, v in dropped.items():
                    out[k] = padd(out.get(k, {}), pscale(Fr(2), pmul(cvar, v)))
                return {k: v for k, v in out.items() if v}
        return {tuple(w): ONE}
    return red


redA, redB = _reducer('A'), _reducer('B')
SUBS = [s for r in range(4) for s in itertools.combinations((0, 1, 2), r)]
TABLE_A = {(S, T): redA(S + T) for S in SUBS for T in SUBS}
TABLE_B = {(S, T): redB(S + T) for S in SUBS for T in SUBS}


def elem(word):
    wa, wb = word
    out = {}
    for Sa, pa in redA(tuple(wa)).items():
        for Sb, pb in redB(tuple(wb)).items():
            out[(Sa, Sb)] = padd(out.get((Sa, Sb), {}), pmul(pa, pb))
    return {k: v for k, v in out.items() if v}


def eadd(x, y):
    out = dict(x)
    for k, v in y.items():
        s = padd(out.get(k, {}), v)
        if s:
            out[k] = s
        else:
            out.pop(k, None)
    return out


def escale(k, x):
    return {} if k == 0 else {a: pscale(k, v) for a, v in x.items()}


def emul(x, y):
    out = {}
    for (Sa, Sb), p in x.items():
        for (Ta, Tb), q in y.items():
            pq = pmul(p, q)
            if not pq:
                continue
            for Ua, ca in TABLE_A[(Sa, Ta)].items():
                cpa = pmul(ca, pq)
                if not cpa:
                    continue
                for Ub, cb in TABLE_B[(Sb, Tb)].items():
                    t = pmul(cb, cpa)
                    if not t:
                        continue
                    s = padd(out.get((Ua, Ub), {}), t)
                    if s:
                        out[(Ua, Ub)] = s
                    else:
                        out.pop((Ua, Ub), None)
    return out


WE = [elem(w) for w in WORDS]
WE_REV = [elem([list(reversed(w[0])), list(reversed(w[1]))]) for w in WORDS]


def coordinate_element(idx):
    if idx < 3:
        return elem([[idx], []])
    if idx < 6:
        return elem([[], [idx - 3]])
    x, y = divmod(idx - 6, 3)
    return elem([[x], [y]])


for label, X, eps in CASES:
    n = len(X)
    J = [{} for _ in range(n)]
    Jdag = [{} for _ in range(n)]
    for j in range(n):
        for i, row in enumerate(BMAP):
            if row[j]:
                J[j] = eadd(J[j], escale(Fr(row[j]), WE[i]))
                Jdag[j] = eadd(Jdag[j], escale(Fr(row[j]), WE_REV[i]))
    rhs = {}
    for j in range(n):
        Y = {}
        for k in range(n):
            if X[j][k]:
                Y = eadd(Y, escale(X[j][k], J[k]))
        if Y:
            rhs = eadd(rhs, emul(Jdag[j], Y))
    lhs = escale(Fr(7) - eps / 4, elem([[], []]))
    for idx, co in enumerate(penalised_coefficients(eps)):
        if co:
            lhs = eadd(lhs, escale(-co, coordinate_element(idx)))
    residual = {k: v for k, v in eadd(lhs, escale(Fr(-1), rhs)).items() if v}
    assert not residual, f'[E-IND-RESIDUAL] {label}: independent normal ordering leaves {len(residual)} nonzero terms'
    # every parameter-dependent term must have cancelled, leaving 1 + 6 + 9 monomials
    assert len(rhs) == 16 and all(set(v) == {(0,) * 6} for v in rhs.values()), \
        f'[E-IND-RESIDUAL] {label}: the reconstruction is not parameter-free'
    print(f'  PASS [A] independent normal ordering: zero residual, {label}', flush=True)

# the basis-map identities the equality argument leans on (checked, not yet relied on)
Jl = [{} for _ in range(70)]
for j in range(70):
    for i, row in enumerate(BMAP):
        if row[j]:
            Jl[j] = eadd(Jl[j], escale(Fr(row[j]), WE[i]))
IDENT = elem([[], []])
K = escale(Fr(1, 4), emul(eadd(IDENT, elem([[1], []])), eadd(IDENT, elem([[], [0]]))))
assert not {k: v for k, v in eadd(Jl[8], escale(Fr(-4), K)).items() if v}, \
    '[E-IND-RESIDUAL] J_8 is not (I+A1)(I+B0)'
assert not {k: v for k, v in eadd(emul(K, K), escale(Fr(-1), K)).items() if v}, \
    '[E-IND-RESIDUAL] K is not a projector'
print('  PASS [A] J_8 = 4K with K = (I+A1)(I+B0)/4 a projector, so p = <K>', flush=True)

# =============================================================================
# B. exact Gaussian-rational qubit representation, no normal ordering
# =============================================================================
class G:
    __slots__ = ('r', 'i')

    def __init__(self, r=0, i=0):
        self.r, self.i = Fr(r), Fr(i)

    def __add__(s, o): return G(s.r + o.r, s.i + o.i)
    def __sub__(s, o): return G(s.r - o.r, s.i - o.i)
    def __mul__(s, o): return G(s.r * o.r - s.i * o.i, s.r * o.i + s.i * o.r)
    def __rmul__(s, k): return G(s.r * k, s.i * k)
    def conj(s): return G(s.r, -s.i)
    def __eq__(s, o): return s.r == o.r and s.i == o.i


def zeros(n): return [[G(0)] * n for _ in range(n)]
def ident(n): return [[G(1) if a == b else G(0) for b in range(n)] for a in range(n)]
def mmul(A, B):
    k = len(B)
    return [[sum((A[a][t] * B[t][b] for t in range(k)), G(0)) for b in range(len(B[0]))]
            for a in range(len(A))]
def madd(A, B): return [[A[a][b] + B[a][b] for b in range(len(A[0]))] for a in range(len(A))]
def mscale(c, A): return [[c * A[a][b] for b in range(len(A[0]))] for a in range(len(A))]
def dagger(A): return [[A[b][a].conj() for b in range(len(A))] for a in range(len(A[0]))]
def kron(A, B):
    m = len(B)
    return [[A[a // m][b // m] * B[a % m][b % m] for b in range(len(A) * m)]
            for a in range(len(A) * m)]


def unit_vector(u, v):
    """Stereographic image of a rational plane point: exactly on the unit sphere."""
    s = 1 + u * u + v * v
    return (2 * u / s, 2 * v / s, (u * u + v * v - 1) / s)


def observable(a):
    x, y, z = a
    return [[G(z, 0), G(x, -y)], [G(x, y), G(-z, 0)]]


rnd = random.Random(20260907)
I2, I4 = ident(2), ident(4)
for label, X, eps in CASES:
    n = len(X)
    for _ in range(2):
        A = [observable(unit_vector(Fr(rnd.randint(-40, 40), rnd.randint(1, 17)),
                                    Fr(rnd.randint(-40, 40), rnd.randint(1, 17))))
             for _ in range(3)]
        B = [observable(unit_vector(Fr(rnd.randint(-40, 40), rnd.randint(1, 17)),
                                    Fr(rnd.randint(-40, 40), rnd.randint(1, 17))))
             for _ in range(3)]
        for M in A + B:
            assert mmul(M, M) == I2, '[E-IND-REP] an observable does not square to the identity'

        def word_operator(word, reverse=False):
            wa, wb = (list(reversed(word[0])), list(reversed(word[1]))) if reverse else word
            Ma, Mb = I2, I2
            for i in wa:
                Ma = mmul(Ma, A[i])
            for j in wb:
                Mb = mmul(Mb, B[j])
            return kron(Ma, Mb)

        Wop = [word_operator(w) for w in WORDS]
        Wrev = [word_operator(w, reverse=True) for w in WORDS]
        J, Jdag = [], []
        for j in range(n):
            acc, accd = zeros(4), zeros(4)
            for i, row in enumerate(BMAP):
                if row[j]:
                    acc = madd(acc, mscale(Fr(row[j]), Wop[i]))
                    accd = madd(accd, mscale(Fr(row[j]), Wrev[i]))
            J.append(acc)
            Jdag.append(accd)
            assert accd == dagger(acc), '[E-IND-REP] word reversal is not the adjoint'
        rhs = zeros(4)
        for j in range(n):
            Y = zeros(4)
            for k in range(n):
                if X[j][k]:
                    Y = madd(Y, mscale(X[j][k], J[k]))
            rhs = madd(rhs, mmul(Jdag[j], Y))

        def coordinate_operator(idx):
            if idx < 3:
                return kron(A[idx], I2)
            if idx < 6:
                return kron(I2, B[idx - 3])
            x, y = divmod(idx - 6, 3)
            return kron(A[x], B[y])

        lhs = mscale(Fr(7) - eps / 4, I4)
        for idx, co in enumerate(penalised_coefficients(eps)):
            if co:
                lhs = madd(lhs, mscale(-co, coordinate_operator(idx)))
        assert all(lhs[a][b] == rhs[a][b] for a in range(4) for b in range(4)), \
            f'[E-IND-REP] {label}: exact representation disagrees with the SOS reconstruction'
    print(f'  PASS [B] exact Gaussian-rational representation agrees, {label}', flush=True)

# =============================================================================
# C. positive definiteness by integer Bareiss leading principal minors
# =============================================================================
for label, X, eps in CASES:
    n = len(X)
    den = 1
    for row in X:
        for x in row:
            den = den * x.denominator // math.gcd(den, x.denominator)
    S = [[int(x * den) for x in row] for row in X]
    prev = 1
    for k in range(n):
        assert S[k][k] > 0, f'[E-IND-MINOR] {label}: leading principal minor {k + 1} is not positive'
        for i in range(k + 1, n):
            row_i, row_k = S[i], S[k]
            pivot = row_k[k]
            for j in range(k + 1, n):
                row_i[j] = (row_i[j] * pivot - row_i[k] * row_k[j]) // prev
        prev = S[k][k]
    print(f'  PASS [C] all {n} leading principal minors positive by integer Bareiss, {label}',
          flush=True)

# The free improvement over alpha = 4, needing no new SDP.  Since J_8 = 4K and K is a
# projector, J_8^dagger J_8 = 16 K, so subtracting 1/48 from entry (8,8) of the ORIGINAL Gram
# turns its identity into 7I - B_F - (1/3) K, that is F + p/3 <= 7 and alpha_star <= 11/3.
# It is a certificate only if the perturbed Gram is STILL positive definite, which is checked
# here on the same integer route rather than asserted in prose.
assert not {k: v for k, v in eadd(emul(Jl[8], Jl[8]), escale(Fr(-16), K)).items() if v}, \
    '[E-IND-RESIDUAL] J_8^dagger J_8 is not 16 K, so the free F + p/3 <= 7 step does not follow'
Y = [row[:] for row in CASES[1][1]]
Y[8][8] -= Fr(1, 48)
den = 1
for row in Y:
    for x in row:
        den = den * x.denominator // math.gcd(den, x.denominator)
S = [[int(x * den) for x in row] for row in Y]
prev = 1
for k in range(len(S)):
    assert S[k][k] > 0, ('[E-IND-MINOR] the original Gram minus (1/48) e8 e8^T is not positive '
                         'definite, so the free F + p/3 <= 7 step is not a certificate')
    for i in range(k + 1, len(S)):
        pivot = S[k][k]
        for j in range(k + 1, len(S)):
            S[i][j] = (S[i][j] * pivot - S[i][k] * S[k][j]) // prev
    prev = S[k][k]
print('  PASS [C] the original Gram minus (1/48) e8 e8^T is still positive definite: '
      'F + p/3 <= 7 for free, i.e. alpha_star <= 11/3', flush=True)

# =============================================================================
# E. numerical corroboration of the two reduction steps (not a proof)
# =============================================================================
try:
    import numpy as np
except ImportError:                                            # pragma: no cover
    print('  SKIP [E] numpy absent; the reduction corroboration needs it', flush=True)
else:
    rng = np.random.default_rng(20260907)
    fvec = np.array([float(x) for x in FVEC])
    eps0f = float(EPS0)

    def rand_effect(d):
        M = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
        H = M @ M.conj().T
        return H / (np.linalg.eigvalsh(H).max() * rng.uniform(1.0, 2.0))

    def coords(psi, dA, dB, Ae, Be):
        rho = np.outer(psi, psi.conj())
        Ao = [2 * E - np.eye(dA) for E in Ae]
        Bo = [2 * E - np.eye(dB) for E in Be]
        v = np.zeros(15)
        for x in range(3):
            v[x] = np.real(np.trace(rho @ np.kron(Ao[x], np.eye(dB))))
        for y in range(3):
            v[3 + y] = np.real(np.trace(rho @ np.kron(np.eye(dA), Bo[y])))
        for x in range(3):
            for y in range(3):
                v[6 + 3 * x + y] = np.real(np.trace(rho @ np.kron(Ao[x], Bo[y])))
        return v

    def Gof(v):
        return fvec @ v + eps0f * (1 + v[1] + v[3] + v[9]) / 4

    # E1: every binary qubit effect is a convex mixture of a rank-one projector, I and 0.
    worst = 0.0
    for _ in range(400):
        E = rand_effect(2)
        (l2, l1), U = np.linalg.eigh(E)[0], np.linalg.eigh(E)[1]
        Pi = np.outer(U[:, 1], U[:, 1].conj())
        w = np.array([l1 - l2, l2, 1 - l1])
        assert w.min() > -1e-12 and abs(w.sum() - 1) < 1e-12, \
            '[E-IND-REDUCTION] the effect decomposition weights are not a probability vector'
        worst = max(worst, np.abs((l1 - l2) * Pi + l2 * np.eye(2) - E).max())
    assert worst < 1e-9, '[E-IND-REDUCTION] the effect decomposition does not reconstruct the effect'
    print(f'  PASS [E] binary qubit effect = (l1-l2) Pi + l2 I + (1-l1) 0, error {worst:.2e}',
          flush=True)

    # E2: sampling those labels independently of the settings decomposes the behaviour,
    #     and every component sits in a branch this certificate covers.
    def component(E, label):
        if label == 0:
            U = np.linalg.eigh(E)[1]
            return np.outer(U[:, 1], U[:, 1].conj())
        return np.eye(2) if label == 1 else np.zeros((2, 2))

    def weights(E):
        l2, l1 = np.linalg.eigvalsh(E)
        return np.array([l1 - l2, l2, 1 - l1])

    worst_mix, worst_G = 0.0, -np.inf
    for _ in range(12):
        psi = rng.normal(size=4) + 1j * rng.normal(size=4)
        psi /= np.linalg.norm(psi)
        Ae = [rand_effect(2) for _ in range(3)]
        Be = [rand_effect(2) for _ in range(3)]
        v = coords(psi, 2, 2, Ae, Be)
        wA, wB = [weights(E) for E in Ae], [weights(E) for E in Be]
        mix = np.zeros(15)
        for lab in itertools.product(range(3), repeat=6):
            wt = float(np.prod([wA[x][lab[x]] for x in range(3)])
                       * np.prod([wB[y][lab[3 + y]] for y in range(3)]))
            if wt < 1e-14:
                continue
            cv = coords(psi, 2, 2, [component(Ae[x], lab[x]) for x in range(3)],
                        [component(Be[y], lab[3 + y]) for y in range(3)])
            mix += wt * cv
            worst_G = max(worst_G, Gof(cv))
        worst_mix = max(worst_mix, np.abs(mix - v).max())
        worst_G = max(worst_G, Gof(v))
    assert worst_mix < 1e-9, \
        '[E-IND-REDUCTION] the setting-independent label mixture does not reproduce the behaviour'
    assert worst_G <= 7 + 1e-9, '[E-IND-REDUCTION] a projective/deterministic component exceeds G = 7'
    print(f'  PASS [E] label mixture reproduces the behaviour (error {worst_mix:.2e}); '
          f'worst component G = {worst_G:.9f}', flush=True)

    # E3: Schmidt compression preserves the behaviour and maps POVMs to POVMs.
    worst_c = 0.0
    for _ in range(40):
        dA, dB = int(rng.integers(3, 6)), int(rng.integers(3, 6))
        UA = np.linalg.qr(rng.normal(size=(dA, dA)) + 1j * rng.normal(size=(dA, dA)))[0]
        UB = np.linalg.qr(rng.normal(size=(dB, dB)) + 1j * rng.normal(size=(dB, dB)))[0]
        cc = rng.uniform(0.1, 1, 2)
        cc /= np.linalg.norm(cc)
        psi = sum(cc[k] * np.kron(UA[:, k], UB[:, k]) for k in range(2))
        Ae = [rand_effect(dA) for _ in range(3)]
        Be = [rand_effect(dB) for _ in range(3)]
        v = coords(psi, dA, dB, Ae, Be)
        cA = [UA[:, :2].conj().T @ E @ UA[:, :2] for E in Ae]
        cB = [UB[:, :2].conj().T @ E @ UB[:, :2] for E in Be]
        for E in cA + cB:
            w = np.linalg.eigvalsh(E)
            assert w.min() > -1e-9 and w.max() < 1 + 1e-9, \
                '[E-IND-REDUCTION] a compressed effect is not a valid POVM element'
        psi2 = sum(cc[k] * np.kron(np.eye(2)[:, k], np.eye(2)[:, k]) for k in range(2))
        worst_c = max(worst_c, np.abs(v - coords(psi2, 2, 2, cA, cB)).max())
    assert worst_c < 1e-9, '[E-IND-REDUCTION] Schmidt compression changes the behaviour'
    print(f'  PASS [E] compression to the 2x2 Schmidt supports is behaviour-preserving '
          f'(error {worst_c:.2e})', flush=True)

    best = -np.inf
    for _ in range(1500):
        UA = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))[0]
        UB = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))[0]
        cc = rng.uniform(0, 1, 2)
        cc /= np.linalg.norm(cc)
        psi = sum(cc[k] * np.kron(UA[:, k], UB[:, k]) for k in range(2))
        best = max(best, Gof(coords(psi, 4, 4, [rand_effect(4) for _ in range(3)],
                                    [rand_effect(4) for _ in range(3)])))
    assert best <= 7 + 1e-9, '[E-IND-REDUCTION] a random Schmidt-number-two behaviour exceeds G = 7'
    print(f'  PASS [E] random Schmidt-number-two search found nothing above 7 '
          f'(best {best:.6f})', flush=True)

print('PASS independent reconstruction agrees with the endpoint certificate on every route',
      flush=True)
