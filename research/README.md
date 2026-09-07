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
| `audit_catalog_folds.py` | a scoped COMPARISON, not a proof: folds the 129 four-setting inequalities of arXiv:0810.1615 Table I down to three settings, 51,600 reductions, zero matches against `F`'s orbit |
| `search_qubits.py`, `search_schmidt_profile.py` | counterexample searches over qubit strategies |
| `qubit_theta_profile.py`, `qubit_joint_search.py`, `qubit_endpoint_scaling.py` | the angle-profile, joint and endpoint-scaling searches reviewed in `docs/review_2026-09-06_ai.md` |

## Limitations

A candidate produced here is not a certificate. Promotion requires exact verification by the
standalone verifier, a diff of every claim whose value or scope changes, and a regenerated
manifest. A solver status is not evidence.

These are two different kinds of workflow and should not be described together.

`rational_sharp.py` is the **generator of the shipped sharp certificate**: it identifies exact
equality-family kernels, solves on the remaining Gram subspace, and corrects a numerical matrix
onto the exact rational affine constraints. Its output is what `proofs/verify_sharp_qubit.py`
checks. Rerunning it is a reproduction of the certificate, and needs the SDP stack.

The **historical discovery scripts** — the fixed-target searches, and the three profile and
endpoint scripts — were exploratory. The fixed-target run they were written for did not
succeed; the sharp bound came from the exact Gram construction above. They are kept because
`docs/review_2026-09-06_ai.md` quotes figures from them and those figures should be
reproducible, not because any current claim rests on them.

Outputs: `qubit_theta_profile.py`, `qubit_joint_search.py` and `qubit_endpoint_scaling.py`
write **nothing** — their results go to stdout, and they record no seed, workload or optimizer
status. Every other script here writes to the git-ignored `build/`. Nothing under `research/`
is committed as a result file, so no claim can rest on a stale one.

Some scripts still read another script's source text to reuse a builder; replacing that with
explicit builder functions is a known follow-up, to be done only after comparing basis ordering
and coefficient maps against the archived inputs.
