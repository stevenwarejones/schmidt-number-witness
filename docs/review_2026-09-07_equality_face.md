# Independent review: the Schmidt-number-two equality-face theorem

**Reviewer:** Claude (Anthropic), 7 September 2026. **Not** human expert review.
**Subject:** the claim, supplied by ChatGPT ("Astra") alongside the penalty-endpoint package,
that

> `S2 ∩ {F = 7} = L_F`, the convex hull of five local deterministic behaviours, of affine
> dimension four.

**Status: the argument is sound and its certificates check out.** Nothing below is a defect
found in the theorem. What follows is what was checked, how, and what is still missing — which
is not nothing.

This review was requested to be independent of the supplied verifier, so none of it imports the
supplied verifier, which is not in this repository. The linear-programming formulation, the exact dual check, the forced-zero
tests and the projector-closure classifier were all rebuilt from `P(ab|xy) = (1 + a A_x + b B_y +
ab E_xy)/4 >= 0`.

## 1. The projector argument (§2.1) — correct

The chain is: equality forces `J_j|psi> = 0` for every `j`; three basis-map identities turn
that into three vanishing joint probabilities; those force Bob's three measurements to coincide;
a party with one effective measurement makes the behaviour local.

Each step checks out.

* **Equality forces every `J_j|psi> = 0`.** With `w_j = J_j|psi>`, equality says
  `sum_{j,k} X[j,k] <w_j, w_k> = 0`. Writing `X = sum_a lambda_a u_a u_a^T` with every
  `lambda_a > 0` gives `sum_a lambda_a || sum_j u_{a,j} w_j ||^2 = 0`, so each
  `sum_j u_{a,j} w_j = 0`; the `u_a` are a basis, hence every `w_j = 0`. This needs `X`
  **positive definite**, not merely semidefinite — which is what the certificate supplies.
* **The three identities.** `J_5 - J_0 = (I-A0)(I-B0)`, `J_6 - J_0 = (I-A0)(I-B1)`,
  `J_7 - J_0 = (I-A0)(I-B2)` were reconstructed here symbolically, in a Clifford rewriting
  written for this review with coefficients kept as exact polynomials in the six Gram
  parameters. All three hold identically. So do `J_8 = (I+A1)(I+B0)` and `K^2 = K`.
* **The geometry.** `(I-A0)/2` and `(I-B_y)/2` are rank-one projectors on a qubit and act on
  different factors, so `(I-A0)(I-B_y)|psi> = 0` gives `P(A0 = -1, B_y = -1) = 0`. For a rank-two
  state the coefficient matrix is invertible, so projecting Alice onto `A0 = -1` leaves a
  **nonzero** conditional vector on Bob's side, which all three of Bob's minus-projectors
  annihilate. Their kernels are one-dimensional, so all three coincide, hence
  `B_0 = B_1 = B_2` up to outcome labels. A party with one effective setting makes any
  behaviour local.
* Rank one is disposed of first: a product state gives a product behaviour.

The argument needs the state to be a **pure two-qubit** state. That is supplied by the reduction
in §3 below, applied in the right order.

## 2. Completeness of the deterministic branches (§2.2) — complete

For binary projective qubit measurements each observable is either traceless (nondegenerate,
rank-one projectors) or `+I` / `-I`. There is no third case, so counting deterministic
observables `(d_A, d_B)` partitions everything:

| case | disposition |
|---|---|
| `d_A = d_B = 0` | the sum-of-squares argument of §1 |
| `d_A >= 2` or `d_B >= 2` | that party has at most one nontrivial measurement, hence jointly measurable measurements, hence a local behaviour |
| `(1,0)`, `(0,1)` | `3 x 2 + 3 x 2 = 12` patterns |
| `(1,1)` | `3 x 3 x 2 x 2 = 36` patterns |

`12 + 36 = 48`, and the shipped file carries exactly those 48 keys — verified here to be
distinct and to be precisely the expected set, not merely to number 48.

**The certificates were re-checked exactly, in a formulation written for this review.**

