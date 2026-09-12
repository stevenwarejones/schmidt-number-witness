"""Exact projected SN2 simulators for ALL relabelings of Q and both GK branches.
No supplied quantum bound, numerical optimization, or discovery code is used.
Three-score matching certifies non-detection by the family, NOT full-Q simulation.
"""

import sys, json, itertools
from fractions import Fraction as F
from pathlib import Path
import sympy as sp

if sys.flags.optimize:
    raise SystemExit("Run without -O")
R = Path(__file__).resolve().parent
c = json.loads((R / "qutrit_certificate.json").read_text())
data = json.loads((R / "gigena_complete_certificate.json").read_text())


def vec(a):
    return sp.Matrix([sp.Integer(x) + sp.I * y for x, y in a])


psi = vec(c["state"])
norm = (psi.conjugate().T * psi)[0]


def measurements(rows):
    out = []
    for row in rows:
        u = vec(row["vector"])
        p = u * u.conjugate().T / (u.conjugate().T * u)[0]
        out.append(
            [p, sp.eye(3) - p] if row["rank_one_outcome"] == 0 else [sp.eye(3) - p, p]
        )
    return out


A = measurements(c["Alice"])
B = measurements(c["Bob"])
P = {}
for x, y, a, b in itertools.product(range(3), range(3), range(2), range(2)):
    value = sp.expand(
        (psi.conjugate().T * sp.kronecker_product(A[x][a], B[y][b]) * psi)[0] / norm
    )
    P[x, y, a, b] = F(value)
    assert value >= 0
assert list(P.values()) == list(map(F, c["Q"])), "Q Born probabilities mismatch"
v = (
    tuple(
        sum((-1) ** a * P[x, 0, a, b] for a, b in itertools.product(range(2), repeat=2))
        for x in range(3)
    )
    + tuple(
        sum((-1) ** b * P[0, y, a, b] for a, b in itertools.product(range(2), repeat=2))
        for y in range(3)
    )
    + tuple(
        sum(
            (-1) ** (a + b) * P[x, y, a, b]
            for a, b in itertools.product(range(2), repeat=2)
        )
        for x, y in itertools.product(range(3), repeat=2)
    )
)
assert (
    sum(
        a * b
        for a, b in zip([1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1], v)
    )
    > 7
)


def rename(v, args):
    pa, pb, sa, sb, swap = args
    if swap:
        v = v[3:6] + v[:3] + tuple(v[6 + 3 * j + i] for i in range(3) for j in range(3))
    return (
        tuple(sa[i] * v[pa[i]] for i in range(3))
        + tuple(sb[j] * v[3 + pb[j]] for j in range(3))
        + tuple(
            sa[i] * sb[j] * v[6 + 3 * pa[i] + pb[j]] for i in range(3) for j in range(3)
        )
    )


def projection(v, branch):
    return (
        v[0] + v[1] + branch * (v[3] + v[4]),
        v[6] + v[7] + v[9] + v[10],
        v[12] - v[13] + v[8] - v[11],
    )


expected = set()
for args in itertools.product(
    itertools.permutations(range(3)),
    itertools.permutations(range(3)),
    itertools.product([-1, 1], repeat=3),
    itertools.product([-1, 1], repeat=3),
    [False, True],
):
    vv = rename(v, args)
    for b in [-1, 1]:
        expected.add((b, projection(vv, b)))
# Reconstruct the fixed rational-qubit seed from its state and effects.
u = sp.Matrix([64474, 73134, 17575, -13624])
rays = [
    [100000, 312],
    [98313, 18289],
    [94227, -33485],
    [64814, 76152],
    [-35243, 93584],
    [-11537, -99332],
]
O = []
for d in rays:
    q = sp.Matrix(d)
    O.append(2 * q * q.T / q.dot(q) - sp.eye(2))


def exp(o):
    return F((u.T * o * u)[0] / u.dot(u))


seed = (
    tuple(exp(sp.kronecker_product(a, sp.eye(2))) for a in O[:3])
    + tuple(exp(sp.kronecker_product(sp.eye(2), b)) for b in O[3:])
    + tuple(exp(sp.kronecker_product(a, b)) for a in O[:3] for b in O[3:])
)


def strategy(s):
    k = s["kind"]
    if k == "local":
        a = tuple(s["A"])
        b = tuple(s["B"])
        assert all(x in [-1, 1] for x in a + b)
        return a + b + tuple(x * y for x in a for y in b)
    if k == "rational_qubit":
        return rename(seed, s["relabel"])
    if k == "phi":
        t = F(s["t"])
        z = F(s["z"])
        assert t * t + z * z == 1
        a = [(t, z), (-t, z), (F(1), F(0))]
        base = (F(0),) * 6 + tuple(x[0] * y[0] + x[1] * y[1] for x in a for y in a)
        return rename(base, s["relabel"])
    if k == "schmidt_half_tangents":
        q = list(map(F, s["coordinates"]))
        assert len(q) == 7
        t = q[0]
        zs = q[1:]
        C = (1 - t * t) / (1 + t * t)
        S = 2 * t / (1 + t * t)
        X = [2 * z / (1 + z * z) for z in zs]
        Z = [(1 - z * z) / (1 + z * z) for z in zs]
        return tuple(C * z for z in Z) + tuple(
            S * X[i] * X[3 + j] + Z[i] * Z[3 + j] for i in range(3) for j in range(3)
        )
    raise AssertionError("unknown strategy kind")


seen = set()
for entry in data["proofs"]:
    branch = entry["branch"]
    assert branch in [-1, 1]
    target = tuple(map(F, entry["target"]))
    key = (branch, target)
    assert key not in seen, "duplicate target"
    seen.add(key)
    weights = list(map(F, entry["weights"]))
    assert len(weights) == len(entry["strategies"]) == len(entry["points"])
    assert sum(weights) == 1 and min(weights) >= 0, "invalid convex weights"
    points = [projection(strategy(s), branch) for s in entry["strategies"]]
    assert points == [
        tuple(map(F, p)) for p in entry["points"]
    ], "strategy projection mismatch"
    assert (
        tuple(sum(w * p[j] for w, p in zip(weights, points)) for j in range(3))
        == target
    ), "target mismatch"
assert seen == expected, "incomplete relabeling coverage"
print("PASS: exact qutrit Born probabilities and F(Q)>7")
print(
    "PASS:",
    len(seen),
    "projected targets, both branches, all relabelings, exact rational SN2 mixtures",
)
print(
    "CONCLUSION: every scalar score in the GK eq (1) family on Q is attainable by SN2; full-Q simulation is NOT claimed."
)
