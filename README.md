# Schmidt-number witness

An exact, dependency-free certificate that a joint-probability-penalized M3322 functional is
bounded by 7 for **every Schmidt-number-two quantum behavior**, with an explicit qutrit
realization that exceeds it — so the witness certifies Schmidt number at least three. The same
functional is a facet of the two-sided partial-locality hull, which is where it came from and
is reported here as a supporting result. Also included: a certified lower bound on the quantum
remainder in decompositions with a Schmidt-number-two component, and a **strengthened
functional** `G = F + 3.83689 p` that keeps the Schmidt-number-two bound while detecting
qutrit behaviors the original misses.

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
| Smallest universally valid penalty `alpha_star` in `M_A <= 6 + alpha p`, `p = P(00\|10)` | certified to `(0.1631016, 0.16311]`; exact value **open** |
| Qutrit realization for the strengthened `G = F + 3.83689 p` | `G = 7.0928393387`, white-noise tolerance `1.5136%` |
| Where `F = 7` is attained on Schmidt number two | exactly a four-simplex of five local deterministic behaviors — and the same face for every `F + eps p`, `0 <= eps <= 3.83689` |

The remainder figure is a certified lower bound for the supplied behavior. It is not a measured
fraction of experimental runs and not a proven optimal decomposition cost.

The last row is about `F` again: the sharp bound is attained **only** locally, and only inside
that four-simplex. It classifies observed behaviors, not states — deterministic measurements can
reach `F = 7` on an entangled state while revealing none of its entanglement.

The two rows before it concern a **different functional**. `F` does two things at once — it is a
facet of the partial-local hull `H` *and* it is bounded on Schmidt number two. The strengthened
`G = F + eps p` keeps only the second: `proofs/verify_penalty_not_partial_local.py` proves,
from this repository's own facet certificate, that `G <= 7` fails on `H` for **every** `eps > 0`
— one of the fifteen facet-defining points has `F = 7` and `p = 1/3`. Read
`docs/CERTIFICATE_PENALTY_ENDPOINT.md` §0 before carrying any `F` statement across to `G`.

Consequently `F > 7` certifies Schmidt number at least three, and separately excludes the
two-sided compatible-pair mixture class. One functional does both.

## Verifying

**[`VERIFY.md`](VERIFY.md) — one command, what it establishes, and what it does not.**
Verifying these proofs does not require rerunning the search that found them.

