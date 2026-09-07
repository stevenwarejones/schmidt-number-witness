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
| `words` | 84 words in the six observables, each `[[Alice indices], [Bob indices]]`, giving the monomial basis |
| `basis_map` | 84 integer rows expressing each word in the reduced basis |
| `reduced_gram` | the 70×70 rational Gram matrix `X`, lower-triangular by rows |
| `method` | `exact positive Gram with identically zero polynomial residual` |

## What the verifier checks

Two things, both in exact rational arithmetic, and the bound follows from them alone — the
numerical search that produced `X` need not be trusted or rerun.

1. **Positivity.** `X` is positive definite, by exact LDL decomposition with every pivot
   verified positive over the rationals. No eigenvalue estimate, no floating point.
2. **The identity.** With `J_1..J_84` the words above,

   ```
   sum_{j,k} X[j,k] J_j^dagger J_k  =  7 I - Bell_F
   ```

   holds identically, reducing every word with only `A_i^2 = B_j^2 = I`, the qubit
   anticommutator relations, and commutation between parties. **Every coefficient of the
   residual is exactly zero** — not small.

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
| deterministic observables (`+I` or `-I`) | **machine-checked** by a different certificate: such an observable is jointly measurable with another on that party, so the behavior lies in a partial-local class, where `proofs/verify_facet.py` gives `F <= 7` |
| arbitrary binary qubit POVMs ⇒ projective or deterministic | **mathematical argument**, `docs/SCHMIDT_NUMBER_BOUND.md` §2 |
| Schmidt rank ≤ 2 in any finite dimension ⇒ qubit POVMs | **mathematical argument**, `docs/SCHMIDT_NUMBER_BOUND.md` §3 |
| Schmidt **number** ≤ 2 ⇒ average over rank-≤2 components | **mathematical argument**, same section |

The last three are the honest gap: they are elementary and constructive but not machine-checked.
They are written out explicitly rather than asserted — the POVM step exhibits the mixture
`M = λ₋ I + (λ₊ − λ₋) Π + (1 − λ₊) 0` and samples its component labels **before** the settings,
which is what makes the weights setting-independent; extremality alone would not establish that.
The compression step notes that compressed effects need not be projective, which is why it must
precede the POVM step rather than follow it.

## Sharpness

`F = 7` is attained, so the bound cannot be lowered. The 15 affinely independent saturating
points in `proofs/facet_certificate.json` each come with an explicit deterministic local model,
verified by `proofs/verify_facet.py`.

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

`tests/adversarial_sharp_checks.py` and `tests/test_standalone_optimized.py` alter substantive
content — a Gram entry, a coefficient, a required constraint — and require rejection, including
under `python -O` where assertions used as proof gates would otherwise vanish. The verifier
prints no affirmative conclusion on rejected input.
