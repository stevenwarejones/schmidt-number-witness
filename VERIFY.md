# Verification in one command

```sh
python -m pip install -r requirements.txt
python run_checks.py
```

That is the whole thing. It takes well under a minute and needs no SDP solver, no network, and
no Git history.

**Verifying these proofs does not require rerunning the search that found them.** The
certificates are data; the verifiers re-derive every claim from that data in exact arithmetic.
The discovery code under `research/` produced the certificates and is never invoked by
verification. If you want to regenerate a certificate from scratch that is a separate,
expensive undertaking — see `research/README.md` — and it is not what `run_checks.py` does.

## Even less than that

The headline bound alone needs **nothing installed at all**:

```sh
python proofs/verify_sharp_qubit.py     # Python 3.10+, standard library only
```

There are two entry points a reader most likely wants, and neither touches research code:

| Question | Command |
|---|---|
| Is the universal bound `F <= 7` for Schmidt number two real? | `python proofs/verify_sharp_qubit.py` |
| Is there really a quantum behavior exceeding it? | `python proofs/verify_qutrit.py` |

## What `run_checks.py` establishes

| | Claim | Verifier |
|---|---|---|
| 1 | `F <= 7` on all six partial-local classes, and the `F = 7` face of `H` has affine dimension 14 against `dim H = 15` — a facet of `H` | `proofs/verify_facet.py` |
| 2 | each one-sided face has dimension 13 | `proofs/verify_face_dimensions.py` |
| 3 | the valid inequality `F <= 7` on `H` is a **corollary of published work** plus positivity | `proofs/verify_m3322_corollary.py` |
| 4 | `Q` satisfies every relabeled ordinary I3322/M3322/CHSH qubit-achievable threshold while violating `F <= 7` | `proofs/verify_novelty_comparison.py` |
| 5 | the same for the correlation-weighted `I3322(c)` family, for every `c >= 1` | `proofs/verify_i3322_family.py` |
| 6 | exact qutrit Born probabilities: `F = 7.0129123854899715 > 7` | `proofs/verify_qutrit.py` |
| 7 | `F <= 7` for **every Schmidt-number-two behavior** | `proofs/verify_sharp_qubit.py` |
| 8 | `F <= 7.041387041` with no dimension assumption | `proofs/verify_quantum_upper.py` |
| 9 | the strengthening `F + 3.83689 p <= 7` on Schmidt number two, i.e. `M_A <= 6 + 0.16311 p`, against a lower strategy reaching `0.16310160` | `proofs/verify_penalty_endpoint.py` |
| 10 | a qutrit realization with `G = 7.0928393387` and `1.5136%` white-noise tolerance, which the original `F` does **not** detect | `proofs/verify_improved_qutrit.py` |
| 11 | that same strengthening is **not** valid on the partial-local hull `H`, for any `eps > 0` | `proofs/verify_penalty_not_partial_local.py` |
| 12 | `S2` intersected with `{F = 7}` is exactly a four-simplex of five local deterministic behaviours — and the same face for every `F + eps p` with `0 <= eps <= 3.83689` | `proofs/verify_equality_face.py` |
| 13 | a draft continuation of that Gram to its singular boundary: `alpha_star <= 0.1631067188466586...`, hence the quotable `0.16310672`. **Its arithmetic is exact; its equality and remainder arguments are prose awaiting review** | `proofs/verify_penalty_boundary.py` |

Check 13 subsumes checks 9 and 12: it re-runs both before printing anything of its own, so
`run_checks.py` calls it instead of running them twice and requires both of their conclusions to
appear in the transcript.

Checks 9–11 concern a **different functional**, `G = F + eps * p` with `p = P(00|10)`. Check 11
is the scope guard: `F` is both a facet of `H` and bounded on Schmidt number two, and `G` keeps
only the second property. `docs/CERTIFICATE_PENALTY_ENDPOINT.md` is the guide, and its §0 is the
part not to skip. Check 12 is about `F` again: it classifies where the sharp bound is attained.
Checks 9–12 add roughly 30 seconds, almost all of it exact rational LDL on a Gram whose least
pivot is `1.4 * 10^-7`.

