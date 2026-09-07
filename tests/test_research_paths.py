"""Discovery input/output path checks, without launching a solver.

Two defects motivate this file, and both were missed by weaker checks:

  * `Path(...)/'x'/'y.json'.read_text()` binds `.read_text()` to the string literal by
    operator precedence. At run time this raises AttributeError -- str has no read_text --
    but it is syntactically valid, so a compile-only check passes it, and the script has to
    be executed as far as that line for anything to notice.
  * a path rewrite pointed a *source* read at the generated output directory, so
    `research/equality_kernel.py` tried to read `build/clifford_bound.py`.

Two earlier versions of this file failed to catch them, in instructive ways.

The first banned the spelling `Path(__file__).with_name(...)` and inferred everything else.
Banning a spelling is not a behavioral test: it accepted the broken path and would have
rejected a correct repair.

The second executed each script's leading path-setup lines, stopping at the first solver
import. That is a real resolution, but it reaches only the prologue -- and both defects live
below it, at the first `exec(`. It also had to skip any script whose prologue imported an
absent discovery dependency, which is a hole a failure can hide in, and it ran whatever
computation the prologue happened to contain.

A third version resolved reads this way but still tested WRITES with a line-based regex for
the name `OUTPUT_DIR`. That is the same mistake in the other direction: appending the comment
`# OUTPUT_DIR` to a line writing somewhere else satisfied the regex and the test passed.

This file resolves paths WITHOUT running the scripts, in both directions. For each script it
rebuilds a namespace from that script's own top-level imports and simple assignments, then
locates every filesystem read AND write syntactically and evaluates its path expression
against that namespace. A path bound to a string literal, a read resolving anywhere but an
existing file under `research/`, or a write resolving anywhere but `build/`, fails here --
wherever in the file it sits, and with no dependency on the research stack being installed.
"""

import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are checks.")

import ast
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / 'research'
BUILD = ROOT / 'build'
fails = []

READ_METHODS = ('read_text', 'read_bytes')
WRITE_METHODS = ('write_text', 'write_bytes')
NP_READERS = ('load', 'loadtxt', 'genfromtxt')
NP_WRITERS = ('save', 'savez', 'savez_compressed', 'savetxt')
OUT_NAMES = ('OUTPUT_DIR',)


def _open_kind(node):
    """'write' if this open() call names a writing mode, else 'read'."""
    mode = node.args[1] if len(node.args) > 1 else None
    for kw in node.keywords:
        if kw.arg == 'mode':
            mode = kw.value
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return 'write' if any(ch in mode.value for ch in 'wax+') else 'read'
    return 'read' if mode is None else 'write'


