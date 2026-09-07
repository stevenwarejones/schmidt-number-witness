"""Regression: a corrupted certificate must be rejected -- both normally and under
`python -O` -- and neither run may print an affirmative conclusion.

Scope: the facet verifier and the sharp-bound verifier. Those are the two with mutation
cases here; the other verifiers carry the same -O guard but are not mutation-tested by this
file. Do not read a passing run as evidence that every verifier has a mutation test.

This covers the defect where assertions used as proof gates were removed by -O, so
`python -O verify_facet.py` exited 0 on a corrupted certificate and printed "IS A FACET".
Runs against temporary copies; the shipped certificates are never modified."""

import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")

import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = [
    ("proofs/verify_facet.py", "proofs/facet_certificate.json",
     lambda c: c['saturating_points'][0]['v'].__setitem__(0, "100"), "IS A FACET"),
    ("proofs/verify_sharp_qubit.py", "proofs/sharp_qubit_certificate.json",
     lambda c: c['reduced_gram'][0].__setitem__(0, "-1"), "SHARP CERTIFICATE VALID"),
]
fails = []
for script, cert, mutate, affirmative in CASES:
    sp, cp = ROOT / script, ROOT / cert
    if not sp.exists() or not cp.exists():
        fails.append(f"missing {script} or {cert}"); continue
    for flags in ([], ["-O"]):
        d = tempfile.mkdtemp(prefix="tspl-reg-")
        try:
            shutil.copy(sp, d); shutil.copy(cp, d)
            c = json.load(open(os.path.join(d, cp.name))); mutate(c)
            json.dump(c, open(os.path.join(d, cp.name), "w"))
            p = subprocess.run([sys.executable] + flags + [os.path.join(d, sp.name)],
                               capture_output=True, text=True)
            tag = f"{sp.name} {'-O' if flags else '  '}"
            if p.returncode == 0:
                fails.append(f"{tag}: corrupted certificate ACCEPTED (exit 0)")
            elif affirmative in (p.stdout + p.stderr):
                fails.append(f"{tag}: printed the affirmative conclusion on a rejected input")
            else:
                print(f"  PASS {tag}: rejected, no affirmative conclusion")
        finally:
            shutil.rmtree(d, ignore_errors=True)
    p = subprocess.run([sys.executable, str(sp)], capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        fails.append(f"{sp.name}: SHIPPED certificate rejected (exit {p.returncode})")
    else:
        print(f"  PASS {sp.name}   : shipped certificate accepted normally")
if fails:
    print("\nFAILED:"); [print("   " + f) for f in fails]; raise SystemExit(1)
print("\nPASS standalone verifiers reject corrupted certificates under -O as well")
