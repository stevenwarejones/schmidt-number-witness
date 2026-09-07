"""The Schmidt-number-two equality face of F is a four-simplex of local behaviours.

    S2 intersect {F = 7}  =  L_F  :=  conv of five local deterministic behaviours,

of affine dimension four.  So attaining the sharp bound is possible only locally, and only
in that four-simplex.  The face is NOT a facet of S2, whose affine dimension is 15.

Do not overread this.  It classifies observed BEHAVIOURS.  It does not say the underlying
state is unentangled: deterministic measurements can reach F = 7 on an entangled state while
revealing none of its entanglement.

Three branches cover every Schmidt-number-two behaviour, in the same shape as
docs/SCHMIDT_NUMBER_BOUND.md but with equality imposed.

  1. All six qubit observables traceless.  Since the sharp Gram is positive DEFINITE (not
     merely semidefinite), equality forces J_j |psi> = 0 for every j.  Three exact identities
     in the shipped basis map,

         J_5 - J_0 = (I-A0)(I-B0),  J_6 - J_0 = (I-A0)(I-B1),  J_7 - J_0 = (I-A0)(I-B2),

     which this file re-derives from the basis map, turn that into
     P(A0 = -1, B_y = -1) = 0 for y = 0,1,2.  A rank-one state is already local.  Otherwise the
     2x2 Schmidt matrix is invertible, so projecting Alice onto A0 = -1 leaves a NONZERO
     conditional vector on Bob's qubit which all three of Bob's minus-projectors annihilate.
     In dimension two each such kernel is one-dimensional, so the three projectors coincide:
     Bob has one effective measurement, and the behaviour is local.

  2. At least one observable deterministic.  A binary projective qubit observable is either
     traceless or +-I, so counting deterministic observables (d_A, d_B) partitions everything:
     d_A >= 2 or d_B >= 2 leaves that party at most one nontrivial measurement, hence jointly
     measurable measurements and a local behaviour; (0,0) is branch 1; and the remainder is
     exactly 12 patterns with one deterministic observable in total and 36 with one on each
     party.  This file checks that the certificate carries precisely those 48 keys -- not
     merely 48 of them.

     17 patterns carry a single dual proving max F < 7 on that branch of the no-signaling
     polytope, so equality is unreachable there before any quantum structure is used.  The
     other 31 carry duals forcing individual joint probabilities to vanish on the face; the
     closure below turns those zeros into projector equalities and closes each pattern as
     impossible or local.

  3. POVMs and Schmidt-number-two mixtures, by componentwise saturation.  F is affine, every
     component obeys F <= 7, so a mixture at F = 7 has every positive-weight component at
     F = 7 and hence local.  Mixtures of local behaviours are local, and F <= 7 is valid on the
     local polytope, so the local F = 7 face is the hull of the deterministic vertices attaining
     it -- the five recomputed here.  The order matters and is not the order of the prose:
     mixed state -> pure components of Schmidt rank at most two -> compress to the 2x2 Schmidt
     supports -> decompose the effects.  Purity survives, which is what branch 2 needs.

THE WHOLE CERTIFIED FAMILY HAS THIS SAME FACE.  For 0 <= eps <= eps0 = 383689/100000:

  * eps < eps0: if F + eps p = 7 then F + eps0 p = 7 + (eps0 - eps) p, which the endpoint
    certificate bounds by 7, so p = 0 and F = 7 -- the theorem above applies.
  * eps = eps0: the endpoint Gram is positive definite, so equality forces J_j |psi> = 0 for
    every j, including J_8 = 4K, whence p = <K> = 0 and the branch-1 argument runs unchanged.
    In a deterministic branch F + 4p <= 7 with eps0 < 4 gives p = 0 the same way.  The
    componentwise reduction is unchanged.
  * conversely all five vertices have p = 0 as well as F = 7, so they saturate every member.

This file checks the arithmetic of that corollary; the two facts it leans on are checked by
proofs/verify_penalty_endpoint.py (positive definiteness and the endpoint bound).

WHAT REMAINS CONJECTURAL.  alpha_star itself is undetermined, and what happens to the equality
face at the exact critical penalty is a SEPARATE question this file does not touch: the
certified family stops at eps0, and a nonlocal behaviour with p > 0 attaining the bound at the
true endpoint is neither exhibited nor excluded here.

Diagnostic codes: [E-FACE-COVERAGE] [E-FACE-DUAL] [E-FACE-ZERO] [E-FACE-UNRESOLVED]
[E-FACE-VERTICES] [E-FACE-DIM] [E-FACE-PROJECTOR-ID] [E-FAMILY-SATURATION]
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Run without -O: assertions here are exact certificate gates.')

import itertools
import json
from fractions import Fraction as Fr
from pathlib import Path

PROOFS = Path(__file__).resolve().parent
cert = json.loads((PROOFS / 'equality_face_certificate.json').read_text())
f = cert['coefficients']
assert Fr(cert['bound']) == 7

# --- the 36 positivity constraints, rebuilt from the Born-rule parametrisation -------------
# 4 P(ab|xy) = 1 + r.v, with a, b the observable VALUES in {-1, +1}.
EVENTS = list(itertools.product(range(3), range(3), (-1, 1), (-1, 1)))


def positivity_row(x, y, a, b):
    r = [0] * 15
    r[x] += a
    r[3 + y] += b
    r[6 + 3 * x + y] += a * b
    return r


ROWS = [positivity_row(*e) for e in EVENTS]


def check_dual(c, target, eq, rhs, code, where):
    """Exact weak duality: max target.v over {A v <= 1, eq v = rhs} is at most `upper`."""
    t = [Fr(x) for x in c['t']]
    nu = [Fr(x) for x in c['nu']]
    assert len(t) == 36 and len(nu) == len(eq), f'{code} {where}: dual has the wrong shape'
    assert all(x >= 0 for x in t), f'{code} {where}: a positivity multiplier is negative'
    for k in range(15):
        lhs = (sum(-ROWS[j][k] * t[j] for j in range(36))
               + sum(eq[j][k] * nu[j] for j in range(len(eq))))
        assert lhs == Fr(target[k]), f'{code} {where}: dual identity fails at coordinate {k}'
    upper = sum(t) + sum(nu[j] * Fr(rhs[j]) for j in range(len(eq)))
    assert upper == Fr(c['upper']), f'{code} {where}: stated value disagrees with its multipliers'
    return upper


# --- the projector-equality closure, from the five geometric rules --------------------------
def closure(det, zeros):
    """'impossible', 'local', or 'unresolved' for one deterministic-observable pattern.

    The state is pure of Schmidt rank two, so both reduced density operators are positive
    definite and the 2x2 coefficient matrix is invertible.  Under those hypotheses:

      1. a joint zero pairing a deterministic party's ACTUAL outcome with a nonzero projector
         on the other side is impossible, since Tr(rho Pi) > 0;
      2. two rank-one projectors annihilating the same nonzero conditional vector coincide --
         and because the coefficient matrix is invertible, equal conditional vectors also mean
         equal projectors on the conditioning side, so classes on both sides mean the same
         thing;
      3. equal rank-one qubit projectors have equal complements;
      4. a projector cannot equal its orthogonal complement;
      5. if every nontrivial measurement on one party shares a basis up to outcome swaps, that
         party's measurements commute and the behaviour is local.

    An incomplete rule set fails SAFE: an unresolved pattern is rejected below, never accepted.
    """
    live = [(i, a) for i in range(6) if i not in det for a in (-1, 1)]
    parent = {x: x for x in live}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        parent[rx] = ry
        return True

    edges = []
    for x, y, a, b in zeros:
        if (x in det and det[x] != a) or (3 + y in det and det[3 + y] != b):
            continue                                   # trivially zero, carries no information
        if x in det or 3 + y in det:
            return 'impossible'                        # rule 1
        edges.append(((x, a), (3 + y, b)))
    changed = True
    while changed:
        changed = False
        for (a1, b1), (a2, b2) in itertools.combinations(edges, 2):
            if find(a1) == find(a2):
                changed |= union(b1, b2)               # rule 2
            if find(b1) == find(b2):
                changed |= union(a1, a2)               # rule 2
        for x, y in itertools.combinations(live, 2):
            if find(x) == find(y):
                changed |= union((x[0], -x[1]), (y[0], -y[1]))     # rule 3
    for i in range(6):
        if i not in det and find((i, 1)) == find((i, -1)):
            return 'impossible'                        # rule 4
    for side in (range(3), range(3, 6)):
        ids = [i for i in side if i not in det]
        if len(ids) <= 1:
            return 'local'
        root = ids[0]
        if all(find((i, 1)) in (find((root, 1)), find((root, -1))) for i in ids):
            return 'local'                             # rule 5
    return 'unresolved'


# --- branch 2: the 48 patterns --------------------------------------------------------------
expected = {tuple(sorted({i: s}.items())) for i, s in itertools.product(range(6), (-1, 1))}
expected |= {tuple(sorted({i: s, j: t}.items()))
             for i, j, s, t in itertools.product(range(3), range(3, 6), (-1, 1), (-1, 1))}
assert len(expected) == 48

seen = set()
counts = {}
n_zeros = 0
for c in cert['patterns']:
    det = {int(k): v for k, v in c['det'].items()}
    key = tuple(sorted(det.items()))
    assert key in expected, f'[E-FACE-COVERAGE] unexpected pattern {det}'
    assert key not in seen, f'[E-FACE-COVERAGE] pattern {det} appears twice'
    seen.add(key)
    eq = [[int(k == i) for k in range(15)] for i in det]
    rhs = list(det.values())
    if 'bound' in c:
        upper = check_dual(c['bound'], f, eq, rhs, '[E-FACE-DUAL]', f'pattern {det}')
        assert upper < 7, f'[E-FACE-DUAL] pattern {det}: dual value {upper} does not exclude F = 7'
        counts['no-signaling: F = 7 unreachable'] = counts.get('no-signaling: F = 7 unreachable', 0) + 1
    else:
        eqf, rhsf = [f] + eq, [7] + rhs
        zs = c['zeros']
        assert len(zs) == len(c['certs']), f'[E-FACE-ZERO] pattern {det}: zeros and duals disagree in number'
        for z, proof in zip(zs, c['certs']):
            row = ROWS[EVENTS.index(tuple(z))]
            upper = check_dual(proof, row, eqf, rhsf, '[E-FACE-ZERO]', f'pattern {det} event {z}')
            assert upper == -1, (f'[E-FACE-ZERO] pattern {det} event {z}: certified only to '
                                 f'{upper}, which does not force the probability to zero')
            n_zeros += 1
        verdict = closure(det, [tuple(z) for z in zs])
        assert verdict in ('local', 'impossible'), \
            f'[E-FACE-UNRESOLVED] pattern {det}: the projector closure returns {verdict}'
        counts[f'quantum: {verdict}'] = counts.get(f'quantum: {verdict}', 0) + 1
assert seen == expected, '[E-FACE-COVERAGE] the 48 deterministic-observable patterns are not all present'
print(f'PASS all 48 deterministic-observable patterns closed, from {n_zeros} exact forced-zero '
      f'duals: {counts}', flush=True)

# --- branch 1: the three projector identities in the shipped basis map ----------------------
sharp = json.loads((PROOFS / 'sharp_qubit_certificate.json').read_text())
assert sharp['coefficients'] == f, '[E-FACE-PROJECTOR-ID] the sharp certificate uses a different functional'
words = [(tuple(a), tuple(b)) for a, b in sharp['words']]
P = sharp['basis_map']


def word_vector(terms):
    v = [0] * len(words)
    for a, b, coeff in terms:
        v[words.index((tuple(a), tuple(b)))] += coeff
    return v


for y, col in enumerate((5, 6, 7)):
    # (I - A0)(I - B_y) = I - A0 - B_y + A0 B_y
    want = word_vector([([], [], 1), ([0], [], -1), ([], [y], -1), ([0], [y], 1)])
    got = [row[col] - row[0] for row in P]
    assert got == want, \
        f'[E-FACE-PROJECTOR-ID] J_{col} - J_0 is not (I-A0)(I-B{y}), so the equality argument fails'
print('PASS J_5 - J_0, J_6 - J_0, J_7 - J_0 are (I-A0)(I-B_y): equality forces '
      'P(A0 = -1, B_y = -1) = 0 for every y', flush=True)

# --- the face itself -------------------------------------------------------------------------
vertices = []
for z in itertools.product((-1, 1), repeat=6):
    v = [Fr(t) for t in list(z) + [a * b for a in z[:3] for b in z[3:]]]
    if sum(Fr(a) * b for a, b in zip(f, v)) == 7:
        vertices.append(v)
assert len(vertices) == 5, \
    f'[E-FACE-VERTICES] {len(vertices)} local deterministic behaviours attain F = 7, expected 5'

M = [[a - b for a, b in zip(v, vertices[0])] for v in vertices[1:]]
rank = 0
for k in range(15):
    piv = next((j for j in range(rank, len(M)) if M[j][k]), None)
    if piv is None:
        continue
    M[rank], M[piv] = M[piv], M[rank]
    q = M[rank][k]
    M[rank] = [x / q for x in M[rank]]
    for j in range(rank + 1, len(M)):
        q = M[j][k]
        M[j] = [a - q * b for a, b in zip(M[j], M[rank])]
    rank += 1
assert rank == 4, f'[E-FACE-DIM] the five vertices span affine dimension {rank}, expected 4'
print('PASS exactly five local deterministic behaviours attain F = 7, affinely independent: '
      'the face is a four-simplex, not a facet of the 15-dimensional S2', flush=True)

# --- the corollary for the whole certified family ---------------------------------------------
endpoint = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
eps0 = Fr(endpoint['epsilon'])
assert endpoint['coefficients'] == f, '[E-FAMILY-SATURATION] the endpoint certificate uses a different functional'
assert 0 < eps0 < 4, '[E-FAMILY-SATURATION] the family argument needs 0 < eps0 < 4'
for v in vertices:
    p = (1 + v[1] + v[3] + v[9]) / 4
    assert p == 0, '[E-FAMILY-SATURATION] a vertex of L_F has p > 0, so it does not saturate the family'
    assert sum(Fr(a) * b for a, b in zip(f, v)) + eps0 * p == 7, \
        '[E-FAMILY-SATURATION] a vertex of L_F fails to saturate F + eps0 p = 7'
print(f'PASS every vertex of L_F has p = 0 as well as F = 7, so it saturates F + eps p = 7 for '
      f'EVERY eps: L_F is contained in the equality face of the whole family', flush=True)
print(f'PASS the converse for 0 <= eps <= {eps0}: below the endpoint, F + eps p = 7 gives '
      f'F + eps0 p = 7 + (eps0 - eps) p <= 7 hence p = 0; at the endpoint, positive definiteness '
      f'gives J_8 |psi> = 0 with J_8 = 4K hence p = 0, and F + 4p <= 7 does the same in the '
      f'deterministic branches (both checked by proofs/verify_penalty_endpoint.py)', flush=True)

print('EQUALITY FACE VALID: S2 intersect {F = 7} = L_F, a four-simplex of local behaviours, '
      f'and the same face for every F + eps p with 0 <= eps <= {eps0}.', flush=True)
print('     What happens at the exact critical penalty alpha_star remains OPEN: alpha_star is '
      'not determined, and no behaviour attaining the bound there with p > 0 is exhibited or '
      'excluded.', flush=True)
