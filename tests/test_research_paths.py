"""Every discovery input and output path resolves, without executing any of the code.

Four earlier versions of this file failed, each in a way that let a real defect through, and
each failure is a regression test below.

  1. It banned the spelling `Path(__file__).with_name(...)`.  Banning a spelling is not a
     behavioral test: it accepted a path rewritten to read `build/clifford_bound.py` and
     would have rejected the correct repair.
  2. It executed each script's leading path-setup lines, stopping at the first solver import.
     That reaches only the prologue, and both defects of the day lived below it; it also had
     to skip any script whose prologue imported an absent dependency, which is a hole a
     failure can hide in.
  3. It resolved reads properly but still tested WRITES with a line regex for the name
     `OUTPUT_DIR`.  Appending the comment `# OUTPUT_DIR` to a line writing elsewhere
     satisfied the regex.
  4. It resolved both directions, but rebuilt each script's namespace with `exec` over its
     top-level assignments, and claimed "no solver work happens here".  That claim was false:
     an assignment's right-hand side may contain arbitrary calls, so
     `probe = (OUTPUT_DIR / 'x.txt').write_text('side effect')` made the TEST perform the
     write.  Its resolver also dropped the right operand of a division on NameError until
     some prefix resolved, which discards later `..` segments -- so
     `OUTPUT_DIR / dynamic / '..' / '..' / 'escaped.txt'` was approved on the strength of its
     `build/` prefix while normalizing to a destination outside `build/`.

This version executes NOTHING.  It evaluates a deliberately restricted path-expression
language -- string constants, `__file__`, `Path(...)`, `.parent`, `.resolve()`, previously
bound path names, and `/` joining -- and reports anything outside it rather than skipping it.
An unknown component computed at run time is tolerated only as the FINAL filename; unknown
directory components, absolute components and `..` traversal are rejected.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are checks.")

import ast
import json
import numpy as np
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / 'research'
BUILD = (ROOT / 'build').resolve()
fails = []

READ_METHODS = ('read_text', 'read_bytes')
WRITE_METHODS = ('write_text', 'write_bytes')
NP_READERS = ('load', 'loadtxt', 'genfromtxt')
NP_WRITERS = ('save', 'savez', 'savez_compressed', 'savetxt')
PATH_ATTRS = ('parent',)
PATH_CALLS = ('resolve', 'absolute', 'expanduser')


class Unsupported(Exception):
    """A path expression outside the restricted language.  Reported, never skipped."""


class Resolved:
    """A path, plus whether its final component is only known at run time."""

    __slots__ = ('path', 'exact')

    def __init__(self, path, exact=True):
        self.path, self.exact = path, exact


def _component(name):
    """Validate one path component before joining it. Traversal never gets past here."""
    p = PurePosixPath(name)
    if p.is_absolute() or name.startswith('/') or name.startswith('\\'):
        raise Unsupported(f"absolute path component {name!r}")
    for part in p.parts:
        if part in ('..', '.'):
            raise Unsupported(f"traversal component {part!r} in {name!r}")
    return name


def evaluate(node, env, script):
    """Evaluate a path expression, or raise Unsupported. Never calls into user code."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return node.value
        raise Unsupported(f"non-string constant {node.value!r}")
    if isinstance(node, ast.JoinedStr):
        return None                                    # an f-string: known only at run time
    if isinstance(node, ast.Name):
        if node.id == '__file__':
            return str(script)
        if node.id == 'Path':
            return 'Path'                              # only ever used as Path(...)
        if node.id in env:
            return env[node.id]
        return None                                    # a name we did not bind: unknown
    if isinstance(node, ast.Attribute):
        if node.attr in PATH_ATTRS:
            base = evaluate(node.value, env, script)
            if not isinstance(base, Resolved):
                raise Unsupported(f".{node.attr} on a non-path")
            if not base.exact:
                raise Unsupported(f".{node.attr} applied after an unknown component")
            return Resolved(base.path.parent)
        raise Unsupported(f"attribute .{node.attr}")
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Name) and f.id == 'Path' and len(node.args) == 1:
            arg = evaluate(node.args[0], env, script)
            if isinstance(arg, Resolved):
                return arg
            if arg is None:
                raise Unsupported("Path() of a value not known statically")
            return Resolved(Path(arg))
        if isinstance(f, ast.Attribute) and f.attr in PATH_CALLS and not node.args:
            base = evaluate(f.value, env, script)
            if not isinstance(base, Resolved):
                raise Unsupported(f".{f.attr}() on a non-path")
            return Resolved(base.path.resolve(), base.exact)
        raise Unsupported(f"call {ast.unparse(f)}(...)")
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = evaluate(node.left, env, script)
        if not isinstance(left, Resolved):
            raise Unsupported("left operand of / is not a path")
        if not left.exact:
            # the reviewer's escape: a later component after an unknown one is a directory,
            # and an unknown directory can carry the destination anywhere.
            raise Unsupported("component joined after an unknown directory component")
        right = evaluate(node.right, env, script)
        if right is None:
            return Resolved(left.path, exact=False)    # unknown FINAL filename: allowed
        if isinstance(right, Resolved):
            raise Unsupported("right operand of / is itself a path")
        return Resolved(left.path / _component(right))
    raise Unsupported(f"expression form {type(node).__name__}")


