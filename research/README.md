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
| `search_qubits.py`, `search_schmidt_profile.py` | counterexample searches over qubit strategies |
| `qubit_theta_profile.py`, `qubit_joint_search.py`, `qubit_endpoint_scaling.py` | the angle-profile, joint and endpoint-scaling searches reviewed in `docs/review_2026-09-06_ai.md` |

## Limitations

A candidate produced here is not a certificate. Promotion requires exact verification by the
standalone verifier, a diff of every claim whose value or scope changes, and a regenerated
manifest. A solver status is not evidence.

The fixed-target run these scripts were written for was unsuccessful; the sharp bound was
subsequently established by the exact Gram certificate in `proofs/`. Their outputs are not
committed — everything here writes to the git-ignored `build/`, so a claim can never rest on
a stale result file. Some scripts still read another script's source text to reuse a builder;
replacing that with explicit builder functions is a known follow-up, to be done only after
comparing basis ordering and coefficient maps against the archived inputs.
