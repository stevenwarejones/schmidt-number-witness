# The equality face: `S2 ∩ {F = 7}` is a four-simplex of local behaviours

**Later draft continuation:** `docs/CERTIFICATE_PENALTY_BOUNDARY.md` extends the
certificate range while retaining these original inputs. Bounds and endpoint
limitations below describe this original certificate, not a proof of optimality.
The new prose extension is awaiting separate review.

Status: exact computer-assisted certificate, independently reviewed inside this repository
(`docs/review_2026-09-07_equality_face.md`). Its branch infeasibilities and forced zeros are
re-derived by a second route that reads none of the supplied duals
(`tests/verify_equality_face_independent.py`); that route does **not** re-derive the projector
rules or their closure, so it is not a second proof of the theorem. No human expert has reviewed
any of it. Novelty is **not** established — see §7.

## 1. The statement

    S2 ∩ {F = 7}  =  L_F  :=  conv { five local deterministic behaviours },   dim aff L_F = 4.

The five, in the ordering `(A0, A1, A2, B0, B1, B2)` with correlators the products of local
signs:

```
( 1, -1,  1, -1, -1, -1)
( 1, -1,  1,  1, -1, -1)
( 1,  1, -1, -1, -1,  1)
( 1,  1,  1, -1, -1, -1)
( 1,  1,  1, -1, -1,  1)
```

So the sharp bound is attained **only** locally, and only inside that four-simplex. The face is
an exposed face of `S2`, not a facet: `S2` has affine dimension 15, because it contains the
full-dimensional local polytope.

**Do not overread it.** The theorem classifies observed *behaviours*. It does not say the
underlying state is unentangled — deterministic measurements can reach `F = 7` on an entangled
state while revealing none of its entanglement.

## 2. Branch 1 — all six observables traceless

The sharp Gram is positive **definite**, not merely semidefinite, and that is exactly what the
argument needs. For a pure state, equality gives

    0 = <psi| (7I - B_F) |psi> = sum_{j,k} X[j,k] <J_j psi, J_k psi>,

and writing `X = sum_a lambda_a u_a u_a^T` with every `lambda_a > 0` turns that into
`sum_a lambda_a || sum_j u_{a,j} J_j psi ||^2 = 0`, so every `J_j |psi> = 0`.

Three identities in the shipped basis map — re-derived from the map itself by
`proofs/verify_equality_face.py`, not quoted —

    J_5 - J_0 = (I-A0)(I-B0),   J_6 - J_0 = (I-A0)(I-B1),   J_7 - J_0 = (I-A0)(I-B2),

then give `P(A0 = -1, B_y = -1) = 0` for `y = 0, 1, 2`, since `(I-A0)/2` and `(I-B_y)/2` are
rank-one projectors acting on different factors.

A Schmidt-rank-one state is already local. Otherwise the 2×2 coefficient matrix is invertible,
so projecting Alice onto `A0 = -1` leaves a **nonzero** conditional vector on Bob's qubit which
all three of Bob's minus-projectors annihilate. In dimension two each such kernel is
one-dimensional, so the three projectors coincide: Bob has one effective measurement, and any
behaviour with one setting on a side is local.

## 3. Branch 2 — at least one deterministic observable

A binary projective qubit observable is either traceless or `±I`; there is no third case. So
counting deterministic observables `(d_A, d_B)` partitions everything:

| case | disposition |
|---|---|
| `d_A = d_B = 0` | branch 1 |
| `d_A >= 2` or `d_B >= 2` | that party has at most one nontrivial measurement, hence jointly measurable measurements, hence a local behaviour |
| `(1,0)` and `(0,1)` | `3·2 + 3·2 = 12` patterns |
| `(1,1)` | `3·3·2·2 = 36` patterns |

48 patterns, and the verifier checks the certificate carries **precisely those keys** — not
merely 48 of them.

**17 patterns** carry one dual proving `max F < 7` over that branch of the no-signaling
polytope, so equality is unreachable there before any quantum structure is used — `max F < 7`
already says the `F = 7` face is empty. The independent checker reaches that same conclusion by
a different mechanism, detecting infeasibility in phase 1 rather than bounding the objective;
that is a second derivation, not a stronger one.

