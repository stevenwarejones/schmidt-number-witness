# Legacy routing and record calculation

**Nothing here supports any claim in the current paper or repository.**

The qutrit behavior that separates `F > 7` was found while studying a routing/record question
about trusted classical channels. That question is not the subject of this repository, and its
conclusions are not premises of the Schmidt-number-two theorem. The active realization check is
`proofs/verify_qutrit.py`; the geometry is in `proofs/verify_facet.py`.

This directory is kept for one reason: a calculation that once motivated a shipped certificate
is easier to audit if it is preserved than if it is only in Git history.

| File | What it is |
|---|---|
| `routing_certificate.json` | the ORIGINAL certificate, byte for byte, before the active fields were extracted into `proofs/qutrit_certificate.json` |
| `verify_routing.py` | the original verifier, unchanged except for its header and certificate path |

The active fields — `state`, `Alice`, `Bob`, `Q`, `coefficients`, `bound`, `score` — were copied
into `proofs/qutrit_certificate.json` without alteration; the extraction was checked field by
field. The `duals` record in this file duplicates `partial_hull_duals` in
`proofs/facet_certificate.json` exactly, which is why the active verifier no longer re-checks
it.

```sh
python research/legacy/verify_routing.py                    # Born reconstruction only
python research/legacy/verify_routing.py --legacy-routing   # plus the routing optimisations
```

Both pass. The routing value is `0.00968428911747865…`, and the anchored and ordinary classes
give the identical minimum — that is, the record-preservation constraint added nothing, which
is why this line of work was set aside.
