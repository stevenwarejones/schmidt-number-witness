"""Corruption tests for the two prior-art comparisons: substantive edits must be rejected.

The comparisons in proofs/verify_i3322_family.py and research/audit_catalog_folds.py rest on
two pieces of archived data -- the qutrit behavior Q and the 129 catalogue coefficient vectors.
A comparison that would pass on corrupted data is not evidence of anything, so this file edits
each substantively and requires a nonzero exit.

The edits are not cosmetic.  One probability of Q is set to a value that breaks normalization;
one catalogue coefficient is shifted so that its source local bound is no longer zero.  Both
are the kind of error a bad transcription actually produces.

There is deliberately NO skip path here.  A missing dependency is a failure, not a pass: a
test that reports success because it could not run is exactly the defect this repository has
already shipped twice.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are checks.")

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails = []


def run(script, cwd, expect_ok, what):
    """Run a checker from an unrelated working directory and require the expected verdict."""
    r = subprocess.run([sys.executable, str(script)], cwd=cwd,
                       capture_output=True, text=True)
    ok = r.returncode == 0
    label = 'accept' if expect_ok else 'reject'
    if ok != expect_ok:
        tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ['(no output)']
        fails.append(f"{what}: expected to {label}, exit={r.returncode} -- {tail[0][:110]}")
        return
    print(f"  PASS {label}s as required: {what}")


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    # --- positive: both comparisons pass on the shipped data, from an unrelated cwd --------
    run(ROOT / 'proofs' / 'verify_i3322_family.py', td, True,
        'proofs/verify_i3322_family.py on the shipped Q')
    run(ROOT / 'research' / 'audit_catalog_folds.py', td, True,
        'research/audit_catalog_folds.py on the shipped catalogue')

    # --- negative: corrupt Q, and the family comparison must reject it ---------------------
    bad_q = tmp / 'repo_bad_q'
    (bad_q / 'proofs').mkdir(parents=True)
    shutil.copy(ROOT / 'proofs' / 'verify_i3322_family.py', bad_q / 'proofs')
    cert = json.loads((ROOT / 'proofs' / 'qutrit_certificate.json').read_text())
    cert['Q'][0] = '2'                                    # breaks normalization outright
    (bad_q / 'proofs' / 'qutrit_certificate.json').write_text(json.dumps(cert))
    run(bad_q / 'proofs' / 'verify_i3322_family.py', td, False,
        'verify_i3322_family.py on a Q with a corrupted probability')

    # --- negative: corrupt one catalogue vector, and the fold search must reject it --------
    bad_cat = tmp / 'repo_bad_catalog'
    (bad_cat / 'research' / 'inputs').mkdir(parents=True)
    shutil.copy(ROOT / 'research' / 'audit_catalog_folds.py', bad_cat / 'research')
    cat = json.loads((ROOT / 'research' / 'inputs' / 'catalog_coefficients.json').read_text())
    cat['1'][0] += 100                                    # source local bound is no longer 0
    (bad_cat / 'research' / 'inputs' / 'catalog_coefficients.json').write_text(json.dumps(cat))
    run(bad_cat / 'research' / 'audit_catalog_folds.py', td, False,
        'audit_catalog_folds.py on a catalogue with a corrupted coefficient')

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS both comparisons accept the shipped data and reject substantively corrupted data")
