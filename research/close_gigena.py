"""Discovery of exact convex projected simulators for previously uncovered targets."""

import json, itertools
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import least_squares, linprog
import sympy as sp

R = Path(__file__).resolve().parent
OUTPUT_DIR = R.parent / "build"
OUTPUT_DIR.mkdir(exist_ok=True)
full = json.loads((R.parent / "proofs/gigena_complete_certificate.json").read_text())
old = {
    "proofs": [
        e
        for e in full["proofs"]
        if all(s["kind"] != "schmidt_half_tangents" for s in e["strategies"])
    ]
}
c = json.loads((R.parent / "proofs/qutrit_certificate.json").read_text())
P = dict(zip(itertools.product(range(3), range(3), range(2), range(2)), map(F, c["Q"])))
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


def relabel(w, pa, pb, sa, sb, swap):
    a = w[:3]
    b = w[3:6]
    e = [w[6 + 3 * i : 9 + 3 * i] for i in range(3)]
    if swap:
        a, b = b, a
        e = list(zip(*e))
    return (
        tuple(sa[i] * a[pa[i]] for i in range(3))
        + tuple(sb[j] * b[pb[j]] for j in range(3))
        + tuple(
            sa[i] * sb[j] * e[pa[i]][pb[j]]
            for i, j in itertools.product(range(3), repeat=2)
        )
    )


def proj(w, b):
    return (
        w[0] + w[1] + b * (w[3] + w[4]),
        w[6] + w[7] + w[9] + w[10],
        w[12] - w[13] + w[8] - w[11],
    )


alltargets = {b: set() for b in [-1, 1]}
for args in itertools.product(
    itertools.permutations(range(3)),
    itertools.permutations(range(3)),
    itertools.product([-1, 1], repeat=3),
    itertools.product([-1, 1], repeat=3),
    [False, True],
):
    ww = relabel(v, *args)
    for b in [-1, 1]:
        alltargets[b].add(proj(ww, b))
covered = {
    b: {tuple(map(F, x["target"])) for x in old["proofs"] if x["branch"] == b}
    for b in [-1, 1]
}


def behavior(q):
    t = q[0]
    zs = q[1:]
    C = (1 - t * t) / (1 + t * t)
    S = 2 * t / (1 + t * t)
    X = [2 * z / (1 + z * z) for z in zs]
    Z = [(1 - z * z) / (1 + z * z) for z in zs]
    return tuple(C * z for z in Z) + tuple(
        S * X[i] * X[3 + j] + Z[i] * Z[3 + j] for i in range(3) for j in range(3)
    )


rng = np.random.default_rng(834)
extra = []
for b in [-1, 1]:
    for target in sorted(alltargets[b] - covered[b]):
        tf = np.array(target, float)
        best = None
        for _ in range(25):
            sol = least_squares(
                lambda q: np.array(proj(behavior(q), b), float) - tf,
                rng.normal(0, 1, 7),
                max_nfev=600,
                gtol=1e-12,
                ftol=1e-12,
                xtol=1e-12,
            )
            if best is None or np.linalg.norm(sol.fun) < np.linalg.norm(best.fun):
                best = sol
            if np.linalg.norm(best.fun) < 1e-10:
                break
        print("fit", b, tf.tolist(), np.linalg.norm(best.fun), flush=True)
        if np.linalg.norm(best.fun) > 1e-8:
            continue
        coords = [
            [F(str(round(float(x), 10))) for x in best.x + rng.normal(0, 1e-3, 7)]
            for _ in range(50)
        ]
        pts = [proj(behavior(q), b) for q in coords]
        M = np.array([[1] + list(p) for p in pts], float).T
        lp = linprog(
            np.zeros(len(pts)),
            A_eq=M,
            b_eq=np.r_[1, tf],
            bounds=(0, None),
            method="highs",
        )
        assert lp.success
        ix = np.where(lp.x > 1e-9)[0]
        A = sp.Matrix([[1] + list(pts[i]) for i in ix]).T
        weights = A.inv() * sp.Matrix([1] + list(target))
        assert all(x > 0 for x in weights)
        extra.append(
            {
                "branch": b,
                "target": list(map(str, target)),
                "points": [list(map(str, pts[i])) for i in ix],
                "weights": list(map(str, weights)),
                "strategies": [
                    {
                        "kind": "schmidt_half_tangents",
                        "coordinates": list(map(str, coords[i])),
                    }
                    for i in ix
                ],
            }
        )
print(
    "CLOSED",
    len(extra),
    "of",
    sum(len(alltargets[b] - covered[b]) for b in [-1, 1]),
    flush=True,
)
(OUTPUT_DIR / "gigena_extra.json").write_text(json.dumps(extra, indent=2) + "\n")
