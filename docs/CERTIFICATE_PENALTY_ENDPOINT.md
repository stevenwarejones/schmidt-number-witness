# The penalty endpoint: `M_A <= 6 + alpha0 p`, with `alpha0 = 0.16311`

Status: exact computer-assisted certificate, verified along four independent routes in this
repository. No human expert has reviewed it. The **exact** optimal coefficient is not
determined, and is not claimed to be.

This document is about a *different functional* from the rest of the repository. Read §0
before anything else.

## 0. Scope, and the one thing not to carry over

`docs/CERTIFICATE_SHARP_BOUND.md` and `docs/CERTIFICATE_FACET.md` concern `F`, which does two
things at once: it is bounded by 7 on Schmidt number at most two, **and** it is a facet of the
two-sided partial-local hull `H`.

The penalised functional

    G := F + eps * p,     p := P(00|10) = (1 + A1 + B0 + E10)/4,   eps > 0

keeps the first property in strengthened form and **loses the second outright**. This is not a
gap in the write-up; it is a theorem, and `proofs/verify_penalty_not_partial_local.py` proves
it from the repository's own facet certificate:

> Of the fifteen affinely independent points of `H` that saturate `F = 7` — the points that
> establish the facet, each carrying its own exact partial-local model — exactly one has
> `p > 0`. It is the side-`B`, pair-`(0,2)` point, with `F = 7` and `p = 1/3` exactly. So
> `G = 7 + eps/3` there.

Hence for **every** `eps > 0`, `G <= 7` is false on `H`. There is no positive penalty that
keeps the partial-local reading. Statements about `H` must be made about `F`; statements about
the strengthened bound must be made about `G` and Schmidt number at most two. Nothing in this
document weakens or revises any earlier result about `F`.

A structural consequence worth stating: the original proof for `F` handles a deterministic
observable by routing it into a partial-local class and invoking the facet certificate
(`docs/SCHMIDT_NUMBER_BOUND.md` §2). That route is unavailable for `G`, precisely because `G`
is not valid on `H`. §3 below replaces it with twelve no-signaling dual certificates.

## 1. What is certified

With

    eps0   = 383689/100000 = 3.83689,
    alpha0 = 4 - eps0 = 16311/100000 = 0.16311,
    M_A    = F + 4p - 1,

the certificate proves, for every behaviour arising from a bipartite state of **Schmidt number
at most two** with three binary local POVMs per party and setting-independent shared
randomness,

    F + eps0 * p  <=  7,      equivalently      M_A <= 6 + alpha0 * p.

`F <= 7` is the `eps = 0` case, so this strictly strengthens the repository's sharp bound and
recovers it exactly when the penalty is switched off. Since `p >= 0`, validity for `eps0` gives
validity for every `eps` in `[0, eps0]`.

Define

    alpha_star := sup { (M_A - 6)/p : behaviour in S2, p > 0 },

the smallest coefficient that makes `M_A <= 6 + alpha * p` universally valid on `S2`. The
original `F <= 7` gives only `alpha_star <= 4`. This certificate gives `alpha_star <= 0.16311`,
and an explicit two-qubit strategy (§4) gives a matching lower bound:

    0.1631016 < alpha_star <= 16311/100000.

**`alpha_star` itself is undetermined.** The interval has width below `8.4 * 10^-6`. No exact
algebraic value, no matching sharp sum-of-squares, and no self-testing statement at the
critical penalty is claimed. `docs/SCHMIDT_NUMBER_BOUND.md` §7 previously recorded "is 4 the
smallest universally valid coefficient?" as open; the answer is no, and by a wide margin, but
the optimum is still open.

## 2. Branch 1 — all six observables traceless

For nondegenerate projective qubit measurements the certificate is a positive-definite rational
Gram matrix `X` (70 by 70) satisfying the exact operator identity

    (7 - eps0/4) I  -  B_{f + eps0 d}  =  sum_{j,k} X[j,k] J_j^dagger J_k,
    J_j = sum_i P[i,j] W_i,

over the repository's existing 84 words and 84-by-70 integer basis map `P` — the same `W` and
`P` as `proofs/sharp_qubit_certificate.json`. Here `d` carries `1/4` in the `A1`, `B0` and `E10`
slots and zero elsewhere.

The constant `eps0/4` is part of the statement and is easy to lose. `G` contains a
*probability*, not only correlators: `p = (1 + A1 + B0 + E10)/4`, so `G = eps0/4 + B_{f+eps0 d}`
and the operator being certified positive is `(7 - eps0/4)I - B_{f+eps0 d}`, not `7I - B_{f+eps0 d}`.

