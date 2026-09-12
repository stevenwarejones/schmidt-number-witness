"""Exact rational continuation of the penalty Gram; standard library only.

Run from any directory: python proofs/verify_penalty_boundary.py
This entry point verifies the new arithmetic, THEN runs the inherited endpoint
and equality-face verifiers before printing its conclusion. No skip flag.

Positive semidefiniteness of the continued Gram Y -- the fact the whole bound
rests on -- is checked here rather than argued in prose: Y differs from X only
in entry (8,8), so the corank-one argument reduces to positive definiteness of a
principal submatrix of X, which the inherited endpoint verifier establishes.
The kernel equality argument and the convexity reduction remain prose proofs in
docs/CERTIFICATE_PENALTY_BOUNDARY.md, not machine formalizations.
"""
import hashlib
import json
import runpy
import sys
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Run without -O: exact assertions are proof gates.')
if hasattr(sys, 'set_int_max_str_digits'):
    # Exact solved rationals exceed Python 3.11's default decimal digit limit.
    sys.set_int_max_str_digits(0)

PROOFS = Path(__file__).resolve().parent
SUCCESS = 'PENALTY BOUNDARY VALID'


def check_arithmetic(d, base_bytes, sharp_bytes):
    """Check added algebra only. Full certificate acceptance also needs main()."""
    assert hashlib.sha256(base_bytes).hexdigest() == d['base_sha256'], '[E-BOUNDARY-INPUT] base changed'
    assert hashlib.sha256(sharp_bytes).hexdigest() == d['sharp_sha256'], '[E-BOUNDARY-INPUT] basis changed'
    base, sharp = json.loads(base_bytes), json.loads(sharp_bytes)
    X = [[Q(t) for t in row] for row in base['gram']]
    n = len(X)
    assert n == 70 and all(len(row) == n for row in X), '[E-BOUNDARY-SHAPE] Gram shape'
    assert all(X[i][j] == X[j][i] for i in range(n) for j in range(n)), '[E-BOUNDARY-SHAPE] symmetry'
    v, a, z = ([Q(t) for t in d[k]] for k in ('v', 'a', 'z'))
    assert all(len(t) == n for t in (v, a, z)), '[E-BOUNDARY-SHAPE] vector shape'

    def dot(u, w):
        return sum((x*y for x, y in zip(u, w)), Q(0))

    assert [dot(row, v) for row in X] == [Q(i == 8) for i in range(n)], '[E-BOUNDARY-SOLVE] Xv != e8'
    delta, alpha, r = (Q(d[k]) for k in ('delta', 'alpha_boundary', 'r'))
    assert v[8] > 0 and delta*v[8] == 16, '[E-BOUNDARY-SCALE] rank-one subtraction'
    assert alpha == Q(base['alpha'])-delta, '[E-BOUNDARY-SCALE] alpha mismatch'
    assert Q(d['epsilon_boundary']) == 4-alpha, '[E-BOUNDARY-SCALE] epsilon mismatch'
    Y = [row[:] for row in X]
    Y[8][8] -= delta/16
    assert all(dot(row, v) == 0 for row in Y), '[E-BOUNDARY-KERNEL] Yv != 0'
    # Y is positive semidefinite with corank EXACTLY one, and that needs no new computation.
    # Y differs from X only in entry (8,8), so its principal submatrix on the other 69 indices
    # IS X's, which is positive definite because X is -- established by verify_penalty_endpoint.py,
    # which main() runs before any conclusion is printed.  Given Yv = 0 and v8 != 0, every w
    # splits as w = (w8/v8) v + w' with w'[8] = 0, and then
    #     w^T Y w = w'^T Y w' = w'^T X|_{i,j != 8} w' >= 0,
    # zero exactly when w' = 0, i.e. exactly on span(v).  So Y >= 0 with kernel span(v).
    # An earlier draft left this to a prose appeal to conjugation by X^{-1/2}; reducing it to a
    # principal submatrix of X makes the load-bearing positivity claim checkable right here.
    assert all(Y[i][j] == X[i][j] for i in range(n) for j in range(n) if (i, j) != (8, 8)), \
        '[E-BOUNDARY-PSD] Y differs from X away from entry (8,8): the corank-one argument needs ' \
        'the other 69 indices to carry X exactly'
    assert r == v[9]/v[8] and r < 0, '[E-BOUNDARY-SIGN] event coefficients not opposite'
    assert a == [Q(1) if i == 9 else -r if i == 8 else Q(0) for i in range(n)], '[E-BOUNDARY-RANGE] a mismatch'
    assert dot(a, v) == 0 and [dot(row, z) for row in Y] == a, '[E-BOUNDARY-RANGE] Yz != a'
    c0, C = Q(d['c0']), Q(d['C'])
    assert c0*dot(a, z) == 1 and C == 16*c0*r*r, '[E-BOUNDARY-REMAINDER] coefficient mismatch'
    assert Q(9, 10**7) < C < alpha, '[E-BOUNDARY-REMAINDER] branch extension needs 0 < C < alpha'
    assert Q(d['simple_PD_alpha']) == Q(1019417, 6250000), '[E-BOUNDARY-SIMPLE] wrong advertised rational'
    assert alpha < Q(d['simple_PD_alpha']) < Q(base['alpha']), '[E-BOUNDARY-SIMPLE] outside PD range'
    words = [(tuple(x), tuple(y)) for x, y in sharp['words']]
    for j, b in [(8, 0), (9, 1)]:
        got = {words[i]: row[j] for i, row in enumerate(sharp['basis_map']) if row[j]}
        want = {((), ()): 1, ((1,), ()): 1, ((), (b,)): 1, ((1,), (b,)): 1}
        assert got == want, '[E-BOUNDARY-PROJECTOR] J8/J9 identity fails'
    return alpha, Q(d['epsilon_boundary']), C