**31 patterns** carry duals forcing individual joint probabilities to vanish on the face —
**665** of them in total, 12 to 27 per pattern. Each certifies that the event's row functional
is at most `-1` on `{A v <= 1, F·v = 7, deterministic marginals fixed}`, which with
`4P = 1 + r·v` and `P >= 0` pins `P = 0`.

Those zeros are then turned into projector equalities by five geometric rules, under the
standing hypotheses that the state is pure of Schmidt rank two (so both reduced density
operators are positive definite and the coefficient matrix is invertible):

1. a joint zero pairing a deterministic party's **actual** outcome with a nonzero projector on
   the other side is impossible, since `Tr(rho Pi) > 0`;
2. two rank-one projectors annihilating the same nonzero conditional vector coincide — and
   since the coefficient matrix is invertible, equal conditional vectors also mean equal
   projectors on the conditioning side, so classes on both sides mean the same thing;
3. equal rank-one qubit projectors have equal complements;
4. a projector cannot equal its orthogonal complement;
5. if every nontrivial measurement on one party shares a basis up to outcome swaps, that
   party's measurements commute and the behaviour is local.

The closure yields **30 impossible, 1 local**. The local one is `A0 = +I`, `B1 = -I`, where two
forced zeros make the projectors for `A1 = +1` and `A2 = -1` coincide, so `A1 = -A2` and
Alice's measurements commute.

**The rule set fails safe.** A pattern the closure cannot resolve comes out `unresolved`, and
the verifier rejects that. An incomplete rule set therefore shows up as a failed check, never as
a silent acceptance.

## 4. Branch 3 — POVMs and mixtures, and the order that matters

The reduction is the same as `docs/SCHMIDT_NUMBER_BOUND.md` §2–3, but it is **order-sensitive**
and the prose there presents the steps in the opposite order to the one that must be applied:

    mixed SN2 state
      -> pure components of Schmidt rank at most two
      -> compress each to its 2x2 Schmidt supports
      -> decompose the six effects into projector / I / 0 with setting-independent weights
      -> projective or deterministic measurements on a PURE two-qubit state.

Purity survives that chain, which is what branch 2 assumes. Two details worth recording:

* **A degenerate effect is harmless.** When an effect's two eigenvalues coincide the "top
  eigenvector" is not well defined — but the projector label's weight is exactly `L+ - L- = 0`,
  so every positive-weight component carries a genuinely nontrivial projector, which is what the
  patterns of §3 require.
* **Saturation is componentwise because `F` is affine.** Every component obeys `F <= 7`, so a
  mixture at `F = 7` has every positive-weight component at `F = 7`, hence local by §2–§3.
  Mixtures of local behaviours are local, and `F <= 7` is valid on the local polytope, so the
  local `F = 7` face is the hull of the deterministic vertices attaining it — the five above.
  The reverse inclusion is immediate: those five are local, hence Schmidt number one, and attain
  7.

This branch is **prose**. It has no certificate, and the identities it rests on are only
corroborated numerically.

## 5. The same face for the whole certified family

For every `eps` in `[0, eps0]` with `eps0 = 383689/100000`, the equality face of
`F + eps * p` is the same `L_F`.

* **`eps < eps0`.** If `F + eps p = 7` then `F + eps0 p = 7 + (eps0 - eps) p`, which the
  endpoint certificate bounds by 7. Since `eps0 - eps > 0` and `p >= 0`, that forces `p = 0`,
  hence `F = 7`, and §2–§4 apply.
* **`eps = eps0`.** The endpoint Gram is positive definite, so equality forces `J_j |psi> = 0`
  for every `j` — including `J_8 = 4K`, whence `p = <K> = 0` and `F = 7`. Note this delivers the
  branch-1 hypothesis directly: the same `J_j |psi> = 0` that §2 starts from. In a deterministic
  branch, `F + 4p <= 7` together with `F + eps0 p = 7` and `eps0 < 4` forces `p = 0` the same
  way. The componentwise reduction of §4 is unchanged.
* **Conversely**, all five vertices have `p = 0` as well as `F = 7`, so `F + eps p = 7` at each
  of them for **every** `eps`. `L_F` saturates the whole family.

`proofs/verify_equality_face.py` checks the arithmetic; the two inputs it leans on — positive
definiteness of the endpoint Gram, and `F + 4p <= 7` in the deterministic branches — are checked
by `proofs/verify_penalty_endpoint.py`.