Since `X > 0`, the right-hand side is positive semidefinite for every choice of unit Bloch
vectors, and its expectation in any state gives `G <= 7`. The Gram is close to the boundary of
the positive-definite cone: its least exact LDL pivot is about `1.39 * 10^-7`. That is why
positivity is checked in exact rational arithmetic and cross-checked by integer elimination.

Two identities in the same basis map are worth recording, since they are what ties `p` to the
algebra: `J_8 = (I+A1)(I+B0) = 4K` where `K` is the projector onto the event `p` counts, and
`K^2 = K`. Both are checked in `tests/verify_endpoint_independent.py`. They also give a
one-line improvement over `alpha = 4` needing no new SDP at all: subtracting `1/48` from entry
`(8,8)` of the ORIGINAL Gram preserves positive definiteness, and since
`J_8^dagger J_8 = 16 K`, that already proves `F + p/3 <= 7`, i.e. `alpha_star <= 11/3`. The
`0.16311` certificate is very much stronger, but the `11/3` step is worth knowing because it is
free. Its positivity is checked on the integer route in
`tests/verify_endpoint_independent.py` §C, not merely asserted here.

## 3. Branch 2 — at least one observable deterministic

The sum-of-squares presumes traceless observables and says nothing when some `A_x` or `B_y`
equals `+I` or `-I`. As noted in §0, the route the original proof uses here is closed for `G`.

Instead, twelve exact **no-signaling dual certificates** are supplied, one for each pair
(observable index `i` in `0..5`, sign `s` in `{-1,+1}`). Each is a vector `t` of 36 nonnegative
multipliers on the positivity constraints `P(ab|xy) >= 0`, together with one multiplier `nu` on
the equality `v_i = s`, satisfying the exact linear identity

    sum_j t_j * (-r_j)  +  nu * e_i  =  M_A          (as vectors in R^15),

where `4 P(ab|xy) = 1 + r.v`. Weak duality then gives, on that branch,

    M_A  <=  sum_j t_j  +  nu * s  =: upper  <=  6,

i.e. `F + 4p <= 7`. Since `p >= 0` and `eps0 < 4`, this yields `F + eps0 p <= 7` there too.

Three points about this branch:

* **Coverage is by construction, not by enumeration.** A deterministic observable `A_i = sI`
  forces the marginal `v_i = s`, which is the only hypothesis each dual uses. The twelve duals
  exhaust all `(i, s)` pairs, so "at least one deterministic observable" is fully covered. No
  count of *how many* observables are deterministic is needed, and no pattern enumeration.
* **The bound is a no-signaling bound, so it holds a fortiori for quantum behaviours.** It does
  not use the Born rule at all.
* **The duals are tight.** Eleven of the twelve values are attained by an explicit local
  deterministic behaviour on that branch; the twelfth (`B1 = +I`, value 4) is attained by an
  explicit PR-box behaviour. `tests/verify_endpoint_independent.py` exhibits the attaining
  behaviour in each case, so a vacuous or mis-scaled dual would be visible rather than silently
  accepted. For contrast, without any deterministic-observable hypothesis the no-signaling
  maximum of `M_A` is 8, not 6 — the branch hypothesis is doing real work.

## 4. The lower endpoint

The lower certificate fixes a rational `t > 0` and six rational half-angle tangents `z_i`. The
state is `(|00> + t|11>)/sqrt(1+t^2)` and each observable is

    [2z/(1+z^2)] X  +  [(1-z^2)/(1+z^2)] Z,

whose squared Bloch norm is exactly 1. Despite the square root in the normalization, every Born
expectation is rational: with `C = (1-t^2)/(1+t^2)` and `S = 2t/(1+t^2)`,

    <A_i> = C z_i,   <B_j> = C z_j,   <A_i B_j> = S x_i x_j + z_i z_j.

The verifier rebuilds the behaviour from `t` and the six tangents, recomputes `F`, `p` and the
ratio `4 + (F-7)/p` as exact rationals, and checks the result exceeds `1631016/10^7`. The
behaviour has `M_A > 6`, so it is nonlocal — this is not another product-state attainer.

## 5. POVMs and Schmidt-number-two mixtures

Branches 1 and 2 cover projective and deterministic qubit measurements. Two elementary
reductions carry them to the full statement. Both are prose; neither has a certificate.

**Binary qubit effects.** An effect `E` with eigenvalues `L- <= L+` in `[0,1]` and rank-one
eigenprojection `PI` for `L+` satisfies

    E  =  (L+ - L-) * PI  +  L- * I  +  (1 - L+) * 0,

