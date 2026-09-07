"""F <= 7 on H is a COROLLARY of a published one-sided facet plus positivity.

This file exists to bound our own novelty claim, not to support it.  Standard library
only; every check is exact integer or rational arithmetic.

Quintino, Budroni, Woodhead, Cabello and Cavalcanti, PRL 123, 180401 (2019),
arXiv:1902.05841, Appendix G, characterize the ONE-SIDED hull

    L^A_2conv := Conv(L^A_12, L^A_23, L^A_13)

-- the convex hull of the three sets in which a pair of ALICE's settings is Bell-local --
and report 4452 facets in six relabeling classes F_1..F_6.  Their eq. (48),

    F_6 = <A1> + <A2> + <B1> + <B2> + <A1B1> - <A1B2> + <A1B3>
                 + <A2B1> - <A2B2> - <A2B3> + <A3B1> + <A3B2>   <=  6,

is stated there to be equivalent to the M3322 inequality and is the only one of the six
violated in quantum physics.  Their hull is one-sided; ours is the two-sided
H = Conv(H_A, H_B), a different set, and F is not a relabeling of F_6.  Neither fact stops
F <= 7 from FOLLOWING from theirs, and it does:

    F  =  M_A  -  4 p(00|10)  +  1
    F  =  M_B  -  4 p(11|22)  +  1

M_A is obtained from eq. (48) by relabeling settings and outcomes -- on BOTH parties; what
matters is that the parties are not EXCHANGED.  The whole such subgroup maps L^A_2conv to
itself: permuting Alice's settings permutes the three constituent sets L^A_12, L^A_23,
L^A_13 and so fixes their hull, while Bob's relabelings and either party's outcome flips
fix each constituent.  So M_A <= 6 holds throughout H_A, and M_B <= 6 throughout H_B by the
party exchange.  Probabilities are nonnegative.  Hence F <= 6 - 0 + 1 = 7 on H_A, likewise
on H_B, and therefore on their convex hull H.  Three lines, from a published facet.

That relabeling argument is not taken on trust here.  It is the load-bearing step -- if it
failed the corollary would collapse -- so both bounds are certified DIRECTLY instead, on
each of the six constituent classes, by exact duals over the same positivity and 2x2 CHSH
rows verify_facet.py uses for F.  Each certificate is a plain sum of five rows.  The
transcription of eq. (48) itself, which was read from the paper's HTML through a summarizer
rather than from the PDF, has its local bound checked against the published 6 -- a necessary
condition only, since many coefficient vectors share a local bound, so the vector is printed
for comparison against the displayed equation.

What this derivation does NOT give, and what the rest of the repository is for:

  * that F <= 7 is a FACET of H (verify_facet.py: an exact 14-dimensional face).  Neither
    one-sided inequality even holds across the whole face: the table below finds one
    certified saturating point at which M_A exceeds 6 and another at which M_B does.  That
    is consistent -- each such point lies in the opposite side's hull, where that inequality
    was never claimed -- but it means neither derivation alone reaches the whole face.
  * the sharp Schmidt-number-two bound (proofs/verify_sharp_qubit.py).  The partial-locality
    derivation DISPLAYED HERE does not establish that bound; it requires the separate quantum
    argument given there.  That is a statement about this derivation, not a proof that no
    partial-local argument could ever reach it -- no such universal claim is made.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")

import json
from fractions import Fraction as Fr
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = json.loads((HERE / 'facet_certificate.json').read_text())

# layout: [A1,A2,A3, B1,B2,B3, E11,E12,E13,E21,E22,E23,E31,E32,E33]
def vec(A, B, E):
    return tuple(A) + tuple(B) + tuple(E[i][j] for i in range(3) for j in range(3))

W = tuple(CERT['w'])                                   # our functional, bound 7
F6 = vec([1, 1, 0], [1, 1, 0],
         [[1, -1, 1], [1, -1, -1], [1, 1, 0]])         # eq. (48), bound 6
assert sum(x != 0 for x in W) == 15
assert sum(x != 0 for x in F6) == 12


def relabel(w, sa, sb, sig, tau, swap):
    """Outcome flips and setting permutations on both parties, plus the party exchange."""
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


FLIPS = list(product([1, -1], repeat=3))
PERMS = list(permutations(range(3)))
# Both parties are relabeled throughout.  The distinction that matters is the party
# EXCHANGE: without it the subgroup fixes H_A, with it it carries H_A to H_B.
NO_EXCHANGE = [(sa, sb, sig, tau, 0) for sa in FLIPS for sb in FLIPS
               for sig in PERMS for tau in PERMS]
EXCHANGED = [(g[0], g[1], g[2], g[3], 1) for g in NO_EXCHANGE]

orbit_A = {relabel(F6, *g) for g in NO_EXCHANGE}       # valid on H_A
orbit_B = {relabel(F6, *g) for g in EXCHANGED}         # valid on H_B
orbit6 = orbit_A | orbit_B
orbitF = {relabel(W, *g) for g in NO_EXCHANGE + EXCHANGED}
assert len(orbit6) == len(orbitF) == 2304, (len(orbit6), len(orbitF))

# F is NOT itself a relabeling of M3322 -- the orbits are disjoint.
assert W not in orbit6
assert not (orbit6 & orbitF)
print('PASS F is not a relabeling of M3322: the two 2304-element orbits are disjoint')


# --- the LOCAL BOUND of the transcribed expression, checked ------------------------------
# F_6 was read from the paper's HTML through a summarizer, not from the PDF, so it is treated
# as unverified input.  What follows is a NECESSARY CONDITION, not an authentication: many
# coefficient vectors share a local bound, so agreement here cannot establish that this IS
# eq. (48).  It only rules out a transcription whose local bound differs from the published
# one.  The vector is printed for human comparison against the displayed equation, which is
# the only thing that can settle it.
LOCAL = [list(a) + list(b) + [x * y for x in a for y in b]
         for a, b in product(product([-1, 1], repeat=3), repeat=2)]
assert len(LOCAL) == 64
for name, w, bound in (('F', W, 7), ('eq. (48) = M3322', F6, 6)):
    got = max(sum(u * v for u, v in zip(w, p)) for p in LOCAL)
    assert got == bound, (name, got, bound)
    print(f'PASS {name} has local bound {bound}, matching the published value (maximum over '
          f'the 64 deterministic local vertices; necessary, not sufficient)')
    print(f'     for human comparison against the displayed equation: {list(w)}')


# --- M_A <= 6 on H_A and M_B <= 6 on H_B, by exact dual certificates ----------------------
# The relabeling argument alone would leave this step as prose: the subgroup that does not
# exchange parties maps L^A_2conv to itself, so a relabeling of eq. (48) inherits its bound
# there.  That reasoning is correct but unverified, and it is the load-bearing step -- if it
# failed, the corollary would collapse.  So the bound is certified directly instead, on each
# of the six constituent classes, using the same row set verify_facet.py uses for F: exact
# positivity and all 2x2 CHSH inequalities of the designated 2x3-local restriction, which
# characterize locality there.  Each certificate turns out to be a plain SUM OF FIVE ROWS.
def class_rows(side, pair):
    """r . (1,v) >= 0 for every v in the partial-local class (side, pair)."""
    rows = []
    for x, y, a, b in product(range(3), range(3), [-1, 1], [-1, 1]):
        r = [0] * 16
        r[0], r[1 + x], r[4 + y], r[7 + 3 * x + y] = 1, a, b, a * b
        rows.append(r)
    for other in combinations(range(3), 2):
        inds = list(product(pair, other)) if side == 'A' else list(product(other, pair))
        for ss in product([-1, 1], repeat=4):
            if ss[0] * ss[1] * ss[2] * ss[3] == -1:
                r = [0] * 16
                r[0] = 2
                for z, (x, y) in zip(ss, inds):
                    r[7 + 3 * x + y] = -z
                rows.append(r)
    return rows


# row indices whose sum certifies 6 - M(v) >= 0 on that class; all weights are 1
DUALS = {
    ('A', (0, 1)): [0, 25, 31, 32, 52],
    ('A', (0, 2)): [8, 19, 21, 32, 37],
    ('A', (1, 2)): [0, 7, 8, 25, 54],
    ('B', (0, 1)): [8, 15, 19, 21, 45],
    ('B', (0, 2)): [4, 19, 25, 31, 36],
    ('B', (1, 2)): [0, 15, 25, 31, 36],
}


def prob_coeffs(a, b, x, y):
    """p(ab|xy) = (1 + (-1)^a A_x + (-1)^b B_y + (-1)^(a+b) E_xy)/4, as [const]+15 coefficients."""
    c = [0] * 16
    c[0], c[1 + x], c[4 + y], c[7 + 3 * x + y] = 1, (-1) ** a, (-1) ** b, (-1) ** (a + b)
    return [Fr(t, 4) for t in c]


# Every way of writing F as (a relabeling of M3322) minus four times a single probability.
found = []
for M in orbit6:
    for a, b, x, y in product(range(2), range(2), range(3), range(3)):
        c = prob_coeffs(a, b, x, y)
        if all(Fr(W[i] - M[i]) == -4 * c[1 + i] for i in range(15)):
            found.append((M, (a, b, x, y), 4 * c[0]))
assert len(found) == 2, found
assert all(k == 1 for _, _, k in found)

sides = {}
for M, key, _ in found:
    assert (M in orbit_A) != (M in orbit_B)            # exactly one side, never both
    sides['A' if M in orbit_A else 'B'] = (M, key)
assert set(sides) == {'A', 'B'}
for s in 'AB':
    a, b, x, y = sides[s][1]
    print(f'PASS F = M_{s} - 4 p({a}{b}|{x}{y}) + 1 with M_{s} a relabeling of M3322 '
          f'valid on H_{s}  =>  F <= 6 - 0 + 1 = 7 on H_{s}')
# certify each side's bound on its own three classes, with the side's own functional
for s_ in 'AB':
    M = sides[s_][0]
    target = [6] + [-z for z in M]
    for pair in combinations(range(3), 2):
        rows = class_rows(s_, pair)
        picked = DUALS[(s_, pair)]
        assert all(min(rows[i]) is not None for i in picked)
        total = [sum(rows[i][j] for i in picked) for j in range(16)]
        assert total == target, (s_, pair, total, target)
    print(f'PASS M_{s_} <= 6 on all three H_{s_} classes, by exact dual certificates '
          f'(each a sum of five positivity/CHSH rows)')
print('PASS therefore F <= 7 on H = Conv(H_A, H_B): a corollary of eq. (48) plus positivity')

# The identity, and each one-sided inequality's status, at the fifteen certified
# saturating points of the facet.
def evaluate(m, v):
    return sum(Fr(t) * Fr(u) for t, u in zip(m, v))


def prob(v, a, b, x, y):
    return (1 + (-1) ** a * Fr(v[x]) + (-1) ** b * Fr(v[3 + y])
            + (-1) ** (a + b) * Fr(v[6 + 3 * x + y])) / 4


exceeds = {'A': [], 'B': []}
points = CERT['saturating_points']
assert len(points) == 15
for n, e in enumerate(points):
    v = [Fr(t) for t in e['v']]
    assert evaluate(W, v) == 7
    for s in 'AB':
        M, (a, b, x, y) = sides[s]
        assert evaluate(W, v) == evaluate(M, v) - 4 * prob(v, a, b, x, y) + 1
        val = evaluate(M, v)
        assert val >= 6                                # never below the published bound here
        if val > 6:
            # Permitted only because this point lies in the OTHER side's hull, where this
            # inequality is not claimed to hold.  Anything else would contradict eq. (48).
            assert e['side'] != s, (n, s, e['side'], val)
            exceeds[s].append((n, val))
print('PASS the identity holds exactly at all 15 certified saturating points of the facet')

assert exceeds['A'] and exceeds['B'], exceeds
for s in 'AB':
    other = 'B' if s == 'A' else 'A'
    n, val = exceeds[s][0]
    print(f'PASS M_{s} EXCEEDS its bound 6 at saturating point {n} (value {val}), which lies '
          f'in H_{other}; so M_{s} <= 6 does not hold across the whole face')
print('PASS neither one-sided inequality holds on the whole F=7 face, so the FACET property '
      'on the two-sided hull does not follow from either alone')

print('CONCLUSION: the VALID INEQUALITY F <= 7 on H is prior art -- a corollary of eq. (48) of '
      'arXiv:1902.05841 plus positivity.\n'
      '            Not established by that derivation: that F <= 7 is a facet of H, and the '
      'sharp Schmidt-number-two bound,\n'
      '            which needs the separate quantum argument in proofs/verify_sharp_qubit.py.')
