"""Exact fixtures for the convex dilution lemma; general proof is in the note."""

from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import sys

if sys.flags.optimize:
    raise SystemExit("Run without -O: assertions are checks.")
R = Path(__file__).resolve().parent
w = [1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1]


def score(v):
    return sum(a * b for a, b in zip(w, v))


def event(v):
    return (1 + v[1] + v[3] + v[9]) / 4


vertices = []
for s in product([Q(-1), Q(1)], repeat=6):
    v = list(s) + [s[i] * s[3 + j] for i in range(3) for j in range(3)]
    assert score(v) <= 7, (
        "[E-CVX-LOCAL-BOUND] a deterministic local behaviour exceeds F = 7, contradicting "
        "the local bound the whole penalty construction rests on"
    )
    if score(v) == 7:
        assert event(v) == 0, (
            "[E-CVX-SATURATOR-EVENT] a local saturator of F = 7 has positive event "
            "probability, which would break the dilution identity p((1-t)L + tQ) = t p(Q)"
        )
        vertices.append(v)
assert len(vertices) == 5, (
    "[E-CVX-FACE-VERTICES] the local F = 7 face does not have exactly five deterministic "
    "vertices, contradicting the equality-face theorem this note builds on"
)
c = json.loads((R / "penalty_lower_certificate.json").read_text())
t = Q(c["t"])
z = list(map(Q, c["measurement_half_tangents"]))
C = (1 - t * t) / (1 + t * t)
S = 2 * t / (1 + t * t)
X = [2 * a / (1 + a * a) for a in z]
Z = [(1 - a * a) / (1 + a * a) for a in z]
v = [C * a for a in Z] + [
    S * X[i] * X[3 + j] + Z[i] * Z[3 + j] for i in range(3) for j in range(3)
]
p = event(v)
f = score(v)
ratio = (f + 4 * p - 7) / p
assert ratio == Q(c["ratio"]) and p > 0, (
    "[E-CVX-LOWER-RATIO] the reconstructed lower strategy does not reproduce the certified "
    "ratio with positive event probability"
)
for L in vertices:
    for tau in [Q(1, 2), Q(1, 10**6), Q(1, 10**30)]:
        mix = [(1 - tau) * a + tau * b for a, b in zip(L, v)]
        pm = event(mix)
        fm = score(mix)
        assert pm == tau * p and (fm + 4 * pm - 7) / pm == ratio, (
            "[E-CVX-DILUTION] dilution failed to scale the event probability by tau while "
            "preserving the ratio, which is the whole content of the rare-event lemma"
        )
# Symbolic coefficient collapse when B0=B1=B2=B:
for b in [-1, 1]:
    coeff = [w[i] + b * sum(w[6 + 3 * i : 9 + 3 * i]) for i in range(3)]
    constant = b * sum(w[3:6])
    upper = constant + sum(abs(a) for a in coeff)
    assert upper == ({1: 3, -1: 7}[b]), (
        "[E-CVX-COMMON-B] the conditional Alice bound for the common-B branch is not the "
        "value the nonattainment argument uses (3 for B = +1, 7 for B = -1)"
    )
print(
    "PASS five local saturators, all p=0; exact rational Born strategy; 15 dilution identities"
)
print("PASS common-B block upper bounds: B=+1 gives 3; B=-1 gives 7")
