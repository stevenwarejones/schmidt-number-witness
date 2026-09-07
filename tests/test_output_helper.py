"""research/outputs.py:output_path must accept ordinary names and refuse everything else.

The safety property for generated file names now lives in this helper rather than in a source
lint, because three rounds of review showed the lint could not carry it: proving a computed
name safe by inference kept admitting binding forms nobody had enumerated.  The helper
validates the actual value at run time, so it is checkable here, exhaustively over the cases
that matter.

If this file is weakened, the containment claim in tests/test_research_paths.py loses its
foundation -- that file checks only that scripts USE this helper.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are checks.")

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'research'))
from outputs import BUILD, output_path                                    # noqa: E402

fails = []

ACCEPT = ['clifford_level3.json', 'a.npz', 'x', 'name with spaces.txt',
          'clifford_scs_level10.npz', 'dots.in.name.json', '-leading-dash.json']

REFUSE = [
    ('', 'empty'),
    ('.', 'current directory'),
    ('..', 'parent directory'),
    ('../escaped.txt', 'traversal'),
    ('../../escaped.txt', 'double traversal'),
    ('sub/nested.json', 'separator'),
    ('sub\\nested.json', 'backslash separator'),
    ('/etc/passwd', 'absolute path'),
    ('a/../../b', 'traversal in the middle'),
    ('with\0null', 'NUL byte'),
]

for name in ACCEPT:
    try:
        got = output_path(name)
    except Exception as exc:                                              # noqa: BLE001
        fails.append(f"refused an ordinary name {name!r}: {type(exc).__name__}: {exc}")
        continue
    if got.parent != BUILD.resolve():
        fails.append(f"{name!r} resolved to {got}, whose parent is not {BUILD}")
    elif got.name != name:
        fails.append(f"{name!r} resolved to a different file name {got.name!r}")
    else:
        print(f"  PASS accepted, inside build/: {name!r}")

for name, why in REFUSE:
    try:
        got = output_path(name)
    except (ValueError, TypeError) as exc:
        print(f"  PASS refused ({why}): {name!r} -- {str(exc)[:60]}")
        continue
    except Exception as exc:                                              # noqa: BLE001
        fails.append(f"{name!r} ({why}) raised {type(exc).__name__}, expected ValueError")
        continue
    fails.append(f"ACCEPTED {name!r} ({why}) and returned {got} -- containment is broken")

for bad in (3, None, b'bytes.json', Path('a.json')):
    try:
        output_path(bad)
    except (ValueError, TypeError):
        print(f"  PASS refused a non-string name: {bad!r}")
    else:
        fails.append(f"accepted a non-string name {bad!r}")

# Whatever it returns must be inside build/, checked against the resolved directory itself.
for name in ACCEPT:
    p = output_path(name)
    if BUILD.resolve() != p.parent or not str(p).startswith(str(BUILD.resolve())):
        fails.append(f"{name!r} escaped build/: {p}")

# --- the resolved-parent branch, which no string test reaches ----------------------------
# Every case above is decided by inspecting the NAME.  The final check in output_path compares
# the RESOLVED destination's parent against the resolved build directory, and only the
# filesystem can exercise it: a name with no separators at all can still leave the directory
# if it is a symlink.  Skipping this branch would leave containment resting on string rules.
#
# Run against a TEMPORARY build directory, so the repository's own build/ is never touched.
import os                                                                 # noqa: E402
import tempfile                                                           # noqa: E402

import outputs                                                            # noqa: E402

if not hasattr(os, 'symlink'):
    fails.append('this platform has no os.symlink, so the resolved-parent branch is untested')
else:
    real_build = outputs.BUILD
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        outputs.BUILD = tmp / 'build'
        outputs.BUILD.mkdir()
        target = tmp / 'outside' / 'escaped.json'
        target.parent.mkdir()
        target.write_text('')
        try:
            os.symlink(target, outputs.BUILD / 'symlink_probe.json')
        except OSError as exc:                                            # noqa: BLE001
            fails.append(f'could not create a symlink to test that branch: {exc}')
        else:
            try:
                got = outputs.output_path('symlink_probe.json')
            except ValueError as exc:
                print(f"  PASS refused (symlink leaving the output directory): "
                      f"'symlink_probe.json' -- {str(exc)[:56]}")
            except Exception as exc:                                      # noqa: BLE001
                fails.append(f'symlink case raised {type(exc).__name__}, expected ValueError')
            else:
                fails.append(f'ACCEPTED a name resolving outside the output directory via a '
                             f'symlink: {got} -- containment rests on string rules alone')
        finally:
            outputs.BUILD = real_build

if fails:
    print("\nFAILED:")
    for f in fails:
        print("   " + f)
    raise SystemExit(1)
print(f"\nPASS output_path accepts {len(ACCEPT)} ordinary names and refuses "
      f"{len(REFUSE) + 5} escaping or ill-typed ones -- including a symlink that leaves the\n"
      f"     output directory, which is the one case the name rules alone cannot decide.")