Expected final output:

```
All exact checks passed: sharp bound 7, qutrit separation, and quantum remainder weight >31.19%.
Penalty endpoint: M_A <= 6 + 16311/100000 p on Schmidt number two, against a lower strategy at
0.16310160 -- and NOT valid on the partial-local hull H.
Equality face: F = 7 is attained on Schmidt number two only inside a four-simplex of local
behaviours, and the same face serves the whole certified family.
Global quantum maximum, tight decomposition cost, the exact optimal penalty alpha_star, the
equality face AT that critical penalty, novelty, and external review remain open.
```

Any failure raises a `CalledProcessError` and stops. Every verifier uses `assert` as a proof
gate and refuses to run under `python -O`, where assertions would be stripped;
`tests/test_standalone_optimized.py` checks that refusal.

## What it does NOT establish

- **Not novelty.** `docs/PRIOR_ART.md` states what is settled and what is open. The valid
  inequality on the partial-local hull is prior art; check 3 above proves that against us.
- **Not peer review.** No human domain expert has reviewed any of this. The reviews under
  `docs/` are by AI systems — Claude and ChatGPT ("Astra") — not by people.
- **Not authenticity or provenance.** `python manifest.py check` compares file hashes against
  the Git index: it is an integrity check on a checkout, and it refuses to run without one.
  `python manifest.py verify-archive` answers the different question a downloaded archive
  raises — do these files match the hashes shipped beside them, and is anything present
  unlisted — with no Git metadata. **Neither implies the other**, and neither is mathematical
  correctness, proof authenticity, or historical priority.
- **Not experimental feasibility.** For `F` the violation is `0.0129`, with roughly `0.18%`
  tolerance to uniform white-noise admixture of the output distribution. Under the same
  uniform-output-noise model, the supplied strengthened-witness realization tolerates
  approximately 8.2 times more noise than the supplied original realization. That compares
  different functionals and realizations, not their proven optimal robustness. Neither figure is
  a detection efficiency, a visibility, or a demonstrated experimental tolerance. **The
  white-noise model is stated exactly** in `docs/CERTIFICATE_PENALTY_ENDPOINT.md` §6: uniform
  outputs give `F(U) = 0` but `G(U) = eps/4`, so the threshold for `G` is
  `(G(Q)-7)/(G(Q)-eps/4)` and the naive `(G(Q)-7)/G(Q)` is wrong.
- **Not the optimal penalty.** `0.1631016 < alpha_star <= 0.16311` is certified from both
  sides; the exact value of `alpha_star` is undetermined, and `research/endpoint_numerics.json`
  records a numerical stationary point that is evidence and not a certificate. The equality-face
  corollary covers `0 <= eps <= 3.83689` and **stops there**: what happens at the exact critical
  penalty is a separate open question.
- **Not every step of the equality theorem.** Its Hilbert-space argument, its five projector
  rules, and its POVM/compression reduction are prose. `docs/CERTIFICATE_EQUALITY_FACE.md` §6
  marks which steps are machine-checked and which are not, and
  `docs/review_2026-09-07_equality_face.md` records what an internal review did and did not
  settle.
- **Not one step of the sharp bound.** The reduction from arbitrary binary POVMs and Schmidt
  rank two to the projective qubit case is a mathematical argument, not machine-checked. It is
  written out constructively in `docs/SCHMIDT_NUMBER_BOUND.md` §2–3 and mapped in
  `docs/CERTIFICATE_SHARP_BOUND.md`.

## Everything else

