"""Fail-fast runner for the active exact certificate chain.

Run from anywhere:  python run_checks.py
Paths resolve against this file, not the caller's working directory."""
import sys, subprocess, json
from fractions import Fraction
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Run without -O: certificate checks use assertions.')

ROOT = Path(__file__).resolve().parent
PROOFS = ROOT / 'proofs'


def run(path, *args):
    subprocess.run([sys.executable, str(path), *args], check=True)


# --- active proof chain -------------------------------------------------------
run(PROOFS / 'verify_facet.py')
run(PROOFS / 'verify_face_dimensions.py')
# Bounds our own claim rather than supporting it: the valid inequality F <= 7 on H is a
# corollary of eq. (48) of arXiv:1902.05841 plus positivity.  See docs/PRIOR_ART.md.
run(PROOFS / 'verify_m3322_corollary.py')
# The affirmative counterweight: what F detects that the standard score thresholds do not.
run(PROOFS / 'verify_novelty_comparison.py')
# And the same for the published one-parameter family, over its whole parameter range.
run(PROOFS / 'verify_i3322_family.py')
run(PROOFS / 'verify_qutrit.py')
run(PROOFS / 'verify_sharp_qubit.py')
run(PROOFS / 'verify_quantum_upper.py')

q = json.loads((PROOFS / 'qutrit_certificate.json').read_text())
s = json.loads((PROOFS / 'sharp_qubit_certificate.json').read_text())
u = json.loads((PROOFS / 'quantum_upper_certificate.json').read_text())
facet = json.loads((PROOFS / 'facet_certificate.json').read_text())

if not q['coefficients'] == s['coefficients'] == u['coefficients'] == facet['w']:
    raise SystemExit('Bell coefficients mismatch across certificates')
if not Fraction(q['score']) > Fraction(s['bound']):
    raise SystemExit('Sharp quantum separation FAILED')
weight = (Fraction(q['score']) - 7) / (Fraction(u['bound']) - 7)
if not weight > Fraction(3119, 10000):
    raise SystemExit('Weight bound FAILED')

print('All exact checks passed: sharp bound 7, qutrit separation, and quantum remainder weight >31.19%.')
print('Global quantum maximum, tight decomposition cost, novelty, and external review remain open.')
