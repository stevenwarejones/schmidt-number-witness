"""Independent Born-rule check of analytic Bob elimination (numerical cross-check)."""

import json
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent
I = np.eye(2)
pauli = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]])
w = np.array([1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1])


def eliminate(theta, A, alpha):
    c = np.cos(2 * theta)
    s = np.sin(2 * theta)
    u = alpha / 4
    K = np.array([[-1, -1, -1], [-u, -1, 1], [1, -1, -1]])
    b = np.array([-u, -1, 1])
    T = np.diag([s, -s, 1])
    V = (T @ A.T @ K).T + c * b[:, None] * np.array([0, 0, 1])
    norms = np.linalg.norm(V, axis=1)
    B = V / np.where(norms > 0, norms, 1)[:, None]
    for j in range(3):
        if norms[j] == 0:
            B[j] = [0, 0, 1]
    value = -u + c * (A[0, 2] - u * A[1, 2] + A[2, 2]) + norms.sum()
    return value, B


def born(th, obs, alpha):
    """M_A - alpha p directly from 4x4 Born operators, for given Alice and Bob vectors."""
    psi = np.array([np.cos(th), 0, 0, np.sin(th)])
    v = np.array(
        [np.vdot(psi, np.kron(O, I) @ psi).real for O in obs[:3]]
        + [np.vdot(psi, np.kron(I, O) @ psi).real for O in obs[3:]]
        + [np.vdot(psi, np.kron(a, b) @ psi).real for a in obs[:3] for b in obs[3:]]
    )
    event = np.kron((I + obs[1]) / 2, (I + obs[3]) / 2)
    p = np.vdot(psi, event @ psi).real
    return w @ v + 4 * p - 1 - alpha * p


rng = np.random.default_rng(9401)
err = 0
for _ in range(4000):
    th = rng.uniform(0, np.pi / 4)
    alpha = rng.uniform(0, 4)
    A = rng.normal(size=(3, 3))
    A /= np.linalg.norm(A, axis=1)[:, None]
    value, B = eliminate(th, A, alpha)
    obs = np.einsum("ij,jkl->ikl", np.r_[A, B], pauli)
    direct = born(th, obs, alpha)
    err = max(err, abs(value - direct))
    assert abs(value - direct) < 1e-12, (
        "the elimination formula disagrees with the Born rule at the Bob vectors it returns"
    )
print("4000 complex Bloch/Born reconstructions; max discrepancy", err)

# The formula claims a MAXIMUM over Bob, not merely a consistent value.  Sampling other
# Bob vectors cannot prove optimality, but it can refute it, and it is the only part of
# the claim the check above does not touch at all.
slack = 0
for _ in range(2000):
    th = rng.uniform(0, np.pi / 4)
    alpha = rng.uniform(0, 4)
    A = rng.normal(size=(3, 3))
    A /= np.linalg.norm(A, axis=1)[:, None]
    value, _ = eliminate(th, A, alpha)
    Balt = rng.normal(size=(3, 3))
    Balt /= np.linalg.norm(Balt, axis=1)[:, None]
    obs = np.einsum("ij,jkl->ikl", np.r_[A, Balt], pauli)
    other = born(th, obs, alpha)
    assert other <= value + 1e-10, (
        "an alternative Bob triple beats the claimed exact maximum over Bob, so the "
        "elimination formula is not the maximum it is used as"
    )
    slack = max(slack, value - other)
print("2000 alternative Bob triples; none exceeded the claimed maximum; largest shortfall",
      slack)
