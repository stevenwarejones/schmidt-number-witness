"""The equality-face checker must reject corrupted certificates for the RIGHT reason.

Same acceptance condition as tests/test_checker_mutations.py and
tests/test_endpoint_mutations.py: rejection counts only when the specific diagnostic code for
the defect introduced actually appears.  The two controls at the end guard the suite itself --
the refuse-everything sentinel that defeated an earlier suite in this repository must NOT count
as a valid rejection, and a mutation must not satisfy the wrong code.

The cases are chosen so that each isolates one part of the argument.  Two are worth calling out:

  * Deleting a single forced zero from ONE pattern leaves every remaining dual valid and every
    other pattern untouched.  The certificate still checks out arithmetically; what breaks is
    that the projector closure can no longer resolve that pattern.  Only the closure catches it,
    and it must catch it by returning `unresolved` rather than by quietly reporting `local`.
  * Weakening one forced-zero dual so that it certifies the event to 0 instead of -1 keeps the
    dual IDENTITY exact -- it is still a valid bound, just a useless one, since it no longer
    forces the probability to vanish.  Only the `== -1` test sees it.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit('Run without -O: assertions in this file are checks.')

import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails = []
SETUP_NOISE = ('ModuleNotFoundError', 'FileNotFoundError', 'SyntaxError', 'ImportError')
SUCCESS_LINES = ('EQUALITY FACE VALID', 'PASS the equality face re-derived independently')

FACE = 'proofs/verify_equality_face.py'
CERT = 'proofs/equality_face_certificate.json'


def copy_repo(dest):
    for rel in ('proofs', 'tests'):
        shutil.copytree(ROOT / rel, dest / rel, ignore=shutil.ignore_patterns('__pycache__'))
    return dest


def load(tree):
    return json.loads((tree / CERT).read_text())


def save(tree, obj):
    (tree / CERT).write_text(json.dumps(obj, indent=1))


def rejection_problem(tree, script, code):
    r = subprocess.run([sys.executable, str(tree / script)], cwd=str(tree),
                       capture_output=True, text=True)
    out = (r.stdout or '') + (r.stderr or '')
    if r.returncode == 0:
        return 'ACCEPTED (exit 0) -- the defect is back'
    noise = [n for n in SETUP_NOISE if n in (r.stderr or '')]
    if noise:
        return f'exited nonzero but for an unrelated reason ({noise[0]})'
    if code not in out:
        first = next((ln for ln in out.splitlines() if ln.strip()), '(no output)')
        return (f'rejected, but NOT for the intended reason: expected {code} and did not find '
                f'it; first output line was {first.strip()[:90]!r}')
    if any(line in out for line in SUCCESS_LINES):
        return 'rejected, yet still printed an affirmative conclusion'
    return None


def expect_reject(what, code, mutate, script=FACE):
    with tempfile.TemporaryDirectory() as td:
        tree = copy_repo(Path(td))
        mutate(tree)
        problem = rejection_problem(tree, script, code)
    if problem:
        fails.append(f'{what}: {problem}')
    else:
        print(f'  PASS rejected with {code}: {what}', flush=True)


def expect_accept(what, script=FACE):
    with tempfile.TemporaryDirectory() as td:
        tree = copy_repo(Path(td))
        r = subprocess.run([sys.executable, str(tree / script)], cwd=str(tree),
                           capture_output=True, text=True)
    if r.returncode != 0:
        tail = ((r.stderr or r.stdout).strip().splitlines() or ['(no output)'])[-1]
        fails.append(f'{what}: the unmodified tree was REJECTED -- {tail[:110]}')
    else:
        print(f'  PASS accepted: {what}', flush=True)


def first_zero_pattern(c):
    return next(i for i, pat in enumerate(c['patterns']) if 'bound' not in pat)


def first_bound_pattern(c):
    return next(i for i, pat in enumerate(c['patterns']) if 'bound' in pat)


expect_accept('unmodified equality-face certificate')


# --- coverage ------------------------------------------------------------------------------
def drop_a_pattern(tree):
    c = load(tree)
    del c['patterns'][first_zero_pattern(c)]
    save(tree, c)


def duplicate_a_pattern(tree):
    c = load(tree)
    c['patterns'].append(json.loads(json.dumps(c['patterns'][0])))
    save(tree, c)


def relabel_a_pattern(tree):
    """Point a pattern at a deterministic observable index outside 0..5."""
    c = load(tree)
    i = first_bound_pattern(c)
    det = c['patterns'][i]['det']
    key = next(iter(det))
    det['9'] = det.pop(key)
    save(tree, c)


expect_reject('one of the 48 deterministic-observable patterns removed, leaving a gap in the '
              'case analysis', '[E-FACE-COVERAGE]', drop_a_pattern)
expect_reject('a pattern listed twice, which would let 48 entries cover only 47 cases',
              '[E-FACE-COVERAGE]', duplicate_a_pattern)
expect_reject('a pattern pointing at an observable index that does not exist',
              '[E-FACE-COVERAGE]', relabel_a_pattern)


# --- the duals -----------------------------------------------------------------------------
def bump_bound_multiplier(tree):
    c = load(tree)
    b = c['patterns'][first_bound_pattern(c)]['bound']
    b['t'][0] = str(Fr(b['t'][0]) + 1)
    save(tree, c)


def negate_bound_multiplier(tree):
    c = load(tree)
    b = c['patterns'][first_bound_pattern(c)]['bound']
    k = next(i for i, x in enumerate(b['t']) if Fr(x) > 0)
    b['t'][k] = str(-Fr(b['t'][k]))
    save(tree, c)


def overstate_bound(tree):
    """Keep the dual exact but let it certify only max F <= 7, which excludes nothing."""
    c = load(tree)
    b = c['patterns'][first_bound_pattern(c)]['bound']
    b['nu'] = [str(Fr(b['nu'][0]) + Fr(7 - Fr(b['upper']), 1))]
    b['upper'] = '7'
    save(tree, c)


def bump_zero_multiplier(tree):
    c = load(tree)
    pat = c['patterns'][first_zero_pattern(c)]
    pat['certs'][0]['t'][0] = str(Fr(pat['certs'][0]['t'][0]) + 1)
    save(tree, c)


def weaken_a_zero(tree):
    """A still-EXACT dual that bounds the event by 0 rather than -1: valid, but useless."""
    c = load(tree)
    pat = c['patterns'][first_zero_pattern(c)]
    proof = pat['certs'][0]
    proof['nu'][0] = str(Fr(proof['nu'][0]) + Fr(1, 7))     # nu[0] multiplies the F = 7 equality
    proof['upper'] = str(Fr(proof['upper']) + 1)
    save(tree, c)


expect_reject('a multiplier bumped in a no-signaling dual, breaking the identity it certifies',
              '[E-FACE-DUAL]', bump_bound_multiplier)
expect_reject('a negative multiplier on a positivity constraint, which reverses its direction',
              '[E-FACE-DUAL]', negate_bound_multiplier)
expect_reject('a no-signaling dual weakened to max F <= 7, which excludes nothing',
              '[E-FACE-DUAL]', overstate_bound)
expect_reject('a multiplier bumped in a forced-zero dual', '[E-FACE-ZERO]', bump_zero_multiplier)
expect_reject('a forced-zero dual weakened to bound the event by 0 instead of -1: still exact, '
              'still valid, no longer forces the probability to vanish',
              '[E-FACE-ZERO]', weaken_a_zero)


# --- the closure ----------------------------------------------------------------------------
def delete_a_forced_zero(tree):
    """Every remaining dual stays exact; only the closure can notice the missing edge."""
    c = load(tree)
    for pat in c['patterns']:
        if 'bound' in pat:
            continue
        trimmed_z, trimmed_c = pat['zeros'][:], pat['certs'][:]
        for k in range(len(trimmed_z)):
            probe = json.loads(json.dumps(c))
            idx = c['patterns'].index(pat)
            probe['patterns'][idx]['zeros'] = trimmed_z[:k] + trimmed_z[k + 1:]
            probe['patterns'][idx]['certs'] = trimmed_c[:k] + trimmed_c[k + 1:]
            save(tree, probe)
            r = subprocess.run([sys.executable, str(tree / FACE)], cwd=str(tree),
                               capture_output=True, text=True)
            if '[E-FACE-UNRESOLVED]' in (r.stdout or '') + (r.stderr or ''):
                return
    raise AssertionError('no single forced zero is load-bearing for the closure; this mutation '
                         'cannot test it')


expect_reject('one forced zero deleted: every remaining dual is still exact, and only the '
              'projector closure can see that the pattern no longer resolves',
              '[E-FACE-UNRESOLVED]', delete_a_forced_zero)


# --- the face and the family -----------------------------------------------------------------
def change_the_functional(tree):
    c = load(tree)
    c['coefficients'] = [-x for x in c['coefficients']]
    save(tree, c)


expect_reject('the functional negated, so the five saturating vertices are no longer the '
              'saturators of the certified inequality', '[E-FACE-DUAL]', change_the_functional)


# --- controls ---------------------------------------------------------------------------------
def sentinel(tree):
    p = tree / FACE
    p.write_text("raise SystemExit('sentinel: refuses everything')\n" + p.read_text())


with tempfile.TemporaryDirectory() as td:
    tree = copy_repo(Path(td))
    sentinel(tree)
    verdict = rejection_problem(tree, FACE, '[E-FACE-COVERAGE]')
    if verdict is None:
        fails.append('CONTROL: a checker that refuses everything before reading its input was '
                     'accepted as "rejected for the intended reason" -- the reason-checking has '
                     'regressed to exit-code checking')
    else:
        print(f'  PASS control: the refuse-everything sentinel is NOT counted as a valid '
              f'rejection ({verdict[:60]}...)', flush=True)

with tempfile.TemporaryDirectory() as td:
    tree = copy_repo(Path(td))
    drop_a_pattern(tree)
    verdict = rejection_problem(tree, FACE, '[E-FACE-ZERO]')
    if verdict is None:
        fails.append('CONTROL: a missing pattern was accepted as a forced-zero rejection -- the '
                     'suite is not distinguishing between diagnostic codes')
    else:
        print('  PASS control: a missing pattern does not satisfy the forced-zero code',
              flush=True)

if fails:
    print('\nFAILED:')
    for f in fails:
        print('   ' + f)
    raise SystemExit(1)
print('\nPASS every equality-face mutation is rejected, and for the intended mathematical reason')