Two certificate guides are written for a reader who wants to inspect the mathematics before
running code: [`docs/CERTIFICATE_SHARP_BOUND.md`](docs/CERTIFICATE_SHARP_BOUND.md) for the
sharp Schmidt-number-two bound, with a proof map separating the machine-checked steps from the
mathematical ones, and [`docs/CERTIFICATE_FACET.md`](docs/CERTIFICATE_FACET.md) for the
two-sided facet. A third,
[`docs/CERTIFICATE_PENALTY_ENDPOINT.md`](docs/CERTIFICATE_PENALTY_ENDPOINT.md), covers the
strengthened penalty and — in its §0 — exactly which earlier results do *not* carry over to it.
A fourth, [`docs/CERTIFICATE_EQUALITY_FACE.md`](docs/CERTIFICATE_EQUALITY_FACE.md), covers the
equality face; it was integrated only after the internal review recorded in
[`docs/review_2026-09-07_equality_face.md`](docs/review_2026-09-07_equality_face.md).

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
python tests/verify_facet_independent.py     # independent reconstruction, no dependencies
python tests/test_research_paths.py          # discovery input/output paths
python tests/test_docs_consistency.py        # documented paths exist; no unreferenced script
python tests/test_comparison_acceptance.py   # corrupt the comparison data, require rejection
python tests/test_output_helper.py           # the validated output-path helper
python tests/test_checker_mutations.py       # replay the defects the checkers once accepted
python tests/verify_endpoint_independent.py  # the endpoint by three non-proof-path routes
python tests/test_endpoint_mutations.py      # corrupt each endpoint certificate (~6 min)
python tests/verify_equality_face_independent.py  # exact simplex; reads no supplied dual (~4 min)
python tests/test_equality_face_mutations.py      # corrupt the equality-face certificate (~3 min)
python research/audit_catalog_folds.py       # comparison only, not a proof gate
python research/legacy/verify_routing.py --legacy-routing   # historical; no current claim
python manifest.py check                     # hash and coverage (needs a checkout)
python make_snapshot.py                      # a self-contained, Git-free verification archive
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
| `proofs/verify_qutrit.py` | `proofs/qutrit_certificate.json` | exact qutrit Born probabilities from Gaussian-integer data: `F = 7.0129123854899715 > 7` |
| `proofs/verify_m3322_corollary.py` | — | bounds our own claim: the *valid inequality* `F <= 7` follows from a published one-sided facet plus positivity |
| `proofs/verify_novelty_comparison.py` | — | the counterweight: the shipped behavior satisfies every relabeled ordinary I3322/M3322/CHSH score threshold while violating `F <= 7`, and `F` is not either family tilted by a one-party marginal |
| `proofs/verify_i3322_family.py` | — | the same for the published correlation-weighted `I3322(c)` family, for **every** `c >= 1` and every relabeling, against a qubit benchmark derived here from the Born rule |
| `proofs/verify_penalty_endpoint.py` | `proofs/penalty_endpoint_certificate.json`, `proofs/penalty_branch_certificates.json`, `proofs/penalty_lower_certificate.json` | `F + 3.83689 p <= 7` on Schmidt number two, from a second positive-definite 70×70 Gram on the same word basis, twelve exact no-signaling duals for the deterministic-observable branches, and an explicit two-qubit strategy pinning `alpha_star` from below |
| `proofs/verify_improved_qutrit.py` | `proofs/improved_qutrit_certificate.json` | all 36 Born probabilities rebuilt from raw integers: Schmidt rank three by a nonzero determinant, `G = 7.0928393387 > 7`, original `F = 6.4692250395 <= 7`, and the exact white-noise threshold |
| `proofs/verify_penalty_not_partial_local.py` | `proofs/facet_certificate.json` | the scope guard: `G <= 7` is **false** on `H` for every `eps > 0`, proved at one of the repository's own facet-defining points |
| `proofs/verify_equality_face.py` | `proofs/equality_face_certificate.json` | `S2` intersected with `{F = 7}` is exactly a four-simplex of five local deterministic behaviors: 48 deterministic-observable patterns closed by 665 exact forced-zero duals plus a projector-equality closure, and the same face for the whole certified family |

| Path | Role |
|---|---|
| `docs/` | model and geometry, the two certificate guides, the sharp proof, prior-art status, and the dated independent AI reviews |
| `tests/` | adversarial corruption tests, the optimized-execution regression, documentation and discovery-path checks, and `tests/verify_sos_independent.py`, a second implementation of the SOS check deliberately not shared with the primary verifier |
| `research/` | discovery code that produced the certificates: SDP search, rational rounding, counterexample searches. Not part of any proof. `research/endpoint_numerics.json` is the one committed result file here, and it is **numerical evidence only** — a stationary point for `alpha_star`, carrying its own disclaimer, on which no certified claim rests |
| `paper/` | the manuscript source and its build script. A **review draft**: unpublished, no author identity, journal status, priority or expert validation asserted. The PDF is git-ignored — build it with `bash paper/build.sh` |
| `research/legacy/` | the historical routing/record calculation the qutrit certificate originated from, with its original certificate byte for byte. Supports no current claim |

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
has taken place; the reviews in `docs/review_2026-09-06_ai.md` and `docs/review_2026-09-07_ai.md` are by AI systems (Claude and ChatGPT/Astra respectively). The global quantum
maximum of `F` and the tight decomposition cost are unresolved. Experimental feasibility is
not demonstrated — the quantum violation of `F` is `0.0129`, and the corresponding tolerance to
**uniform white-noise admixture of the output distribution** is roughly `0.18%`. Under the same
uniform-output-noise model, the supplied strengthened-witness realization tolerates
approximately 8.2 times more noise than the supplied original realization. This compares
different functionals and realizations, not their proven optimal robustness. Neither figure is
a detection efficiency, a visibility, or a demonstrated experimental tolerance. The exact
optimal penalty `alpha_star` is bracketed but **not determined**, and what happens to the
equality face at that exact critical penalty is a separate open question. The equality theorem's
Hilbert-space argument, its five projector rules and its POVM/compression reduction are prose,
not machine-checked; `docs/CERTIFICATE_EQUALITY_FACE.md` §6 marks which steps are which. Nothing here concerns faster-than-light communication,
observer-relative events, or an interpretation of quantum mechanics.

