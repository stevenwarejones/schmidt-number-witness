"""The penalised functional is a Schmidt-number witness ONLY -- it is not valid on H.

F <= 7 is a facet of the two-sided partial-local hull H (proofs/verify_facet.py) and
is also valid on Schmidt number at most two (proofs/verify_sharp_qubit.py).  The
penalised functional G = F + eps * p strengthens the SECOND statement.  It does not
inherit the first, and this file shows the failure is not marginal.

Among the fifteen affinely independent points of H that saturate F = 7 -- the very
points that establish the facet, each shipped with its own exact partial-local model
and re-verified by proofs/verify_facet.py -- exactly one has p > 0.  It has

    F = 7   and   p = P(00|10) = 1/3,   so   G = 7 + eps/3.

So for EVERY eps > 0, G <= 7 fails on H, at a point of H that lies on the F-facet.
There is no positive penalty that keeps the partial-local reading.  Anything said
about H must be said about F, and anything said about G must be said about S2.

Nothing here weakens the original results: F itself is untouched, and this file
only reads the existing facet certificate.

Diagnostic code: [E-HULL-COUNTEREXAMPLE]
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Run without -O: assertions here are exact certificate gates.')

import json
from fractions import Fraction as Fr
from itertools import product
from pathlib import Path

PROOFS = Path(__file__).resolve().parent
facet = json.loads((PROOFS / 'facet_certificate.json').read_text())
endpoint = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
eps = Fr(endpoint['epsilon'])
w = facet['w']
assert w == endpoint['coefficients'], \
    '[E-HULL-COUNTEREXAMPLE] the facet and endpoint certificates use different functionals'

witnesses = []
for k, e in enumerate(facet['saturating_points']):
    v = [Fr(x) for x in e['v']]
    assert len(v) == 15
    P = {(x, y, a, b): (1 + (-1) ** a * v[x] + (-1) ** b * v[3 + y]
                        + (-1) ** (a + b) * v[6 + 3 * x + y]) / 4
         for x, y, a, b in product(range(3), range(3), range(2), range(2))}
    assert min(P.values()) >= 0, \
        f'[E-HULL-COUNTEREXAMPLE] facet point {k} is not a behaviour'
    F_val = sum(Fr(a) * b for a, b in zip(w, v))
    assert F_val == 7, f'[E-HULL-COUNTEREXAMPLE] facet point {k} does not saturate F = 7'
    p_val = (1 + v[1] + v[3] + v[9]) / 4
    assert p_val == P[1, 0, 0, 0], '[E-HULL-COUNTEREXAMPLE] p must equal P(00|10)'
    if p_val > 0:
        witnesses.append((k, e['side'], tuple(e['pair']), F_val, p_val))

assert witnesses, ('[E-HULL-COUNTEREXAMPLE] no facet-defining point of H has p > 0, so this '
                   'file can no longer separate G from F')
for k, side, pair, F_val, p_val in witnesses:
    G_val = F_val + eps * p_val
    assert G_val > 7, (f'[E-HULL-COUNTEREXAMPLE] facet point {k} was expected to violate '
                       f'G <= 7 and does not')
    print(f'PASS facet point {k} of H (side {side}, pair {pair}): F = {F_val}, '
          f'p = {p_val}, G = F + {eps} p = {float(G_val):.10f} > 7', flush=True)

k, side, pair, F_val, p_val = witnesses[0]
print(f'CONCLUSION: G <= 7 is FALSE on the two-sided partial-local hull H, for every eps > 0 '
      f'(the point above gives G = 7 + eps * {p_val}).', flush=True)
print('     The penalised family certifies Schmidt number at most two and nothing about H. '
      'The facet result belongs to F alone.', flush=True)
