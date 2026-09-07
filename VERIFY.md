# Verification in one command

```sh
python -m pip install -r requirements.txt
python run_checks.py
```

That is the whole thing. It takes a few seconds and needs no SDP solver, no network, and no
Git history.

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

Expected final output:

```
All exact checks passed: sharp bound 7, qutrit separation, and quantum remainder weight >31.19%.
Global quantum maximum, tight decomposition cost, novelty, and external review remain open.
```

Any failure raises a `CalledProcessError` and stops. Every verifier uses `assert` as a proof
gate and refuses to run under `python -O`, where assertions would be stripped;
`tests/test_standalone_optimized.py` checks that refusal.

## What it does NOT establish

- **Not novelty.** `docs/PRIOR_ART.md` states what is settled and what is open. The valid
  inequality on the partial-local hull is prior art; check 3 above proves that against us.
- **Not peer review.** No human domain expert has reviewed any of this. The reviews under
  `docs/` are by AI systems.
- **Not authenticity or provenance.** `python manifest.py check` compares file hashes against
  the Git index. That is an integrity check on a checkout — it is not mathematical
  correctness, and it does not work from an archive with no Git metadata.
- **Not experimental feasibility.** The violation is `0.0129`, with roughly `0.18%` tolerance
  to uniform white-noise admixture of the output distribution. That is not a detection
  efficiency, a visibility, or a demonstrated experimental tolerance.
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
| `python tests/test_research_paths.py` | discovery scripts' input/output paths resolve |
| `python tests/test_docs_consistency.py` | documented paths exist; no unreferenced script |
| `python manifest.py check` | file hashes against the Git index |
| `python research/audit_catalog_folds.py` | a scoped comparison, not a proof gate |
| `python tests/test_comparison_acceptance.py` | corrupt Q and the catalogue, require both comparisons to reject |
| `python research/legacy/verify_routing.py --legacy-routing` | historical; supports no current claim |
| `bash paper/build.sh` | rebuild the manuscript PDF (needs Pandoc + XeLaTeX) |

## Environment

Tested on CPython 3.10.12 with sympy 1.14.0 and numpy 2.2.6; CI also runs 3.12.
`proofs/verify_sharp_qubit.py` needs neither. SymPy is needed for the face-dimension verifier,
the exact qubit benchmarks and the Pauli check; NumPy for the independent SOS cross-check and
for loading archived inputs. SDP solvers appear only in `research/requirements.txt` and are
never needed to verify anything.
