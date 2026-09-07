"""Build a self-contained verification snapshot: extract, run one command, no Git, no solvers.

    python make_snapshot.py

Writes build/verification-snapshot-<short-commit>.tar.gz.  Extracting it anywhere gives a tree
that verifies itself with the standard library plus SymPy and NumPy -- no Git metadata, no SDP
solver, no network.

WHY THIS EXISTS.  `manifest.py check` compares hashes against the Git index, so it cannot run
against a downloaded archive.  A reader who fetches a tarball needs a different question
answered: do the files here match the hashes shipped beside them, and is anything present that
is not listed?  That is `manifest.py verify-archive`, and the snapshot ships with the hashes it
needs.  The two checks are not interchangeable, and SNAPSHOT.md inside the archive says so.

Contents are exactly the tracked files, so nothing generated and nothing ignored is included.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O.")

import hashlib
import platform
import subprocess
import sys
import tarfile
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / 'build'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args],
                          capture_output=True, check=True, text=True).stdout.strip()


commit = git('rev-parse', 'HEAD')
short = commit[:7]
dirty = bool(git('status', '--porcelain'))
tracked = [p for p in git('ls-files', '-z').split('\0') if p]
missing = [p for p in tracked if not (ROOT / p).is_file()]
if missing:
    raise SystemExit(f"refusing to build: tracked but missing from the working tree: {missing}")

versions = []
for mod in ('sympy', 'numpy'):
    try:
        versions.append(f"{mod} {__import__(mod).__version__}")
    except ImportError:
        versions.append(f"{mod} NOT INSTALLED when this snapshot was built")

SNAPSHOT = f"""# Verification snapshot

Repository: schmidt-number-witness
Commit: `{commit}`{'  **(built from a DIRTY working tree; it does not match that commit)**' if dirty else ''}
Built: {date.today().isoformat()}
Built with: CPython {platform.python_version()}, {', '.join(versions)}

## Verify

```sh
python -m pip install -r requirements.txt
python run_checks.py
python manifest.py verify-archive
```

Two of the checks need nothing installed at all:

```sh
python proofs/verify_sharp_qubit.py        # the universal bound
python tests/verify_facet_independent.py   # an independent reconstruction of the geometry
```

## What each command answers

`run_checks.py` re-derives every claim from the certificate data in exact arithmetic. It does
**not** rerun the search that produced the certificates; that lives in `research/` and is never
invoked. See `VERIFY.md`.

`manifest.py verify-archive` asks whether the files here match `hashes.txt` and whether anything
present is unlisted. It needs no Git metadata. This is **archive integrity only** — it is not
Git-index coverage (that is `manifest.py check`, which requires a checkout and will not run
here), and it is not mathematical correctness, proof authenticity, or historical priority.

## Scope

No claim here has been reviewed by a human domain expert. The valid inequality on the
partial-local hull is prior art. Novelty is unresolved. `docs/PRIOR_ART.md` states what is
settled and what is not; `VERIFY.md` states what verification does and does not establish.
"""

with tempfile.TemporaryDirectory() as td:
    stage = Path(td) / f'verification-snapshot-{short}'
    for rel in tracked:
        dest = stage / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / rel).read_bytes())
    (stage / 'SNAPSHOT.md').write_text(SNAPSHOT)

    # hashes.txt inside the archive covers the archive, SNAPSHOT.md included.
    payload = sorted(str(f.relative_to(stage)) for f in stage.rglob('*')
                     if f.is_file() and f.name != 'hashes.txt')
    (stage / 'hashes.txt').write_text(
        '\n'.join(f"{hashlib.sha256((stage / p).read_bytes()).hexdigest()}  {p}"
                  for p in payload) + '\n')

    out = OUTPUT_DIR / f'verification-snapshot-{short}.tar.gz'
    with tarfile.open(out, 'w:gz') as tar:
        tar.add(stage, arcname=stage.name)

digest = hashlib.sha256(out.read_bytes()).hexdigest()
print(f"wrote {out.relative_to(ROOT)}")
print(f"  commit   {commit}{'  (DIRTY TREE)' if dirty else ''}")
print(f"  files    {len(tracked)} tracked + SNAPSHOT.md + hashes.txt")
print(f"  sha256   {digest}")
print("\nThe archive verifies itself with 'python manifest.py verify-archive' after extraction.")
print("That is archive integrity, not Git-index coverage and not mathematical correctness.")
