"""Joint (theta, U) search for the (pre-certificate) qubit conjecture.

Supplied so the 600-restart figure quoted in docs/review_2026-09-06_ai.md is reproducible rather
than externally reported.  Superseded by the exact sharp-bound certificate; retained only
as the record of the pre-certificate numerical position.

Shipped workload: 600 Nelder-Mead restarts over theta in [0, pi/4] and three unit Bloch
vectors."""

import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")

import numpy as np
from scipy.optimize import minimize

a = np.array([1., -1, 1]); b = np.array([-1., -1, 1])
E = np.array([[-1, -1, -1], [-1, -1, 1], [1, -1, -1]], float)


def G1(th, U):
    c = np.cos(2 * th); s = np.sin(2 * th)
    w = np.einsum('xy,xi->yi', E, U)
    t = np.sqrt(s * s * (w[:, 0] ** 2 + w[:, 1] ** 2) + (w[:, 2] + c * b) ** 2)
    return c * (a * U[:, 2]).sum() + t.sum()


def U_of(q):
    q = q.reshape(3, 2)
    return np.stack([np.array([np.sin(t) * np.cos(f), np.sin(t) * np.sin(f), np.cos(t)])
                     for t, f in q])


RESTARTS = 600

if __name__ == '__main__':
    rng = np.random.default_rng(7)
    best = (-9.0, None)
    for _ in range(RESTARTS):
        z = np.concatenate([[rng.uniform(0, np.pi / 4)], rng.uniform(0, np.pi, 6)])
        z[2::2] = rng.uniform(0, 2 * np.pi, 3)
        r = minimize(lambda q: -G1(float(np.clip(q[0], 0, np.pi / 4)), U_of(q[1:])), z,
                     method='Nelder-Mead',
                     options={'maxiter': 30000, 'maxfev': 30000, 'fatol': 1e-15, 'xatol': 1e-13})
        if -r.fun > best[0]:
            best = (-r.fun, r.x.copy())
    th = float(np.clip(best[1][0], 0, np.pi / 4))
    print(f"restarts: {RESTARTS}")
    print(f"best G = {best[0]:.15f}   at theta/pi = {th / np.pi:.10f}")
    print(f"exceeds 7? {best[0] > 7 + 1e-12}")
    assert best[0] <= 7 + 1e-9, "numerical search exceeded the certified bound"
    print("PASS numerical search consistent with the certified bound F <= 7")
