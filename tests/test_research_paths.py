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

  5. It executed nothing and rejected traversal, but still approved two escapes.
     `OUTPUT_DIR / f'../../{name}'` passed because an unknown FINAL operand was treated as a
     harmless filename without any evidence that it contains no separators, and
     `(OUTPUT_DIR.parent / 'escaped.txt').open('w')` passed because `Path.open` was not
     recognised as a filesystem access at all.

This version executes NOTHING.  It evaluates a deliberately restricted path-expression
language -- string constants, `__file__`, `Path(...)`, `.parent`, `.resolve()`, previously
bound path names, and `/` joining -- and reports anything outside it rather than skipping it.

A name computed at run time is NOT resolved here at all.  Three rounds of review showed that
proving such a name safe by source inference does not converge: each round closed the reported
binding forms and the next found others -- annotated assignment, assignment inside a
conditional, loop variables, `match` pattern capture, and a shadowed `int` builtin.  The
"fails closed over every binding" claim in the previous version was itself the fourth such
overclaim.

Dynamic names go through `research/outputs.py:output_path` instead, which validates the name
at run time, where the value exists.  This file checks only that scripts USE that helper --
a convention it can actually verify by reading the source.

WHAT THIS ESTABLISHES.  For the supported I/O forms below, every static path resolves where it
should, and every computed name is routed through the validated helper.

WHAT IT DOES NOT.  It is not a sandbox and cannot be one.  A script that wants to write
elsewhere can bypass the helper, and no source lint over arbitrary Python could stop it;
`tests/test_checker_mutations.py` covers the mistakes this project has actually made, not
every possible one.  Runtime behaviour and general static analysis are different problems.
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


# Stable diagnostic codes.  tests/test_checker_mutations.py requires the SPECIFIC code for
# each mutation, so that an unrelated early failure cannot be mistaken for the intended
# rejection.  Do not reword these without updating that suite.
E_TRAVERSAL = '[E-TRAVERSAL]'
E_ABSOLUTE = '[E-ABSOLUTE]'
E_UNKNOWN_DIR = '[E-UNKNOWN-DIR]'
E_DYNAMIC = '[E-DYNAMIC-NAME]'
E_UNBOUND = '[E-UNBOUND-NAME]'
E_UNSUPPORTED = '[E-UNSUPPORTED]'
E_OUTSIDE = '[E-OUTSIDE-BUILD]'
E_READ_GENERATED = '[E-READ-GENERATED]'
E_MISSING = '[E-MISSING-INPUT]'
E_LITERAL = '[E-STRING-LITERAL]'
E_HELPER = '[E-HELPER]'

HELPER = 'output_path'          # research/outputs.py, validated at run time and tested directly


class Resolved:
    """A path, plus whether its final component is only known at run time."""

    __slots__ = ('path', 'exact')

    def __init__(self, path, exact=True):
        self.path, self.exact = path, exact


def all_binding_sites(tree):
    """Count the bindings of each name in the ENUMERATED forms below.

    This is a conservative heuristic over supported source forms, NOT a general analysis of
    Python binding.  It counts Name stores, function and class definitions, imports,
    parameters, `global` and `nonlocal`.  It does not cover every way Python can bind a name
    -- `match`/`case` pattern capture binds through MatchAs.name and is not counted here, and
    there are certainly others.

    A name is trusted only when this count matches the module-level simple assignments that
    `trusted_module_values` can actually read, so any binding form it DOES see makes the name
    untrusted.  What it does not see, it does not catch, which is why the containment
    guarantee for computed file names lives in research/outputs.py and not here.
    """
    counts = {}

    def bump(name):
        counts[name] = counts.get(name, 0) + 1

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bump(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bump(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                bump(a.asname or a.name.split('.')[0])
        elif isinstance(node, ast.arg):
            bump(node.arg)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for n in node.names:
                bump(n)
    return counts


def trusted_module_values(tree):
    """name -> its single module-level assigned value, for names bound nowhere else."""
    counts = all_binding_sites(tree)
    simple = {}
    for stmt in tree.body:
        if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)):
            simple.setdefault(stmt.targets[0].id, []).append(stmt.value)
    return {n: v[0] for n, v in simple.items()
            if len(v) == 1 and counts.get(n, 0) == 1}


def _component(name):
    """Validate one path component before joining it. Traversal never gets past here."""
    p = PurePosixPath(name)
    if p.is_absolute() or name.startswith('/') or name.startswith('\\'):
        raise Unsupported(f"{E_ABSOLUTE} absolute path component {name!r}")
    for part in p.parts:
        if part in ('..', '.'):
            raise Unsupported(f"{E_TRAVERSAL} traversal component {part!r} in {name!r}")
    return name


