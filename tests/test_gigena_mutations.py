"""Corruption tests for the complete Gigena-Kaniewski comparison.

Every case must be rejected for the INTENDED mathematical reason: the diagnostic code of
that case must appear and no other case's code may appear.  Two anti-degradation controls
sit alongside them, because a suite that only demands "some failure" is passed by a
verifier that refuses everything, and a suite that only demands "some diagnostic" is
passed by one that always prints the same one.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "proofs"
BASE = json.loads((R / "gigena_complete_certificate.json").read_text())
SUPPORT = ["verify_gigena_complete.py", "qutrit_certificate.json"]

# Each case: how to damage the certificate, and the code that damage must provoke.
CASES = {}


def case(code, note):
    def add(fn):
        CASES[fn.__name__] = (fn, code, note)
        return fn

    return add


@case("[E-GK-COVERAGE]", "dropping a target leaves part of the relabeling orbit uncompared")
def missing(c):
    c["proofs"].pop()


@case("[E-GK-DUPLICATE]", "proving one target twice does not cover a second target")
def duplicate(c):
    c["proofs"][1] = json.loads(json.dumps(c["proofs"][0]))


@case("[E-GK-WEIGHTS]", "a negative weight is not a convex mixture, so not an SN2 behaviour")
def weight(c):
    c["proofs"][0]["weights"][0] = "-1"


@case("[E-GK-WEIGHTS]", "weights that do not sum to one are not a convex mixture either")
def unnormalized(c):
    c["proofs"][0]["weights"][0] = str(
        __import__("fractions").Fraction(c["proofs"][0]["weights"][0]) + 1
    )


@case("[E-GK-PROJECTION]", "a stored point must really be its strategy's projection")
def point(c):
    c["proofs"][0]["points"][0][0] = "123456"


@case("[E-GK-TARGET]", "the mixture must actually land on the target it claims")
def target(c):
    e = c["proofs"][0]
    e["target"] = [str(__import__("fractions").Fraction(t) + 1) for t in e["target"]]


@case("[E-GK-NOT-UNIT]", "a phi strategy off the unit circle is not a projective measurement")
def not_unit(c):
    for e in c["proofs"]:
        for s in e["strategies"]:
            if s["kind"] == "phi":
                s["t"] = str(__import__("fractions").Fraction(s["t"]) + 1)
                return
    raise SystemExit("no phi strategy in the certificate; adjust this case")


@case("[E-GK-NOT-DETERMINISTIC]", "a local strategy's outcomes must be deterministic signs")
def not_deterministic(c):
    for e in c["proofs"]:
        for s in e["strategies"]:
            if s["kind"] == "local":
                s["A"][0] = 2
                return
    raise SystemExit("no local strategy in the certificate; adjust this case")


ALL_CODES = {code for _, code, _ in CASES.values()}


def run(tmp, cert_text, script_text=None):
    p = Path(tmp)
    for f in SUPPORT:
        shutil.copy(R / f, p / f)
    if script_text is not None:
        (p / "verify_gigena_complete.py").write_text(script_text)
    (p / "gigena_complete_certificate.json").write_text(cert_text)
    return subprocess.run(
        [sys.executable, str(p / "verify_gigena_complete.py")],
        capture_output=True,
        text=True,
    )


# Control 0: the untouched certificate must PASS in the same temporary layout, so that a
# rejection below is caused by the damage and not by the way these cases are staged.
with tempfile.TemporaryDirectory() as td:
    r = run(td, json.dumps(BASE))
    assert r.returncode == 0, ("baseline must pass in the staged layout", r.stderr[-2000:])
    assert "1152 projected targets" in r.stdout, r.stdout
print("PASS control: the unmodified certificate passes in the staged layout", flush=True)

for name, (damage, code, note) in CASES.items():
    c = json.loads(json.dumps(BASE))
    damage(c)
    with tempfile.TemporaryDirectory() as td:
        r = run(td, json.dumps(c))
    assert r.returncode != 0, (name, "was accepted", r.stdout[-2000:])
    assert code in r.stderr, (name, "did not report", code, r.stderr[-2000:])
    others = {o for o in ALL_CODES if o != code and o in r.stderr}
    assert not others, (name, "also reported unintended codes", others)
    print("PASS", name, "rejected for", code, "--", note, flush=True)

# Control 1: a verifier that refuses everything must NOT satisfy this suite.  It fails the
# baseline control above, and it also fails every case's intended-code requirement.
SENTINEL = (
    "import sys\n"
    "sys.stderr.write('refused\\n')\n"
    "raise SystemExit(1)\n"
)
with tempfile.TemporaryDirectory() as td:
    r = run(td, json.dumps(BASE), SENTINEL)
assert r.returncode != 0 and not any(c in r.stderr for c in ALL_CODES)
print("PASS control: a refuse-everything verifier reports no intended code", flush=True)

# Control 2: a verifier that always emits the coverage code must not be able to stand in
# for one that checks weights, so the code alone is required to be case-specific.
ALWAYS = (
    "import sys\n"
    "sys.stderr.write('[E-GK-COVERAGE] incomplete relabeling coverage\\n')\n"
    "raise SystemExit(1)\n"
)
with tempfile.TemporaryDirectory() as td:
    c = json.loads(json.dumps(BASE))
    CASES["weight"][0](c)
    r = run(td, json.dumps(c), ALWAYS)
assert "[E-GK-WEIGHTS]" not in r.stderr, "wrong-code control must not satisfy the weight case"
print("PASS control: a fixed wrong code does not satisfy a different case", flush=True)
print("PASS", len(CASES), "corruption cases plus three controls", flush=True)
