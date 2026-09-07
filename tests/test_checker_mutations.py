"""The auxiliary checkers must reject the specific defects they were written for.

Every mutation below is a defect one of these checkers ONCE ACCEPTED.  They were previously
run as external acceptance sweeps and reported in commit messages, which is not a regression
test: nothing in the repository re-ran them, so a later edit could silently reopen any of
them.  They live here now.

Each case states what it preserves as well as what it breaks.  A mutation that merely makes
the functional wrong would not isolate the missing condition -- for instance the invalid-point
case keeps F = 7, keeps locality on the designated restriction, and keeps the affine rank, so
only a global positivity check can catch it.

Rejection is required to happen for the INTENDED reason: a missing dependency, a syntax error
or an unrelated crash is recorded as a failure, not as a pass.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are checks.")

import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails = []
SETUP_NOISE = ('ModuleNotFoundError', 'FileNotFoundError', 'SyntaxError', 'ImportError')


def copy_repo(dest):
    for rel in ('proofs', 'research', 'tests'):
        shutil.copytree(ROOT / rel, dest / rel,
                        ignore=shutil.ignore_patterns('__pycache__'))
    return dest


def expect_reject(script, cwd, what, forbid_file=None):
    r = subprocess.run([sys.executable, str(script)], cwd=cwd, capture_output=True, text=True)
    if r.returncode == 0:
        fails.append(f"{what}: ACCEPTED (exit 0) -- the defect is back")
        return
    noise = [n for n in SETUP_NOISE if n in r.stderr]
    if noise:
        fails.append(f"{what}: exited nonzero but for the wrong reason ({noise[0]})")
        return
    if forbid_file is not None and forbid_file.exists():
        fails.append(f"{what}: rejected, but the checker itself wrote {forbid_file}")
        return
    print(f"  PASS rejected for the intended reason: {what}")


def expect_accept(script, cwd, what):
    r = subprocess.run([sys.executable, str(script)], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ['(no output)']
        fails.append(f"{what}: the unmodified tree was REJECTED -- {tail[0][:110]}")
    else:
        print(f"  PASS accepted: {what}")


PATH_CHECK = 'tests/test_research_paths.py'
FACET_CHECK = 'tests/verify_facet_independent.py'

with tempfile.TemporaryDirectory() as td:
    base = copy_repo(Path(td) / 'base')
    expect_accept(base / PATH_CHECK, td, 'unmodified tree, path checker')
    expect_accept(base / FACET_CHECK, td, 'unmodified tree, independent facet checker')

    # --- path checker: five escapes it has accepted at one time or another ----------------
    ESCAPES = [
        ("literal traversal out of build/",
         "\ndef probe():\n    (OUTPUT_DIR / '..' / 'escaped.txt').write_text('x')\n"),
        ("unknown directory component then traversal",
         "\ndef probe(dynamic):\n    (OUTPUT_DIR / dynamic / '..' / '..' / 'e.txt').write_text('x')\n"),
        ("traversal hidden inside an f-string filename",
         "\ndef probe(name):\n    (OUTPUT_DIR / f'../../{name}').write_text('x')\n"),
        ("Path.open, which was not recognised as a filesystem access",
         "\ndef probe():\n    with (OUTPUT_DIR.parent / 'escaped.txt').open('w') as f:\n        f.write('x')\n"),
        ("write outside build/ with a '# OUTPUT_DIR' comment on the line",
         "\ndef probe():\n    (RESEARCH_DIR / 'escaped.txt').write_text('x')  # OUTPUT_DIR\n"),
    ]
    for n, (what, snippet) in enumerate(ESCAPES):
        d = copy_repo(Path(td) / f'esc{n}')
        with (d / 'research' / 'face_sdp.py').open('a') as fh:
            fh.write(snippet)
        expect_reject(d / PATH_CHECK, td, f"path checker: {what}")

    # An assignment whose right-hand side calls write_text must not make the CHECKER write.
    d = copy_repo(Path(td) / 'sideeffect')
    (d / 'build').mkdir(exist_ok=True)
    probe = d / 'build' / 'assigned_probe.txt'
    with (d / 'research' / 'quantum_upper.py').open('a') as fh:
        fh.write("\nprobe = (OUTPUT_DIR / 'assigned_probe.txt').write_text('side effect')\n")
    r = subprocess.run([sys.executable, str(d / PATH_CHECK)], cwd=td,
                       capture_output=True, text=True)
    if probe.exists():
        fails.append("path checker performed the write in an assignment right-hand side")
    else:
        print("  PASS no write side effect from analysing an assignment")

    # --- independent facet checker: a point that is not a behavior at all -----------------
    # Preserves F = 7, the designated-pair locality and the affine rank; breaks global
    # positivity on a setting the designated restriction never looks at.
    d = copy_repo(Path(td) / 'badpoint')
    cert_path = d / 'proofs' / 'facet_certificate.json'
    cert = json.loads(cert_path.read_text())
    e = cert['saturating_points'][0]
    w = cert['w']
    v = [Fr(t) for t in e['v']]
    unused = next(i for i in range(3) if i not in e['pair'])
    slots = ([6 + 3 * unused + j for j in range(2)] if e['side'] == 'A'
             else [6 + 3 * i + unused for i in range(2)])
    v[slots[0]] += 100
    v[slots[1]] -= Fr(100 * w[slots[0]], w[slots[1]])
    assert sum(Fr(a) * b for a, b in zip(w, v)) == 7, 'setup: no longer on F = 7'
    worst = min((1 + (-1) ** a * v[x] + (-1) ** b * v[3 + y] + (-1) ** (a + b) * v[6 + 3 * x + y]) / 4
                for x, y, a, b in product(range(3), range(3), range(2), range(2)))
    assert worst < 0, 'setup: the point is still a valid behavior'
    e['v'] = [str(t) for t in v]
    cert_path.write_text(json.dumps(cert))
    expect_reject(d / FACET_CHECK, td,
                  'independent facet checker: point with F = 7 but a negative probability '
                  'outside the designated restriction')
    expect_reject(d / 'proofs' / 'verify_facet.py', td,
                  'primary facet verifier: the same invalid point')

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS every checker rejects the defect it was written for, for the intended reason")