* 17 patterns carry a single dual proving `max F < 7` on that branch of the no-signaling
  polytope, so `F = 7` is unreachable there before any quantum structure is used. Every dual
  identity holds exactly as an identity of linear functionals in the 15 correlator coordinates,
  every positivity multiplier is nonnegative, and every stated value matches its own
  multipliers. Each was also compared against an independently computed LP optimum: none
  overstates what the branch permits.
* The remaining 31 patterns carry **665** forced-zero duals between them (12 to 27 per
  pattern). Each certifies that the event's row functional is at most `-1` on
  `{A v <= 1, F.v = 7, deterministic marginals fixed}`, which with `4P = 1 + r.v` and `P >= 0`
  pins `P = 0`. All 665 check exactly, and an independent LP confirms for each that the
  probability really is forced to zero on that face rather than merely bounded.

**The inference from forced zeros to projector equalities** was re-implemented here from the
five stated geometric rules rather than from their union-find, and reproduces their
classification exactly: 30 patterns impossible, 1 local. The single local case is `A0 = +I`,
`B1 = -I`, where two forced zeros make the projectors for `A1 = +1` and `A2 = -1` coincide, so
`A1 = -A2` and Alice's measurements commute.

The five rules are individually correct. Rule 1 — a joint zero pairing a deterministic party's
*actual* outcome with a nonzero projector on the other side is impossible — holds because a
rank-two pure state has both reduced density operators positive definite, so
`Tr(rho_B Pi) > 0`. Rules 2–4 are the one-dimensionality of a rank-one projector's kernel in
dimension two and the fact that a projector cannot equal its complement.

One design point in their favour: an incomplete rule set fails **safe**. Any pattern the closure
cannot resolve comes out `unresolved`, and the verifier asserts against that, so a gap in the
reasoning would show up as a failed check rather than as a silent acceptance.

**Caveat that should not be glossed.** Two implementations of the *same five rules* agreeing
tests the implementations, not the rules. The rules themselves I checked by hand, above; that
hand-check is the weakest link in this section and it is prose.

## 3. Componentwise saturation in the POVM and mixed-state extensions (§2.3) — correct, and order-sensitive

The reduction is sound, but only in one order, and the write-up should state that order
explicitly because presenting the POVM step first invites the wrong one.

The correct order is: **mixed state → pure components of Schmidt rank at most two → compress
each to its 2x2 Schmidt supports → decompose the six effects → projective or deterministic
measurements on a pure two-qubit state.** Purity is preserved throughout, which matters because
§2.2 assumes a pure state.

* **Effect decomposition.** A binary qubit effect with eigenvalues `L- <= L+` splits as
  `(L+ - L-) Pi + L- I + (1 - L+) 0` with nonnegative weights summing to one. Sampling the six
  labels **before** the settings are chosen gives setting-independent product weights, so the
  behaviour is a convex mixture of behaviours using only projective or deterministic
  observables on the same state. Checked numerically over random effects and random two-qubit
  states: the mixture reproduces the original behaviour to `10^-15`.
* **An edge case worth stating.** When `L+ = L-` the "top eigenvector" is not well defined — but
  the projector's weight is then exactly `L+ - L- = 0`, so any choice gives the same mixture and
  no positive-weight component carries an ill-defined projector. Positive-weight components
  therefore always have genuinely nontrivial projectors where the pattern demands them, which is
  what §2.2 assumes.
* **Compression.** For a pure state of Schmidt rank at most two, `V_A^dagger E V_A` is positive
  and sums to the identity on the support, so compressed effects are valid qubit POVM elements,
  and every Born probability is preserved. Checked numerically in ambient dimensions 3 to 5.
* **Saturation is componentwise because `F` is affine.** Every component obeys `F <= 7`, so a
  mixture at `F = 7` has every positive-weight component at `F = 7`, hence local by §1–§2.
  Mixtures of local behaviours are local.
* **Closing the loop.** `F <= 7` is valid on the local polytope, so the local polytope's
  `F = 7` face is the hull of the deterministic vertices attaining it. There are exactly five —
  recomputed here — and their affine hull has dimension four, also recomputed. So
  `local ∩ {F = 7} = L_F`, and the mixture lands in `L_F`. The reverse inclusion is immediate:
  local behaviours have Schmidt number one and these five attain 7.

