"""Exact endpoint certificate for the penalised functional G = F + eps0 * p.

    eps0 = 383689/100000,   alpha0 = 4 - eps0 = 16311/100000,
    p    = P(00|10) = (1 + A1 + B0 + E10)/4,
    G    = F + eps0 * p <= 7   for every Schmidt-number-at-most-two behaviour,

equivalently M_A = F + 4p - 1 <= 6 + alpha0 * p.  The original F <= 7 gives only
alpha0 <= 4, so this is a strict strengthening of the repository's sharp bound;
setting eps0 = 0 recovers it exactly.

WHAT IS PROVED HERE AND WHAT IS NOT.  This file certifies validity of the
inequality on S2.  It says nothing about the two-sided partial-local hull H:
G is a different functional from F, and the facet property proved in
proofs/verify_facet.py belongs to F alone.  See docs/CERTIFICATE_PENALTY_ENDPOINT.md.

Three branches cover every Schmidt-number-two behaviour.

  1. All six qubit observables traceless (nondegenerate projective).  The
     positive-definite 70x70 rational Gram below satisfies the operator identity

         (7 - eps0/4) I - B_{f + eps0 d}  =  sum_{j,k} X[j,k] J_j^dagger J_k,

     where d carries 1/4 in the A1, B0 and E10 slots.  The constant eps0/4 is
     part of the statement: G contains a probability, not only correlators.
     The word list, the 84x70 integer basis map and the Clifford normal-ordering
     algorithm are the repository's existing ones, reached through
     proofs/verify_sharp_qubit.py, so the endpoint rides the already-reviewed
     verification path rather than a new one.

  2. At least one observable deterministic (equal to +I or -I).  The SOS is
     unavailable there because it presumes traceless observables.  Twelve exact
     no-signaling dual certificates instead give M_A <= 6, i.e. F + 4p <= 7, in
     each branch.  Since p >= 0 and eps0 < 4 this implies F + eps0 p <= 7.
     The twelve cover every (observable, sign) pair, so "at least one
     deterministic" is fully covered -- no enumeration of how many are
     deterministic is needed.

  3. General POVMs and Schmidt-number-two mixed states in any dimension reduce to
     branches 1-2 by an effect decomposition and Schmidt compression that involve
     no certificate; the argument is written out in
     docs/CERTIFICATE_PENALTY_ENDPOINT.md and checked numerically in
     tests/verify_endpoint_independent.py.

The lower strategy at the end shows the certified coefficient is nearly optimal:
0.1631016 < alpha_star <= 16311/100000.  The optimum alpha_star is NOT determined.

Diagnostic codes emitted on failure -- tests/test_endpoint_mutations.py requires
rejection to carry the right one:
    [E-EPS-RANGE] [E-GRAM-SHAPE] [E-GRAM-NOT-PD] [E-SOS-RESIDUAL]
    [E-DUAL-NEGATIVE] [E-DUAL-IDENTITY] [E-DUAL-UPPER] [E-BRANCH-COVERAGE]
    [E-LOWER-RATIO]
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Run without -O: assertions here are exact certificate gates.')

import itertools
import json
import runpy
from fractions import Fraction as Fr
from pathlib import Path

PROOFS = Path(__file__).resolve().parent
# The Bell coefficients, fixed here so the cheap checks below need no heavy import.
f = [1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1]

cert = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
eps = Fr(cert['epsilon'])
alpha = Fr(cert['alpha'])
assert eps + alpha == 4 and 0 < eps < 4, '[E-EPS-RANGE] epsilon and alpha must satisfy eps+alpha=4, 0<eps<4'
assert cert['coefficients'] == f, '[E-EPS-RANGE] certificate is stated for a different functional'

X = [[Fr(a) for a in row] for row in cert['gram']]
n = len(X)
assert n == 70 and all(len(r) == n for r in X), '[E-GRAM-SHAPE] Gram must be 70x70'
assert all(X[i][j] == X[j][i] for i in range(n) for j in range(n)), '[E-GRAM-SHAPE] Gram not symmetric'

# --- branch 2: the twelve deterministic-observable no-signaling duals ----------
# 4 * P(ab|xy) = 1 + r.v with a,b the observable VALUES in {-1,+1}.
EVENTS = list(itertools.product(range(3), range(3), (-1, 1), (-1, 1)))


def positivity_row(x, y, a, b):
    r = [0] * 15
    r[x] += a
    r[3 + y] += b
    r[6 + 3 * x + y] += a * b
    return r


ROWS = [positivity_row(*e) for e in EVENTS]
# M_A = F + 4p - 1 = f.v + v1 + v3 + v9, a homogeneous linear functional.
M_A = [Fr(c) for c in f]
for k in (1, 3, 9):
    M_A[k] += 1

branches = json.loads((PROOFS / 'penalty_branch_certificates.json').read_text())
seen = set()
for c in branches:
    i, s = c['i'], c['s']
    t = [Fr(x) for x in c['t']]
    nu = Fr(c['nu'])
    upper = Fr(c['upper'])
    assert len(t) == 36, '[E-DUAL-IDENTITY] a branch dual does not carry 36 multipliers'
    assert all(x >= 0 for x in t), '[E-DUAL-NEGATIVE] a positivity multiplier is negative'
    # weak duality:  M_A = sum_j t_j (-r_j) + nu e_i  as an identity in v, so on
    # {A v <= 1, v_i = s} we get M_A.v <= sum(t) + nu*s.
    for k in range(15):
        lhs = sum(-ROWS[j][k] * t[j] for j in range(36)) + (nu if k == i else Fr(0))
        assert lhs == M_A[k], f'[E-DUAL-IDENTITY] branch ({i},{s}) dual identity fails at coordinate {k}'
    assert sum(t) + nu * s == upper, f'[E-DUAL-UPPER] branch ({i},{s}) states the wrong dual value'
    assert upper <= 6, f'[E-DUAL-UPPER] branch ({i},{s}) certifies only M_A <= {upper}'
    seen.add((i, s))
assert seen == set(itertools.product(range(6), (-1, 1))), \
    '[E-BRANCH-COVERAGE] the twelve (observable, sign) branches are not all present'
print('PASS M_A <= 6, i.e. F + 4p <= 7, in all twelve no-signaling '
      'deterministic-observable branches', flush=True)
assert eps < 4
print(f'     and p >= 0 with eps = {eps} < 4 carries that to F + eps p <= 7 there', flush=True)

# --- the near-matching lower strategy ------------------------------------------
low = json.loads((PROOFS / 'penalty_lower_certificate.json').read_text())
t = Fr(low['t'])
assert t > 0, '[E-LOWER-RATIO] the lower strategy needs t > 0'
zs = [Fr(z) for z in low['measurement_half_tangents']]
assert len(zs) == 6, '[E-LOWER-RATIO] six half-tangents are required'
# Observable  [2z/(1+z^2)] X + [(1-z^2)/(1+z^2)] Z, exactly on the Bloch sphere.
obs = [(2 * z / (1 + z * z), (1 - z * z) / (1 + z * z)) for z in zs]
assert all(x * x + z * z == 1 for x, z in obs), '[E-LOWER-RATIO] an observable is off the Bloch sphere'
# State (|00> + t|11>)/sqrt(1+t^2): <Z(x)I> = C, <X(x)X> = S, <Z(x)Z> = 1, <X(x)Z> = 0.
C = (1 - t * t) / (1 + t * t)
S = 2 * t / (1 + t * t)
A = [C * z for _, z in obs[:3]]
B = [C * z for _, z in obs[3:]]
E = [S * x * y + z * v for x, z in obs[:3] for y, v in obs[3:]]
v = A + B + E
F_val = sum(a * b for a, b in zip(f, v))
p_val = (1 + v[1] + v[3] + v[9]) / 4
assert p_val > 0, '[E-LOWER-RATIO] the lower strategy must have p > 0'
ratio = 4 + (F_val - 7) / p_val
assert F_val == Fr(low['F']) and p_val == Fr(low['p']) and ratio == Fr(low['ratio']), \
    '[E-LOWER-RATIO] the recomputed behaviour disagrees with the stored values'
assert ratio > Fr(1631016, 10 ** 7), '[E-LOWER-RATIO] the lower strategy does not clear 0.1631016'
assert ratio < alpha, '[E-LOWER-RATIO] the lower strategy exceeds the certified upper endpoint'
print(f'PASS explicit two-qubit strategy attains (M_A - 6)/p = {float(ratio):.10f} > 0.1631016',
      flush=True)

# --- branch 1: positivity and the exact operator identity ----------------------
# The repository's own words, basis map and right-insertion Clifford normaliser.
_base = runpy.run_path(str(PROOFS / 'verify_sharp_qubit.py'))
words, P, pair_normal, positive_ldl = (_base['words'], _base['P'],
                                       _base['pair_normal'], _base['positive_ldl'])
zero = _base['zero']
assert _base['w'] == f, '[E-EPS-RANGE] the base certificate uses a different functional'

try:
    D = positive_ldl(X)
except AssertionError as exc:
    raise AssertionError(f'[E-GRAM-NOT-PD] endpoint Gram is not positive definite: {exc}') from None
print(f'PASS endpoint Gram is positive definite by exact LDL '
      f'(least pivot ~ {float(min(D)):.4e})', flush=True)

rows = [[(k, a) for k, a in enumerate(row) if a] for row in P]
poly = {}
for i, (wa, wb) in enumerate(words):
    for j, (ua, ub) in enumerate(words):
        coeff = sum(Fr(v * u) * X[k][l] for k, v in rows[i] for l, u in rows[j])
        if not coeff:
            continue
        for key, val in pair_normal(wa[::-1] + ua, wb[::-1] + ub).items():
            poly[key] = poly.get(key, Fr(0)) + coeff * val
poly = {k: v for k, v in poly.items() if v}

penalised = [Fr(c) for c in f]
for k in (1, 3, 9):                       # A1, B0, E10, each with weight eps/4
    penalised[k] += eps / 4
target = {(zero, (), ()): 7 - eps / 4}
for i in range(3):
    target[zero, (i,), ()] = -penalised[i]
    target[zero, (), (i,)] = -penalised[3 + i]
for i, j in itertools.product(range(3), repeat=2):
    target[zero, (i,), (j,)] = -penalised[6 + 3 * i + j]
assert poly == target, '[E-SOS-RESIDUAL] endpoint SOS identity has a nonzero residual'
print(f'PASS exact identity: sum X[j,k] J_j^dag J_k = (7 - eps/4) I - B_(f + eps d), '
      f'eps = {eps}', flush=True)

print(f'ENDPOINT CERTIFICATE VALID: F + {eps} p <= 7 on Schmidt number at most two, '
      f'equivalently M_A <= 6 + {alpha} p.', flush=True)
print(f'     0.1631016 < alpha_star <= {alpha} = {float(alpha)}; the optimum alpha_star '
      f'is NOT determined here.', flush=True)
print('     This certifies the inequality only. It makes no claim about the partial-local '
      'hull H, whose facet result is proved for F alone.', flush=True)
