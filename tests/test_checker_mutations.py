"""The auxiliary checkers must reject the specific defects they were written for.

Every mutation below is a defect one of these checkers ONCE ACCEPTED.  They were previously
run as external acceptance sweeps and reported in commit messages, which is not a regression
test: nothing in the repository re-ran them, so a later edit could silently reopen any of
them.  They live here now.

Each case states what it preserves as well as what it breaks.  A mutation that merely makes
the functional wrong would not isolate the missing condition -- for instance the invalid-point
case keeps F = 7, keeps locality on the designated restriction, and keeps the affine rank, so
only a global positivity check can catch it.

Rejection is required to happen for the INTENDED reason, and "intended reason" means a
SPECIFIC stable diagnostic code emitted by the check that is supposed to fire -- not merely a
nonzero exit.  An earlier version only excluded four exception names, which a review defeated
by prepending an unrelated `raise SystemExit` to the checker: every mutation was then rejected
before its path was ever analysed, and the suite still reported each as rejected for the
intended reason.

The last case below is the control for exactly that.  It reproduces the reviewer's sentinel and
requires this suite's own acceptance condition to REJECT it.  If the control ever stops firing,
the reason-checking has regressed to exit-code checking.
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


SUCCESS_LINES = ('PASS every discovery read and write resolves',
                 'PASS independent reconstruction agrees',
                 'CONCLUSION: F <= 7 IS A FACET')


def rejection_problem(script, cwd, code):
    """None if the script rejected with diagnostic `code`, else why that verdict fails."""
    r = subprocess.run([sys.executable, str(script)], cwd=cwd, capture_output=True, text=True)
    out = (r.stdout or '') + (r.stderr or '')
    if r.returncode == 0:
        return 'ACCEPTED (exit 0) -- the defect is back'
    noise = [n for n in SETUP_NOISE if n in r.stderr]
    if noise:
        return f'exited nonzero but for an unrelated reason ({noise[0]})'
    if code not in out:
        first = next((ln for ln in out.splitlines() if ln.strip()), '(no output)')
        return (f'rejected, but NOT for the intended reason: expected the diagnostic {code} '
                f'and did not find it; first output line was {first.strip()[:90]!r}')
    if any(line in out for line in SUCCESS_LINES):
        return 'rejected, yet still printed an affirmative conclusion'
    return None


def expect_reject(script, cwd, what, code):
    problem = rejection_problem(script, cwd, code)
    if problem:
        fails.append(f"{what}: {problem}")
    else:
        print(f"  PASS rejected with {code}: {what}")


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
        ("literal traversal out of build/", '[E-TRAVERSAL]',
         "\ndef probe():\n    (OUTPUT_DIR / '..' / 'escaped.txt').write_text('x')\n"),
        ("an unbound name used as a path component", '[E-UNBOUND-NAME]',
         "\ndef probe(dynamic):\n    (OUTPUT_DIR / dynamic / '..' / '..' / 'e.txt').write_text('x')\n"),
        ("a proven-safe filename used as a DIRECTORY, then joined again", '[E-UNKNOWN-DIR]',
         "\nlvl = int('3')\ndef probe():\n    (OUTPUT_DIR / f'{lvl}' / 'e.txt').write_text('x')\n"),
        ("traversal hidden inside an f-string filename", '[E-TRAVERSAL]',
         "\ndef probe(name):\n    (OUTPUT_DIR / f'../../{name}').write_text('x')\n"),
        ("Path.open, which was not recognised as a filesystem access", '[E-OUTSIDE-BUILD]',
         "\ndef probe():\n    with (OUTPUT_DIR.parent / 'escaped.txt').open('w') as f:\n        f.write('x')\n"),
        ("write outside build/ with a '# OUTPUT_DIR' comment on the line", '[E-OUTSIDE-BUILD]',
         "\ndef probe():\n    (RESEARCH_DIR / 'escaped.txt').write_text('x')  # OUTPUT_DIR\n"),
        ("an 'integer' name reassigned to an escaping string", '[E-DYNAMIC-NAME]',
         "\nlevel = 3\nlevel = '../../escaped'\ndef probe():\n    (OUTPUT_DIR / f'{level}').write_text('x')\n"),
        ("an 'integer' name shadowed by a function parameter", '[E-DYNAMIC-NAME]',
         "\nlevel = 3\ndef probe(level):\n    (OUTPUT_DIR / f'{level}').write_text('x')\n"),
        ("an 'integer' name rebound by an ANNOTATED assignment", '[E-DYNAMIC-NAME]',
         "\nlevel = 3\nlevel: str = '../../escaped'\ndef probe():\n    (OUTPUT_DIR / f'{level}').write_text('x')\n"),
        ("an 'integer' name rebound inside a module-level conditional", '[E-DYNAMIC-NAME]',
         "\nlevel = 3\nif True:\n    level = '../../escaped'\ndef probe():\n    (OUTPUT_DIR / f'{level}').write_text('x')\n"),
        ("an 'integer' name bound by a loop variable", '[E-DYNAMIC-NAME]',
         "\nfor level in ['../../escaped']:\n    pass\ndef probe():\n    (OUTPUT_DIR / f'{level}').write_text('x')\n"),
        ("OUTPUT_DIR itself shadowed by a function parameter", '[E-UNBOUND-NAME]',
         "\ndef probe(OUTPUT_DIR):\n    (OUTPUT_DIR / 'escaped.txt').write_text('x')\n"),
    ]
    for n, (what, code, snippet) in enumerate(ESCAPES):
        d = copy_repo(Path(td) / f'esc{n}')
        with (d / 'research' / 'face_sdp.py').open('a') as fh:
            fh.write(snippet)
        expect_reject(d / PATH_CHECK, td, f"path checker: {what}", code)

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
                  'outside the designated restriction', '[E-NEGATIVE-PROB]')
    expect_reject(d / 'proofs' / 'verify_facet.py', td,
                  'primary facet verifier: the same invalid point', '[E-NEGATIVE-PROB]')

    # --- CONTROL 2: the same idea aimed at the primary verifier ---------------------------
    # A reviewer defeated the previous version of this case by making verify_facet.py assert
    # on its own DIRECTORY NAME: it rejected before reaching any certificate condition, and
    # 'AssertionError' -- all the case then required -- was still in the output.  Requiring
    # the specific code closes that, and this control keeps it closed.
    sentinel_facet = copy_repo(Path(td) / 'facetsentinel')
    fv = sentinel_facet / 'proofs' / 'verify_facet.py'
    fv.write_text("from pathlib import Path as _AuditPath\n"
                  "assert 'facetsentinel' not in str(_AuditPath(__file__)), "
                  "'UNRELATED DIRECTORY SENTINEL'\n" + fv.read_text())
    problem = rejection_problem(fv, td, '[E-NEGATIVE-PROB]')
    if problem is None:
        fails.append("CONTROL FAILED: verify_facet.py rejecting on its own directory name was "
                     "accepted as the intended reason")
    else:
        print(f"  PASS control: an unrelated AssertionError is not the intended reason "
              f"({problem[:52]}...)")

    # --- CONTROL: an unrelated early rejection must NOT count as the intended reason ------
    # Exactly the reviewer's sentinel.  The path checker is made to bail out before it
    # analyses anything, so every mutation "fails" for a reason that has nothing to do with
    # paths.  This suite's own acceptance condition must catch that.
    d = copy_repo(Path(td) / 'sentinel')
    check = d / PATH_CHECK
    check.write_text(
        "from pathlib import Path as _Path\n"
        "if any('def probe(' in f.read_text()\n"
        "       for f in (_Path(__file__).resolve().parent.parent / 'research').glob('*.py')):\n"
        "    raise SystemExit('UNRELATED SENTINEL REJECTION')\n" + check.read_text())
    with (d / 'research' / 'face_sdp.py').open('a') as fh:
        fh.write("\ndef probe():\n    (OUTPUT_DIR / '..' / 'escaped.txt').write_text('x')\n")
    problem = rejection_problem(check, td, '[E-TRAVERSAL]')
    if problem is None:
        fails.append("CONTROL FAILED: an unrelated early rejection was accepted as the "
                     "intended reason -- this suite is back to checking exit codes only")
    else:
        print(f"  PASS control: an unrelated rejection is not mistaken for the intended one "
              f"({problem[:58]}...)")

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS every checker rejects the defect it was written for, for the intended reason")