a convex mixture with nonnegative weights summing to 1. The three components correspond to
observables `2PI - I` (traceless projective), `+I` and `-I`. Decompose all six effects
independently and sample their labels **before** the settings are chosen. The joint weight is a
product of six setting-independent weights, so the behaviour is a convex mixture of behaviours
each of which uses only projective or deterministic observables on the same state. Every
component is covered by branch 1 or branch 2, and `G` is affine in the behaviour.

**Schmidt compression.** For a pure state of Schmidt rank at most two, write
`psi = (V_A tensor V_B) psi~` with isometries onto the Schmidt supports. The compressed effects
`V_A^dagger E V_A` are positive and sum to the identity on the support, so they are valid qubit
POVM elements, and every Born probability is unchanged. A rank-one support embeds in a qubit.
For a mixed state of Schmidt number at most two, decompose into pure components of Schmidt rank
at most two and apply the argument componentwise; the bound is universal over states and
effects, so averaging preserves it.

Both reductions are identical in structure to `docs/SCHMIDT_NUMBER_BOUND.md` §2–3 and were
written there for `F`. What changes for `G` is only which branch handles the deterministic
components — §3 above rather than the facet certificate. The identities they rest on are
checked numerically in `tests/verify_endpoint_independent.py` §E; that is corroboration, not a
proof, and it is labelled as such there.

## 6. The improved qutrit realization, and the white-noise model

`proofs/improved_qutrit_certificate.json` gives a real 3-by-3 integer coefficient matrix and six
integer measurement vectors. Each of the six settings is a **binary projective measurement
consisting of a rank-one projector and its rank-two orthogonal complement**; the certificate's
`rank_one_outcome` field says which outcome carries the rank-one projector, and the verifier
uses that assignment as given. `proofs/verify_improved_qutrit.py` rebuilds all 36 Born
probabilities from those integers in exact rational arithmetic — it reads no stored probability
table — and checks positivity, normalization, no-signaling, and a nonzero determinant of the
coefficient matrix.

**What the determinant does and does not establish.** It establishes that the *supplied state*
has Schmidt rank three. It does not by itself say anything about the behaviour: a
Schmidt-rank-three state can produce a behaviour some Schmidt-number-two state also produces.
What rules that out is `G > 7` together with §1: no Schmidt-number-two realization reproduces
this behaviour, whatever state it uses. The determinant confirms the supplied realization is not
a rank-two one in disguise; the violation is what makes the behaviour a witness.

| Quantity | Value (exact rational, shown to 12 places) |
|---|---|
| original `F` | `6.469225039506` |
| `p = P(00|10)` | `0.162531190409` |
| `G = F + eps0 p` | `7.092839338673` |
| uniform-output white-noise tolerance | `1.513615%` |

Note the first row: the **original** `F` does not detect this point at all. It is detected only
by the penalised functional.

**The white-noise model, stated precisely.** `U` is the uniform-output behaviour,
`P_U(ab|xy) = 1/4` for all `a,b,x,y`. All of its marginals and correlators vanish, so `F(U) = 0`
and `p(U) = 1/4`, giving

    G(U) = eps0/4,   which is NOT zero.

For a noise fraction `eta`, `G((1-eta)Q + eta U) = (1-eta) G(Q) + eta eps0/4`, so the largest
`eta` still exceeding 7 is

    eta_crit = (G(Q) - 7) / (G(Q) - eps0/4).

The naive `(G(Q)-7)/G(Q)` drops the constant term and is **wrong for `G`**; it happens to be
right for `F` only because `F(U) = 0`. The verifier constructs the threshold mixture explicitly
and checks it lands exactly on `G = 7`.

This is depolarizing noise applied to the outputs of a fixed behaviour. It is **not** a
detector-efficiency threshold, not a bound for arbitrary physical noise, not a visibility, and
not a finite-statistics statement.

Under the same uniform-output-noise model, the supplied strengthened-witness realization
tolerates approximately 8.2 times more noise than the supplied original realization —
`1.513615%` against `0.184123%`. Both witnesses are normalized to the same bound 7, so the two
percentages are computed the same way; what differs is the functional and the realization, so
this compares two particular certified realizations and **not** their proven optimal robustness.
The see-saw search that found the new realization is a lower-bound discovery method, not a proof
of the global qutrit maximum of `G`.

## 7. Proof map: what is machine-checked and what is not

