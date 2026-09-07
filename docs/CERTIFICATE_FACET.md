# Certificate guide: the two-sided partial-locality facet

One page, companion to `docs/CERTIFICATE_SHARP_BOUND.md`.

**Verifiers** `proofs/verify_facet.py` and `proofs/verify_face_dimensions.py`.
**Certificates** `proofs/facet_certificate.json`, `proofs/face_dimension_points.json`.

## The claim

> `F <= 7` is valid on `H = conv(H_A ∪ H_B)`, and its `F = 7` face has affine dimension 14
> against `dim H = 15`. So it is a **facet of `H`**, and of neither one-sided hull — those
> faces have dimension 13 each.

Read this alongside `docs/PRIOR_ART.md`: the **valid inequality** is prior art, a corollary of
a published one-sided facet plus positivity, proved against us in
`proofs/verify_m3322_corollary.py`. The facet property is not covered by that derivation.

## The sets

- `H_A` — nonsignaling behaviors that are Bell-local on some **pair** of Alice's settings
  together with all of Bob's; the convex hull over the three pairs.
- `H_B` — the same with the parties exchanged.
- `H = conv(H_A ∪ H_B)`, the **two-sided** hull. The published comparator characterizes the
  one-sided hull only.
- `C` — behaviors from setting-independent mixtures of local quantum implementations in which
  one party's pair is jointly measurable. `C ⊆ H ∩ Q` is an **inclusion**; no equality is
  established, and `H` is strictly larger than `C`.

Variable ordering and the outcome convention are as in `docs/CERTIFICATE_SHARP_BOUND.md`.

## The certificate

| Field | Meaning |
|---|---|
| `w` | the 15 coefficients of `F` |
| `partial_hull_duals` | six records, one per `(side, pair)`: nonnegative rational weights on the positivity and 2×2 CHSH rows of that constituent |
| `saturating_points` | 15 behaviors with `F = 7`, each with `side`, `pair`, and an explicit deterministic `local_model` |
| `local_tight_count`, `local_face_rank`, `H_face_rank` | 5, 4 and 14 |

## What the verifiers check

**Validity, six times.** For each constituent, the weighted sum of its rows equals
`[7] + [-w]` exactly, with all weights nonnegative. That is a dual certificate: `7 - F` is a
nonnegative combination of inequalities valid on that constituent, so `F <= 7` there, hence on
the hull. Coverage is asserted — the six records must be exactly the six `(side, pair)` pairs,
no duplicates and none missing — in **both** verifiers; removing any one is rejected.

**A note on what this rests on.** Positivity plus all 2×2 CHSH inequalities is complete for
binary 2×3 locality (Fine's theorem plus an interval-intersection argument). But the
upper-bound duals do **not** need that completeness: positive combinations of *necessary*
inequalities already prove validity. Completeness matters only where these rows are used as a
membership test.

**Dimension, from both sides.** The upper bound comes from the dual support: at a saturating
point every row with strictly positive weight must vanish, and the nullspace of those active
rows caps the face. The lower bound comes from exhibiting points. For the two-sided face,
15 affinely independent saturating points give rank 14; each carries a deterministic local
model checked to reproduce its probabilities exactly, so membership is verified rather than
asserted.

There is also a short analytic route to the one-sided upper bound: on `H_A`, `F = 7` forces
`p(00|10) = 0` through the `M_A` identity, and on `H_B` it forces `p(11|22) = 0`. Each is an
affine constraint independent of `F = 7`, so each one-sided face has dimension at most 13.

**Not a facet of the local polytope.** `F` is tight on only 5 of the 64 local vertices, affine
rank 4 against local dimension 15. It is a valid non-facet inequality there.

## The attaining example

`proofs/verify_qutrit.py` gives `F = 7.0129123854899715 > 7`, so that behavior is outside `H`,
and hence outside `C`. The exclusion runs one way only: a violation puts a behavior outside
`H`; satisfying `F <= 7` implies nothing.

## Corruption tests

Deleting any one of the six duals is rejected by both verifiers. Altering a dual weight, a
saturating point, or a local model is rejected. `tests/test_standalone_optimized.py` checks
that rejection also holds under `python -O`.