## 4. What this review did not settle

* **The `eps > 0` extension.** The claim that the whole certified family `F + eps p <= 7`,
  `0 <= eps <= eps0`, has the *same* four-simplex equality face was not reviewed in this pass.
  It was reviewed immediately afterwards and is now integrated — see the addendum below.
* **The rules themselves.** As noted in §2, my agreement with their classifier is agreement
  between two implementations of one rule set.
* **Novelty.** Goh et al. ([arXiv:1710.05892](https://arxiv.org/abs/1710.05892)) reportedly
  contain a five-vertex four-dimensional local face in a two-setting example whose quantum face
  has dimension five. The numbers "five" and "four" coinciding is not evidence that it is this
  face — but the comparison has to be made properly before this theorem is written up as new,
  and the full text was **not reachable** from this session (arXiv abstract pages resolved;
  the PDF and HTML endpoints returned HTTP 429 throughout). Same for Rai et al.
  ([arXiv:1812.06057](https://arxiv.org/abs/1812.06057)), whose zero-probability faces are the
  closest conceptual neighbour to the forced-zero branches.
* **Human review.** None.

## 5. Recommendation

The theorem is ready to integrate as a *reviewed* result: a verifier for the 48 patterns and the
five saturators, a certificate guide, and a paper section — kept distinct from the endpoint
material, which is a different claim about a different functional. It should not be written up
as novel until the Goh and Rai full texts have actually been read.

The one presentational change worth making at integration: state the reduction order of §3
explicitly, and record the degenerate-effect edge case, so that a later reader does not have to
rediscover why purity survives the POVM step.


## Addendum, same day: the family corollary

A short proof of the `eps > 0` extension was supplied after this review and checked here. It is
correct, and `proofs/verify_equality_face.py` now carries its arithmetic.

* **`eps < eps0`.** If `F + eps p = 7` then `F + eps0 p = 7 + (eps0 - eps) p`, which the endpoint
  certificate bounds by 7. With `eps0 - eps > 0` and `p >= 0` that forces `p = 0`, hence `F = 7`,
  and the theorem reviewed above applies.
* **`eps = eps0`.** Positive definiteness of the endpoint Gram forces `J_j |psi> = 0` for every
  `j` in the nondegenerate projective case, and `J_8 = 4K` gives `p = <K> = 0` directly. Worth
  noting: this delivers the *same* hypothesis `J_j |psi> = 0` that §1 above starts from, so the
  projector argument runs unchanged rather than having to be re-entered through `F = 7`. In a
  deterministic branch, `F + 4p <= 7` with `eps0 < 4` forces `p = 0` the same way, and
  componentwise saturation carries it to POVMs and mixtures.
* **Converse.** All five vertices have `p = 0` as well as `F = 7` — recomputed here — so
  `F + eps p = 7` at each of them for every `eps`.

Two things this does not do, and the write-up says so. It does not extend past `eps0`: the true
validity endpoint is `4 - alpha_star`, which is undetermined. And it says nothing about the
equality face *at* that critical penalty, where a nonlocal behaviour with `p > 0` attaining the
bound is neither exhibited nor excluded. Both are recorded as open in
`docs/CERTIFICATE_EQUALITY_FACE.md` §5 and §7.

The theorem is integrated as of this addendum. `tests/verify_equality_face_independent.py`
carries an exact rational simplex that re-derives the branch infeasibilities and all 665 forced
zeros without reading any of the supplied duals. For the 17 "no-signaling" patterns it reaches
the same conclusion by a different mechanism — phase-1 infeasibility rather than a dual bound —
which is a second derivation and not a stronger one, since `max F < 7` already says the `F = 7`
face is empty. It does **not** re-derive the projector rules or their closure, so it is not an
independent proof of the theorem. `tests/test_equality_face_mutations.py` requires rejection for
the intended reason, including a single deleted forced zero that leaves every remaining dual
exact and is caught only by the projector closure.