def bind_paths(tree, script):
    """Bind top-level names to paths by EVALUATION, never by execution."""
    env = {}
    for stmt in tree.body:
        if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)):
            continue
        try:
            value = evaluate(stmt.value, env, script)
        except Unsupported:
            continue                                   # not a path expression; leave unbound
        if isinstance(value, Resolved) and value.exact:
            env[stmt.targets[0].id] = value
    return env


def _open_kind(node):
    mode = node.args[1] if len(node.args) > 1 else None
    for kw in node.keywords:
        if kw.arg == 'mode':
            mode = kw.value
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return 'write' if any(ch in mode.value for ch in 'wax+') else 'read'
    return 'read' if mode is None else 'write'


def io_sites(tree):
    """(lineno, path-expression node, 'read'|'write') for every filesystem access."""
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


def mkdir_targets(tree):
    return {n.func.value.id for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == 'mkdir' and isinstance(n.func.value, ast.Name)}


scripts = sorted(RESEARCH.glob('*.py'))
trees = {p: ast.parse(p.read_text()) for p in scripts}
envs = {p: bind_paths(t, p) for p, t in trees.items()}

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

# 2. every read and every write resolves, inside the restricted language
for p in scripts:
    rel, env = p.relative_to(ROOT), envs[p]
    n_sites = 0
    for lineno, expr, kind in sorted(io_sites(trees[p]), key=lambda t: (t[0], t[2])):
        n_sites += 1
        where, shown = f"{rel}:{lineno}", ast.unparse(expr)
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            fails.append(f"{where}: {kind} is bound to the string literal {shown}, not to a "
                         f"path -- parenthesize the path expression")
            continue
        try:
            r = evaluate(expr, env, p)
        except Unsupported as exc:
            fails.append(f"{where}: unsupported {kind} path expression `{shown}` -- {exc}")
            continue
        if not isinstance(r, Resolved):
            fails.append(f"{where}: `{shown}` is not a path expression")
            continue
        resolved = r.path.resolve()
        note = '' if r.exact else '  [directory only; the file name is computed at run time]'
        if kind == 'write':
            if not (BUILD in resolved.parents or (not r.exact and resolved == BUILD)):
                fails.append(f"{where}: writes to {resolved}, outside the output directory "
                             f"{BUILD}")
            else:
                print(f"  PASS write resolves into build/: {where} -> "
                      f"{resolved.relative_to(ROOT)}{note}")
        elif BUILD in resolved.parents:
            fails.append(f"{where}: reads the generated file {resolved.relative_to(ROOT)}; "
                         f"discovery inputs must come from the source tree")
        elif RESEARCH.resolve() not in resolved.parents:
            fails.append(f"{where}: `{shown}` resolves outside research/: {resolved}")
        elif r.exact and not resolved.is_file():
            fails.append(f"{where}: `{shown}` resolves to {resolved}, which does not exist")
        else:
            print(f"  PASS read resolves: {where} -> {resolved.relative_to(ROOT)}{note}")
    if n_sites == 0:
        print(f"  PASS no filesystem access: {rel}")

# 3. a script that writes routes its writes through an OUTPUT_DIR that resolves to build/
for p in scripts:
    if not any(k == 'write' for _, _, k in io_sites(trees[p])):
        continue
    rel, env = p.relative_to(ROOT), envs[p]
    if 'OUTPUT_DIR' not in env:
        fails.append(f"{rel}: writes but defines no OUTPUT_DIR that resolves to a path")
    elif env['OUTPUT_DIR'].path.resolve() != BUILD:
        fails.append(f"{rel}: OUTPUT_DIR is {env['OUTPUT_DIR'].path}, expected {BUILD}")
    elif 'OUTPUT_DIR' not in mkdir_targets(trees[p]):
        fails.append(f"{rel}: OUTPUT_DIR is never created with .mkdir()")
    else:
        print(f"  PASS OUTPUT_DIR resolves to build/ and is created: {rel}")

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print("\nPASS every discovery read and write resolves, with no code executed")