| Command | Purpose |
|---|---|
| `python tests/adversarial_sharp_checks.py` | corrupt the certificate, require rejection |
| `python tests/test_standalone_optimized.py` | the same under `python -O` |
| `python tests/check_sharp_pauli.py` | exact Pauli reconstruction of the identity |
| `python tests/verify_sos_independent.py` | a second implementation of the SOS check, sharing no code with the primary verifier |
| `python tests/verify_facet_independent.py` | an independent reconstruction of the geometry and the realization — local models built from scratch by Fine's theorem, Born rule from full 9×9 operators. Standard library only |
| `python tests/test_research_paths.py` | discovery scripts' input/output paths resolve |
| `python tests/test_docs_consistency.py` | documented paths exist; no unreferenced script |
| `python manifest.py check` | file hashes **and index coverage**; needs a checkout |
| `python manifest.py verify-archive` | file hashes only; works in an unpacked archive, no Git needed |
| `python make_snapshot.py` | build `build/verification-snapshot-<commit>.tar.gz`: extract it anywhere and it verifies itself |
| `python research/audit_catalog_folds.py` | a scoped comparison, not a proof gate |
| `python tests/test_comparison_acceptance.py` | corrupt Q and the catalogue, require both comparisons to reject |
| `python tests/test_output_helper.py` | the validated output-path helper accepts ordinary names and refuses escaping ones |
| `python tests/test_checker_mutations.py` | replay every defect the auxiliary checkers once accepted, and require rejection for the intended reason |
| `python tests/verify_endpoint_independent.py` | the endpoint certificate by three routes that are not the proof path — a second Clifford rewriting, exact Gaussian-rational qubit matrices with no normal ordering, and integer Bareiss minors — plus the branch duals rebuilt from the 36 probability positivity constraints, with an attaining behaviour exhibited for each. About 30 s |
| `python tests/test_endpoint_mutations.py` | corrupt each endpoint certificate and require rejection **for the intended reason**, including a Gram perturbation that leaves the operator identity exactly intact and destroys only positivity. About 6 minutes |
| `python tests/verify_equality_face_independent.py` | branch infeasibility and every forced zero re-derived by an exact rational simplex carried in the file, reading **no** supplied dual. It does *not* re-derive the projector rules or their closure, so it is not an independent proof of the theorem. Its numerical section reports and gates nothing. About 4 minutes |
| `python tests/test_equality_face_mutations.py` | corrupt the equality-face certificate and require rejection for the intended reason, including a single deleted forced zero that leaves every remaining dual exact and is caught only by the projector closure. About 3 minutes |
| `python research/legacy/verify_routing.py --legacy-routing` | historical; supports no current claim |
| `bash paper/build.sh` | build the manuscript into `build/paper/manuscript.pdf` (needs Pandoc + XeLaTeX) |

## Environment

Tested on CPython 3.10.12 with sympy 1.14.0 and numpy 2.2.6; CI also runs 3.12.
`proofs/verify_sharp_qubit.py` needs neither. SymPy is needed for the face-dimension verifier,
the exact qubit benchmarks and the Pauli check; NumPy for the independent SOS cross-check and
for loading archived inputs. SDP solvers appear only in `research/requirements.txt` and are
never needed to verify anything.

## Draft boundary continuation

The original endpoint transcript above remains correct for the original
certificate. The latest bound comes from `proofs/verify_penalty_boundary.py`,
which the full runner also executes. What is certified is the singular-continuation
bound, exactly: `alpha_star <= 0.1631067188466586...`, the exact rational living in
`proofs/penalty_boundary_certificate.json`. The quotable `alpha_star <= 0.16310672`
follows from it, and is quotable only because the exact rational has several
thousand digits.
The new conclusion follows only after the inherited endpoint and equality-face
verifiers succeed. New prose arguments still await separate review.

Run `python tests/test_penalty_boundary_mutations.py` for targeted corruptions
and dependency-failure controls. Read `docs/CERTIFICATE_PENALTY_BOUNDARY.md`
for the singular-kernel equality proof and the quadratic correction.