| Step | Status | Where |
|---|---|---|
| `X` is positive definite (exact rational LDL) | machine-checked | `proofs/verify_penalty_endpoint.py` |
| `X` is positive definite (integer Bareiss leading minors) | machine-checked, independent route | `tests/verify_endpoint_independent.py` §C |
| the operator identity, repository normaliser | machine-checked | `proofs/verify_penalty_endpoint.py` |
| the operator identity, second normaliser written from scratch | machine-checked, independent route | `tests/verify_endpoint_independent.py` §A |
| the operator identity, explicit Gaussian-rational 2-qubit matrices, no normal ordering at all | machine-checked, independent route | `tests/verify_endpoint_independent.py` §B |
| the twelve branch duals, and behaviours attaining each value | machine-checked, twice | `proofs/verify_penalty_endpoint.py`, `tests/verify_endpoint_independent.py` §D |
| the lower strategy and the ratio | machine-checked | `proofs/verify_penalty_endpoint.py` |
| the qutrit behaviour, Schmidt rank, score and noise threshold | machine-checked | `proofs/verify_improved_qutrit.py` |
| `G` is not valid on `H` | machine-checked, from the existing facet certificate | `proofs/verify_penalty_not_partial_local.py` |
| binary-effect decomposition and Schmidt compression (§5) | **prose**, numerically corroborated only | this document; `tests/verify_endpoint_independent.py` §E |
| `alpha_star` itself | **open** | — |

`tests/test_endpoint_mutations.py` corrupts each certificate and requires rejection to carry the
specific diagnostic code for the defect introduced, with two controls against the suite
degrading into exit-code checking. The sharpest case perturbs the Gram inside the kernel of
`X |-> sum X[j,k] J_j^dagger J_k`, so the operator identity still reconstructs with zero residual
and only positivity fails — a verifier that rebuilt the identity but skipped the positivity test
would accept it.

## 8. What is not established

* the exact value of `alpha_star`, or any exact algebraic form for it;
* the global qutrit maximum, or the dimension-unrestricted quantum maximum, of `G`;
* a self-testing or rigidity statement at the conjectured critical penalty;
* any facet, dimension or partial-locality property of `G` — §0 shows the natural one is false;
* a quantitative distance-to-equality theorem for near-saturating `S2` behaviours (the equality
  face itself is now classified — `docs/CERTIFICATE_EQUALITY_FACE.md` — but how *fast* a
  near-saturating behaviour approaches it is not);
* the equality face at the exact critical penalty `alpha_star`, as opposed to on `[0, eps0]`;
* experimental feasibility, loss tolerance, or finite-sample significance;
* novelty. `docs/PRIOR_ART.md` records the audit status, including three comparators located
  in this round — Pauwels [arXiv:2608.29734](https://arxiv.org/abs/2608.29734), Goh et al.
  [arXiv:1710.05892](https://arxiv.org/abs/1710.05892) and Rai et al.
  [arXiv:1812.06057](https://arxiv.org/abs/1812.06057) — for which only abstract-level
  verification was possible here, plus one (Connor) of which no text has been read at all.
  Nothing here has been cleared against the dimension-witness or quantum-set-geometry
  literature. In particular, a machine-formalized exact result about I3322 in this same
  scenario exists as an August 2026 preprint, so "exact and independently checkable" is not by
  itself a contribution.

## 9. Provenance

The endpoint Gram, the twelve branch duals, the lower strategy and the improved qutrit
realization were produced by **ChatGPT ("Astra")** in an adversarial review round and supplied
as data. They were **not** adopted on the strength of the accompanying verifier. Before
integration, every claim above was re-derived here by Claude: the operator identity twice more
(a second normal-ordering algorithm, and explicit Gaussian-rational matrices with no normal
ordering), positivity by integer elimination as well as rational LDL, the duals rebuilt from
`P(ab|xy) >= 0` with attaining behaviours exhibited, the qutrit rebuilt from raw integers, and
the `H` counterexample located inside the repository's own facet certificate rather than taken
on report. The verifiers and tests committed here are Claude's.

The equality-face theorem that arrived in the same package — that the `F = 7` face of `S2` is
the convex hull of five local deterministic points — was held out of the repository until it had
been reviewed on its own. That review is `docs/review_2026-09-07_equality_face.md`; the theorem
is now integrated, with its own guide at `docs/CERTIFICATE_EQUALITY_FACE.md`, and its §5 records
the corollary that the whole family `F + eps p`, `0 <= eps <= eps0`, has that same equality
face. What happens at the exact critical penalty is still open.
