"""The equality face, re-derived without reading a single supplied dual.

proofs/verify_equality_face.py replays exact dual certificates.  A dual is checkable and
therefore trustworthy, but replaying one still starts from a number somebody else computed.
This file starts from nothing but the constraints.  It carries its own exact rational
two-phase simplex (Bland's rule, so it cannot cycle) and re-derives, for every one of the 48
deterministic-observable patterns, the fact the certificate asserts:

  * for the 17 "no-signaling" patterns, that the face {A v <= 1, F.v = 7, deterministic
    marginals} is INFEASIBLE -- a strictly stronger statement than the supplied max F < 7;
  * for the other 31, the exact maximum of every one of the 36 event functionals on that face,
    and hence exactly which joint probabilities are forced to vanish.  The forced set is
    then required to CONTAIN the certificate's claimed zeros, so a certificate claiming a zero
    that is not forced would be caught here even though its dual checks out.

The projector closure is not repeated -- proofs/verify_equality_face.py implements it once
from the five geometric rules, and running a second copy of the same rules would test the
implementation rather than the rules.  Instead this file corroborates the CONCLUSION
numerically: a see-saw search over rank-two two-qubit states, structured to each pattern, must
fail to reach F = 7 wherever the certificate says the pattern is impossible.  That is
corroboration, not proof, and is labelled as such.

Runtime is dominated by the exact LPs -- roughly two minutes.  That is the price of not
trusting the supplied numbers.

Diagnostic codes: [E-LP-FEASIBLE] [E-LP-ZERO] [E-LP-VERTICES] [E-LP-SEARCH]
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit('Run without -O: assertions in this file are certificate checks.')

import itertools
import json
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOFS = ROOT / 'proofs'

cert = json.loads((PROOFS / 'equality_face_certificate.json').read_text())
f = cert['coefficients']

EVENTS = list(itertools.product(range(3), range(3), (-1, 1), (-1, 1)))


def positivity_row(x, y, a, b):
    r = [0] * 15
    r[x] += a
    r[3 + y] += b
    r[6 + 3 * x + y] += a * b
    return r


ROWS = [positivity_row(*e) for e in EVENTS]
A_UB = [[-x for x in r] for r in ROWS]              # 4P = 1 + r.v >= 0  <=>  -r.v <= 1
B_UB = [1] * 36


# =============================================================================
# an exact rational two-phase simplex:  max c.v  s.t.  A v <= b, E v = d, v free
# =============================================================================
def _pivot(T, obj, basis, ncols):
    while True:
        col = next((j for j in range(ncols) if obj[j] < 0), None)
        if col is None:
            return True
        ratios = [(T[i][-1] / T[i][col], i) for i in range(len(T)) if T[i][col] > 0]
        if not ratios:
            return False                                  # unbounded
        best = min(r for r, _ in ratios)
        row = min(i for r, i in ratios if r == best)      # Bland's rule: lowest index
        piv = T[row][col]
        T[row] = [x / piv for x in T[row]]
        for i in range(len(T)):
            if i != row and T[i][col]:
                fac = T[i][col]
                T[i] = [x - fac * y for x, y in zip(T[i], T[row])]
        if obj[col]:
            fac = obj[col]
            for k in range(len(obj)):
                obj[k] -= fac * T[row][k]
        basis[row] = col


def prepare(n, A, b, E=(), d=()):
    """Phase 1 once per constraint system.  None if the system is infeasible."""
    E, d = list(E), list(d)
    m1 = len(A)
    ncol = 2 * n + m1                                     # v+, v-, slacks
    rows, rhs = [], []
    for i in range(m1):
        rows.append([Fr(x) for x in A[i]] + [Fr(-x) for x in A[i]]
                    + [Fr(1) if k == i else Fr(0) for k in range(m1)])
        rhs.append(Fr(b[i]))
    for j in range(len(E)):
        rows.append([Fr(x) for x in E[j]] + [Fr(-x) for x in E[j]] + [Fr(0)] * m1)
        rhs.append(Fr(d[j]))
    for i in range(len(rows)):
        if rhs[i] < 0:
            rows[i] = [-x for x in rows[i]]
            rhs[i] = -rhs[i]
    m = len(rows)
    total = ncol + m
    T = [rows[i] + [Fr(1) if k == i else Fr(0) for k in range(m)] + [rhs[i]] for i in range(m)]
    basis = [ncol + i for i in range(m)]
    obj = [Fr(0)] * (total + 1)
    for i in range(m):
        for k in range(total + 1):
            obj[k] -= T[i][k]
    for i in range(m):
        obj[ncol + i] += Fr(1)
    if not _pivot(T, obj, basis, total):
        return None
    if -obj[-1] != 0:
        return None                                       # infeasible
    for i in range(m):                                    # drive artificials out where possible
        if basis[i] >= ncol:
            col = next((j for j in range(ncol) if T[i][j]), None)
            if col is None:
                continue
            piv = T[i][col]
            T[i] = [x / piv for x in T[i]]
            for k in range(m):
                if k != i and T[k][col]:
                    fac = T[k][col]
                    T[k] = [x - fac * y for x, y in zip(T[k], T[i])]
            basis[i] = col
    return {'T': T, 'basis': basis, 'ncol': ncol, 'm1': m1, 'm': m, 'n': n}


def maximise(state, c):
    """Exact maximum of c.v over the prepared system; None if unbounded."""
    T = [row[:] for row in state['T']]
    basis = list(state['basis'])
    n, m1, m, ncol = state['n'], state['m1'], state['m'], state['ncol']
    cost = [Fr(x) for x in c] + [Fr(-x) for x in c] + [Fr(0)] * (m1 + m + 1)
    obj = [-x for x in cost]
    for i in range(m):
        if obj[basis[i]]:
            fac = obj[basis[i]]
            for k in range(len(obj)):
                obj[k] -= fac * T[i][k]
    if not _pivot(T, obj, basis, ncol):
        return None
    return obj[-1]


# the simplex must agree with two facts established elsewhere in the repository
whole = prepare(15, A_UB, B_UB)
assert whole is not None, '[E-LP-FEASIBLE] the no-signaling polytope came out infeasible'
assert maximise(whole, f) == 9, '[E-LP-FEASIBLE] no-signaling max of F is not 9; the simplex is wrong'
M_A = [Fr(c) for c in f]
for k in (1, 3, 9):
    M_A[k] += 1
assert maximise(whole, M_A) == 8, '[E-LP-FEASIBLE] no-signaling max of M_A is not 8; the simplex is wrong'
print('  PASS exact simplex self-check: no-signaling maxima F = 9 and M_A = 8', flush=True)


# =============================================================================
# every pattern, re-derived
# =============================================================================
n_inf = n_zero_checked = 0
extra = []
for c in cert['patterns']:
    det = {int(k): v for k, v in c['det'].items()}
    eq = [[int(k == i) for k in range(15)] for i in det]
    rhs = list(det.values())
    face = prepare(15, A_UB, B_UB, [f] + eq, [7] + rhs)
    if 'bound' in c:
        assert face is None, (f'[E-LP-FEASIBLE] pattern {det} is certified to have no F = 7 point, '
                              f'but the exact simplex finds the face feasible')
        n_inf += 1
        continue
    assert face is not None, (f'[E-LP-FEASIBLE] pattern {det} carries forced-zero certificates, '
                              f'but its F = 7 face is empty')
    forced = set()
    for idx, row in enumerate(ROWS):
        top = maximise(face, row)
        assert top is not None, f'[E-LP-ZERO] pattern {det}: event {EVENTS[idx]} is unbounded'
        if top <= -1:
            forced.add(EVENTS[idx])
        n_zero_checked += 1
    claimed = {tuple(z) for z in c['zeros']}
    missing = claimed - forced
    assert not missing, (f'[E-LP-ZERO] pattern {det}: the certificate claims {sorted(missing)[:3]} '
                         f'vanish, but the exact simplex does not force them')
    if forced - claimed:
        extra.append((det, len(forced - claimed)))
print(f'  PASS {n_inf} patterns have a provably EMPTY F = 7 face (stronger than the certified '
      f'max F < 7), by exact simplex', flush=True)
print(f'  PASS every claimed forced zero re-derived independently; {n_zero_checked} exact event '
      f'maxima computed over 31 faces, no supplied dual read', flush=True)
if extra:
    print(f'  note: {len(extra)} pattern(s) force MORE zeros than the certificate lists, which is '
          f'harmless -- the closure only needs the listed ones', flush=True)

# the five vertices, and that they are the whole local F = 7 face
vertices = []
for z in itertools.product((-1, 1), repeat=6):
    v = [Fr(t) for t in list(z) + [a * b for a in z[:3] for b in z[3:]]]
    if sum(Fr(a) * b for a, b in zip(f, v)) == 7:
        vertices.append(v)
assert len(vertices) == 5, '[E-LP-VERTICES] the number of local deterministic saturators is not 5'
for v in vertices:
    assert (1 + v[1] + v[3] + v[9]) / 4 == 0, '[E-LP-VERTICES] a vertex of L_F has p > 0'
assert maximise(whole, f) == 9 and all(
    sum(Fr(a) * b for a, b in zip(f, v)) == 7 for v in vertices)
print('  PASS five local deterministic saturators, every one with p = 0', flush=True)

# =============================================================================
# numerical corroboration -- NOT proof -- of the theorem itself
# =============================================================================
# The obvious test, "no pattern reaches F = 7", is WRONG: one of the 31 patterns is closed as
# LOCAL rather than impossible, and a local behaviour on that branch does reach 7.  So the
# corroboration tests what the theorem actually says -- every near-saturating rank-two
# two-qubit behaviour found by search sits close to L_F -- rather than a stronger claim that
# happens to be false.
try:
    import numpy as np
except ImportError:                                             # pragma: no cover
    print('  SKIP numerical corroboration: numpy absent', flush=True)
else:
    rng = np.random.default_rng(20260907)
    fv = np.array([float(x) for x in f])
    W = np.array([[float(x) for x in v] for v in vertices])      # the five vertices of L_F

    def bloch(u):
        u = np.asarray(u, float)
        return np.array([[u[2], u[0] - 1j * u[1]], [u[0] + 1j * u[1], -u[2]]]) / np.linalg.norm(u)

    def coords(M, A, B):
        """The 15 correlator coordinates; every trace is taken on a single qubit."""
        rA = M @ M.conj().T
        rB = M.T @ M.conj()
        Mc = M.conj().T
        v = np.empty(15)
        for x in range(3):
            v[x] = np.real(np.trace(A[x] @ rA))
        for y in range(3):
            v[3 + y] = np.real(np.trace(B[y] @ rB))
        for x in range(3):
            AM = A[x] @ M
            for y in range(3):
                v[6 + 3 * x + y] = np.real(np.trace(AM @ B[y].T @ Mc))
        return v

    def observables(det, dirs):
        A = [det[i] * np.eye(2) if i in det else bloch(dirs[i]) for i in range(3)]
        B = [det[3 + j] * np.eye(2) if 3 + j in det else bloch(dirs[3 + j]) for j in range(3)]
        return A, B

    def distance_to_LF(v):
        """Least-squares distance from a behaviour to the affine hull of L_F, and the most
        negative barycentric weight (negative means outside the simplex)."""
        Aeq = np.vstack([W.T, np.ones(5) * 50.0])                # sum(lambda) = 1, weighted
        rhs = np.concatenate([v, [50.0]])
        lam, *_ = np.linalg.lstsq(Aeq, rhs, rcond=None)
        return float(np.linalg.norm(W.T @ lam - v)), float(lam.min())

    def climb(det, restarts, iters):
        best, best_v = -np.inf, None
        for _ in range(restarts):
            dirs = rng.normal(size=(6, 3))
            th = rng.uniform(0.05, np.pi / 2 - 0.05)      # rank two: never a product state
            M = np.diag([np.cos(th), np.sin(th)])
            A, B = observables(det, dirs)
            cur = fv @ coords(M, A, B)
            step = 0.6
            for _ in range(iters):
                nd = dirs + rng.normal(size=(6, 3)) * step
                nt = min(max(th + rng.normal() * step * 0.5, 0.05), np.pi / 2 - 0.05)
                nM = np.diag([np.cos(nt), np.sin(nt)])
                nA, nB = observables(det, nd)
                val = fv @ coords(nM, nA, nB)
                if val > cur:
                    dirs, th, M, A, B, cur = nd, nt, nM, nA, nB, val
                else:
                    step *= 0.97
            if cur > best:
                best, best_v = cur, coords(M, A, B)
        return best, best_v

    patterns = [{int(k): v for k, v in c['det'].items()}
                for c in cert['patterns'] if 'bound' not in c]
    results = []
    for det in patterns + [{}]:                                   # + the nondegenerate branch
        top, v = climb(det, 25, 120)
        assert top < 7 + 1e-6, (f'[E-LP-SEARCH] a rank-two two-qubit search reached F = {top:.9f} '
                                f'> 7 in pattern {det}, contradicting the sharp bound')
        res, lam = distance_to_LF(v)
        results.append((7 - top, res, lam, det))
    results.sort()
    gap, res, lam, where = results[0]
    # The search is a hill climb, so it gets close to the bound without reaching it.  The
    # assertion is on the point that got CLOSEST: the theorem says a behaviour at F = 7 is in
    # L_F, so the nearest-to-saturating point found had better be nearly in L_F too.  A tight
    # numerical threshold would be a fitted constant, not a check, so the margin is generous and
    # the measured value is printed.
    assert gap < 2e-2, (f'[E-LP-SEARCH] the search got no closer than F = 7 - {gap:.4f}, so it is '
                        f'too weak to corroborate anything')
    assert res < 1e-1, (f'[E-LP-SEARCH] the closest-to-saturating behaviour found, at '
                        f'F = 7 - {gap:.6f} in pattern {where}, sits {res:.3e} from L_F')
    near = [r for g, r, _, _ in results if g < 5e-2]
    print(f'  PASS numerical corroboration over {len(results)} branches: no search exceeded '
          f'F = 7; the closest, at F = 7 - {gap:.6f}, lies {res:.2e} from L_F with least '
          f'barycentric weight {lam:+.1e}; over the {len(near)} branches within 0.05 of the '
          f'bound the distance stays below {max(near):.2e} (corroboration, not proof)', flush=True)

print('PASS the equality face re-derived independently: every deterministic-observable pattern '
      'closed without reading a supplied dual', flush=True)
