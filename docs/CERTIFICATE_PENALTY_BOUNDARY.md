# Certificate guide: continuing the penalty bound to a singular Gram boundary

Date: 2026-09-08. Base certificates: PR #1, merged in `37bfaec`.

Draft research supplement: new prose arguments await adversarial review; no human validation. The new arithmetic has been checked by two routes in this session; the new prose arguments have not yet received a separate adversarial review. The original SOS, deterministic-branch bounds, equality theorem and Schmidt/POVM reduction remain dependencies.

## Results and calibration

1. An exact rank-one continuation of the existing Gram lowers the upper bound on the critical penalty from 0.16311 to approximately **0.1631067188466586**. That is the CERTIFIED bound: the exact value is the rational produced by the matrix solve below and stored in `proofs/penalty_boundary_certificate.json`, and the positive semidefiniteness it needs is machine-checked, not argued in prose. The printed decimal is a display of it, nothing more.
2. Because that exact rational has several thousand digits, the quotable form is the short rational just above it, **0.16310672 = 1019417/6250000**. It is a CONSEQUENCE of result 1, not a separate claim: the verifier checks `alpha_b < 1019417/6250000 < 0.16311`. A strictly positive-definite Gram also exists at that rounder value and the repository's existing endpoint verifier accepts it, but no such Gram is shipped and none is needed, since the singular certificate proves the stronger statement. Together this closes approximately 39% of the previous gap to the explicit lower strategy, without a new SDP optimization.
3. The five-vertex equality face persists even at the singular endpoint of this rank-one continuation. Positive definiteness is sufficient for the earlier proof, but not necessary for this new proof.
4. A small certified quadratic correction is available: `G_boundary <= 7 - C p^2`, with exact rational `C` approximately `9.23281185174e-7`. One may replace C by the simpler smaller value `9e-7`.
5. None of these results determines alpha_star. The new witness changes the experimental noise tolerance only negligibly. Do not describe this additional step as another eightfold robustness improvement.

The existing explicit lower strategy still gives approximately 0.16310160137870294. The previously found numerical stationary candidate remains approximately 0.16310160137893096; it is not a certified global optimum.

## 1. Exact continuation of the Gram

Write the inherited certificate as

`7 I - F_operator - epsilon0 K = J^dagger X J`,

where X is the shipped positive-definite 70 by 70 rational Gram, `epsilon0 = 3.83689`, `p = <K>`, and

`J8 = (I+A1)(I+B0) = 4 K`.

All operator statements in this section first concern the nondegenerate projective qubit branch. Therefore `K` is a projector and `J8^dagger J8 = 16 K`.

Let e be coordinate vector e8 and solve exactly

`X v = e`.

Define

`delta = 16/v8`,
`Y = X - (delta/16) e e^T`,
`epsilon_b = epsilon0 + delta`,
`alpha_b = 4 - epsilon_b`.

The exact rational data are in `proofs/penalty_boundary_certificate.json`. Numerically,

```
delta      = 0.0000032811533413942333...
alpha_b    = 0.1631067188466586...
epsilon_b  = 3.8368932811533414...
```

**Rank-one lemma.** If X is positive definite, then `X - t e e^T` is positive semidefinite precisely for `t <= 1/(e^T X^-1 e)`, and at equality its kernel is exactly the span of `X^-1 e`. This follows by conjugating with `X^-1/2`: the resulting matrix is identity minus a rank-one projector at the boundary. Here `e^T X^-1 e = v8 > 0`. That is what fixes the value of `delta`.

**The positivity itself is checked, not assumed.** At the boundary the conclusion does not need the lemma at all, and does not need any new computation either. `Y` differs from `X` in entry `(8,8)` and nowhere else, so its principal submatrix on the other 69 indices *is* `X`'s, which is positive definite because `X` is — a fact the inherited endpoint verifier establishes by exact LDL. Given `Yv = 0` and `v8 != 0`, every `w` splits as `w = (w8/v8) v + w'` with `w'[8] = 0`, and then

    w^T Y w  =  w'^T Y w'  =  w'^T X|_(i,j != 8) w'  >=  0,

