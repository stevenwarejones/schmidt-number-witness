"""The improved qutrit realization for the penalised functional G = F + eps0 * p.

The state is a real 3x3 coefficient matrix and each measurement is a rank-one
projector on a real 3-vector, all given as integers, so every Born probability is
an exact rational.  This file rebuilds all 36 of them from the raw integers -- it
does not read any stored probability table -- then checks

  * positivity, normalization and nonsignaling;
  * Schmidt rank exactly three, via a nonzero determinant of the coefficient matrix
    (that is what makes the point inaccessible to Schmidt number two);
  * G = F + eps0 * p > 7, so the point is detected by the endpoint witness;
  * F <= 7, so the ORIGINAL functional does not detect it at all;
  * the white-noise threshold under the uniform-output noise model.

WHITE-NOISE MODEL.  U is the uniform-output behaviour, P_U(ab|xy) = 1/4 for every
a, b, x, y.  All its marginals and correlators vanish, so F(U) = 0 and
p(U) = 1/4, giving G(U) = eps0/4 -- NOT zero.  For a noise fraction eta,

    G((1-eta) Q + eta U) = (1-eta) G(Q) + eta * eps0/4,

so the largest eta still exceeding 7 is

    eta_crit = (G(Q) - 7) / (G(Q) - eps0/4).

The naive (G(Q)-7)/G(Q) drops the constant term and is wrong for G.  It is right
for F only because F(U) = 0.  This is depolarizing noise on the OUTPUTS of a fixed
behaviour; it is not a detector-efficiency threshold, not a bound for arbitrary
physical noise, and not a finite-statistics statement.

Diagnostic codes: [E-QUTRIT-SHAPE] [E-QUTRIT-PROB] [E-QUTRIT-NONSIGNALING]
[E-QUTRIT-RANK] [E-QUTRIT-SCORE] [E-NOISE-MODEL]
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Run without -O: assertions here are exact certificate gates.')

import json
from fractions import Fraction as Fr
from itertools import product
from pathlib import Path

PROOFS = Path(__file__).resolve().parent
cert = json.loads((PROOFS / 'improved_qutrit_certificate.json').read_text())
endpoint = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
eps = Fr(endpoint['epsilon'])
f = endpoint['coefficients']

state = cert['state']
assert len(state) == 9 and all(isinstance(z, int) for z in state), \
    '[E-QUTRIT-SHAPE] the state must be nine integers, indexed 3i+j'
norm = sum(z * z for z in state)
assert norm > 0, '[E-QUTRIT-SHAPE] the state vector is zero'


def effects(entry):
    """[projector, complement] indexed by outcome, from an integer 3-vector."""
    u = entry['vector']
    assert len(u) == 3 and all(isinstance(z, int) for z in u), \
        '[E-QUTRIT-SHAPE] a measurement vector is not three integers'
    nu = sum(z * z for z in u)
    assert nu > 0, '[E-QUTRIT-SHAPE] a measurement vector is zero'
    r = entry['rank_one_outcome']
    assert r in (0, 1), '[E-QUTRIT-SHAPE] rank_one_outcome must be 0 or 1'
    proj = [[Fr(u[i] * u[k], nu) for k in range(3)] for i in range(3)]
    comp = [[Fr(int(i == k)) - proj[i][k] for k in range(3)] for i in range(3)]
    return [proj if a == r else comp for a in range(2)]


A = [effects(e) for e in cert['Alice']]
B = [effects(e) for e in cert['Bob']]
assert len(A) == 3 and len(B) == 3, '[E-QUTRIT-SHAPE] three settings per party are required'

# P(ab|xy) = sum_{ijkl} psi[3i+j] Ax[a][i][k] By[b][j][l] psi[3k+l] / |psi|^2
Q = {}
for x, y, a, b in product(range(3), range(3), range(2), range(2)):
    Ea, Fb = A[x][a], B[y][b]
    tot = Fr(0)
    for i, j in product(range(3), repeat=2):
        c1 = state[3 * i + j]
        if not c1:
            continue
        for k, l in product(range(3), repeat=2):
            c2 = state[3 * k + l]
            if not c2:
                continue
            t = Ea[i][k] * Fb[j][l]
            if t:
                tot += Fr(c1 * c2) * t
    Q[x, y, a, b] = tot / norm

assert min(Q.values()) >= 0, '[E-QUTRIT-PROB] a Born probability is negative'
for x, y in product(range(3), repeat=2):
    assert sum(Q[x, y, a, b] for a, b in product(range(2), repeat=2)) == 1, \
        '[E-QUTRIT-PROB] a setting pair does not normalize'
for x, y in product(range(3), repeat=2):
    for a in range(2):
        assert sum(Q[x, y, a, b] for b in range(2)) == sum(Q[x, 0, a, b] for b in range(2)), \
            "[E-QUTRIT-NONSIGNALING] Alice's marginal depends on Bob's setting"
    for b in range(2):
        assert sum(Q[x, y, a, b] for a in range(2)) == sum(Q[0, y, a, b] for a in range(2)), \
            "[E-QUTRIT-NONSIGNALING] Bob's marginal depends on Alice's setting"
print(f'PASS 36 exact Born probabilities: valid nonsignaling behaviour '
      f'(least probability ~ {float(min(Q.values())):.6f})', flush=True)

# Schmidt rank of the pure state = rank of the 3x3 coefficient matrix.
M = [[state[3 * i + j] for j in range(3)] for i in range(3)]
det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
       - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
       + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
assert det != 0, '[E-QUTRIT-RANK] the coefficient matrix is singular, so Schmidt rank < 3'
print(f'PASS Schmidt rank three: coefficient-matrix determinant = {det} != 0', flush=True)


def coordinates(P):
    """The 15 correlator coordinates (A0..A2, B0..B2, E00..E22) of a behaviour."""
    sgn = lambda o: 1 - 2 * o
    v = [Fr(0)] * 15
    for x in range(3):
        v[x] = sum(sgn(a) * P[x, 0, a, b] for a, b in product(range(2), repeat=2))
    for y in range(3):
        v[3 + y] = sum(sgn(b) * P[0, y, a, b] for a, b in product(range(2), repeat=2))
    for x, y in product(range(3), repeat=2):
        v[6 + 3 * x + y] = sum(sgn(a) * sgn(b) * P[x, y, a, b]
                               for a, b in product(range(2), repeat=2))
    return v


v = coordinates(Q)
F_val = sum(Fr(c) * t for c, t in zip(f, v))
p_val = (1 + v[1] + v[3] + v[9]) / 4
assert p_val == Q[1, 0, 0, 0], '[E-QUTRIT-SCORE] p must equal P(00|10)'
G_val = F_val + eps * p_val
assert F_val <= 7, '[E-QUTRIT-SCORE] the original F already exceeds 7 here, which cannot happen'
assert G_val > 7, '[E-QUTRIT-SCORE] the penalised score does not exceed 7'
assert G_val > Fr(709, 100), '[E-QUTRIT-SCORE] the penalised score falls below the claimed 7.09'
print(f'PASS original F = {float(F_val):.12f} <= 7: the ORIGINAL witness does not detect this point',
      flush=True)
print(f'PASS p = P(00|10) = {float(p_val):.12f}', flush=True)
print(f'PASS penalised G = F + {eps} p = {float(G_val):.12f} > 7', flush=True)

# Uniform-output white noise.
U = {k: Fr(1, 4) for k in Q}
u = coordinates(U)
assert all(c == 0 for c in u), '[E-NOISE-MODEL] uniform output noise must have vanishing coordinates'
F_U = sum(Fr(c) * t for c, t in zip(f, u))
p_U = (1 + u[1] + u[3] + u[9]) / 4
assert F_U == 0 and p_U == Fr(1, 4), '[E-NOISE-MODEL] F(U) = 0 and p(U) = 1/4 are required'
G_U = F_U + eps * p_U
assert G_U == eps / 4, '[E-NOISE-MODEL] G(U) must equal epsilon/4, not zero'
eta = (G_val - 7) / (G_val - G_U)
mixed = {k: (1 - eta) * Q[k] + eta * U[k] for k in Q}
mv = coordinates(mixed)
G_mixed = sum(Fr(c) * t for c, t in zip(f, mv)) + eps * (1 + mv[1] + mv[3] + mv[9]) / 4
assert G_mixed == 7, '[E-NOISE-MODEL] the threshold mixture does not sit exactly on the bound'
assert eta > Fr(15, 1000), '[E-NOISE-MODEL] the white-noise tolerance falls below 1.5%'
print(f'PASS uniform-output white-noise tolerance = {float(eta) * 100:.6f}% '
      f'(threshold mixture lands exactly on G = 7)', flush=True)

print(f'IMPROVED QUTRIT VALID: Schmidt rank three, G = {float(G_val):.10f} > 7, '
      f'noise tolerance {float(eta) * 100:.4f}%.', flush=True)
print('     This is a see-saw discovery, not a proven global qutrit maximum of G.', flush=True)
