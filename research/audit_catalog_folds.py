"""Is F a four-setting catalogue inequality with settings identified?  Scoped answer: no match.

COMPARISON, NOT A PROOF.  This is discovery-side work and no claim in proofs/ or the paper
rests on it.  It is here because it is a finite, checkable question that a reviewer would
otherwise have to redo by hand.

Pal and Vertesi, arXiv:0810.1615, catalogue tight two-outcome Bell inequalities.  Their Table I
gives 129 four-setting J^n_4422 inequalities as integer coefficient vectors, archived verbatim
in research/inputs/catalog_coefficients.json.  The natural worry is that F is one of them with
Alice's and Bob's settings identified down to three -- a "fold".

For each party this file builds the 20 surjective reductions from four labels to three: the 12
signed pair identifications and the 8 deterministic substitutions.  Folding an inequality with
one map per party gives a three-setting functional, normalized by its coefficient gcd, and the
question is whether it lands in the 2304-element relabeling orbit of F.

    129 inequalities  x  20 Alice maps  x  20 Bob maps  =  51,600 reductions
    matches: 0

Two integrity checks make that number mean something.  Every one of the 129 source vectors is
independently confirmed to have classical maximum 0 in the source's probability convention --
which is a check on the COEFFICIENTS, not authentication of which published equation was
transcribed; a matching bound is necessary, not sufficient.  And a positive control lifts F
itself to four settings by adding an unused all-zero setting, then requires the fold to find it
again, so a search that could never match anything would fail here.  That control does not
split a nonzero row between two settings, and is weaker than one that did.

ORIGIN.  The 129 coefficient vectors were extracted from the paper's source by ChatGPT
("Astra"), whose fold search this is adapted from; see docs/review_2026-09-07_ai.md.  The
integrity checks below are what make the extraction usable without re-reading the source.

WHAT THIS DOES NOT COVER.  Not all 241 inequalities of that survey, and not all 175 four-setting
classes -- only the 129 rows of that one table.  Not arbitrary wirings, not positive
combinations of several inequalities, not five-setting scenarios, not non-surjective or
non-signed reductions.  Zero matches here is not evidence of novelty.  See docs/PRIOR_ART.md.

Reads its archived input; writes its report to the git-ignored build/.
"""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are integrity checks.")

import json
import math
from itertools import permutations, product
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'build'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CATALOG_PATH = RESEARCH_DIR / 'inputs' / 'catalog_coefficients.json'

rows = {int(k): v for k, v in json.loads(CATALOG_PATH.read_text()).items()}
assert set(rows) == set(range(1, 130)) and all(len(v) == 24 for v in rows.values())

W = (1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1)


def norm(v):
    g = math.gcd(*v)
    return tuple(x // g for x in v) if g else tuple(v)


def relabel(w, pa, pb, sa, sb, swap):
    a, b = w[:3], w[3:6]
    e = [w[6 + 3 * i:9 + 3 * i] for i in range(3)]
    if swap:
        a, b = b, a
        e = list(zip(*e))
    return (tuple(sa[i] * a[pa[i]] for i in range(3))
            + tuple(sb[j] * b[pb[j]] for j in range(3))
            + tuple(sa[i] * sb[j] * e[pa[i]][pb[j]] for i, j in product(range(3), repeat=2)))


orbit = {relabel(W, *args) for args in
         product(permutations(range(3)), permutations(range(3)),
                 product([-1, 1], repeat=3), product([-1, 1], repeat=3), [False, True])}
assert len(orbit) == 2304

# Canonical setting labels by first occurrence, first occurrence positive: the final orbit
# already contains every permutation and outcome flip, so fixing that gauge loses nothing.
maps = []
for labels in product(range(4), repeat=4):
    if not {1, 2, 3} <= set(labels):
        continue
    seen = []
    for x in labels:
        if x and x not in seen:
            seen.append(x)
    if seen != [1, 2, 3]:
        continue
    first = {x: labels.index(x) for x in (1, 2, 3)}
    for signs in product([-1, 1], repeat=4):
        if any(signs[i] != 1 for i in first.values()):
            continue
        maps.append(tuple(zip(labels, signs)))
assert len(maps) == 20


def fold(M, ma, mb):
    R = [[0] * 4 for _ in range(4)]
    for i, j in product(range(5), repeat=2):
        a, sa = (0, 1) if i == 0 else ma[i - 1]
        b, sb = (0, 1) if j == 0 else mb[j - 1]
        R[a][b] += sa * sb * M[i][j]
    return R[0][0], (tuple(R[i][0] for i in (1, 2, 3)) + tuple(R[0][j] for j in (1, 2, 3))
                     + tuple(R[i][j] for i, j in product((1, 2, 3), repeat=2)))


# Positive control: lift F to four settings by giving Alice an UNUSED fourth setting (an
# all-zero row), then require the fold to recover it.  This exercises the search end to end,
# so a fold procedure that could never match anything fails here.  It does NOT split a nonzero
# row across two settings, so it is a weaker control than that would be.
M = [[0] * 5 for _ in range(5)]
for i in range(3):
    M[i + 1][0] = W[i]
    M[0][i + 1] = W[i + 3]
for i, j in product(range(3), repeat=2):
    M[i + 1][j + 1] = W[6 + 3 * i + j]
assert any(norm(fold(M, a, b)[1]) in orbit for a, b in product(maps, repeat=2))

results = []
for n, v in sorted(rows.items()):
    a, b = v[:4], v[4:8]
    E = [v[8 + 4 * i:12 + 4 * i] for i in range(4)]
    # Source probability convention: classical maximum is zero.  A bad transcription fails here.
    maximum = max(sum(a[i] * x[i] for i in range(4)) + sum(b[j] * y[j] for j in range(4))
                  + sum(E[i][j] * x[i] * y[j] for i, j in product(range(4), repeat=2))
                  for x, y in product(product((0, 1), repeat=4), repeat=2))
    assert maximum == 0, (n, maximum)
    M = [[0] * 5 for _ in range(5)]
    M[0][0] = 2 * sum(a + b) + sum(map(sum, E))
    for i in range(4):
        M[i + 1][0] = 2 * a[i] + sum(E[i])
    for j in range(4):
        M[0][j + 1] = 2 * b[j] + sum(E[i][j] for i in range(4))
    for i, j in product(range(4), repeat=2):
        M[i + 1][j + 1] = E[i][j]
    for ma, mb in product(maps, repeat=2):
        const, w = fold(M, ma, mb)
        if norm(w) in orbit:
            results.append({'J': n, 'constant': const, 'scale': math.gcd(*w),
                            'Alice': ma, 'Bob': mb})

report = {'source': 'https://arxiv.org/abs/0810.1615', 'inequalities': 129,
          'maps_per_party': len(maps), 'comparisons': 129 * len(maps) ** 2,
          'functional_matches': results, 'target_orbit_size': len(orbit),
          'positive_control': True, 'all_source_local_bounds_verified': True}
(OUTPUT_DIR / 'catalog_fold_results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
print('\nCOMPARISON ONLY: zero matches over these reductions is not evidence of novelty. '
      'Scope is in the module docstring and docs/PRIOR_ART.md.')