## License, citation and provenance

**Every file in this repository is MIT licensed** under `LICENSE`, copyright 2026
Steven W. Jones — sources, certificate data and documentation alike. There is no dual
license. `CITATION.cff` carries the citation metadata; `CONTRIBUTING.md` describes what a
change to a certificate must demonstrate.

### Which parts were written by which system

This repository was produced by **two AI systems working adversarially against each other**,
directed by the owner, who is not a physicist: **Claude (Anthropic)** and **ChatGPT (OpenAI),
working as "Astra"**. Everything below is contributed by the owner under the repository's
license. No third-party code has been imported; record the origin and license here before
adding any.

| Artifact | Origin |
|---|---|
| `docs/review_2026-09-06_ai.md` | review by Claude |
| `tests/verify_sos_independent.py` | written by Claude alongside that review |
| `docs/review_2026-09-07_ai.md` | Claude's condensed record of a review **by Astra**; the findings are Astra's |
| `paper/manuscript.md` | written **by Astra**, installed here near-verbatim (paths repointed only) |
| `research/inputs/catalog_coefficients.json` | the 129 catalogue vectors, extracted **by Astra** from arXiv:0810.1615 Table I |
| `research/audit_catalog_folds.py` | adapted from **Astra's** fold search |
| `docs/SCHMIDT_NUMBER_BOUND.md` §2–3 | the constructive binary-POVM and Schmidt-compression proof is **Astra's**, written up here |
| the qubit benchmark constructions in `proofs/verify_novelty_comparison.py` and `proofs/verify_i3322_family.py` | the states and measurements are **Astra's**; the verifier code is Claude's, and each construction was re-derived independently before being adopted |
| the interval construction in `tests/verify_facet_independent.py` | method described **by Astra**; implementation is Claude's |
| `proofs/penalty_endpoint_certificate.json`, `proofs/penalty_branch_certificates.json`, `proofs/penalty_lower_certificate.json`, `proofs/improved_qutrit_certificate.json`, `research/endpoint_numerics.json` | the certificate **data** is **Astra's**; every claim it makes was re-derived here before adoption, and the verifiers, the independent checker and the mutation suite around it are Claude's |
| `proofs/equality_face_certificate.json` and the equality argument it certifies | **Astra's**; held out of the repository until reviewed in `docs/review_2026-09-07_equality_face.md`, and re-derived here by an exact rational simplex that reads none of its duals |
| everything else — verifiers, certificates, tests, other docs | Claude |

Neither system's output has been reviewed by a human domain expert. Where one system's
mathematics was adopted by the other it was re-derived first, and the specific re-derivations
are named rather than assumed: the qubit benchmarks are rebuilt symbolically in
`proofs/verify_i3322_family.py` and `proofs/verify_novelty_comparison.py`, and the geometry and
Born reconstruction are redone from different mathematics in
`tests/verify_facet_independent.py`. Two systems participating does not by itself make any
other statement independent. Disagreements that surfaced are recorded in the review documents
rather than silently reconciled.