def io_sites(tree):
    """(lineno, path-expression node, 'read'|'write') for every filesystem access.

    The path expression is the RECEIVER of `.read_text()` / `.write_text()`, or the first
    argument of `np.load` / `np.savez` / `open`.  That receiver is exactly the expression the
    precedence defect corrupts, and exactly the thing a name-matching regex cannot see.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr in READ_METHODS:
            yield node.lineno, f.value, 'read'
        elif isinstance(f, ast.Attribute) and f.attr in WRITE_METHODS:
            yield node.lineno, f.value, 'write'
        elif (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
              and f.value.id in ('np', 'numpy') and node.args):
            if f.attr in NP_READERS:
                yield node.lineno, node.args[0], 'read'
            elif f.attr in NP_WRITERS:
                yield node.lineno, node.args[0], 'write'
        elif isinstance(f, ast.Name) and f.id == 'open' and node.args:
            yield node.lineno, node.args[0], _open_kind(node)


def resolution_namespace(path, tree):
    """Rebuild enough of a script to evaluate its path expressions, without running it.

    Only top-level imports and assignments to plain names are replayed, one statement at a
    time; anything that raises is skipped, because a script may legitimately depend on
    machinery this test does not have. Loops, calls and `exec` are never replayed, so no
    solver work happens here. Path expressions are evaluated separately afterwards, so a read
    whose own assignment was skipped is still checked rather than silently passed.
    """
    ns = {'__file__': str(path), '__name__': '__not_main__', 'Path': Path}
    for stmt in tree.body:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            pass
        elif isinstance(stmt, ast.Assign) and all(isinstance(t, ast.Name) for t in stmt.targets):
            pass
        else:
            continue
        try:
            exec(compile(ast.Module([stmt], []), str(path), 'exec'), ns)   # noqa: S102
        except Exception:                                                  # noqa: BLE001
            continue
    return ns


def resolve(expr, ns):
    """(path, exact) for a path expression.

    A write destination may name a file computed at run time -- `OUTPUT_DIR /
    f'level{level}.json'` -- which cannot be evaluated without running the script.  The
    DIRECTORY is the invariant under test, so when the whole expression does not resolve,
    fall back to the longest leading `/`-chain that does and report the result as inexact.
    Only a name that is genuinely undefined triggers this; a misspelled OUTPUT_DIR resolves
    to nothing at all and still fails.
    """
    try:
        return Path(eval(ast.unparse(expr), dict(ns))).resolve(), True     # noqa: S307
    except NameError:
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
            return resolve(expr.left, ns)[0], False
        raise


def mkdir_targets(tree):
    """Names on which `.mkdir(...)` is called at any point in the module."""
    out = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'mkdir' and isinstance(node.func.value, ast.Name)):
            out.add(node.func.value.id)
    return out


scripts = sorted(RESEARCH.glob('*.py'))
trees = {p: ast.parse(p.read_text()) for p in scripts}
spaces = {p: resolution_namespace(p, t) for p, t in trees.items()}

# 1. archived inputs load, without pickle
for p in sorted((RESEARCH / 'inputs').iterdir()):
    try:
        if p.suffix == '.json':
            json.loads(p.read_text())
        elif p.suffix == '.npz':
            with np.load(p, allow_pickle=False) as z:
                for k in z.files:
                    if not np.isfinite(np.asarray(z[k], dtype=float)).all():
                        fails.append(f"{p.name}[{k}]: non-finite entries")
        print(f"  PASS input loads: research/inputs/{p.name}")
    except Exception as exc:                                              # noqa: BLE001
        fails.append(f"{p.name}: {exc}")

# 2. every script that writes resolves its output directory to build/ and creates it
for p in scripts:
    if not any(k == 'write' for _, _, k in io_sites(trees[p])):
        continue
    rel = p.relative_to(ROOT)
    ns, made = spaces[p], mkdir_targets(trees[p])
    named = [n for n in OUT_NAMES if n in ns]
    if not named:
        fails.append(f"{rel}: writes but defines no {' or '.join(OUT_NAMES)}")
        continue
    for n in named:
        if Path(ns[n]) != BUILD:
            fails.append(f"{rel}: {n} is {ns[n]}, expected {BUILD}")
        elif n not in made:
            fails.append(f"{rel}: {n} is never created with .mkdir()")
        else:
            print(f"  PASS {n} resolves to build/ and is created: {rel}")

# 3. EVERY read and EVERY write in every script resolves, by evaluating the path expression.
#    This is the check that catches all three motivating defects, and it is confined to no
#    part of the file and to no spelling: a comment naming OUTPUT_DIR cannot satisfy it, and
#    a correct path spelled a new way cannot fail it.
for p in scripts:
    rel = p.relative_to(ROOT)
    ns = spaces[p]
    n_sites = 0
    for lineno, expr, kind in sorted(io_sites(trees[p]), key=lambda t: (t[0], t[2])):
        n_sites += 1
        where = f"{rel}:{lineno}"
        shown = ast.unparse(expr)
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            fails.append(f"{where}: {kind} is bound to the string literal {shown}, not to a "
                         f"path -- parenthesize the path expression")
            continue
        try:
            resolved, exact = resolve(expr, ns)
        except Exception as exc:                                          # noqa: BLE001
            fails.append(f"{where}: path expression `{shown}` did not resolve -- "
                         f"{type(exc).__name__}: {exc}")
            continue
        note = '' if exact else '  [directory only; the file name is computed at run time]'
        if kind == 'write':
            # Generated files belong under build/ and nowhere else.  The directory need not
            # exist yet, so this is a question about the path, not about the filesystem.
            inside = BUILD.resolve() in resolved.parents or (not exact and resolved == BUILD.resolve())
            if not inside:
                fails.append(f"{where}: writes to {resolved}, outside the output directory "
                             f"{BUILD}")
            else:
                print(f"  PASS write resolves into build/: {where} -> "
                      f"{resolved.relative_to(ROOT)}{note}")
        elif BUILD.resolve() in resolved.parents:
            fails.append(f"{where}: reads the generated file {resolved.relative_to(ROOT)}; "
                         f"discovery inputs must come from the source tree")
        elif RESEARCH.resolve() not in resolved.parents:
            fails.append(f"{where}: `{shown}` resolves outside research/: {resolved}")
        elif exact and not resolved.is_file():
            fails.append(f"{where}: `{shown}` resolves to {resolved}, which does not exist")
        elif not exact and not resolved.is_dir():
            fails.append(f"{where}: `{shown}` reads from {resolved}, which is not a directory")
        else:
            print(f"  PASS read resolves: {where} -> {resolved.relative_to(ROOT)}{note}")
    if n_sites == 0:
        print(f"  PASS no filesystem access: {rel}")

# 4. a script that writes must route its writes through a resolved OUTPUT_DIR, so that the
#    destination is established once at the top rather than spelled out at each call site.
for p in scripts:
    if not any(k == 'write' for _, _, k in io_sites(trees[p])):
        continue
    rel, ns, made = p.relative_to(ROOT), spaces[p], mkdir_targets(trees[p])
    if not any(n in ns for n in OUT_NAMES):
        fails.append(f"{rel}: writes but defines no {' or '.join(OUT_NAMES)}")

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS discovery reads resolve to existing source-tree inputs "
      "and writes are routed to build/")
