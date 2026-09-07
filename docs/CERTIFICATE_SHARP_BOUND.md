# Certificate guide: the sharp Schmidt-number-two bound

One page, for a reader who wants to inspect the mathematics before running anything.

**Verifier** `proofs/verify_sharp_qubit.py` — Python standard library only, no dependencies.
**Certificate** `proofs/sharp_qubit_certificate.json`.

## The claim

> For every bipartite behavior `P` arising from a quantum state of **Schmidt number at most
> two** with binary measurements, `F(P) <= 7`. The bound is attained.

## Assumptions, stated as premises

- A standard bipartite Bell model: two parties, three settings each, two outcomes each,
  setting-independent source and measurements, no communication.
- Arbitrary **finite** ambient dimension. The local Hilbert spaces may be any size; what is
  bounded is the Schmidt number of the state.
- Arbitrary binary POVMs, not only projective measurements. Mixed states allowed.
- Nothing is claimed for signaling devices, input-dependent source mixtures, or postselected
  probability tables.

## The functional and its variable ordering

`F` is a linear functional on the 15 correlators, in this order throughout the repository:

```
index   0    1    2     3    4    5     6    7    8    9   10   11   12   13   14
        A0   A1   A2    B0   B1   B2    E00  E01  E02  E10  E11  E12  E20  E21  E22
W  =     1   -1    1    -1   -1    1    -1   -1   -1   -1   -1    1    1   -1   -1
```

Settings and outcomes are **zero-based**. The outcome convention is

```
P(ab|xy) = [ 1 + (-1)^a A_x + (-1)^b B_y + (-1)^(a+b) E_xy ] / 4
```

so outcome `0` maps to `+1` and outcome `1` to `-1`.

## The certificate

| Field | Meaning |
|---|---|
| `coefficients` | the 15 entries of `W` above; `run_checks.py` cross-checks these against every other certificate |
| `bound` | `7` |
| `words` | the 84 words `W_1..W_84` in the six observables, each `[[Alice indices], [Bob indices]]` |
| `basis_map` | the integer matrix `P`, **84 rows by 70 columns**. Its columns define 70 operators as combinations of the 84 words — it is not a re-expression of each word in a smaller basis |
| `reduced_gram` | the **full symmetric** 70×70 rational matrix `X`. It is not stored triangularly; the LDL factor built during verification is a different object |
| `method` | `exact positive Gram with identically zero polynomial residual` |

## What the verifier checks

Two things, both in exact rational arithmetic, and the bound follows from them alone — the
numerical search that produced `X` need not be trusted or rerun.

1. **Positivity.** `X` is positive definite, by exact LDL decomposition with every pivot
   verified positive over the rationals. No eigenvalue estimate, no floating point.
2. **The identity.** The 70 operators are

   ```
   J_j  =  sum_{i=1..84} P[i,j] W_i,        j = 1..70,
   ```

   and the certified statement is

   ```
   sum_{j,k = 1..70} X[j,k] J_j^dagger J_k  =  7 I - Bell_F,
   ```

   equivalently `Z = P X P^T` as a Gram matrix on the original word list, which is what the
   verifier actually computes. It holds identically, reducing every word with only
   `A_i^2 = B_j^2 = I`, the qubit anticommutator relations, and commutation between parties.
   **Every coefficient of the residual is exactly zero** — not small.

   Note the shapes: 84 words, 70 operators, `X` is 70×70. The sum runs to 70, not 84.

A positive-definite `X` makes the left side positive semidefinite for every choice of qubit
observables, so `7 I - Bell_F >= 0` as an operator, and taking the expectation in any state
gives `F <= 7`. The relations used hold for arbitrary unit Bloch vectors, so this covers all
six traceless projective qubit observables, not a selected or coplanar configuration.

## Proof map: what is machine-checked, and what is not

