# Two-sided partial locality

Exact certificates for a two-sided partial-locality facet and a sharp Schmidt-number-two
bound for the same Bell functional. The repository includes a violating qutrit realization
and a certified lower bound on the quantum remainder in decompositions with a
Schmidt-number-two component.

This is a public research repository, not a paper announcement. Priority is unresolved and
no human expert has reviewed the results.

## Results

For the Bell functional `F` defined in [docs/THEORY.md](docs/THEORY.md):

| Result | Value |
|---|---|
| Face dimensions of `F = 7` on `H_A` / `H_B` / `H = conv(H_A u H_B)` | 13 / 13 / 14, against ambient dimension 15 |
| So `F <= 7` is a facet of the two-sided hull, and of neither one-sided hull | — |
| Sharp bound for every Schmidt-number-at-most-two behavior | `F <= 7`, attained |
| Supplied qutrit realization | `F = 7.0129123854899715...` |
| Dimension-unrestricted quantum upper bound (certified, not claimed sharp) | `F <= 7.041387041` |
| Quantum remainder in any Schmidt-two-plus-remainder decomposition of that behavior | `> 31.19%` |

The last figure is a certified lower bound for the supplied behavior. It is not a measured
fraction of experimental runs and not a proven optimal decomposition cost.

Consequently `F > 7` certifies Schmidt number at least three, and separately excludes the
two-sided compatible-pair mixture class. One functional does both.

## Quick start

Tested on CPython 3.10.12; CI also runs 3.12. The sharp Schmidt-number-two verifier is
standard-library only. The face-dimension and Pauli checks need `sympy`, and the numerical
cross-check needs `numpy` — both are in `requirements.txt`. SDP solvers are needed only for
discovery (`research/requirements.txt`), never to verify.

```sh
python -m pip install -r requirements.txt    # needed by everything except the sharp verifier
python proofs/verify_sharp_qubit.py          # the sharp bound alone: no dependencies
python run_checks.py                         # active exact certificate chain
python tests/adversarial_sharp_checks.py     # corruption and -O rejection
python tests/test_standalone_optimized.py    # standalone verifiers reject under -O too
python tests/check_sharp_pauli.py            # exact Pauli reconstruction
python tests/verify_sos_independent.py       # numerical, independent of the word reduction
python tests/test_research_paths.py          # discovery input/output paths
python tests/test_docs_consistency.py        # documented paths exist; no unreferenced script
python manifest.py check                     # hash and coverage
```

`run_checks.py` resolves paths against itself and can be run from any working directory.
Verification never rewrites the manifest or any certificate.

## Proof map

Every verifier reruns its claim from the certificate data in the same directory. All are
exact; none calls a solver.

| Verifier | Certificate | Claim |
|---|---|---|
| `proofs/verify_facet.py` | `proofs/facet_certificate.json` | `F <= 7` on all six partial-local classes, and the `F=7` face of `H` has affine dimension 14 against `dim H = 15` — a facet of `H`, though not of the local polytope |
| `proofs/verify_face_dimensions.py` | `proofs/face_dimension_points.json` | each one-sided face has dimension 13, by exact dual-support upper bounds and matching explicit points |
| `proofs/verify_sharp_qubit.py` | `proofs/sharp_qubit_certificate.json` | `F <= 7` for every Schmidt-number-two behavior, from a 70×70 rational Gram positive definite by exact LDL. Standard library only |
| `proofs/verify_quantum_upper.py` | `proofs/quantum_upper_certificate.json` | `F <= 7.041387041` with no dimension-specific identities, which is what makes the qutrit violation a bounded fraction of the available room |
| `proofs/verify_routing.py` | `proofs/routing_certificate.json` | exact qutrit Born probabilities from Gaussian-integer data: `F = 7.0129123854899715 > 7` |
| `proofs/verify_m3322_corollary.py` | — | bounds our own claim: the *valid inequality* `F <= 7` follows from a published one-sided facet plus positivity |
| `proofs/verify_novelty_comparison.py` | — | the counterweight: the shipped behavior satisfies every relabeled ordinary I3322/M3322/CHSH score threshold while violating `F <= 7`, and `F` is not either family tilted by a one-party marginal |

| Path | Role |
|---|---|
| `docs/` | model and geometry, the sharp proof, prior-art status, and the dated independent AI reviews |
| `tests/` | adversarial corruption tests, the optimized-execution regression, documentation and discovery-path checks, and `tests/verify_sos_independent.py`, a second implementation of the SOS check deliberately not shared with the primary verifier |
| `research/` | discovery code that produced the certificates: SDP search, rational rounding, counterexample searches. Not part of any proof |

## Limitations

The *valid inequality* `F <= 7` on `H` is **not new**: it follows in three lines from a
published one-sided facet plus positivity, as proved exactly by
`proofs/verify_m3322_corollary.py` and set out in `docs/PRIOR_ART.md`. What that
derivation does not cover is the facet property and the sharp Schmidt-number-two bound.
Pointing the other way, `proofs/verify_novelty_comparison.py` proves exactly that the
shipped behavior satisfies every relabeled ordinary I3322, M3322 and CHSH score threshold
while violating `F <= 7`, and that `F` has nine nonzero correlator coefficients where every
relabeling of I3322 and M3322 has eight — so `F` is not either family tilted by a one-party
marginal, which is the shape of the published detection-efficiency dimension witnesses. Both
are exact, and neither is a novelty clearance; `docs/PRIOR_ART.md` states what the audits did
not reach.
The rest of the prior-art audit is incomplete and priority is unresolved. No human expert or peer review
has taken place; the reviews in `docs/review_2026-09-06_ai.md` and `docs/review_2026-09-07_ai.md` are by AI systems. The global quantum
maximum of `F` and the tight decomposition cost are unresolved. Experimental feasibility is
not demonstrated — the quantum violation is `0.0129` and the corresponding uniform-noise
tolerance is roughly `0.18%`. Nothing here concerns faster-than-light communication,
observer-relative events, or an interpretation of quantum mechanics.

## License, citation and provenance

**Every file in this repository is MIT licensed** under `LICENSE`, copyright 2026
Steven W. Jones — sources, certificate data and documentation alike. There is no dual
license. `CITATION.cff` carries the citation metadata; `CONTRIBUTING.md` describes what a
change to a certificate must demonstrate.

`docs/review_2026-09-06_ai.md`, `docs/review_2026-09-07_ai.md` and `tests/verify_sos_independent.py` contain prose and code written by AI systems
(Claude, Anthropic) acting as an adversarial reviewer, contributed by the owner under the same
terms. No third-party code has been imported; record the origin and license here before adding
any.
