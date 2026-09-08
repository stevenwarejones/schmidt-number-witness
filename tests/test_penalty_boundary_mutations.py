"""Targeted regressions for the continuation arithmetic and acceptance order."""
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
        assert code in str(exc), (field, 'wrong rejection reason', str(exc))
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
        assert code in str(exc), (field, 'wrong rejection reason', str(exc))
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
