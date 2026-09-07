# Discovery code

Search and rounding code that *produced* the certificates. It is not part of the proof: the
verifiers in `proofs/` accept or reject a certificate without any of this.

## Inputs, commands, outputs

| | |
|---|---|
| Inputs | `research/inputs/` — archived SDP solutions and kernels, treated as immutable |
| Outputs | `build/` at the repository root, which is git-ignored |
| Dependencies | `research/requirements.txt` (SDP solvers). Not needed to verify anything. |

| Script | Produces |
|---|---|
| `clifford_bound.py`, `clifford_scs.py` | level-2 / level-3 moment relaxations |
| `equality_kernel.py` | the word list and kernel map |
| `face_sdp.py`, `reduced_face_sdp.py` | face maps for the sharp target |
| `rational_sharp.py` | rational rounding of the reduced face solution |
| `certify_upper.py`, `certify_upper_level3.py` | rational SOS upper certificates rounded from the level-2 and level-3 numerical Gram duals |
| `quantum_upper.py` | the dimension-unrestricted upper bound |
| `outputs.py` | the one supported way to name a generated file: validates a computed filename at run time and keeps it inside `build/`. Scripts with dynamic output names must use it |
| `audit_catalog_folds.py` | a scoped COMPARISON, not a proof: folds the 129 four-setting inequalities of arXiv:0810.1615 Table I down to three settings, 51,600 reductions, zero matches against `F`'s orbit |
| `search_qubits.py`, `search_schmidt_profile.py` | counterexample searches over qubit strategies |
| `qubit_theta_profile.py`, `qubit_joint_search.py`, `qubit_endpoint_scaling.py` | the angle-profile, joint and endpoint-scaling searches reviewed in `docs/review_2026-09-06_ai.md` |

## Limitations

A candidate produced here is not a certificate. Promotion requires exact verification by the
standalone verifier, a diff of every claim whose value or scope changes, and a regenerated
manifest. A solver status is not evidence.

These are two different kinds of workflow and should not be described together.

`rational_sharp.py` is the **rational-rounding step** that produced the shipped sharp
certificate. It does *not* identify the equality kernels or solve a new SDP. It reads the
archived reduced face map and face solution, projects the numerical matrix, rounds it, corrects
the selected affine equations exactly, verifies every coefficient equation, and checks exact
Gram positivity. It needs NumPy, SciPy and Python-FLINT — **not** CVXPY or any SDP solver.

Rerunning it regenerates a **valid** certificate, not the shipped bytes: an independent audit
ran it with CVXPY absent and obtained a positive rational 70x70 Gram, which
was accepted by `proofs/verify_sharp_qubit.py`, with only `reduced_gram` differing from the shipped file. Numerical QR and
floating-point steps need not reproduce identical rationals across environments, so the shipped
certificate is kept unless there is a substantive reason to change it.

Three activities are easy to conflate and are not the same thing:

| Activity | Inputs | What it establishes |
|---|---|---|
| Proof verification | the shipped exact data | deterministic acceptance of the theorem; needs no solver — see `VERIFY.md` |
| Rational regeneration | the archived numerical arrays | a separately verified exact certificate, not guaranteed byte-identical |
| Full numerical rediscovery | solver runs and searches | how the original certificate was found; expensive, and not rerun by anything here |

The **historical discovery scripts** — the fixed-target searches, and the three profile and
endpoint scripts — were exploratory. The fixed-target run they were written for did not
succeed; the sharp bound came from the exact Gram construction above. They are kept because
`docs/review_2026-09-06_ai.md` quotes figures from them and those figures should be
reproducible, not because any current claim rests on them.

Every generated file goes to the git-ignored `build/`. A **static** file name is written as
`OUTPUT_DIR / 'name.json'` and is checked by reading the source; a name **computed at run
time** must go through `outputs.py:output_path`, which validates it where the value actually
exists. `tests/test_research_paths.py` checks that convention, and
`tests/test_output_helper.py` tests the helper itself — that is where the containment
guarantee lives, because three rounds of review showed a source lint could not carry it.

Outputs: `qubit_theta_profile.py`, `qubit_joint_search.py` and `qubit_endpoint_scaling.py`
write **nothing** — their results go to stdout. Seeds and workloads are hard-coded in their
source, and the joint search prints its restart count; what is missing is a machine-readable
run artifact recording environment, optimizer status and results. Every other script here
writes to the git-ignored `build/`. Nothing under `research/`
is committed as a result file, so no claim can rest on a stale one.

Some scripts still read another script's source text to reuse a builder; replacing that with
explicit builder functions is a known follow-up, to be done only after comparing basis ordering
and coefficient maps against the archived inputs.
