# Contributing

## Commands

```sh
python -m pip install -r requirements.txt   # SymPy is required by the full chain
python proofs/verify_sharp_qubit.py         # the sharp bound alone: no dependencies
python run_checks.py                        # active exact certificate chain
python tests/adversarial_sharp_checks.py
python tests/test_standalone_optimized.py
python tests/check_sharp_pauli.py
python tests/verify_sos_independent.py
python tests/verify_facet_independent.py
python tests/test_research_paths.py
python tests/test_docs_consistency.py
python tests/test_comparison_acceptance.py
python tests/test_output_helper.py
python tests/test_checker_mutations.py
python tests/verify_endpoint_independent.py   # ~30 s; four independent routes to the endpoint
python tests/test_endpoint_mutations.py       # ~6 min; corrupts each endpoint certificate
python research/audit_catalog_folds.py
python research/legacy/verify_routing.py --legacy-routing
python manifest.py check
python make_snapshot.py
```

Run without `-O`. Assertions are used as proof gates, and every verifier refuses optimized
execution rather than silently passing.

## Discovery is separate from proof

`research/` searches for candidate certificates and needs an SDP solver. `proofs/` verifies
them and must not. The central sharp verifier is standard-library only; keep it that way.
Discovery writes to `build/`, which is ignored and created on demand — it must never
overwrite an archived input or a shipped certificate in place. Discovery needs Python >= 3.11
(`research/requirements.txt` pins packages that require it); verification is tested on 3.10
and 3.12.

Do not merge the independent checker `tests/verify_sos_independent.py` into the primary verifier's
word normalization. Its value is that it is a separate implementation. The same applies to
`tests/verify_endpoint_independent.py`, which reaches the endpoint certificate by three routes
none of which is the proof path: its own Clifford rewriting, explicit Gaussian-rational qubit
matrices with no normal ordering at all, and integer Bareiss minors instead of rational LDL.

## Scope discipline for the penalised functional

`F` and `G = F + eps * p` are different functionals and their results do not transfer. `F` is a
facet of `H` **and** bounded by 7 on Schmidt number two; `G` keeps only the second property,
and `proofs/verify_penalty_not_partial_local.py` proves the first fails for every `eps > 0`.
Do not describe `G` as a partial-locality witness, and do not attach `F`'s facet or
convex-class statements to it without a separate proof.

## Changing a certificate

A new or modified certificate needs, in the same pull request:

1. exact verification by its standalone verifier, passing normally and refusing `-O`;
2. a diff of every claim whose value or scope changes, including in `docs/`;
3. a regenerated manifest (`python manifest.py generate`) with the hash change explained;
4. a negative test showing the corrupted form is rejected without printing a conclusion.

A solver exit status is not evidence. Hash integrity is not mathematical correctness, and
neither is independent review.

## Claims

Label numerical results as numerical and exact results as exact. Do not describe an
AI-produced review as peer review, and do not convert a pending prior-art audit into a
novelty claim.
