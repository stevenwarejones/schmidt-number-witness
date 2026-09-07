"""The correlation-weighted I3322(c) family does not detect Q either, for any c >= 1.

proofs/verify_novelty_comparison.py compares Q against the ORDINARY I3322 and M3322 score
thresholds.  That leaves the published one-parameter families, which are the natural next
thing an expert would reach for.  This file settles one of them exactly, over the whole
parameter range and all relabelings at once.

The family is

    I3322(c)  =  <A0> + <A1> + <B0> + <B1>
                 - <A0B0> - <A0B1> - <A1B0> - <A1B1>
                 + c ( <A0B2> - <A1B2> + <A2B0> - <A2B1> ),

as defined at arXiv:1507.07521 Eq. (26) and arXiv:1808.02412 Eq. (E1); c = 1 recovers I3322,
whose local bound is 4.

QUBIT BENCHMARK, derived here rather than quoted.  Take the maximally entangled two-qubit
state and, with t^2 + z^2 = 1,

    A0 =  t X + z Z,   A1 = -t X + z Z,   A2 = X,
    B0 =  t X - z Z,   B1 = -t X - z Z,   B2 = X.

All six are traceless and square to the identity.  The score is 4 z^2 + 4 c t = 4 - 4 t^2 + 4 c t,
so t = c/2 gives 4 + c^2 (admissible while c <= 2) and t = 1 gives 4 c.  These are ACHIEVABLE
scores -- lower witnesses -- and nothing here claims they are the qubit maxima.  A behavior
scoring below an achievable qubit score cannot have crossed the true qubit maximum, which is
all the non-detection argument needs.

THE COMPARISON.  Each relabeling g makes c |-> I3322(c)^g(Q) an affine function a_g + b_g c.
Over all 4608 relabelings these collapse to a few hundred distinct lines, and each is checked
against the benchmark on both intervals in exact rational arithmetic:

    on [1,2]   min over c of  (4 + c^2) - (a + b c)  > 0, the quadratic minimised at c = b/2
                              clamped to the interval;
    on [2,inf) b <= 4 and (8 - a - 2b) > 0, so 4c - (a + bc) is nondecreasing and positive at 2.

SCOPE.  This is one published family, compared against Q, under input/output relabelings and
party exchange.  It says nothing about the broader Gigena-Kaniewski family, about wirings,
filtering, many-copy protocols, or conditional tradeoffs.  See docs/PRIOR_ART.md.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")

import json
from fractions import Fraction as Fr
from itertools import permutations, product
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT = json.loads((HERE / 'qutrit_certificate.json').read_text())

# --- the benchmark, derived symbolically from the Born rule ------------------------------
t, z, cs = sp.symbols('t z c', real=True)
X, Z, I2 = sp.Matrix([[0, 1], [1, 0]]), sp.diag(1, -1), sp.eye(2)
K = sp.kronecker_product
OBS_A = [t * X + z * Z, -t * X + z * Z, X]
OBS_B = [t * X - z * Z, -t * X - z * Z, X]
for o in OBS_A + OBS_B:
    assert sp.simplify(sp.trace(o)) == 0
    assert (o * o - I2).applyfunc(lambda e: sp.expand(e).subs(z * z, 1 - t * t)) == sp.zeros(2)
PHI = sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2)

BASE = (1, 1, 0, 1, 1, 0, -1, -1, 0, -1, -1, 0, 0, 0, 0)
SLOPE = (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, -1, 1, -1, 0)
W_C = [BASE[i] + cs * SLOPE[i] for i in range(15)]

sc = sum(W_C[i] * sp.simplify((PHI.T * K(OBS_A[i], I2) * PHI)[0]) for i in range(3))
sc += sum(W_C[3 + j] * sp.simplify((PHI.T * K(I2, OBS_B[j]) * PHI)[0]) for j in range(3))
sc += sum(W_C[6 + 3 * i + j] * sp.simplify((PHI.T * K(OBS_A[i], OBS_B[j]) * PHI)[0])
          for i, j in product(range(3), repeat=2))
sc = sp.expand(sp.expand(sc).subs(z * z, 1 - t * t))
assert sc == sp.expand(4 - 4 * t ** 2 + 4 * cs * t), sc
assert sp.expand(sc.subs(t, cs / 2)) == sp.expand(4 + cs ** 2)
assert sp.expand(sc.subs(t, 1)) == 4 * cs
print('PASS qubit benchmark derived from the Born rule: score = 4 - 4t^2 + 4ct, giving '
      '4 + c^2 at t = c/2 and 4c at t = 1')
print('     (achievable scores, i.e. lower witnesses; no claim that these are the qubit maxima)')

# --- Q as an exact correlator vector -----------------------------------------------------
IDX = list(product(range(3), range(3), range(2), range(2)))
P = dict(zip(IDX, (Fr(u) for u in CERT['Q'])))
assert len(P) == 36 and min(P.values()) >= 0
for x, y in product(range(3), repeat=2):
    assert sum(P[x, y, a, b] for a, b in product(range(2), repeat=2)) == 1
V = ([sum((-1) ** a * P[x, 0, a, b] for a, b in product(range(2), repeat=2)) for x in range(3)]
     + [sum((-1) ** b * P[0, y, a, b] for a, b in product(range(2), repeat=2)) for y in range(3)]
     + [sum((-1) ** (a + b) * P[x, y, a, b] for a, b in product(range(2), repeat=2))
        for x, y in product(range(3), repeat=2)])
for x, y in product(range(3), repeat=2):                       # nonsignaling, or V is a lie
    assert sum((-1) ** a * P[x, y, a, b] for a, b in product(range(2), repeat=2)) == V[x]
    assert sum((-1) ** b * P[x, y, a, b] for a, b in product(range(2), repeat=2)) == V[3 + y]

# I3322(1) must reproduce the published local bound of 4, or the transcription is wrong.
LOCAL = [list(a) + list(b) + [u * v for u in a for v in b]
         for a, b in product(product([-1, 1], repeat=3), repeat=2)]
w1 = [BASE[i] + SLOPE[i] for i in range(15)]
assert max(sum(u * v for u, v in zip(w1, p)) for p in LOCAL) == 4
print('PASS I3322(c=1) has local bound 4, matching the published value (necessary, not '
      'sufficient)')


def relabel(w, sa, sb, sig, tau, swap):
    A = [sa[i] * w[i] for i in range(3)]
    B = [sb[j] * w[3 + j] for j in range(3)]
    E = [[sa[i] * sb[j] * w[6 + 3 * i + j] for j in range(3)] for i in range(3)]
    A2, B2, E2 = [0] * 3, [0] * 3, [[0] * 3 for _ in range(3)]
    for i in range(3):
        A2[sig[i]] = A[i]
    for j in range(3):
        B2[tau[j]] = B[j]
    for i, j in product(range(3), repeat=2):
        E2[sig[i]][tau[j]] = E[i][j]
    if swap:
        A2, B2, E2 = B2, A2, [[E2[j][i] for j in range(3)] for i in range(3)]
    return tuple(A2) + tuple(B2) + tuple(E2[i][j] for i in range(3) for j in range(3))


GROUP = [(sa, sb, sig, tau, sw)
         for sa in product([1, -1], repeat=3) for sb in product([1, -1], repeat=3)
         for sig in permutations(range(3)) for tau in permutations(range(3)) for sw in (0, 1)]

lines = {(sum(u * v for u, v in zip(relabel(BASE, *g), V)),
          sum(u * v for u, v in zip(relabel(SLOPE, *g), V))) for g in GROUP}

worst, at_c = None, None
for a, b in lines:
    # [1, 2]: benchmark 4 + c^2, so the gap is a quadratic in c minimised at c = b/2.
    cc = max(Fr(1), min(Fr(2), b / 2))
    gap = 4 + cc * cc - a - b * cc
    assert gap > 0, (a, b, cc, gap)
    # [2, inf): benchmark 4c.  The gap 4c - (a + bc) is nondecreasing iff b <= 4.
    assert b <= 4 and 8 - a - 2 * b > 0, (a, b)
    if worst is None or gap < worst:
        worst, at_c = gap, cc

print(f'PASS every relabeling of I3322(c) on Q, for EVERY c >= 1, lies strictly below the '
      f'benchmark')
print(f'     {len(lines)} distinct score lines; smallest margin {float(worst):.16f} at '
      f'c = {float(at_c):.15f}')
print(f'     decided in exact rational arithmetic -- the decimals above are display only')
print('CONCLUSION: the correlation-weighted I3322(c) family does not detect Q beyond qubits, '
      'at any c >= 1.\n'
      '            One published family, under relabelings, on this behavior.  Not a novelty '
      'clearance; see docs/PRIOR_ART.md.')
