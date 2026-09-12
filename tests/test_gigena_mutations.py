import json, subprocess, sys, tempfile, shutil
from pathlib import Path

R = Path(__file__).resolve().parent.parent / "proofs"
base = json.loads((R / "gigena_complete_certificate.json").read_text())
for name, expected in [
    ("missing", "incomplete relabeling coverage"),
    ("weight", "invalid convex weights"),
    ("point", "strategy projection mismatch"),
]:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        for f in ["verify_gigena_complete.py", "qutrit_certificate.json"]:
            shutil.copy(R / f, p / f)
        c = json.loads(json.dumps(base))
        if name == "missing":
            c["proofs"].pop()
        if name == "weight":
            c["proofs"][0]["weights"][0] = "-1"
        if name == "point":
            c["proofs"][0]["points"][0][0] = "123456"
        (p / "gigena_complete_certificate.json").write_text(json.dumps(c))
        r = subprocess.run(
            [sys.executable, str(p / "verify_gigena_complete.py")],
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0 and expected in r.stderr, (name, r.stderr)
        print("PASS", name, "rejected for", expected, flush=True)
