"""Fail-fast runner for the active exact certificate chain.

Run from anywhere:  python run_checks.py
Paths resolve against this file, not the caller's working directory."""
import sys, subprocess, json, os
from fractions import Fraction
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Run without -O: certificate checks use assertions.')

ROOT = Path(__file__).resolve().parent
PROOFS = ROOT / 'proofs'


def run(path, *args):
    subprocess.run([sys.executable, str(path), *args], check=True)


def run_subsuming(path, *required):
    """Run a verifier that re-executes others, and PROVE it really reached them.

    proofs/verify_penalty_boundary.py deliberately re-runs the endpoint and equality-face
    verifiers before printing its own conclusion, with no skip flag, so that the standalone
    entry point cannot announce a result its dependencies never licensed.  Listing those two
    separately here as well would re-do about 35 seconds of exact arithmetic -- with
    verify_sharp_qubit.py running three times per chain, since the endpoint verifier runs it too.

    So they are not listed separately.  Instead their conclusions are REQUIRED to appear in this
    transcript, which is a stronger statement than running them and trusting that it happened.
    If this call is ever removed, restore the two run(...) lines it replaces:
        run(PROOFS / 'verify_penalty_endpoint.py')
        run(PROOFS / 'verify_equality_face.py')

    The child's stdout is STREAMED as it arrives rather than captured and replayed at the end.
    Capturing it and passing check=True would raise before anything was written, so a failing
    verifier's diagnostic code -- the one thing a reader needs -- would vanish from the displayed
    failure; tests/test_penalty_boundary_mutations.py regression-tests exactly that.  Streaming
    also keeps a long exact-arithmetic run from looking like a hang.  stderr is inherited, so
    assertion tracebacks appear as they happen.
    """
    env = dict(os.environ, PYTHONUNBUFFERED='1')
    proc = subprocess.Popen([sys.executable, str(path)], stdout=subprocess.PIPE,
                            text=True, bufsize=1, env=env)
    transcript = []
    with proc.stdout:
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            transcript.append(line)
    proc.wait()
    # Same failure mode as run(): CalledProcessError, but only after the transcript is visible.
    subprocess.CompletedProcess(proc.args, proc.returncode, ''.join(transcript), None
                                ).check_returncode()
    text = ''.join(transcript)
    for line in required:
        if line not in text:
            raise SystemExit(f'{path.name} did not reach: {line}')


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
run(PROOFS / 'verify_gigena_complete.py')
run(PROOFS / 'verify_convex_geometry.py')
run(PROOFS / 'verify_qutrit.py')
run(PROOFS / 'verify_sharp_qubit.py')
run(PROOFS / 'verify_quantum_upper.py')
# The penalised functional G = F + eps0 * p strengthens the sharp Schmidt-number-two bound and
# NOTHING else.  verify_penalty_not_partial_local.py is the guard on that scope: it proves,
# from the facet certificate checked above, that G is not valid on H, so the facet result
# cannot be carried over to it.  See docs/CERTIFICATE_PENALTY_ENDPOINT.md.
# The draft continuation subsumes two verifiers: it re-runs the endpoint verifier and the
# equality-face verifier (the equality set of the sharp bound, and -- via the endpoint
# certificate -- of the whole certified family, reviewed in
# docs/review_2026-09-07_equality_face.md before integration) before printing anything of its
# own.  Both conclusions are required to appear, so nothing is lost by not running them twice.
run_subsuming(PROOFS / 'verify_penalty_boundary.py',
              'ENDPOINT CERTIFICATE VALID',
              'EQUALITY FACE VALID',
              'PENALTY BOUNDARY VALID')
run(PROOFS / 'verify_improved_qutrit.py')
run(PROOFS / 'verify_penalty_not_partial_local.py')

q = json.loads((PROOFS / 'qutrit_certificate.json').read_text())
s = json.loads((PROOFS / 'sharp_qubit_certificate.json').read_text())
u = json.loads((PROOFS / 'quantum_upper_certificate.json').read_text())
facet = json.loads((PROOFS / 'facet_certificate.json').read_text())
endpoint = json.loads((PROOFS / 'penalty_endpoint_certificate.json').read_text())
face = json.loads((PROOFS / 'equality_face_certificate.json').read_text())

if not (q['coefficients'] == s['coefficients'] == u['coefficients'] == facet['w']
        == endpoint['coefficients'] == face['coefficients']):
    raise SystemExit('Bell coefficients mismatch across certificates')
if not Fraction(endpoint['epsilon']) + Fraction(endpoint['alpha']) == 4:
    raise SystemExit('Endpoint epsilon and alpha are not complementary')
if not Fraction(q['score']) > Fraction(s['bound']):
    raise SystemExit('Sharp quantum separation FAILED')
weight = (Fraction(q['score']) - 7) / (Fraction(u['bound']) - 7)
if not weight > Fraction(3119, 10000):
    raise SystemExit('Weight bound FAILED')

print('All exact checks passed: sharp bound 7, qutrit separation, and quantum remainder weight >31.19%.')
print(f"Penalty endpoint: M_A <= 6 + {endpoint['alpha']} p on Schmidt number two, against a lower "
      f"strategy at 0.16310160 -- and NOT valid on the partial-local hull H.")
print('Equality face: F = 7 is attained on Schmidt number two only inside a four-simplex of '
      'local behaviours, and the same face serves the whole certified family.')
print('Boundary continuation: the singular certificate proves alpha_star <= 0.1631067188466586..., '
      'hence the quotable 0.16310672. New prose arguments await separate review.')
print('Global quantum maximum, tight decomposition cost, the exact optimal penalty alpha_star, '
      'the equality face AT that critical penalty, novelty, and external review remain open.')