def main():
    data = json.loads((PROOFS / 'penalty_boundary_certificate.json').read_text())
    alpha, eps, C = check_arithmetic(
        data, (PROOFS / 'penalty_endpoint_certificate.json').read_bytes(),
        (PROOFS / 'sharp_qubit_certificate.json').read_bytes())
    # These establish the inherited positive-definite SOS, deterministic
    # bounds, and equality closure. Their own conclusions concern those older
    # results; the NEW conclusion below is printed only after all succeed.
    runpy.run_path(str(PROOFS / 'verify_penalty_endpoint.py'), run_name='__main__')
    runpy.run_path(str(PROOFS / 'verify_equality_face.py'), run_name='__main__')
    print('PASS continuation identities: Xv=e8, Yv=0, Yz=a, opposite event signs, J8/J9 '
          'projectors, and Y = X off entry (8,8) so Y >= 0 with kernel span(v)')
    # The certified bound is alpha (exact, but a rational with thousands of digits -- it lives in
    # penalty_boundary_certificate.json).  The quotable number is the short rational just above
    # it, and it is IMPLIED by the certified one rather than resting on a separate
    # positive-definite Gram that this repository does not ship.
    print(f'{SUCCESS}: the shipped singular certificate proves alpha_star <= {float(alpha):.16f}...,'
          f' exactly; that implies the quotable alpha_star <= 1019417/6250000 = 0.16310672.')
    print('     The exact bound is the rational in penalty_boundary_certificate.json, not the '
          'printed decimal, and it is certified by the Y >= 0 check above rather than by a '
          'separate positive-definite Gram.')
    print(f'With the prose lemmas, equality remains L_F through epsilon ~ {float(eps):.16f}, '
          f'and 7-G_boundary >= C*p^2 with C ~ {float(C):.12g} > 9e-7.')
    print('The true optimal penalty remains OPEN. New geometric/prose arguments await separate review; '
          'this is not a distance-to-L_F bound or a partial-locality witness.')


if __name__ == '__main__':
    main()