def evaluate(node, env, script):
    """Evaluate a path expression, or raise Unsupported. Never calls into user code."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return node.value
        raise Unsupported(f"{E_UNSUPPORTED} non-string constant {node.value!r}")
    if isinstance(node, ast.JoinedStr):
        raise Unsupported(
            f'{E_DYNAMIC} a computed file name must go through '
            f'research/outputs.py:output_path, which validates it at run time; it is not '
            f'checked by inference here')
    if isinstance(node, ast.Name):
        if node.id == '__file__':
            return str(script)
        if node.id == 'Path':
            return 'Path'                              # only ever used as Path(...)
        if node.id in env:
            return env[node.id]
        raise Unsupported(f'{E_UNBOUND} name {node.id!r} is not a path bound in this module')
    if isinstance(node, ast.Attribute):
        if node.attr in PATH_ATTRS:
            base = evaluate(node.value, env, script)
            if not isinstance(base, Resolved):
                raise Unsupported(f"{E_UNSUPPORTED} .{node.attr} on a non-path")
            if not base.exact:
                raise Unsupported(f"{E_UNSUPPORTED} .{node.attr} applied after an unknown component")
            return Resolved(base.path.parent)
        raise Unsupported(f"{E_UNSUPPORTED} attribute .{node.attr}")
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Name) and f.id == HELPER:
            # Routed through research/outputs.py, which validates the name at run time and
            # is tested directly by tests/test_output_helper.py.  Nothing is inferred here.
            if len(node.args) != 1:
                raise Unsupported(f'{E_HELPER} {HELPER}() takes exactly one name')
            return Resolved(BUILD, exact=False)
        if isinstance(f, ast.Name) and f.id == 'Path' and len(node.args) == 1:
            arg = evaluate(node.args[0], env, script)
            if isinstance(arg, Resolved):
                return arg
            if arg is None:
                raise Unsupported(f"{E_UNSUPPORTED} Path() of a value not known statically")
            return Resolved(Path(arg))
        if isinstance(f, ast.Attribute) and f.attr in PATH_CALLS and not node.args:
            base = evaluate(f.value, env, script)
            if not isinstance(base, Resolved):
                raise Unsupported(f"{E_UNSUPPORTED} .{f.attr}() on a non-path")
            return Resolved(base.path.resolve(), base.exact)
        raise Unsupported(f"{E_UNSUPPORTED} call {ast.unparse(f)}(...)")
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = evaluate(node.left, env, script)
        if not isinstance(left, Resolved):
            raise Unsupported(f"{E_UNSUPPORTED} left operand of / is not a path")
        if not left.exact:
            # the reviewer's escape: a later component after an unknown one is a directory,
            # and an unknown directory can carry the destination anywhere.
            raise Unsupported(f"{E_UNKNOWN_DIR} component joined after an unknown "
                              f"directory component")
        right = evaluate(node.right, env, script)
        if isinstance(right, Resolved):
            raise Unsupported(f"{E_UNSUPPORTED} right operand of / is itself a path")
        return Resolved(left.path / _component(right))
    raise Unsupported(f"{E_UNSUPPORTED} expression form {type(node).__name__}")


def bind_paths(tree, script):
    """Bind top-level names to paths by EVALUATION, never by execution.

    Only names that `trusted_module_values` vouches for are bound: a name rebound anywhere
    else in the module, in one of the binding forms `all_binding_sites` enumerates -- a
    function parameter, say -- resolves to nothing here, so an expression using it is
    reported rather than silently resolved against the module's value.

    This is a statement about the source as written, in the supported syntax.  It does not
    establish what the module does at run time.
    """
    trusted = set(trusted_module_values(tree))
    env = {}
    for stmt in tree.body:
        if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and stmt.targets[0].id in trusted):
            continue
        try:
            value = evaluate(stmt.value, env, script)
        except Unsupported:
            continue                                   # not a path expression; leave unbound
        if isinstance(value, Resolved) and value.exact:
            env[stmt.targets[0].id] = value
    return env


def _open_kind(node, first_arg_is_mode=False):
    args = node.args
    mode = (args[0] if args else None) if first_arg_is_mode else (args[1] if len(args) > 1 else None)
    for kw in node.keywords:
        if kw.arg == 'mode':
            mode = kw.value
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return 'write' if any(ch in mode.value for ch in 'wax+') else 'read'
    return 'read' if mode is None else 'write'


def bound_in(node):
    """Every name a function scope binds: parameters, assignments, loops, comprehensions."""
    names = set()
    a = node.args
    for grp in (a.posonlyargs, a.args, a.kwonlyargs):
        names.update(x.arg for x in grp)
    for x in (a.vararg, a.kwarg):
        if x:
            names.add(x.arg)
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
            names.add(sub.id)
        elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(sub.name)
    return names


def io_sites(node, shadowed=frozenset()):
    """(lineno, path-expression node, kind, names shadowed by enclosing function scopes).

    Recurses through every node, carrying the names each enclosing function binds, because a
    module-level `level = 3` says nothing about the `level` inside `def probe(level)`.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        shadowed = shadowed | bound_in(node)
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr in READ_METHODS:
            yield node.lineno, f.value, 'read', shadowed
        elif isinstance(f, ast.Attribute) and f.attr in WRITE_METHODS:
            yield node.lineno, f.value, 'write', shadowed
        elif (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
              and f.value.id in ('np', 'numpy') and node.args):
            if f.attr in NP_READERS:
                yield node.lineno, node.args[0], 'read', shadowed
            elif f.attr in NP_WRITERS:
                yield node.lineno, node.args[0], 'write', shadowed
        elif isinstance(f, ast.Name) and f.id == 'open' and node.args:
            yield node.lineno, node.args[0], _open_kind(node), shadowed
        elif isinstance(f, ast.Attribute) and f.attr == 'open':
            # Path.open(...) -- the receiver is the path, and the mode is argument 0.
            yield node.lineno, f.value, _open_kind(node, first_arg_is_mode=True), shadowed
    for child in ast.iter_child_nodes(node):
        yield from io_sites(child, shadowed)


