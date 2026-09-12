"""Check AD derivatives independently and confirm meaningful root rejection."""

import importlib.util, json, subprocess, sys, tempfile, shutil
from pathlib import Path
import mpmath as mp

R = Path(__file__).resolve().parent.parent / "proofs"
sys.argv.append("--complex")
spec = importlib.util.spec_from_file_location("cert", R / "verify_local_penalty.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
coords = [
    mp.mpf(x)
    for x in json.loads((R / "local_penalty_candidate.json").read_text())["coordinates"]
] + [mp.mpf(0)] * 5


# Scalar expression independent of AD, with all complex-plane perturbations allowed.
def scalar(*q):
    t = q[0]
    z = q[1:7]
    hs = [mp.mpf(0)] + list(q[7:])
    c = (1 - t * t) / (1 + t * t)
    s = 2 * t / (1 + t * t)
    X = [2 * x / (1 + x * x) * mp.cos(h) for x, h in zip(z, hs)]
    Z = [(1 - x * x) / (1 + x * x) * mp.cos(h) for x, h in zip(z, hs)]
    Y = [mp.sin(h) for h in hs]
    v = [c * x for x in Z] + [
        s * (X[i] * X[3 + j] - Y[i] * Y[3 + j]) + Z[i] * Z[3 + j]
        for i in range(3)
        for j in range(3)
    ]
    F = sum(
        a * b
        for a, b in zip([1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1], v)
    )
    p = (1 + v[1] + v[3] + v[9]) / 4
    return 4 + (F - 7) / p


ad, _ = m.objective([m.iv(mp.nstr(x, 90)) for x in coords])
worst = mp.mpf(0)
for i in range(12):
    for j in range(12):
        orders = [0] * 12
        orders[i] += 1
        orders[j] += 1
        h = mp.diff(scalar, tuple(coords), tuple(orders))
        worst = max(worst, abs(h - m.mid(ad.h[i][j])))
assert worst < mp.mpf("1e-65")
print(
    "PASS 144 Hessian entries independently differentiated; max error",
    mp.nstr(worst, 8),
)
with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    shutil.copy(R / "verify_local_penalty.py", p)
    c = json.loads((R / "local_penalty_candidate.json").read_text())
    c["coordinates"][0] = str(mp.mpf(c["coordinates"][0]) + mp.mpf(".001"))
    (p / "local_penalty_candidate.json").write_text(json.dumps(c))
    run = subprocess.run(
        [sys.executable, str(p / "verify_local_penalty.py"), "--complex"],
        capture_output=True,
        text=True,
    )
    assert (
        run.returncode != 0 and "Krawczyk image is not strictly interior" in run.stderr
    ), run.stderr
    print("PASS displaced root rejected for failed interior inclusion")
