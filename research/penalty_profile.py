"""Exploratory real-projective fixed-Schmidt-angle search; no upper certificates."""

import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

R = Path(__file__).resolve().parent
OUTPUT_DIR = R.parent / "build"
OUTPUT_DIR.mkdir(exist_ok=True)
old = json.loads((R.parent / "proofs/local_penalty_candidate.json").read_text())
a0 = 2 * np.arctan(np.array([float(x) for x in old["coordinates"][1:]]))
w = np.array([1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1])


def values(th, a):
    x = np.sin(a)
    z = np.cos(a)
    v = np.r_[
        np.cos(2 * th) * z,
        (np.sin(2 * th) * np.outer(x[:3], x[3:]) + np.outer(z[:3], z[3:])).ravel(),
    ]
    F = w @ v
    # Born amplitude avoids cancellation in p.
    p = (
        np.cos(th) * np.cos(a[1] / 2) * np.cos(a[3] / 2)
        + np.sin(th) * np.sin(a[1] / 2) * np.sin(a[3] / 2)
    ) ** 2
    return 4 + (F - 7) / p if p > 0 else -1e99, p, F


rng = np.random.default_rng(81)
out = []
prev = a0
for th in [0.3, 0.25, 0.233858, 0.2, 0.15, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005]:

    def fun(a):
        r, p, _ = values(th, a)
        return -r if p > 1e-7 else 1e3 + 1e7 * (1e-7 - p)

    starts = (
        [a0, prev]
        + [a0 + rng.normal(0, 0.3, 6) for _ in range(12)]
        + [rng.uniform(-np.pi, np.pi, 6) for _ in range(12)]
    )
    best = None
    for a in starts:
        res = minimize(fun, a, method="BFGS", options={"maxiter": 600, "gtol": 1e-8})
        r, p, F = values(th, res.x)
        if p > 1e-7 and (best is None or r > best["ratio"]):
            best = {"theta": th, "ratio": r, "p": p, "F": F, "angles": res.x.tolist()}
    prev = np.array(best["angles"])
    out.append(best)
    print({k: v for k, v in best.items() if k != "angles"}, flush=True)
(OUTPUT_DIR / "penalty_profile.json").write_text(
    json.dumps(
        {
            "status": "numerical lower witnesses in real-projective restriction; p cutoff 1e-7; NOT upper bounds",
            "rows": out,
        },
        indent=2,
    )
    + "\n"
)
