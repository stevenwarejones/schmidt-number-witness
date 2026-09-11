"""Targeted regressions for the continuation arithmetic and acceptance order.

Rejection counts only when the message carries the code for the defect introduced AND carries
no OTHER case's code.  That second half matters: this repository has already been bitten once by
a mutation suite that a checker could satisfy without examining its input -- there the defeat was
`raise SystemExit` prepended to the script, and the in-process analogue here is a
`check_arithmetic` that raises one AssertionError mentioning every code.  A plain `code in
str(exc)` test would accept that for all thirteen cases.  The two controls at the end are the
guard: the blanket raiser must NOT count as a valid rejection, and a mutation must not satisfy
some other case's code.
"""
import contextlib
import copy
import importlib.util
import io
import json
import subprocess
import shutil
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Run without -O: assertions are test gates.')
ROOT = Path(__file__).resolve().parent.parent
PROOFS = ROOT / 'proofs'
spec = importlib.util.spec_from_file_location('boundary', PROOFS / 'verify_penalty_boundary.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = json.loads((PROOFS / 'penalty_boundary_certificate.json').read_text())
base = (PROOFS / 'penalty_endpoint_certificate.json').read_bytes()
sharp = (PROOFS / 'sharp_qubit_certificate.json').read_bytes()
module.check_arithmetic(data, base, sharp)
print('PASS unmodified continuation arithmetic accepted')

ALL_CODES = {'[E-BOUNDARY-INPUT]', '[E-BOUNDARY-SHAPE]', '[E-BOUNDARY-SOLVE]',
             '[E-BOUNDARY-SCALE]', '[E-BOUNDARY-KERNEL]', '[E-BOUNDARY-PSD]',
             '[E-BOUNDARY-SIGN]', '[E-BOUNDARY-RANGE]', '[E-BOUNDARY-REMAINDER]',
             '[E-BOUNDARY-SIMPLE]', '[E-BOUNDARY-PROJECTOR]'}


# A rank-one subtraction along u = cross((v0,v1,v2), (z0,z1,z2)) on indices 0,1,2.  That u is
# orthogonal to BOTH v and z, so the perturbed Y still satisfies Yv = 0 AND Yz = a: every
# arithmetic identity in check_arithmetic survives, and the only thing it breaks is positivity,
# which an exact symmetric-pivot LDL confirms it genuinely destroys.  So this isolates the new
# structural guard -- nothing else in the file can catch it.
#
# An earlier version used u = (v1, -v0, 0, ...).  That is orthogonal to v but NOT to z, so it
# also broke Yz = a and would have been caught by [E-BOUNDARY-RANGE] had the guard been absent.
# It still exercised the guard, because the guard runs first, but the comment claiming it
# preserved every identity was false.
INJECTED = ('    Y[8][8] -= delta/16\n'
            '    _i, _j, _k = 0, 1, 2\n'
            '    _u = [Q(0)]*n\n'
            '    _u[_i] = v[_j]*z[_k] - v[_k]*z[_j]\n'
            '    _u[_j] = v[_k]*z[_i] - v[_i]*z[_k]\n'
            '    _u[_k] = v[_i]*z[_j] - v[_j]*z[_i]\n'
            '    for _p in range(n):\n'
            '        for _q in range(n):\n'
            '            Y[_p][_q] -= _u[_p]*_u[_q]\n')


def rejected_for(message, code):
    """True only if `message` names this defect and no other case's defect."""
    return code in message and not (ALL_CODES - {code}) & {c for c in ALL_CODES if c in message}


cases = [
    ('base_sha256', '0'*64, '[E-BOUNDARY-INPUT]'),
    ('delta', str(Q(data['delta'])+1), '[E-BOUNDARY-SCALE]'),
    ('alpha_boundary', '0', '[E-BOUNDARY-SCALE]'),
    ('r', str(-Q(data['r'])), '[E-BOUNDARY-SIGN]'),
    ('C', str(2*Q(data['C'])), '[E-BOUNDARY-REMAINDER]'),
    ('simple_PD_alpha', '0', '[E-BOUNDARY-SIMPLE]'),
]
for field, value, code in cases:
    changed = copy.deepcopy(data)
    changed[field] = value
    try:
        module.check_arithmetic(changed, base, sharp)
    except AssertionError as exc:
        assert rejected_for(str(exc), code), (field, 'wrong rejection reason', str(exc))
    else:
        raise AssertionError(f'{field}: corrupted data accepted')
    print('PASS targeted rejection', code, field)
for field, idx, code in [('v', 0, '[E-BOUNDARY-SOLVE]'),
                         ('z', 0, '[E-BOUNDARY-RANGE]')]:
    changed = copy.deepcopy(data)
    changed[field][idx] = str(Q(changed[field][idx])+1)
    try:
        module.check_arithmetic(changed, base, sharp)
    except AssertionError as exc:
        assert rejected_for(str(exc), code), (field, 'wrong rejection reason', str(exc))
    else:
        raise AssertionError(f'{field}: corrupted solve accepted')
    print('PASS targeted rejection', code, field)

# Both inherited dependencies must be reached before the new conclusion. This
# guard does not count the deliberate dependency failure as a certificate test.
original = module.runpy.run_path
for fail_at in (1, 2):
    seen = []
    def dependency(path, **kwargs):
        seen.append(Path(path).name)
        if len(seen) == fail_at:
            raise AssertionError('deliberate dependency refusal')
        return {}
    module.runpy.run_path = dependency
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            module.main()
    except AssertionError as exc:
        assert str(exc) == 'deliberate dependency refusal'
    else:
        raise AssertionError('main accepted after a failed dependency')
    finally:
        module.runpy.run_path = original
    assert seen == ['verify_penalty_endpoint.py', 'verify_equality_face.py'][:fail_at]
    assert module.SUCCESS not in output.getvalue()
    print('PASS failed dependency suppresses new conclusion', fail_at)
r = subprocess.run([sys.executable, '-O', str(PROOFS/'verify_penalty_boundary.py')],
                   capture_output=True, text=True)
assert r.returncode != 0 and 'Run without -O' in r.stderr+r.stdout
assert module.SUCCESS not in r.stdout+r.stderr
print('PASS optimized execution refused; all boundary mutation checks passed')

# The corank-one reduction needs Y to carry X exactly away from entry (8,8).  No edit to the
# certificate JSON can break that -- Y is derived from X inside the verifier, and touching X
# trips the input hash first -- so the guard is reachable only by a code change, and it is a
# code change that would silently invalidate the positivity argument while leaving every
# arithmetic identity intact.  Tested the same way as the path-lint case below.
with tempfile.TemporaryDirectory() as td:
    tree = Path(td)/'repo'
    shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns('.git', 'build', '__pycache__'))
    target = tree/'proofs/verify_penalty_boundary.py'
    text = target.read_text()
    assert '    Y[8][8] -= delta/16\n' in text
    target.write_text(text.replace('    Y[8][8] -= delta/16\n', INJECTED))
    hurt = importlib.util.spec_from_file_location('boundary_hurt', target)
    hurt_module = importlib.util.module_from_spec(hurt)
    hurt.loader.exec_module(hurt_module)
    try:
        hurt_module.check_arithmetic(data, base, sharp)
    except AssertionError as exc:
        assert rejected_for(str(exc), '[E-BOUNDARY-PSD]'), ('extra rank-one term', str(exc))
    else:
        raise AssertionError('an extra rank-one subtraction orthogonal to v was accepted')
    print('PASS targeted rejection [E-BOUNDARY-PSD] a rank-one term orthogonal to v and z: '
          'every arithmetic identity survives, only positivity dies')