def mkdir_targets(tree):
    return {n.func.value.id for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == 'mkdir' and isinstance(n.func.value, ast.Name)}


def imports_helper(tree):
    return any(isinstance(n, ast.ImportFrom) and n.module == 'outputs'
               and any(a.name == HELPER for a in n.names) for n in ast.walk(tree))


scripts = sorted(p for p in RESEARCH.glob('*.py') if p.name != 'outputs.py')
# This regeneration step continues two shipped certificates rather than an
# archived solver run. Permit precisely those immutable inputs for this script;
# all writes still go to build/, and other proof files are not permitted here.
CERTIFICATE_INPUTS = {
    'derive_penalty_boundary.py': {
        (ROOT / 'proofs/penalty_endpoint_certificate.json').resolve(),
        (ROOT / 'proofs/sharp_qubit_certificate.json').resolve(),
    },
}
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
    if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == HELPER
           for n in ast.walk(trees[p])) and not imports_helper(trees[p]):
        fails.append(f"{rel}: calls {HELPER}() without importing it from research/outputs.py")
    n_sites = 0
    for lineno, expr, kind, shadowed in sorted(io_sites(trees[p]),
                                               key=lambda t: (t[0], t[2])):
        n_sites += 1
        where, shown = f"{rel}:{lineno}", ast.unparse(expr)
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            fails.append(f"{where}: {E_LITERAL} {kind} is bound to the string literal {shown}, "
                         f"not to a path -- parenthesize the path expression")
            continue
        try:
            local = {k: v for k, v in env.items() if k not in shadowed}
            r = evaluate(expr, local, p)
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
                fails.append(f"{where}: {E_OUTSIDE} writes to {resolved}, outside the output "
                             f"directory {BUILD}")
            else:
                print(f"  PASS write resolves into build/: {where} -> "
                      f"{resolved.relative_to(ROOT)}{note}")
        elif BUILD in resolved.parents:
            fails.append(f"{where}: {E_READ_GENERATED} reads the generated file "
                         f"{resolved.relative_to(ROOT)}; discovery inputs must come from the "
                         f"source tree")
        elif (RESEARCH.resolve() not in resolved.parents
              and resolved not in CERTIFICATE_INPUTS.get(p.name, set())):
            fails.append(f"{where}: {E_OUTSIDE} `{shown}` resolves outside research/: {resolved}")
        elif r.exact and not resolved.is_file():
            fails.append(f"{where}: {E_MISSING} `{shown}` resolves to {resolved}, which does not exist")
        else:
            print(f"  PASS read resolves: {where} -> {resolved.relative_to(ROOT)}{note}")
    if n_sites == 0:
        print(f"  PASS no filesystem access: {rel}")

# 3. a script that writes routes its writes through an OUTPUT_DIR that resolves to build/
for p in scripts:
    if not any(k == 'write' for _, _, k, _s in io_sites(trees[p])):
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
print("\nPASS in the supported syntax, every static path in the current discovery scripts "
      "resolves where it should,\n     and every computed file name is routed through "
      "research/outputs.py:output_path.  No code was executed.\n     This is a check of the "
      "documented convention in these scripts, not an analysis of arbitrary Python.")
