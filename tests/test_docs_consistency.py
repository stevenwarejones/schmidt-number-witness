"""Every path named in prose exists, and every tracked script is named somewhere.

Documentation rot is the failure mode this repository is least able to detect on its own:
a verifier that moves leaves a README pointing at nothing, and nothing fails.  A reader who
runs a documented command and gets `No such file` has no way to tell a stale path from a
broken proof.  So the paths are checked the same way the certificates are.

Two directions:

  * every path-like token in the documentation resolves to a file that exists;
  * every tracked script is mentioned in the documentation or the CI workflow, so a file
    cannot sit in the tree unreferenced.

Generated paths under `build/` are exempt: they are git-ignored by design, and the prose
sometimes names one to describe a defect (`build/clifford_bound.py` is where a bad path
rewrite once pointed a source read).  Those are reported, not asserted.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are checks.")

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROSE_SUFFIXES = ('.md', '.yml', '.yaml', '.cff')
# a backticked path, or a documented `python some/script.py` invocation
PATHLIKE = re.compile(r'`([A-Za-z0-9_./-]+\.(?:py|json|md|txt|yml|cff|npz))`')
DIRLIKE = re.compile(r'`([A-Za-z0-9_./-]+/)`')
COMMAND = re.compile(r'python3?\s+([A-Za-z0-9_./-]+\.py)')

fails, exempt = [], []

SKIP_DIRS = {'.git', 'build', '__pycache__', '.venv', '_to_delete'}


def repository_files():
    """Tracked files, or -- outside a checkout -- everything that is not generated.

    Unlike manifest.py, which is a statement ABOUT the Git index, this file only needs to
    know which files exist.  Falling back to a walk lets it run against a `git archive`
    export or an unpacked release, which is exactly where a stale documented path would
    strand a reader who has no repository to consult.
    """
    try:
        out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'],
                             capture_output=True, check=True).stdout
        listed = sorted(p.decode() for p in out.split(b'\0') if p)
        if listed:
            return listed, 'the Git index'
    except (OSError, subprocess.CalledProcessError):
        pass
    walked = []
    for f in ROOT.rglob('*'):
        if f.is_file() and not (SKIP_DIRS & set(f.relative_to(ROOT).parts)):
            walked.append(str(f.relative_to(ROOT)))
    return sorted(walked), 'a filesystem walk (no Git index here)'


TRACKED, SOURCE = repository_files()
assert TRACKED, 'no files found: run this inside the repository or an export of it'
print(f"  file list from {SOURCE}: {len(TRACKED)} files")


def resolves(token, home):
    """A path in prose may be written from the repository root or from its own directory."""
    return (ROOT / token).exists() or (home / token).exists()


# 1. every path named in prose exists
for rel in TRACKED:
    if not rel.endswith(PROSE_SUFFIXES):
        continue
    p = ROOT / rel
    text = p.read_text()
    for token in sorted(set(PATHLIKE.findall(text)) | set(COMMAND.findall(text))
                        | set(DIRLIKE.findall(text))):
        if token.startswith('build/') or token == 'build/':
            exempt.append(f"{rel}: {token}")
        elif not resolves(token, p.parent):
            fails.append(f"{rel}: names `{token}`, which does not exist")
    print(f"  PASS paths resolve: {rel}")

# 2. every tracked script is referenced somewhere, so nothing sits in the tree unreferenced
prose = '\n'.join((ROOT / r).read_text() for r in TRACKED if r.endswith(PROSE_SUFFIXES))
for rel in TRACKED:
    if not rel.endswith('.py') or rel == 'tests/test_docs_consistency.py':
        continue
    name = Path(rel).name
    if rel not in prose and name not in prose:
        fails.append(f"{rel}: tracked but named in no documentation or workflow")

# 3. every entry point is actually run by CI -- directly in the workflow, or through
#    run_checks.py.  A verifier nobody invokes is a verifier nobody notices breaking.
ci = (ROOT / '.github/workflows/verify.yml').read_text()
chain = (ROOT / 'run_checks.py').read_text()
for rel in TRACKED:
    q = Path(rel)
    entry = (q.parts[:1] == ('tests',) and q.suffix == '.py') or q.name.startswith('verify_')
    if not entry or q.suffix != '.py':
        continue
    if rel in ci or q.name in ci or f"'{q.name}'" in chain:
        print(f"  PASS run by CI: {rel}")
    else:
        fails.append(f"{rel}: an entry point that neither the workflow nor run_checks.py runs")

# 4. the README quick start and CONTRIBUTING command list agree on what to run
readme = (ROOT / 'README.md').read_text()
contrib = (ROOT / 'CONTRIBUTING.md').read_text()
for a, b, an, bn in ((readme, contrib, 'README.md', 'CONTRIBUTING.md'),
                     (contrib, readme, 'CONTRIBUTING.md', 'README.md')):
    for cmd in sorted(set(COMMAND.findall(a))):
        if cmd not in b:
            fails.append(f"{an} documents `python {cmd}` but {bn} does not")

if exempt:
    print(f"\nnote: {len(exempt)} generated path(s) named in prose, not required to exist: "
          + ', '.join(exempt))
if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS every documented path exists and every tracked script is documented")