**This does not extend past `eps0`.** The certified family stops there, and the true validity
endpoint is `4 - alpha_star`, which is undetermined. What happens to the equality face at that
exact critical penalty is a **separate open question**: a nonlocal behaviour with `p > 0`
attaining the bound there is neither exhibited nor excluded. Nothing in this document should be
read as settling it.

## 6. Proof map

| Step | Status | Where |
|---|---|---|
| the three projector identities in the basis map | machine-checked, re-derived from the map | `proofs/verify_equality_face.py` |
| the 48 patterns are exactly the required set | machine-checked | `proofs/verify_equality_face.py` |
| 17 no-signaling duals excluding `F = 7` | machine-checked | `proofs/verify_equality_face.py` |
| the same 17 branch infeasibilities, re-derived by exact simplex | machine-checked, independent route | `tests/verify_equality_face_independent.py` |
| 665 forced-zero duals | machine-checked | `proofs/verify_equality_face.py` |
| the same 665 zeros re-derived from the constraints alone, reading no supplied dual | machine-checked, independent route | `tests/verify_equality_face_independent.py` |
| the projector closure, from the five rules | machine-checked | `proofs/verify_equality_face.py` |
| five vertices, affine dimension four | machine-checked, twice | both files |
| every vertex has `p = 0`, so `L_F` saturates the whole family | machine-checked | `proofs/verify_equality_face.py` |
| branch 1's Hilbert-space argument (§2) | **prose** | this document, §2 |
| the five geometric rules themselves (§3) | **prose** | this document, §3 |
| the POVM and compression reduction (§4) | **prose**, numerically corroborated | this document, §4 |
| `alpha_star`, and the face at the critical penalty | **open** | — |

`tests/test_equality_face_mutations.py` corrupts the certificate and requires rejection to carry
the specific diagnostic code for the defect introduced, with the same two controls as the other
mutation suites.

**One honest limit on the independent route.** The exact simplex re-derives the branch
infeasibilities and the forced zeros, so no supplied number is trusted for those. It does **not**
re-derive the *closure*, and therefore does not independently establish the theorem: running a
second implementation of the same five rules would test the implementation, not the rules. The
rules were checked by hand in `docs/review_2026-09-07_equality_face.md`, and that hand-check is
the weakest link in the argument.

The numerical section of that file **gates nothing**. It measures how close each branch optimum
gets to the bound and how far it sits from `L_F`, using a genuine projection onto the simplex
(constrained: `sum(lambda) = 1` eliminated exactly, `lambda >= 0` enforced by enumerating the 31
supports). Those numbers are exploration. The theorem says a behaviour *at* `F = 7` lies in
`L_F`; it gives no quantitative relation between a score deficit and a distance, so no threshold
pairing the two could be an acceptance condition without inventing a guarantee the mathematics
does not supply.

## 7. What is not established

* novelty. Goh et al. ([arXiv:1710.05892](https://arxiv.org/abs/1710.05892)) reportedly contain
  a five-vertex four-dimensional local face in a two-setting example whose quantum face has
  dimension five, and they explicitly discuss several functionals exposing one face — which is
  also what §5 says here. The numbers "five" and "four" coinciding is not evidence that it is
  this face, but the comparison has to be made properly, and the full text was not reachable
  from the session that produced this document. Rai et al.
  ([arXiv:1812.06057](https://arxiv.org/abs/1812.06057)) study zero-probability faces on which
  the quantum set has no nonlocal points, which is the closest conceptual neighbour to the
  forced-zero branches of §3. `docs/PRIOR_ART.md` records the access status. **Do not present
  "zero-probability constraints can force quantum correlations to be local" as discovered
  here.**
* the exact critical penalty, and the equality face at it (§5);
* any facet, dimension or partial-locality property of `F + eps p` for `eps > 0` — the natural
  one is false, see `proofs/verify_penalty_not_partial_local.py`;
* a quantitative distance-to-`L_F` theorem for near-saturating behaviours. The numerical
  corroboration in the independent checker measures exactly that distance for the optima it
  finds, and finds it small; that is evidence, not a theorem;
* human expert review.

## 8. Provenance

The 48 pattern certificates and the equality argument are **ChatGPT ("Astra")'s**, supplied as
data alongside the penalty-endpoint package. They were held out of the repository until
reviewed. The review is `docs/review_2026-09-07_equality_face.md`; the verifier, the independent
exact-simplex route and the mutation suite are Claude's.
