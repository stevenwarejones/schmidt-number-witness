"""The one supported way for a discovery script to name a generated file.

Every write under research/ goes to the git-ignored build/ directory.  Static file names can
be checked by reading the source; names computed at run time cannot, and three rounds of
review demonstrated that trying to prove them safe by inference does not converge -- each
round closed the reported binding forms and the next round found others (annotated
assignment, assignment inside a conditional, loop variables, `match` pattern capture, a
shadowed `int`).

So dynamic names are validated HERE, at run time, where the value actually exists:

    from outputs import output_path
    output_path(f'clifford_level{level}.json').write_text(...)

`tests/test_research_paths.py` then only has to check the CONVENTION -- that scripts use this
helper for computed names -- which is a claim it can actually support.

This is a programming convention plus a validation layer.  It is not a sandbox: a script that
wants to write elsewhere can simply not call this function, and no source lint over arbitrary
Python could prevent that.  What it does give is that every generated file this project
actually produces is named by a checked, single-component filename inside build/.
"""
from pathlib import Path

BUILD = (Path(__file__).resolve().parent.parent / 'build')


def output_path(name):
    """build/<name>, or raise. `name` must be one ordinary filename component."""
    if not isinstance(name, str):
        raise TypeError(f'output name must be a string, got {type(name).__name__}')
    if not name or name in ('.', '..'):
        raise ValueError(f'refusing empty or relative output name {name!r}')
    if '/' in name or '\\' in name or '\0' in name:
        raise ValueError(f'refusing output name containing a path separator: {name!r}')
    if Path(name).is_absolute() or len(Path(name).parts) != 1:
        raise ValueError(f'refusing output name that is not a single component: {name!r}')
    BUILD.mkdir(parents=True, exist_ok=True)
    resolved = (BUILD / name).resolve()
    if resolved.parent != BUILD.resolve():
        raise ValueError(f'output name escapes build/: {name!r} -> {resolved}')
    return resolved
