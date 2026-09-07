"""What F detects that the standard I3322 / M3322 score thresholds do not.

This is an AFFIRMATIVE comparison, and the counterweight to verify_m3322_corollary.py.
That file shows the valid inequality F <= 7 on H is a corollary of published work.  This
one shows the shipped qutrit behavior Q is nonetheless invisible to every relabeled
ordinary score threshold for I3322 and M3322, while F sees it.

    max over relabelings of I3322 on Q  <  a score two qubits explicitly achieve
    max over relabelings of M3322 on Q  <  a score two qubits explicitly achieve
    max over relabelings of CHSH   on Q  <  2*sqrt(2)
    F(Q) = 7.0129...                      >  7, the proved Schmidt-number-two ceiling

So F <= 7 is not implied by the conjunction of those scalar thresholds with quantum
membership: Q is a quantum counterexample to that implication.

SCOPE, stated because it is easy to overclaim from here.  This covers input permutations,
output flips and party exchange of two inequality families, and nothing else.  It does not
cover local preprocessing, filtering, sequential wirings, many-copy protocols, probability-
conditioned tradeoffs, or dimension-constrained inequalities generally -- any of which could
imply our bound while the scalar thresholds do not.  The supported claim is "missed by the
standard score thresholds", not "missed by every existing witness", and this file is not
evidence of historical novelty.  See docs/PRIOR_ART.md.

No published maximum is relied on anywhere in this file.  Each leg needs only an ACHIEVABLE
qubit benchmark: a behavior scoring below something qubits reach cannot have crossed the true
qubit maximum, whatever that maximum is.

  CHSH   2*sqrt(2) is Tsirelson's theorem.  It holds for every quantum behavior in any
         dimension, so it is not a qubit-specific threshold at all.
  I3322  the maximally entangled two-qubit state with A0 = B0 = (sqrt(3) X + Z)/2,
         A1 = B1 = (sqrt(3) X - Z)/2, A2 = B2 = Z scores exactly 5, computed here in exact
         symbolic arithmetic.  That is a LOWER witness, not a proof of the qubit maximum,
         and it is all the argument needs.
  M3322  likewise: an explicit two-qubit state and six binary projective observables are
         built in exact rational arithmetic and their score computed exactly.

The two explicit qubit constructions were supplied by ChatGPT ("Astra") in the review recorded
at docs/review_2026-09-07_ai.md.  Both are checked here from first principles -- the
observables are confirmed traceless and involutive and the scores recomputed -- rather than
taken on trust.
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

# --- the shipped behavior, as an exact correlator vector -----------------------------
IDX = list(product(range(3), range(3), range(2), range(2)))
P = dict(zip(IDX, (Fr(t) for t in CERT['Q'])))
assert len(P) == 36 and min(P.values()) >= 0
for x, y in product(range(3), repeat=2):
    assert sum(P[x, y, a, b] for a, b in product(range(2), repeat=2)) == 1

V = ([sum((-1) ** a * P[x, 0, a, b] for a, b in product(range(2), repeat=2)) for x in range(3)]
     + [sum((-1) ** b * P[0, y, a, b] for a, b in product(range(2), repeat=2)) for y in range(3)]
     + [sum((-1) ** (a + b) * P[x, y, a, b] for a, b in product(range(2), repeat=2))
        for x, y in product(range(3), repeat=2)])
# marginals must not depend on the other party's setting, or the correlator form is a lie
for x in range(3):
    for y in range(3):
        assert sum((-1) ** a * P[x, y, a, b] for a, b in product(range(2), repeat=2)) == V[x]
for y in range(3):
    for x in range(3):
        assert sum((-1) ** b * P[x, y, a, b] for a, b in product(range(2), repeat=2)) == V[3 + y]


def vec(A, B, E):
    return tuple(A) + tuple(B) + tuple(E[i][j] for i in range(3) for j in range(3))


def relabel(w, sa, sb, sig, tau, swap):
    """Same convention as verify_m3322_corollary.py."""
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
    return vec(A2, B2, E2)


GROUP = [(sa, sb, sig, tau, sw)
         for sa in product([1, -1], repeat=3) for sb in product([1, -1], repeat=3)
         for sig in permutations(range(3)) for tau in permutations(range(3)) for sw in (0, 1)]

# eq. (72) of arXiv:1902.05841 (I3322, local bound 4) and eq. (48) (M3322, local bound 6).
REPS = {
    'I3322': vec([-1, -1, 0], [1, 1, 0], [[1, 1, 1], [1, 1, -1], [1, -1, 0]]),
    'M3322': vec([1, 1, 0], [1, 1, 0], [[1, -1, 1], [1, -1, -1], [1, 1, 0]]),
    'CHSH':  vec([0, 0, 0], [0, 0, 0], [[1, 1, 0], [1, -1, 0], [0, 0, 0]]),
}
W = tuple(CERT['coefficients'])

score = sum(a * b for a, b in zip(W, V))
assert score == Fr(CERT['score']) > 7
print(f'PASS F(Q) = {float(score):.16f} > 7, the proved Schmidt-number-two ceiling')

# Each representative was transcribed from the paper's HTML through a summarizer, not from the
# PDF.  Its local bound is checked below.  That is a NECESSARY CONDITION, not an
# authentication: many coefficient vectors share a local bound.  The vectors are printed so a
# human can compare them against the displayed equations, which is what would settle it.
LOCAL = [list(a) + list(b) + [x * y for x in a for y in b]
         for a, b in product(product([-1, 1], repeat=3), repeat=2)]
assert len(LOCAL) == 64
for name, bound in (('I3322', 4), ('M3322', 6), ('CHSH', 2)):
    got = max(sum(u * v for u, v in zip(REPS[name], p)) for p in LOCAL)
    assert got == bound, (name, got, bound)
    print(f'PASS {name} has local bound {bound}, matching the published value '
          f'(necessary, not sufficient): {list(REPS[name])}')

best = {}
for name, w in REPS.items():
    orbit = {relabel(w, *g) for g in GROUP}
    best[name] = (len(orbit), max(sum(a * b for a, b in zip(r, V)) for r in orbit))

# --- CHSH: Tsirelson, exactly, without floating point ---------------------------------
n, m = best['CHSH']
assert m > 0 and m * m < 8
print(f'PASS CHSH: max over {n} relabelings = {float(m):.16f} < 2*sqrt(2)  '
      f'(Tsirelson; holds in every dimension, so not a qubit-specific threshold)')

# --- I3322: below a score that two qubits explicitly achieve ---------------------------
# No published maximum is relied on.  The non-detection argument needs only an ACHIEVABLE
# qubit benchmark: a behavior scoring below something qubits reach cannot have crossed the
# true qubit maximum, whatever that maximum is.  (It is 5 here, equivalently 1/4 in the
# probability normalization I = 4J + 4, but this file does not need that and does not
# assert it -- the construction below is a lower witness, not an upper bound.)
PHI = sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2)
PX, PZ = sp.Matrix([[0, 1], [1, 0]]), sp.diag(1, -1)
I_OBS = [(sp.sqrt(3) * PX + PZ) / 2, (sp.sqrt(3) * PX - PZ) / 2, PZ]
for o in I_OBS:
    assert sp.simplify(o * o - sp.eye(2)) == sp.zeros(2, 2)
    assert sp.simplify(sp.trace(o)) == 0
wI = REPS['I3322']
qubit_I = sum(wI[i] * sp.simplify((PHI.T * sp.kronecker_product(I_OBS[i], sp.eye(2)) * PHI)[0])
              for i in range(3))
qubit_I += sum(wI[3 + j] * sp.simplify((PHI.T * sp.kronecker_product(sp.eye(2), I_OBS[j]) * PHI)[0])
               for j in range(3))
qubit_I += sum(wI[6 + 3 * i + j]
               * sp.simplify((PHI.T * sp.kronecker_product(I_OBS[i], I_OBS[j]) * PHI)[0])
               for i, j in product(range(3), repeat=2))
qubit_I = sp.simplify(qubit_I)
assert qubit_I == 5, qubit_I

n, m = best['I3322']
assert m < Fr(int(sp.numer(qubit_I)), int(sp.denom(qubit_I)))
print(f'PASS I3322: max over {n} relabelings = {float(m):.16f}')
print(f'          < {float(qubit_I):.16f}, achieved EXACTLY by the maximally entangled two-qubit '
      f'state with')
print(f'            A0 = B0 = (sqrt(3) X + Z)/2, A1 = B1 = (sqrt(3) X - Z)/2, A2 = B2 = Z '
      f'(all marginals vanish)')
print('          so no relabeled I3322 score can place Q beyond the qubit maximum, '
      'whatever that maximum is')

# --- M3322: below a score that two qubits explicitly achieve ---------------------------
# A real two-qubit state and six traceless binary projective observables, exact rationals.
PSI = sp.Matrix([64474, 73134, 17575, -13624])
DIRS = [[100000, 312], [98313, 18289], [94227, -33485],
        [64814, 76152], [-35243, 93584], [-11537, -99332]]
OBS = []
for d in DIRS:
    z = sp.Matrix(d)
    o = 2 * z * z.T / z.dot(z) - sp.eye(2)             # reflection: traceless, squares to I
    assert sp.simplify(o * o - sp.eye(2)) == sp.zeros(2, 2)
    assert sp.simplify(sp.trace(o)) == 0
    OBS.append(o)

w = REPS['M3322']
K = sp.kronecker_product
B = sp.zeros(4)
for i in range(3):
    B += w[i] * K(OBS[i], sp.eye(2)) + w[3 + i] * K(sp.eye(2), OBS[3 + i])
for i, j in product(range(3), repeat=2):
    B += w[6 + 3 * i + j] * K(OBS[i], OBS[3 + j])
qubit = sp.Rational((PSI.T * B * PSI)[0], PSI.dot(PSI))

n, m = best['M3322']
assert Fr(int(sp.numer(qubit)), int(sp.denom(qubit))) > m > 6
print(f'PASS M3322: max over {n} relabelings = {float(m):.16f}')
print(f'          < {float(qubit):.16f}, achieved EXACTLY by an explicit two-qubit state '
      f'and six projective observables built here')
print('          so no relabeled M3322 score can place Q beyond the qubit maximum, '
      'whatever that maximum is')

# The party exchange genuinely enlarges the M3322 orbit; the two counts are both meaningful.
half = len({relabel(REPS['M3322'], sa, sb, sig, tau, 0)
            for sa in product([1, -1], repeat=3) for sb in product([1, -1], repeat=3)
            for sig in permutations(range(3)) for tau in permutations(range(3))})
assert (half, best['M3322'][0]) == (1152, 2304)
print(f'PASS M3322 orbit: {half} without party exchange, {best["M3322"][0]} with it')

# --- structural: F is not a marginal-tilt of either family, in any relabeling ---------
# The published dimension-witness families closest to F in shape are TILTS: a 3322 Bell
# expression plus a coefficient times a ONE-PARTY MARGINAL.  The detection-efficiency family
# I3322(eta) of Vertesi, Pironio and Brunner, PRL 104, 060401 (2010), used for dimension
# bounds by Navascues, de la Torre and Vertesi, PRX 4, 011011 (2014), is of exactly that
# shape: its eta-dependent term multiplies a single-party marginal.
#
# A one-party marginal lives in coordinates 0..5.  It cannot change ANY correlator
# coefficient.  So the size of the correlator support is invariant under marginal tilts, and
# it is also invariant under relabeling -- which settles the comparison without needing any
# particular tilt coefficient, and so without needing the family's displayed equation.
def correlator_support(w):
    return sum(1 for c in w[6:] if c)


for name, w, expected in (('F', W, 9), ('I3322', REPS['I3322'], 8), ('M3322', REPS['M3322'], 8)):
    sizes = {correlator_support(relabel(w, *g)) for g in GROUP}
    assert sizes == {expected}, (name, sizes)
    print(f'PASS correlator support of {name} is {expected} across its whole orbit')

for name in ('I3322', 'M3322'):
    orbit = {relabel(REPS[name], *g) for g in GROUP}
    # F = alpha*(J + marginal tilt) + constant needs alpha*corr(J) == corr(F) for some alpha>0
    reachable = [J for J in orbit
                 if all((a == 0) == (b == 0) for a, b in zip(J[6:], W[6:]))
                 and len({Fr(b, a) for a, b in zip(J[6:], W[6:]) if a}) == 1
                 and next(iter({Fr(b, a) for a, b in zip(J[6:], W[6:]) if a})) > 0]
    assert not reachable, (name, len(reachable))
    print(f'PASS F is NOT {name} tilted by any one-party marginal, in any relabeling, at any '
          f'positive scale')
print('          (9 correlators cannot be produced from 8 by adding marginals, so every '
      'marginal-tilted family is excluded at once)')

# Where F's ninth correlator comes from: the penalty is a JOINT probability, and it lands
# exactly on the correlator that the published inequality leaves at zero.
MA, (a, b, x, y) = sides_from_corollary = None, (0, 0, 1, 0)
MA = (1, 0, 1, 0, -1, 1, -1, -1, -1, 0, -1, 1, 1, -1, -1)
assert MA in {relabel(REPS['M3322'], *g) for g in GROUP}
slot = 6 + 3 * x + y
assert MA[slot] == 0 and W[slot] != 0
assert [i for i in range(6, 15) if MA[i] == 0] == [slot]
print(f'PASS the penalty -4 p({a}{b}|{x}{y}) is a JOINT probability, and its correlator E{x}{y} '
      f'is exactly the one entry M3322 leaves at zero')
print('          so the ninth correlator is what a joint-probability penalty buys and a '
      'marginal tilt cannot')

print('CONCLUSION: F <= 7 is NOT implied by the relabeled ordinary I3322, M3322 and CHSH '
      'score thresholds together with\n'
      '            quantum membership -- Q satisfies all of them and violates F <= 7.  '
      'Relabelings only; this is not\n'
      '            a novelty clearance.  See docs/PRIOR_ART.md.')
