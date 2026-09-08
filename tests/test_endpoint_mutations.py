"""The endpoint checkers must reject corrupted certificates for the RIGHT reason.

A verifier that exits nonzero on a corrupted input has not been shown to work: it
may be failing for an unrelated reason, or failing on everything.  Every case below
therefore states which specific diagnostic code the check is supposed to emit, and
the verdict is rejected unless that exact code appears.  This is the same acceptance
condition as tests/test_checker_mutations.py, and it exists for the same reason: an
earlier suite in this repository was defeated by prepending an unrelated
`raise SystemExit` to a checker, after which every mutation was "rejected" before
its input was ever examined.  The final case below reproduces that sentinel and
requires THIS suite to refuse it.

Each mutation is chosen so that only the intended check can catch it.  The most
pointed one is the positive-definiteness case: the perturbation

    X[0][1] += L,  X[1][0] += L,  X[1][1] += 2L,  X[1][5] += L,  X[5][1] += L

lies in the kernel of  X  |->  sum_{j,k} X[j,k] J_j^dagger J_k, so the exact
operator identity is completely untouched -- reconstruction still yields a zero
residual -- and the certificate is destroyed only because the Gram stops being
positive definite.  A verifier that reconstructed the identity and skipped the
positivity test would accept it.  Conversely the off-diagonal case perturbs the
Gram by 10^-12, far too little to disturb a least pivot of 1.4 * 10^-7, so only the
identity can notice it.
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
SUCCESS_LINES = ('ENDPOINT CERTIFICATE VALID',
                 'IMPROVED QUTRIT VALID',
                 'PASS independent reconstruction agrees',
                 'CONCLUSION: G <= 7 is FALSE')

ENDPOINT = 'proofs/verify_penalty_endpoint.py'
QUTRIT = 'proofs/verify_improved_qutrit.py'
HULL = 'proofs/verify_penalty_not_partial_local.py'
INDEP = 'tests/verify_endpoint_independent.py'


def copy_repo(dest):
    for rel in ('proofs', 'tests'):
        shutil.copytree(ROOT / rel, dest / rel, ignore=shutil.ignore_patterns('__pycache__'))
    return dest


def load(tree, rel):
    return json.loads((tree / rel).read_text())


def save(tree, rel, obj):
    (tree / rel).write_text(json.dumps(obj, indent=1))


def rejection_problem(tree, script, code):
    """None if the script rejected with diagnostic `code`, else why that verdict fails."""
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
        return (f'rejected, but NOT for the intended reason: expected {code} and did not '
                f'find it; first output line was {first.strip()[:90]!r}')
    if any(line in out for line in SUCCESS_LINES):
        return 'rejected, yet still printed an affirmative conclusion'
    return None


def expect_reject(what, script, code, mutate):
    with tempfile.TemporaryDirectory() as td:
        tree = copy_repo(Path(td))
        mutate(tree)
        problem = rejection_problem(tree, script, code)
    if problem:
        fails.append(f'{what}: {problem}')
    else:
        print(f'  PASS rejected with {code}: {what}', flush=True)


def expect_accept(what, script):
    with tempfile.TemporaryDirectory() as td:
        tree = copy_repo(Path(td))
        r = subprocess.run([sys.executable, str(tree / script)], cwd=str(tree),
                           capture_output=True, text=True)
    if r.returncode != 0:
        tail = ((r.stderr or r.stdout).strip().splitlines() or ['(no output)'])[-1]
        fails.append(f'{what}: the unmodified tree was REJECTED -- {tail[:110]}')
    else:
        print(f'  PASS accepted: {what}', flush=True)


EP = 'proofs/penalty_endpoint_certificate.json'
BR = 'proofs/penalty_branch_certificates.json'
LO = 'proofs/penalty_lower_certificate.json'
QT = 'proofs/improved_qutrit_certificate.json'
FA = 'proofs/facet_certificate.json'

# --- controls: the unmodified tree must pass every checker ---------------------
for what, script in (('unmodified endpoint certificate', ENDPOINT),
                     ('unmodified improved qutrit', QUTRIT),
                     ('unmodified hull separation', HULL),
                     ('unmodified independent reconstruction', INDEP)):
    expect_accept(what, script)


# --- Gram: positivity and the operator identity, isolated from each other ------
KERNEL_DELTA = ((0, 1, 1), (1, 1, 2), (1, 5, 1))          # (row, col, multiplier)
LAMBDA = Fr(1, 1000)


def perturb_gram_in_identity_kernel(tree):
    c = load(tree, EP)
    X = [[Fr(x) for x in row] for row in c['gram']]
    for a, b, mult in KERNEL_DELTA:
        X[a][b] += LAMBDA * mult
        if a != b:
            X[b][a] += LAMBDA * mult
    c['gram'] = [[str(x) for x in row] for row in X]
    save(tree, EP, c)


def perturb_gram_off_diagonal(tree):
    c = load(tree, EP)
    X = [[Fr(x) for x in row] for row in c['gram']]
    X[0][1] += Fr(1, 10 ** 12)
    X[1][0] += Fr(1, 10 ** 12)
    c['gram'] = [[str(x) for x in row] for row in X]
    save(tree, EP, c)


def weaken_epsilon(tree):
    c = load(tree, EP)
    c['epsilon'] = '383688/100000'          # one part in 10^5 SMALLER: a weaker, still TRUE claim
    c['alpha'] = '16312/100000'             # kept complementary, and still above the lower strategy
    save(tree, EP, c)


def overstate_epsilon(tree):
    c = load(tree, EP)
    c['epsilon'] = '383690/100000'          # one part in 10^5 larger, i.e. alpha = 0.16310
    c['alpha'] = '16310/100000'
    save(tree, EP, c)


def break_epsilon_alpha(tree):
    c = load(tree, EP)
    c['alpha'] = '16312/100000'
    save(tree, EP, c)


expect_reject('a Gram perturbation in the kernel of the SOS map: the operator identity still '
              'reconstructs exactly, only positivity is lost',
              ENDPOINT, '[E-GRAM-NOT-PD]', perturb_gram_in_identity_kernel)
expect_reject('a 10^-12 off-diagonal Gram change: far too small to disturb positivity, so only '
              'the exact identity can see it',
              ENDPOINT, '[E-SOS-RESIDUAL]', perturb_gram_off_diagonal)
expect_reject('epsilon weakened by one part in 10^5: the inequality it states is still TRUE, but '
              'this Gram no longer proves that statement',
              ENDPOINT, '[E-SOS-RESIDUAL]', weaken_epsilon)
expect_reject('epsilon overstated by one part in 10^5: refuted by the repository\'s own explicit '
              'lower strategy, which already reaches 0.16310160',
              ENDPOINT, '[E-LOWER-RATIO]', overstate_epsilon)
expect_reject('alpha no longer complementary to epsilon',
              ENDPOINT, '[E-EPS-RANGE]', break_epsilon_alpha)


# --- the twelve deterministic-observable duals --------------------------------
def bump_multiplier(tree):
    b = load(tree, BR)
    b[0]['t'][0] = str(int(b[0]['t'][0]) + 1)
    save(tree, BR, b)


def negate_multiplier(tree):
    b = load(tree, BR)
    k = next(i for i, x in enumerate(b[0]['t']) if Fr(x) > 0)
    b[0]['t'][k] = str(-Fr(b[0]['t'][k]))
    save(tree, BR, b)


def overstate_bound(tree):
    b = load(tree, BR)
    b[0]['upper'] = '7'
    save(tree, BR, b)


def drop_branch(tree):
    b = load(tree, BR)
    save(tree, BR, [c for c in b if (c['i'], c['s']) != (3, 1)])


expect_reject('a dual multiplier bumped by one, breaking the identity it certifies',
              ENDPOINT, '[E-DUAL-IDENTITY]', bump_multiplier)
expect_reject('a negative multiplier on a positivity constraint, which reverses its direction',
              ENDPOINT, '[E-DUAL-NEGATIVE]', negate_multiplier)
expect_reject('a branch claiming a dual value its own multipliers do not sum to',
              ENDPOINT, '[E-DUAL-UPPER]', overstate_bound)
expect_reject('one of the twelve (observable, sign) branches removed, leaving a gap in the case '
              'analysis', ENDPOINT, '[E-BRANCH-COVERAGE]', drop_branch)


# --- the lower strategy --------------------------------------------------------
def perturb_lower_state(tree):
    c = load(tree, LO)
    c['t'] = str(Fr(c['t']) + Fr(1, 10 ** 7))
    save(tree, LO, c)


expect_reject('the lower strategy state parameter moved, so the stored ratio is no longer the '
              'one its own behaviour attains', ENDPOINT, '[E-LOWER-RATIO]', perturb_lower_state)


# --- the improved qutrit -------------------------------------------------------
def make_state_singular(tree):
    c = load(tree, QT)
    s = c['state']
    s[6], s[7], s[8] = s[0] + s[3], s[1] + s[4], s[2] + s[5]   # third row = sum of the others
    save(tree, QT, c)


def flip_outcome_label(tree):
    c = load(tree, QT)
    c['Alice'][0]['rank_one_outcome'] = 1 - c['Alice'][0]['rank_one_outcome']
    save(tree, QT, c)


expect_reject('the qutrit coefficient matrix made singular, so the state is not Schmidt rank three',
              QUTRIT, '[E-QUTRIT-RANK]', make_state_singular)
expect_reject("one of Alice's outcome labels flipped, keeping a valid behaviour but changing the "
              'score', QUTRIT, '[E-QUTRIT-SCORE]', flip_outcome_label)


# --- the hull separation -------------------------------------------------------
def remove_the_witness(tree):
    c = load(tree, FA)
    keep = []
    for e in c['saturating_points']:
        v = [Fr(x) for x in e['v']]
        if (1 + v[1] + v[3] + v[9]) / 4 == 0:
            keep.append(e)
    c['saturating_points'] = keep
    save(tree, FA, c)


def zero_the_penalty(tree):
    c = load(tree, EP)
    c['epsilon'] = '0'
    save(tree, EP, c)


expect_reject('every facet point with p > 0 removed, so the separation would be vacuous',
              HULL, '[E-HULL-COUNTEREXAMPLE]', remove_the_witness)
expect_reject('a zero penalty, which does not separate G from F at all',
              HULL, '[E-HULL-COUNTEREXAMPLE]', zero_the_penalty)


# --- the independent reconstruction --------------------------------------------
expect_reject('a dual multiplier bumped by one, seen by the independent dual rebuild',
              INDEP, '[E-IND-DUAL]', bump_multiplier)
expect_reject('a 10^-12 off-diagonal Gram change, seen by the independent normal ordering',
              INDEP, '[E-IND-RESIDUAL]', perturb_gram_off_diagonal)
expect_reject('the identity-preserving Gram perturbation, which only the independent Bareiss '
              'minors can see', INDEP, '[E-IND-MINOR]', perturb_gram_in_identity_kernel)


# --- control: the reason-checking itself must not degrade to exit-code checking -
def sentinel(tree):
    """The defeat a reviewer used against an earlier suite: fail before reading anything."""
    p = tree / ENDPOINT
    p.write_text("raise SystemExit('sentinel: refuses everything')\n" + p.read_text())


with tempfile.TemporaryDirectory() as td:
    tree = copy_repo(Path(td))
    sentinel(tree)
    verdict = rejection_problem(tree, ENDPOINT, '[E-GRAM-NOT-PD]')
    if verdict is None:
        fails.append('CONTROL: a checker that refuses everything before reading its input was '
                     'accepted as "rejected for the intended reason" -- the reason-checking has '
                     'regressed to exit-code checking')
    else:
        print(f'  PASS control: the refuse-everything sentinel is NOT counted as a valid '
              f'rejection ({verdict[:60]}...)', flush=True)

# --- control: a mutation must not satisfy the WRONG code ----------------------
with tempfile.TemporaryDirectory() as td:
    tree = copy_repo(Path(td))
    drop_branch(tree)
    verdict = rejection_problem(tree, ENDPOINT, '[E-SOS-RESIDUAL]')
    if verdict is None:
        fails.append('CONTROL: a missing branch was accepted as an SOS-residual rejection -- the '
                     'suite is not distinguishing between diagnostic codes')
    else:
        print('  PASS control: a missing branch does not satisfy the SOS-residual code',
              flush=True)

if fails:
    print('\nFAILED:')
    for f in fails:
        print('   ' + f)
    raise SystemExit(1)
print('\nPASS every endpoint mutation is rejected, and for the intended mathematical reason')
