"""Independent derivative checks and meaningful rejection tests for the local certificate.

The gradient and Hessian produced by the interval AD are compared against a scalar
expression written independently and differentiated by mpmath, so an error in the AD class
cannot be hidden by reusing it on both sides.  The rejection cases then require the
INTENDED diagnostic: a displaced centre must fail interior inclusion, and a factorization
of +Hessian instead of -Hessian must fail the negative-definiteness guard.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import mpmath as mp

R = Path(__file__).resolve().parent.parent / "proofs"
SCRIPT = (R / "verify_local_penalty.py").read_text()
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


ad, pad = m.objective([m.iv(mp.nstr(x, 90)) for x in coords])

# The gradient is what the Krawczyk step drives to zero, so check it on its own terms.
worst_g = mp.mpf(0)
for i in range(12):
    orders = [0] * 12
    orders[i] = 1
    d = mp.diff(scalar, tuple(coords), tuple(orders))
    worst_g = max(worst_g, abs(d - m.mid(ad.g[i])))
assert worst_g < mp.mpf("1e-65"), worst_g
print("PASS 12 gradient entries independently differentiated; max error", mp.nstr(worst_g, 8))

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

# The ratio enclosure is a lower bound on alpha* on its own: every point of the chart is a
# genuine pure two-qubit projective behaviour and p > 0 is certified on the box, so no part
# of the Krawczyk or LDL argument is needed for that consequence.  Check it stands.
from fractions import Fraction as Fr  # noqa: E402

lo = mp.mpf(m.show(m.objective([m.iv(x) for x in
                                json.loads((R / "local_penalty_candidate.json").read_text())
                                ["coordinates"] + ["0"] * 5])[0].v)[0])
old = Fr(json.loads((R / "penalty_lower_certificate.json").read_text())["ratio"])
assert mp.mpf(0) < lo, "the certified ratio enclosure must be positive"
assert lo > mp.mpf(old.numerator) / mp.mpf(old.denominator), (
    "the interval evaluation no longer exceeds the exact rational lower certificate; "
    "docs/PENALTY_RESEARCH.md section 4 records that it does"
)
print("PASS the interval ratio at the candidate exceeds the exact rational lower certificate")


# Serialization: a field advertised as a bound must be one.  mp.nstr rounds to nearest, so
# it can print an endpoint strictly INSIDE the interval; at this candidate it did, by about
# 3e-67 on the ratio's lower end.  These checks compare the emitted decimal strings, as
# exact Fractions, against the exact binary interval endpoints.  Reported by review of
# 661b814.
CAND = json.loads((R / "local_penalty_candidate.json").read_text())["coordinates"]
boxes = [m.iv(x) + m.iv(["-1e-25", "1e-25"]) for x in CAND + ["0"] * 5]
ratio_ad, p_ad = m.objective(boxes)
for label, interval in [("ratio_interval", ratio_ad.v), ("p_interval", p_ad.v)]:
    text = m.show(interval)
    true_lo, true_hi = (m.exact_end(t) for t in interval._mpi_)
    assert Fr(text[0]) <= true_lo, (label, "lower endpoint printed inward", text[0])
    assert Fr(text[1]) >= true_hi, (label, "upper endpoint printed inward", text[1])
    assert Fr(text[0]) < Fr(text[1]), (label, "printed enclosure is empty")
print("PASS both reported intervals are outward-rounded against their exact endpoints")

# Both signs and both directions, on values chosen so that nearest rounding would go the
# wrong way at the requested precision.
for value in [
    Fr(1, 3), Fr(-1, 3), Fr(2, 3), Fr(-2, 3),
    Fr(10 ** 40 + 1, 3 * 10 ** 40), Fr(-(10 ** 40 + 1), 3 * 10 ** 40),
    Fr(999999999999, 10 ** 12), Fr(-999999999999, 10 ** 12),
    Fr(3, 10 ** 45), Fr(-3, 10 ** 45), Fr(0),
]:
    for digits in (5, 20, 65):
        lo, hi = m.floor_str(value, digits), m.ceil_str(value, digits)
        assert Fr(lo) <= value <= Fr(hi), (value, digits, lo, hi)
print("PASS floor_str and ceil_str round outward for both signs at three precisions")

# Teeth: the nearest-rounding serialization these replaced must FAIL the check above, or
# the check is not testing anything.
import mpmath as _mp  # noqa: E402

nearest = [_mp.nstr(_mp.mpf(t), 65) for t in ratio_ad.v._mpi_]
true_lo, true_hi = (m.exact_end(t) for t in ratio_ad.v._mpi_)
assert not (Fr(nearest[0]) <= true_lo and Fr(nearest[1]) >= true_hi), (
    "nearest rounding no longer produces an inward endpoint at this candidate, so this "
    "control has stopped demonstrating the bug it guards against"
)
print("PASS control: nearest-rounded serialization is detected as inward")

# The pivot lower bounds and the two radii are advertised as bounds, so check their
# direction too, by re-parsing what the verifier itself emitted.
report = json.loads(
    subprocess.run(
        [sys.executable, str(R / "verify_local_penalty.py"), "--complex"],
        capture_output=True, text=True, check=True,
    ).stdout
)
assert Fr(report["ratio_interval"][0]) <= true_lo <= true_hi <= Fr(
    report["ratio_interval"][1]
), "the emitted report disagrees with a fresh interval evaluation"
assert all(Fr(x) > 0 for x in report["negative_hessian_pivot_lower_bounds"]), (
    "a printed pivot lower bound is not positive, so it does not certify definiteness"
)
assert Fr(report["contraction_bound"]) < 1 and Fr(report["max_krawczyk_radius"]) < Fr(
    "1e-25"
), "a printed bound does not itself satisfy the condition it is meant to witness"
print("PASS the emitted report's bounds hold as stated when re-parsed exactly")


def run_mutated(text, coords_json=None):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "verify_local_penalty.py").write_text(text)
        c = json.loads((R / "local_penalty_candidate.json").read_text())
        if coords_json is not None:
            c = coords_json(c)
        (p / "local_penalty_candidate.json").write_text(json.dumps(c))
        shutil.copy(R / "penalty_lower_certificate.json", p)
        return subprocess.run(
            [sys.executable, str(p / "verify_local_penalty.py"), "--complex"],
            capture_output=True,
            text=True,
        )


# Control: unmodified script and centre must pass in the staged layout.
base = run_mutated(SCRIPT)
assert base.returncode == 0, base.stderr[-2000:]
print("PASS control: the unmodified certificate passes in the staged layout")


def displace(c):
    c["coordinates"][0] = str(mp.mpf(c["coordinates"][0]) + mp.mpf(".001"))
    return c


run = run_mutated(SCRIPT, displace)
assert (
    run.returncode != 0 and "Krawczyk image is not strictly interior" in run.stderr
), run.stderr
assert "[E-LOCAL-NOT-NEGATIVE-DEFINITE]" not in run.stderr, "wrong guard fired"
print("PASS displaced root rejected for failed interior inclusion")

# Factor +Hessian instead of -Hessian.  At a strict local maximum the Hessian is negative
# definite, so this must fail the negative-definiteness guard and no other.
flipped = SCRIPT.replace(
    "d = -fb.h[i][i] - sum(L[i][k] * L[i][k] * D[k] for k in range(i))",
    "d = fb.h[i][i] - sum(L[i][k] * L[i][k] * D[k] for k in range(i))",
)
assert flipped != SCRIPT, "the LDL pivot line moved; update this mutation"
run = run_mutated(flipped)
assert run.returncode != 0, "factoring +Hessian was accepted"
assert "[E-LOCAL-NOT-NEGATIVE-DEFINITE]" in run.stderr, run.stderr[-2000:]
assert "Krawczyk image is not strictly interior" not in run.stderr, "wrong guard fired"
print("PASS factoring +Hessian rejected for failed negative definiteness")

# Anti-degradation control: a script that refuses everything satisfies no case above.
refuse = "import sys\nsys.stderr.write('refused\\n')\nraise SystemExit(1)\n"
run = run_mutated(refuse)
assert run.returncode != 0 and "[E-LOCAL-NOT-NEGATIVE-DEFINITE]" not in run.stderr
assert "Krawczyk image is not strictly interior" not in run.stderr
print("PASS control: a refuse-everything script reports no intended diagnostic")