zero exactly when `w' = 0`, that is exactly on `span(v)`. So `Y >= 0` with kernel exactly `span(v)`, and `proofs/verify_penalty_boundary.py` checks the one structural fact this rests on — that `Y` carries `X` away from entry `(8,8)` — with diagnostic code `[E-BOUNDARY-PSD]`. An earlier draft of this document left the whole positivity claim to the `X^-1/2` conjugation above.

Consequently Y is PSD with corank one and

`7 I - F_operator - epsilon_b K = J^dagger Y J`.

The deterministic branches retain the stronger bound `F + 4p <= 7`; since `epsilon_b < 4`, they also obey the new bound. The inherited effect decomposition and Schmidt compression extend it to all S2 behaviors.

This continuation is optimal only along the fixed matrix line `X-t e8 e8^T`. It is not optimization over all Gram representations or all quantum strategies.

## 2. The singular endpoint still exposes only L_F

The code checks the additional exact identity

`J9 = (I+A1)(I+B1)`.

Both J8 and J9 are positive semidefinite: each is a tensor product of positive operators on the two parties. The exact solve gives

`r := v9/v8 < 0`, numerically `r = -0.1328547625770212...`.

For a pure state saturating the new bound, the vector of Hilbert-space vectors `(J_j |psi>)_j` lies in `ker(Y) tensor H`. Since this kernel has dimension one,

`J_j |psi> = v_j |eta>` for one vector eta.

In particular `J9 |psi> = r J8 |psi>`. Taking expectation values gives `<J9> = r <J8>`. Both expectations are nonnegative, while r is negative. Hence both vanish. Positivity of J8 then implies `J8 |psi> = 0`; because v8 is nonzero, eta is zero and every `J_j |psi>` vanishes. The original SOS implies F=7; the original equality theorem puts the behavior in L_F.

**This argument is specific to this Gram.** It turns on `r = v9/v8` being negative, which is an outcome of the exact solve rather than a structural feature of the construction. Had `r` come out positive, the two expectations would be consistent at nonzero value and the equality face at `epsilon_b` would be open. Do not read §2 as a general mechanism for singular continuations.

For a deterministic branch, `F+4p<=7` and `F+epsilon_b p=7`, with `epsilon_b<4`, force p=0 and F=7. Saturation passes componentwise through the inherited POVM and mixed-state reductions. Conversely the five local vertices all have F=7 and p=0.

Thus, subject to those inherited results,

`S2 intersect {F + epsilon p = 7} = L_F` for every `0 <= epsilon <= epsilon_b`.

For epsilon below epsilon_b, comparison with the endpoint bound immediately forces p=0. The new endpoint case is what required the argument above.

**Do not conflate the two endpoints.** epsilon_b is where one chosen Gram continuation becomes singular. The true physical validity endpoint is `4-alpha_star`, still unknown. In particular, having only p=0 equality cases at epsilon_b does not prove that a still larger epsilon is valid: a supremum of a ratio can be approached as p tends to zero without being attained at positive p.

## 3. An explicit quadratic remainder

This is a quantitative event-probability result, NOT a distance-to-L_F theorem.

Set `a = e9 - r e8`. It is orthogonal to v, so a lies in the range of Y. Solve `Y z = a`; the supplied solution takes z8=0. Define

`c0 = 1/(a^T z) > 0`.

Cauchy-Schwarz in the PSD form Y gives `Y >= c0 a a^T`. The arithmetic checker verifies `Yz=a`, `a^T v=0` and the required signs exactly. It is not necessary to trust a numerical pseudoinverse.

Define `H = J9 - r J8`. Since r<0 and J8,J9 are PSD, H is PSD and `<H> >= -4 r p`. For a normalized pure state,

```
7 - G_boundary
  >= c0 ||H psi||^2
  >= c0 <H>^2
  >= 16 c0 r^2 p^2.
```

Put `C = 16 c0 r^2`. The exact data give