# --- controls on this suite's own acceptance condition ---------------------------------------
# A checker that refuses everything with one message naming every code satisfies `code in
# message` for every case.  It must NOT satisfy the condition actually used above.
blanket = ' '.join(sorted(ALL_CODES))
assert not any(rejected_for(blanket, code) for code in ALL_CODES), (
    'CONTROL: a blanket refusal naming every diagnostic code was accepted as a valid rejection; '
    'the acceptance condition has degraded to substring matching')
print('PASS control: a refusal naming every code is NOT a valid rejection')

# And a genuine rejection must not satisfy some other case's code.
changed = copy.deepcopy(data)
changed['delta'] = str(Q(data['delta'])+1)
try:
    module.check_arithmetic(changed, base, sharp)
except AssertionError as exc:
    assert rejected_for(str(exc), '[E-BOUNDARY-SCALE]'), 'the delta mutation stopped being caught'
    assert not rejected_for(str(exc), '[E-BOUNDARY-SIGN]'), (
        'CONTROL: a scale mutation was accepted as a SIGN rejection; the suite is not '
        'distinguishing between diagnostic codes')
else:
    raise AssertionError('CONTROL: the delta mutation was accepted')
print('PASS control: a scale mutation does not satisfy the sign code')

# The runner must not swallow a failing verifier's diagnostics.  An earlier run_checks.py
# captured the boundary verifier's output and passed check=True, so subprocess.run raised
# BEFORE anything was written and the specific code vanished from what the reader was shown.
# Break the verifier, run the FULL runner, and require the code to survive into its output.
with tempfile.TemporaryDirectory() as td:
    tree = Path(td)/'repo'
    shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns('.git', 'build', '__pycache__'))
    target = tree/'proofs/verify_penalty_boundary.py'
    target.write_text(target.read_text().replace('    Y[8][8] -= delta/16\n', INJECTED))
    r = subprocess.run([sys.executable, str(tree/'run_checks.py')], capture_output=True, text=True)
    shown = (r.stdout or '') + (r.stderr or '')
    assert r.returncode != 0, 'run_checks accepted a broken boundary verifier'
    assert '[E-BOUNDARY-PSD]' in shown, (
        "run_checks hid the failing verifier's diagnostic: it must show the transcript before "
        'raising, not capture it into an exception nobody prints')
    assert 'PENALTY BOUNDARY VALID' not in shown, 'the runner printed a conclusion anyway'
    print("PASS run_checks shows a failing verifier's diagnostic instead of swallowing it")

# The path lint permits only the two source certificates consumed by this
# regeneration script, not arbitrary reads outside research/.
with tempfile.TemporaryDirectory() as td:
    tree = Path(td)/'repo'
    shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns('.git', 'build', '__pycache__'))
    generator = tree/'research/derive_penalty_boundary.py'
    text = generator.read_text()
    generator.write_text(text.replace("'sharp_qubit_certificate.json'", "'qutrit_certificate.json'"))
    r = subprocess.run([sys.executable, str(tree/'tests/test_research_paths.py')],
                       capture_output=True, text=True)
    assert r.returncode != 0 and '[E-OUTSIDE-BUILD]' in r.stdout+r.stderr
    assert 'ModuleNotFoundError' not in r.stdout+r.stderr
    print('PASS regeneration cannot read an unrelated proof certificate')
