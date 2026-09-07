"""SHA-256 manifest with separate generate and check modes.

Covers every file in the Git index except hashes.txt itself, so review, docs and metadata
are hashed alongside the certificates.

A file that is still tracked but missing from the working tree is FATAL in both modes. It is
not silently dropped from the expected set: doing so would let `generate` erase the evidence
that something disappeared, after which `check` would announce complete coverage. Delete a
file deliberately by staging the deletion, so it leaves the index.

Only tracked files are considered, so a file that has not been staged is invisible to both
modes: `generate` omits it and `check` then passes, reporting complete coverage of a set that
silently excludes the new work. Both modes therefore refuse to run while a non-ignored
untracked file exists. Stage it, or add it to .gitignore, and rerun.

    python manifest.py generate         # rewrite hashes.txt from the Git index
    python manifest.py check            # hashes AND index coverage; needs a checkout
    python manifest.py verify-archive   # hashes only; works in an unpacked archive

`check` and `verify-archive` answer DIFFERENT questions and neither implies the other.
`check` asks whether hashes.txt covers exactly the Git index and every hash matches -- it is a
statement about a checkout, and it cannot run without one.  `verify-archive` asks whether the
files present here match the hashes shipped beside them, and whether anything present is
unlisted; it needs no Git metadata, which is what makes a downloaded snapshot verifiable.
Neither is mathematical correctness, proof authenticity, or historical priority.
"""

import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are integrity checks.")

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'hashes.txt'
EXCLUDE = {'hashes.txt'}


def require_checkout():
    """Fail with an explanation, not a traceback, when there is no Git metadata."""
    r = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--git-dir'],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(
            'this mode compares hashes.txt against the Git index and needs a checkout.\n'
            'In an unpacked archive use:  python manifest.py verify-archive')


def index_paths():
    """Every path in the Git index, NUL-separated so whitespace survives."""
    require_checkout()
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'],
                         capture_output=True, check=True).stdout
    return sorted(p.decode() for p in out.split(b'\0') if p and p.decode() not in EXCLUDE)


def untracked():
    """Non-ignored files the index does not know about.

    `git ls-files` cannot see these, so without this guard `generate` writes a manifest that
    omits new work and `check` then certifies that manifest as complete -- exactly the silent
    gap this tool exists to close, one step earlier in the workflow.
    """
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z',
                          '--others', '--exclude-standard'],
                         capture_output=True, check=True).stdout
    return sorted(p.decode() for p in out.split(b'\0') if p)


def refuse_if_untracked():
    require_checkout()
    stray = untracked()
    if stray:
        for p in stray:
            print(f"  UNTRACKED, so invisible to the manifest: {p}")
        raise SystemExit("refusing to run: stage these files or add them to .gitignore")


def missing(paths):
    return [p for p in paths if not (ROOT / p).is_file()]


def digest(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def parse_manifest():
    listed, seen = {}, set()
    for n, line in enumerate(MANIFEST.read_text().split('\n'), 1):
        if not line.strip():
            continue
        h, sep, p = line.partition('  ')
        p = p.strip()
        if not sep or len(h) != 64 or not all(ch in '0123456789abcdef' for ch in h) or not p:
            raise SystemExit(f"hashes.txt line {n}: malformed record")
        if p in seen:
            raise SystemExit(f"hashes.txt line {n}: duplicate record for {p}")
        seen.add(p)
        listed[p] = h
    return listed


def generate():
    refuse_if_untracked()
    paths = index_paths()
    gone = missing(paths)
    if gone:
        print("refusing to generate: these files are tracked but missing from the working tree.")
        print("stage the deletion if it was intended, so they leave the index:")
        for p in gone:
            print(f"   {p}")
        raise SystemExit(1)
    MANIFEST.write_text('\n'.join(f"{digest(p)}  {p}" for p in paths) + '\n')
    print(f"wrote {MANIFEST.name}: {len(paths)} entries")


SNAPSHOT_SKIP = {'.git', 'build', '__pycache__', '.venv', '_to_delete'}


def verify_archive():
    """Hash check with no Git metadata, for an unpacked snapshot."""
    if not MANIFEST.exists():
        raise SystemExit('hashes.txt missing')
    listed = parse_manifest()
    present = sorted(str(f.relative_to(ROOT)) for f in ROOT.rglob('*')
                     if f.is_file() and not (SNAPSHOT_SKIP & set(f.relative_to(ROOT).parts))
                     and str(f.relative_to(ROOT)) not in EXCLUDE)
    gone = [p for p in listed if p not in present]
    extra = [p for p in present if p not in listed]
    bad = [p for p in listed if p in present and digest(p) != listed[p]]
    print(f"files present: {len(present)}   manifest entries: {len(listed)}")
    for label, items in (('LISTED BUT MISSING', gone),
                         ('PRESENT BUT NOT LISTED', extra),
                         ('HASH MISMATCH', bad)):
        for p in items:
            print(f"  {label}: {p}")
    if gone or extra or bad:
        raise SystemExit(1)
    print('PASS every listed file is present and every hash matches')
    print('(this is archive integrity only: not Git-index coverage, not mathematical '
          'correctness, not authenticity)')


def check():
    refuse_if_untracked()
    if not MANIFEST.exists():
        raise SystemExit('hashes.txt missing')
    listed = parse_manifest()
    paths = index_paths()
    gone = missing(paths)
    absent = [p for p in paths if p not in listed and p not in gone]
    stale = [p for p in listed if p not in paths]
    bad = [p for p in paths if p in listed and p not in gone and digest(p) != listed[p]]
    print(f"tracked payload files: {len(paths)}   manifest entries: {len(listed)}")
    for label, items in (('TRACKED BUT MISSING from the working tree', gone),
                         ('NOT COVERED by the manifest', absent),
                         ('listed but no longer in the index', stale),
                         ('HASH MISMATCH', bad)):
        for p in items:
            print(f"  {label}: {p}")
    if gone or absent or stale or bad:
        raise SystemExit(1)
    print('PASS manifest covers every tracked file and all hashes match')
    print('(hash integrity is not mathematical correctness or independent review)')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if mode == 'generate':
        generate()
    elif mode == 'check':
        check()
    elif mode == 'verify-archive':
        verify_archive()
    else:
        raise SystemExit('usage: manifest.py [generate|check|verify-archive]')