`0 < 9e-7 < C < alpha_b`.

In a deterministic branch, `7-G_boundary >= alpha_b p >= C p^2`, using 0<=p<=1. For convex mixtures, Jensen's inequality gives `sum w_i p_i^2 >= (sum w_i p_i)^2`, so the same bound holds after the POVM and Schmidt-number reductions.

Therefore every S2 behavior satisfies

`F + epsilon_b p <= 7 - C p^2`.

Equivalently, for p>0,

`(M_A-6)/p <= alpha_b - C p`.

This describes a small amount of curvature in the projected (p,M_A) tradeoff and supplies another proof that p>0 cannot saturate this particular supporting line. It does not settle the p->0 limit or global optimality. The tiny coefficient makes it a structural observation, not a meaningful experimental improvement.

## 4. Verification and regeneration

Run `python proofs/verify_penalty_boundary.py` from any directory. It checks the
added rational identities, then runs both inherited endpoint and equality-face
verifiers before printing the new conclusion. Verification uses the standard
library; the original proof chain remains a dependency. `python run_checks.py`
includes it. Assertions are proof gates: optimized Python execution is refused.

`tests/test_penalty_boundary_mutations.py` rejects altered input hashes, solved
vectors, coefficients and the advertised rational bound for the intended reasons,
where "intended reason" means the message carries this defect's diagnostic code
and no other case's. It also tests that either inherited dependency failing
suppresses the new conclusion, that an extra rank-one term orthogonal to `v` --
which preserves `Yv = 0` and every arithmetic identity while silently destroying
the positivity the bound rests on -- is rejected with `[E-BOUNDARY-PSD]`, and
that the regeneration script cannot read an unrelated proof certificate. Two
controls guard the suite itself: a refusal naming every diagnostic code must NOT
count as a valid rejection, and a mutation must not satisfy another case's code.
This is scoped regression coverage, not a proof of arbitrary-program soundness.

`research/derive_penalty_boundary.py` regenerates the rational data using
Python-FLINT and writes `build/penalty_boundary_certificate.json`. It performs
no SDP search. Regeneration and Fraction-based verification use different
arithmetic implementations, but share the mathematical construction. Positive
semidefiniteness of `Y` is now machine-checked by the reduction in §1. The
singular-kernel equality argument of §2 and the convex extension of §3 remain
prose proofs, not Lean formalizations or independent human verification.

The old endpoint certificate is intentionally retained: its positive definiteness
is an input to the continuation. The old qutrit score and noise tolerance still
refer to the old epsilon0; neither is silently recomputed at epsilon_b.

## 5. Questions for the adversarial reviewer

1. Does the application of the rank-one PSD lemma have the right factor 16 and
   kernel convention, including complex Hilbert-space vectors? The positivity
   conclusion no longer depends on the answer -- see the submatrix reduction in
   §1 -- but the value of `delta` still does.
2. Does equality imply that the two positive event operators have expectations
   of opposite signs unless both vanish? Check the transition from zero
   expectation to zero action, and the deterministic-observable branches.
3. Does the PSD Cauchy-Schwarz bound establish `Y >= c0 a a^T`, and does Jensen
   extend `7-G >= C p^2` to the stated S2 model class?
4. Does any existing parameterized three-setting Bell inequality imply this
   particular tradeoff or equality classification? See `docs/PRIOR_ART.md`.

The exact optimum alpha_star, its attainment, the p->0 limit of the ratio, and
its equality face remain open. The one-dimensional Gram continuation is not a
search over all valid certificates. More numerical digits at one stationary
point cannot close the global problem. Historical priority remains unestablished.

## 6. Review status

Constructed and checked by ChatGPT during the 2026-09-08 research continuation.
The simpler positive-definite certificate at alpha=0.16310672 was also accepted
by the existing endpoint verifier in a disposable copy. This PR makes the
additional arithmetic reproducible; it does not promote a self-review to an
independent review. The other agent should review this guide before the new
prose statements are treated as settled project results.
