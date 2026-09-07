"""Independent reconstruction of the facet result and the qutrit realization.

Independence here means DIFFERENT MATHEMATICS, not a second copy of the primary verifier.
This file shares no code with proofs/ and deliberately avoids the machinery those verifiers
use:

  * proofs/verify_qutrit.py computes the 36 probabilities from scalar Gaussian-integer
    formulas for the marginals and the joint rank-one term.  This file instead builds the
    9-dimensional state vector and the full 9x9 measurement operators, forms the 81x81
    tensor products, and evaluates <psi| A tensor B |psi> / <psi|psi> directly.
  * proofs/verify_facet.py certifies membership of the saturating points by exhibiting the
    stored local models and checking positivity/CHSH dual certificates.  This file ignores
    both and CONSTRUCTS a local hidden-variable model for each point from scratch, by Fine's
    theorem and an interval-intersection argument, then checks the model reproduces every
    probability of the designated restriction exactly.

If the two agree, a mistake would have to be present in both formulations at once.

Method for the local models.  Fix a point on side A with local pair (i, j).  For each of Bob's
settings y and outcome b, the joint distribution of Alice's two counterfactual outputs is
determined up to one free parameter t = P(A_i = 1, A_j = 1, B_y = b); positivity confines t to
an interval [max(0, u + v - r), min(u, v)] built from the observed marginals.  Summing over b
gives an interval per y.  Intervals on a line have a common point whenever they pairwise
intersect, which is what the CHSH inequalities guarantee, so a single t works for all of Bob's
settings simultaneously.  Splitting that t across b and taking the conditionally independent
product over Bob's three settings gives an explicit deterministic-strategy decomposition.

This is the construction sketched in docs/review_2026-09-07_ai.md; the implementation here is
written from the description rather than copied.

Exact rational and exact complex-rational arithmetic throughout, in the standard library
only -- no SymPy, so this file can be run against an unpacked archive with nothing installed.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are proof checks.")

import json
from fractions import Fraction as Fr
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOFS = ROOT / 'proofs'
W = [1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1]
fails = []


def prob(v, x, y, a, b):
    return (1 + (-1) ** a * v[x] + (-1) ** b * v[3 + y]
            + (-1) ** (a + b) * v[6 + 3 * x + y]) / 4


def build_local_model(v, side, pair):
    """Construct an explicit LHV decomposition of the (pair x all) restriction, or fail.

    Returns a dict from (Alice's two counterfactual outputs, Bob's three) to a weight.
    """
    if side == 'A':
        def f(k, y, a, b):
            return prob(v, pair[k], y, a, b)
    else:
        def f(k, y, a, b):
            return prob(v, y, pair[k], b, a)

    # per (y, b): the interval of admissible t-contributions
    cells = []
    for y in range(3):
        row = []
        for b in range(2):
            r = sum(f(0, y, a, b) for a in range(2))
            u = f(0, y, 1, b)
            w = f(1, y, 1, b)
            row.append((r, u, w, max(Fr(0), u + w - r), min(u, w)))
        cells.append(row)

    lo = max(sum(c[3] for c in row) for row in cells)
    hi = min(sum(c[4] for c in row) for row in cells)
    if lo > hi:                       # would mean the CHSH constraints are violated
        return None
    t = lo

    joints = []
    for row in cells:
        t0 = max(row[0][3], t - row[1][4])
        parts = [t0, t - t0]
        q = {}
        for b, (r, u, w, l, h) in enumerate(row):
            z = parts[b]
            if not (l <= z <= h):
                return None
            q[1, 1, b] = z
            q[1, 0, b] = u - z
            q[0, 1, b] = w - z
            q[0, 0, b] = r - u - w + z
        joints.append(q)

    marg = {aa: sum(joints[0][aa[0], aa[1], b] for b in range(2))
            for aa in product(range(2), repeat=2)}
    dist = {}
    for aa in product(range(2), repeat=2):
        for bb in product(range(2), repeat=3):
            if marg[aa] == 0:
                dist[aa, bb] = Fr(0)
            else:
                num = Fr(1)
                for y in range(3):
                    num *= joints[y][aa[0], aa[1], bb[y]]
                dist[aa, bb] = num / marg[aa] ** 2
    if sum(dist.values()) != 1 or min(dist.values()) < 0:
        return None
    # the model must reproduce every probability of the designated restriction, exactly
    for k, y, a, b in product(range(2), range(3), range(2), range(2)):
        got = sum(z for (aa, bb), z in dist.items() if aa[k] == a and bb[y] == b)
        if got != f(k, y, a, b):
            return None
    return dist


def rank(rows):
    """Exact rank over the rationals, by elimination.  No linear-algebra library."""
    a = [[Fr(x) for x in r] for r in rows]
    n, r = len(a[0]), 0
    for j in range(n):
        k = next((k for k in range(r, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[r], a[k] = a[k], a[r]
        piv = a[r][j]
        a[r] = [x / piv for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][j]:
                f = a[i][j]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


# --- 1. face dimensions, from independently constructed local models ----------------------
facet = json.loads((PROOFS / 'facet_certificate.json').read_text())
faces = json.loads((PROOFS / 'face_dimension_points.json').read_text())

for side in 'AB':
    homog = []
    for e in faces[side]:
        v = [Fr(t) for t in e['v']]
        assert sum(a * b for a, b in zip(W, v)) == 7, 'point is not on the F = 7 face'
        assert min(prob(v, x, y, a, b) for x, y, a, b
                   in product(range(3), range(3), range(2), range(2))) >= 0
        if build_local_model(v, side, e['pair']) is None:
            fails.append(f"side {side}: no local model constructed for a supplied face point")
        homog.append([1] + v)
    r = rank(homog) - 1
    if r != 13:
        fails.append(f"side {side}: independently computed affine rank {r}, expected 13")
    else:
        print(f"  PASS side {side}: {len(homog)} points, local models built from scratch, "
              f"affine rank 13")

homog = []
for e in facet['saturating_points']:
    v = [Fr(t) for t in e['v']]
    assert sum(a * b for a, b in zip(W, v)) == 7
    if build_local_model(v, e['side'], e['pair']) is None:
        fails.append("facet: no local model constructed for a supplied saturating point")
    homog.append([1] + v)
r = rank(homog) - 1
if r != 14:
    fails.append(f"facet: independently computed affine rank {r}, expected 14")
else:
    print(f"  PASS two-sided face: {len(homog)} points, local models built from scratch, "
          f"affine rank 14 against ambient 15")

# --- 2. the 36 qutrit probabilities, from full 9x9 operators ------------------------------
cert = json.loads((PROOFS / 'qutrit_certificate.json').read_text())

# Exact arithmetic in Q(i): a number is the pair (real, imaginary) of Fractions.
def cadd(u, w):
    return (u[0] + w[0], u[1] + w[1])


def cmul(u, w):
    return (u[0] * w[0] - u[1] * w[1], u[0] * w[1] + u[1] * w[0])


def conj(u):
    return (u[0], -u[1])


PSI = [(Fr(z[0]), Fr(z[1])) for z in cert['state']]
assert len(PSI) == 9
NORM = sum(z[0] * z[0] + z[1] * z[1] for z in PSI)
assert NORM > 0


def effect_pair(entry):
    """The 3x3 rank-one projector on the given vector, and its complement."""
    u = [(Fr(z[0]), Fr(z[1])) for z in entry['vector']]
    nu = sum(z[0] * z[0] + z[1] * z[1] for z in u)
    assert nu > 0
    proj = [[tuple(t / nu for t in cmul(u[i], conj(u[k]))) for k in range(3)] for i in range(3)]
    comp = [[((Fr(int(i == k)) - proj[i][k][0]), -proj[i][k][1]) for k in range(3)]
            for i in range(3)]
    r = entry['rank_one_outcome']
    return [proj if a == r else comp for a in range(2)]


A = [effect_pair(e) for e in cert['Alice']]
B = [effect_pair(e) for e in cert['Bob']]

# p(ab|xy) = <psi| A tensor B |psi> / <psi|psi>, with (A tensor B)[(i,j),(k,l)] = A[i][k] B[j][l].
got = []
for x, y, a, b in product(range(3), range(3), range(2), range(2)):
    Ax, By = A[x][a], B[y][b]
    total = (Fr(0), Fr(0))
    for i, j in product(range(3), repeat=2):
        bra = conj(PSI[3 * i + j])
        for k, l in product(range(3), repeat=2):
            term = cmul(cmul(Ax[i][k], By[j][l]), PSI[3 * k + l])
            total = cadd(total, cmul(bra, term))
    assert total[1] == 0, 'a probability came out with a nonzero imaginary part'
    got.append(total[0] / NORM)

shipped = [Fr(t) for t in cert['Q']]
if got != shipped:
    bad = [i for i, (u, w) in enumerate(zip(got, shipped)) if u != w]
    fails.append(f"Born reconstruction disagrees at {len(bad)} of 36 entries")
else:
    print("  PASS all 36 qutrit probabilities reproduced from full 9x9 operators")

wp = [Fr((-1) ** a * W[x] + (-1) ** b * W[3 + y], 3) + (-1) ** (a + b) * W[6 + 3 * x + y]
      for x, y, a, b in product(range(3), range(3), range(2), range(2))]
score = sum(u * w for u, w in zip(wp, got))
if score != Fr(cert['score']) or score <= 7:
    fails.append(f"independently evaluated F = {float(score)}, expected {cert['score']} and > 7")
else:
    print(f"  PASS F evaluated independently on those probabilities: {float(score)} > 7")

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS independent reconstruction agrees: face dimensions 13/13/14 and the qutrit "
      "separation")
