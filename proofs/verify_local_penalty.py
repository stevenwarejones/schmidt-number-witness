"""Interval Newton/Krawczyk certificate for a projective-qubit stationary point.
Default: seven real parameters. --complex: 12 parameters modulo Schmidt gauge.
Both are LOCAL statements, never global optimality proofs.
Requires mpmath. Identity uses independently coded second-order interval AD.
"""

import json
import sys
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit("Run without -O: assertions are certificate checks.")
import mpmath as mp

mp.mp.dps = 100
mp.iv.dps = 80
R = Path(__file__).resolve().parent
COMPLEX = "--complex" in sys.argv
N = 12 if COMPLEX else 7
iv = mp.iv.mpf
Z = lambda: iv(0)


class AD:
    def __init__(self, v, g=None, h=None):
        self.v = v if hasattr(v, "_mpi_") else iv(v)
        self.g = g if g is not None else [Z() for i in range(N)]
        self.h = h if h is not None else [[Z() for j in range(N)] for i in range(N)]

    def __add__(a, b):
        b = b if isinstance(b, AD) else AD(b)
        return AD(
            a.v + b.v,
            [a.g[i] + b.g[i] for i in range(N)],
            [[a.h[i][j] + b.h[i][j] for j in range(N)] for i in range(N)],
        )

    __radd__ = __add__

    def __neg__(a):
        return a * (-1)

    def __sub__(a, b):
        return a + -b if isinstance(b, AD) else a + (-b)

    def __rsub__(a, b):
        return -a + b

    def __mul__(a, b):
        b = b if isinstance(b, AD) else AD(b)
        return AD(
            a.v * b.v,
            [a.g[i] * b.v + a.v * b.g[i] for i in range(N)],
            [
                [
                    a.h[i][j] * b.v
                    + a.g[i] * b.g[j]
                    + a.g[j] * b.g[i]
                    + a.v * b.h[i][j]
                    for j in range(N)
                ]
                for i in range(N)
            ],
        )

    __rmul__ = __mul__

    def inv(a):
        v = 1 / a.v
        return AD(
            v,
            [-a.g[i] * v * v for i in range(N)],
            [
                [2 * a.g[i] * a.g[j] * v * v * v - a.h[i][j] * v * v for j in range(N)]
                for i in range(N)
            ],
        )

    def __truediv__(a, b):
        return a * (b.inv() if isinstance(b, AD) else AD(b).inv())

    def __rtruediv__(a, b):
        return a.inv() * b


def trig(a, cosine=False):
    v = mp.iv.cos(a.v) if cosine else mp.iv.sin(a.v)
    d = -mp.iv.sin(a.v) if cosine else mp.iv.cos(a.v)
    dd = -v
    return AD(
        v,
        [d * x for x in a.g],
        [[dd * a.g[i] * a.g[j] + d * a.h[i][j] for j in range(N)] for i in range(N)],
    )


def objective(coords):
    q = []
    for i, x in enumerate(coords):
        a = AD(x)
        a.g[i] = iv(1)
        q.append(a)
    t = q[0]
    z = q[1:7]
    c = (1 - t * t) / (1 + t * t)
    s = 2 * t / (1 + t * t)
    X = [2 * a / (1 + a * a) for a in z]
    Zs = [(1 - a * a) / (1 + a * a) for a in z]
    Y = [AD(0) for _ in range(6)]
    if COMPLEX:
        hs = [AD(0)] + q[7:]
        Y = [trig(h) for h in hs]
        X = [a * trig(h, True) for a, h in zip(X, hs)]
        Zs = [a * trig(h, True) for a, h in zip(Zs, hs)]
    v = [c * a for a in Zs] + [
        s * (X[i] * X[3 + j] - Y[i] * Y[3 + j]) + Zs[i] * Zs[3 + j]
        for i in range(3)
        for j in range(3)
    ]
    w = [1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1]
    F = sum(a * b for a, b in zip(w, v))
    p = (1 + v[1] + v[3] + v[9]) / 4
    return 4 + (F - 7) / p, p


def ends(x):
    return tuple(mp.mpf(t) for t in x._mpi_)


def mid(x):
    a, b = ends(x)
    return (a + b) / 2


def mag(x):
    return max(abs(v) for v in ends(x))


def show(x):
    return [mp.nstr(v, 65) for v in ends(x)]


if __name__ == "__main__":
    data = json.loads((R / "local_penalty_candidate.json").read_text())
    cs = data["coordinates"] + (["0"] * 5 if COMPLEX else [])
    rad = mp.mpf("1e-25")
    assert len(data["coordinates"]) == 7, "expected seven real center coordinates"
    centers = [iv(x) for x in cs]
    boxes = [iv(x) + iv(["-1e-25", "1e-25"]) for x in cs]
    assert (
        ends(boxes[0])[0] > 0 and ends(boxes[0])[1] < 1
    ), "Schmidt chart must be entangled and nonmaximal"
    assert (
        ends(boxes[1])[1] < 0 or ends(boxes[1])[0] > 0
    ), "phase gauge requires nonzero A0 transverse component"
    f0, _ = objective(centers)
    fb, pb = objective(boxes)
    assert ends(pb.v)[0] > 0, "event must be strictly positive on the box"
    H = mp.matrix([[mid(x) for x in row] for row in f0.h])
    invH = H**-1
    # A decimal approximation is an exact chosen preconditioner, NOT an assumed exact inverse.
    B = [[iv(mp.nstr(invH[i, j], 70)) for j in range(N)] for i in range(N)]
    T = [
        [
            (iv(int(i == j)) - sum(B[i][k] * fb.h[k][j] for k in range(N)))
            for j in range(N)
        ]
        for i in range(N)
    ]
    correction = [-sum(B[i][j] * f0.g[j] for j in range(N)) for i in range(N)]
    images = [
        correction[i] + sum(T[i][j] * iv(["-1e-25", "1e-25"]) for j in range(N))
        for i in range(N)
    ]
    bounds = [mag(x) for x in images]
    contraction = max(ends(sum(abs(x) for x in row))[1] for row in T)
    assert max(bounds) < rad, "Krawczyk image is not strictly interior"
    assert contraction < 1, "no contraction"
    # Interval LDL of negative Hessian: positive pivots certify all Hessians in box negative definite.
    L = [[iv(int(i == j)) for j in range(N)] for i in range(N)]
    D = []
    for i in range(N):
        d = -fb.h[i][i] - sum(L[i][k] * L[i][k] * D[k] for k in range(i))
        assert ends(d)[0] > 0
        D.append(d)
        for j in range(i + 1, N):
            L[j][i] = (
                -fb.h[j][i] - sum(L[j][k] * L[i][k] * D[k] for k in range(i))
            ) / d
    out = {
        "scope": (
            "unique stationary point and strict local maximum in 12-dimensional complex pure-projective qubit chart modulo Schmidt gauge"
            if COMPLEX
            else "unique stationary point and strict local maximum in seven-dimensional real-projective chart ONLY"
        ),
        "radius": "1e-25",
        "interval_decimal_precision": 80,
        "max_krawczyk_radius": mp.nstr(max(bounds), 20),
        "contraction_bound": mp.nstr(contraction, 20),
        "ratio_interval": show(fb.v),
        "p_interval": show(pb.v),
        "negative_hessian_pivot_lower_bounds": [mp.nstr(ends(d)[0], 20) for d in D],
    }
    print(json.dumps(out, indent=2))