| Step | Status |
|---|---|
| Gram positivity | **machine-checked**, exact rational LDL |
| the SOS operator identity | **machine-checked**, exact symbolic reduction, zero residual |
| ⇒ `F <= 7` for six traceless projective qubit observables, any state | follows from the two above |
| a deterministic observable is jointly measurable with another on that party, so the behavior lies in a partial-local class | **mathematical argument** — the inclusion is reasoned, not computed |
| `F <= 7` on that partial-local class | **machine-checked**, `proofs/verify_facet.py`, exact positivity/CHSH duals |
| arbitrary binary qubit POVMs ⇒ projective or deterministic | **mathematical argument**, `docs/SCHMIDT_NUMBER_BOUND.md` §2 |
| Schmidt rank ≤ 2 in any finite dimension ⇒ qubit POVMs | **mathematical argument**, `docs/SCHMIDT_NUMBER_BOUND.md` §3 |
| Schmidt **number** ≤ 2 ⇒ average over rank-≤2 components | **mathematical argument**, same section |

Those steps are mathematical arguments rather than machine checks. That is a statement about
what is formalized in code, **not** an unresolved gap in the proof: they are elementary, and
they are written out explicitly rather than asserted. The POVM step exhibits the mixture
`M = λ₋ I + (λ₊ − λ₋) Π + (1 − λ₊) 0` and samples its component labels **before** the settings,
which makes the weights setting-independent. A correctly stated sequential-extremality argument
also suffices for the linear maximum; the constructive route is preferred here for being easier
to check by eye, not because extremality methods are incapable of it. The compression step is
applied *first* and the POVM reduction second, because compressed effects need not be
projective.

## Sharpness

`F = 7` is attained by a **product state**, so the bound cannot be lowered — and it is already
attained at Schmidt number *one*:

```
|psi> = |00>,    A_0 = A_1 = A_2 = Z,    B_0 = B_1 = B_2 = -Z
```

Its marginals are `(1,1,1)` and `(-1,-1,-1)`, every correlator is `-1`, and substituting into
`W` gives exactly `F = 7`. The behavior is deterministic, so it is trivially quantum and
trivially local.

**The 15 saturating points of `proofs/facet_certificate.json` are NOT quantum and must not be
cited here.** They are partial-local points: each is local on a *designated two-setting
restriction* only, which is what `proofs/verify_facet.py` certifies, and none carries a local
model for all three settings. Every one of the 15 violates the Tsirelson bound — the maximum
2×2 CHSH value at those points is `10/3` or `4`, against `2*sqrt(2) ≈ 2.8284`. They establish
the *geometry* of the `F = 7` face of `H` (see `docs/CERTIFICATE_FACET.md`), not sharpness of a
quantum bound. An earlier version of this guide made exactly that error.

## The separation

`proofs/verify_qutrit.py` rebuilds a qutrit behavior from Gaussian-integer state and
measurement data and gets `F = 7.0129123854899715 > 7` exactly. So that behavior has Schmidt
number at least three. `proofs/verify_quantum_upper.py` bounds `F <= 7.041387041` with no
dimension assumption — **certified, not claimed sharp** — which is what makes the violation a
bounded fraction of the room available.

## Independent checks

`tests/verify_sos_independent.py` reconstructs the SOS identity from a second implementation
sharing no code with the primary verifier. It is **numerical corroboration** (max discrepancy
`1.33e-13`, Gram least eigenvalue `4.5e-4`), not the proof; the universal statement rests on
the exact rational LDL and symbolic identity above. `tests/check_sharp_pauli.py` reconstructs
the identity again through exact complex Pauli algebra.

## Corruption tests

`tests/adversarial_sharp_checks.py` makes three targeted alterations and requires rejection of
each: a **negative Gram diagonal** entry; a **tiny positive perturbation of a diagonal entry**
that preserves positive-definiteness but breaks the polynomial identity, so positivity alone
cannot catch it; and execution under `python -O`, where assertions used as proof gates would
otherwise vanish. `tests/test_standalone_optimized.py` checks the `-O` refusal across the
standalone verifiers. The verifier prints no affirmative conclusion on rejected input.
