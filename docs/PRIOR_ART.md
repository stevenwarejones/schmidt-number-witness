# Prior-art status

**Nothing below has been reviewed by a human expert. Priority is not claimed.**

This repository does not claim priority. A different convex set and an exact facet
certificate are mathematical facts; they do not establish a new contribution without
comparison of equivalent descriptions and relabelings.

## Resolved: the valid inequality F <= 7 on H is a corollary of published work

This was previously listed as an open question ("our F is not a facet of that hull, but this
does not exclude ... derivability from their inequalities"). It is now settled, against us,
and `proofs/verify_m3322_corollary.py` proves it exactly — including the two steps that would
otherwise be prose: the transcription of eq. (48) is checked against its published local bound
of 6, and `M_A <= 6` on `H_A` / `M_B <= 6` on `H_B` are certified directly by exact duals on
each of the six constituent classes (each a sum of five positivity/CHSH rows) rather than
inferred from the relabeling argument.

Quintino, Budroni, Woodhead, Cabello and Cavalcanti, PRL **123**, 180401 (2019),
[arXiv:1902.05841](https://arxiv.org/abs/1902.05841), Appendix G, characterize the
**one-sided** hull `L^A_2conv := Conv(L^A_12, L^A_23, L^A_13)` with 4452 facets in six
relabeling classes. Their eq. (48) is the M3322 inequality, bound 6, and is the only one of
the six violated in quantum physics. There are exact identities

    F  =  M_A  -  4 p(00|10)  +  1
    F  =  M_B  -  4 p(11|22)  +  1

where `M_A` is a relabeling of eq. (48) by local input/output relabelings **without party
exchange** — both parties may be relabeled; what matters is that an Alice-partial-local class
is not converted into a Bob-partial-local class — and `M_B` is the image of `M_A` under the
party exchange. Setting relabelings map `L^A_2conv` to itself, so `M_A <= 6`
holds throughout `H_A` and `M_B <= 6` throughout `H_B`. With `p >= 0` this gives `F <= 7` on
`H_A`, on `H_B`, and hence on `H = Conv(H_A, H_B)` — in three lines, from a published facet.

Two things are **not** covered by that derivation, and the verifier checks the second of them
explicitly:

- **the sharp Schmidt-number-two bound** (`docs/SCHMIDT_NUMBER_BOUND.md`,
  `proofs/verify_sharp_qubit.py`). That is a penalized statement about quantum
  realizations rather than a statement about `H`, and no facet of a partial-local polytope
  implies it.
- **that `F <= 7` is a facet of `H`** (`proofs/verify_facet.py`: an exact
  14-dimensional face). Neither parent inequality holds over the entire two-sided face:
  `M_A` reaches `22/3 > 6` at one certified saturating point and `M_B` at another. Those are
  violations at points lying outside that parent's own one-sided domain — permitted, and
  checked to be of exactly that kind — so neither one-sided derivation reaches the whole face
  and neither gives the facet property on its own.

`F` itself is not a relabeling of M3322: the two 2304-element orbits under outcome flips,
setting permutations and the party swap are disjoint. That remains true, and is now much less
interesting than it looked, because the derivation above does not need `F` to be one.

## Affirmative: F detects a behavior the standard score thresholds miss

The corollary above is a limit on what the *inequality* contributes. It is not the whole
picture, and `proofs/verify_novelty_comparison.py` proves the complement exactly. The shipped
qutrit behavior `Q` is invisible to every relabeled ordinary score threshold for the two
inequality families in this scenario, while `F` sees it:

| Test | Distinct relabelings | Largest value on `Q` | Benchmark | Detected? |
|---|---:|---:|---|:--:|
| CHSH | 72 | 2.0876402763431794 | `2*sqrt(2)` (Tsirelson; every dimension) | no |
| I3322, local bound 4 | 576 | 4.1403881793679336 | 5, achieved exactly by `Φ⁺` with `A₀=B₀=(√3X+Z)/2`, `A₁=B₁=(√3X−Z)/2`, `A₂=B₂=Z` | no |
| M3322, local bound 6 | 2304 | 6.0221540521920467 | 6.0243205027525546, achieved exactly by an explicit two-qubit state built in the verifier | no |
| `F` | its shipped orientation | 7.0129123854899715 | proved Schmidt-number-two ceiling 7 | **yes** |

**No leg relies on a published maximum.** Each needs only an *achievable* qubit benchmark: a
behavior scoring below something qubits reach cannot have crossed the true qubit maximum,
whatever that maximum is. Both the I3322 and M3322 benchmarks are explicit two-qubit
constructions evaluated exactly in the verifier. Neither is presented as a proof of a qubit
upper bound, because neither is one.

So `F <= 7` is **not implied** by the conjunction of those relabeled scalar thresholds with
quantum membership — `Q` is a quantum counterexample to that implication.

**Scope.** This covers input permutations, output flips and party exchange of two inequality
families, and nothing else: not local preprocessing, filtering, sequential wirings, many-copy
protocols, probability-conditioned tradeoffs, or dimension-constrained inequalities generally,
any of which could imply the bound while the scalar thresholds do not. The supported claim is
"missed by the standard score thresholds", not "missed by every existing witness". `Q` does
violate the *local* I3322 and M3322 bounds, so this says nothing about its nonlocality or its
measurement incompatibility being unseen — the comparison is about entanglement dimension.

## Audit of the two probability-tradeoff leads

The two items previously listed as highest-value were a probability-conditioned / Hardy
tradeoff comparison, and dimension-witness catalogues under setting identifications. Both were
worked; one closed at coefficient level, the other only narrowed.

### The closest published family tilts a MARGINAL; F penalizes a JOINT probability

The nearest published objects in shape are the **detection-efficiency** variants of I3322,
used for local-dimension bounds by Navascués, de la Torre and Vértesi, PRX **4**, 011011 (2014),
[arXiv:1308.3410](https://arxiv.org/abs/1308.3410).

The relevant fact is the *form* of the η-dependent term, and it is now taken from a primary
source rather than a search summary. Brunner, Gisin, Scarani and Simon,
[quant-ph/0702130](https://arxiv.org/abs/quant-ph/0702130), give the probability polynomial and
detection formula; with a fixed local fallback output for the nondetected party at `η_A = 1`,
the one-sided expression is proportional to

    J_η  =  J + ((1−η)/η) · [ p_A(0|0) − 1 ]

— a **one-party marginal plus a constant**. More generally, a fixed local fallback output under
independent one-sided loss changes the surviving joint-probability functional only by a positive
overall scaling and one-party terms. This does **not** extend to setting-dependent efficiencies
or to postselection, and no claim is made about those.

That is enough to settle the comparison without their displayed equation, because a one-party
marginal occupies coordinates 0–5 and **cannot change any correlator coefficient**. The size of
the correlator support is therefore invariant under every marginal tilt, and it is also
invariant under relabeling. `proofs/verify_novelty_comparison.py` checks the three orbits:

| Functional | Nonzero correlator coefficients, across the whole relabeling orbit |
|---|:--:|
| `F` | **9** |
| I3322 | 8 |
| M3322 | 8 |

So `F` is not I3322 or M3322 tilted by any one-party marginal, in any relabeling, at any
positive scale — and neither is any other member of a marginal-tilted family.

**This is coefficient non-equivalence, which is weaker than non-derivability.** It rules out
relabeling and scaling of these two parent families plus marginal tilts. It does **not** rule
out consequences of several inequalities together, other positivity penalties, restrictions of
larger scenarios, filtering, or other dimension tradeoffs. That distinction is maintained in
every novelty statement in this repository. The verifier also
locates the discrepancy exactly: the penalty `−4 p(00|10)` is a **joint** probability, and its
correlator `E21` is precisely the single entry M3322 leaves at zero. The ninth correlator is
what a joint-probability penalty buys and a marginal tilt cannot.

### Hardy-type conditional witnesses cannot be applied to this behavior

The Hardy dimension witnesses — Mukherjee, Roy, Bhattacharya, Das, Gazi and Banik, PRA **92**,
022302 (2015), [arXiv:1407.2146](https://arxiv.org/abs/1407.2146), building on Chen, Cabello,
Xu, Su, Wu and Kwek, [arXiv:1308.4468](https://arxiv.org/abs/1308.4468) — live in the
**(2 settings, 3 outcomes)** scenario, not (3,3,2,2), and condition on probabilities vanishing
**exactly**. Our behavior `Q` has **no exact zeros**: its smallest probability is
`53279182288146183/66660503297129198901092 ≈ 7.99 × 10⁻⁷`. A witness conditioned on exact
zeros does not apply to it as written.

### Context: the usual I3322 threshold does not detect the supplied qutrit behavior

This is a statement about **`Q`**, established directly by the exact benchmark above, and it
must not be inflated into a general claim about tight 3322 inequalities. I3322 *is* a dimension
witness in the qubit-versus-arbitrary-dimension sense: its qubit value is 0.25, its true maximum
0.250875… is larger and is not attained in any finite dimension (Pál and Vértesi,
[arXiv:1006.3032](https://arxiv.org/abs/1006.3032)). What it is not is a qubit-versus-**qutrit**
witness — its maximum is 0.25 in `C³⊗C³` as well (Navascués and Vértesi, PRL **115**, 020501
(2015), [arXiv:1412.0924](https://arxiv.org/abs/1412.0924), certified to 7 digits). A
qubit-versus-qutrit comparison is the narrower question, and it is the one `F` answers.

Separately, Pál and Vértesi's survey of 241 tight two-outcome inequalities up to five settings
per party ([arXiv:0810.1615](https://arxiv.org/abs/0810.1615)) found higher-dimensional
advantage in 43 cases, all at four and five settings, remarking that the simplest three-setting
inequality was "surprisingly" not among them. `F` is **not** a facet of the local polytope, so
it falls outside that survey — which is also why absence from it proves nothing.

### What these audits did NOT clear

- The verbatim defining equation of `I3322(η)` was never retrieved; the exclusion above rests
  on its tilt term being a one-party marginal, which was read from a summarizer rather than
  from a displayed equation. If that term is in fact a joint probability, the exclusion fails
  and the comparison must be redone.
- No catalogue of dimension-witness **coefficient vectors** was located, so the hypothesis that
  `F` is a larger-scenario inequality restricted under setting identifications is **untested**.
  The 4422 and 5522 tables of arXiv:0810.1615 are the obvious place to test it; those vectors
  could not be extracted.
- Non-facet 3322 expressions are outside every survey found. Searching was English-language web
  search only, not INSPIRE or full-text scholarly search.

Absence of hits is not evidence of novelty, and none of the above was performed by a human
expert.

## Still open

| Comparator | Relation to investigate |
| --- | --- |
| [Quintino et al. (2019)](https://arxiv.org/abs/1902.05841) | The inequality is settled above. Whether the **two-sided convexification** and its facet structure appear anywhere in the follow-up literature is not settled. |
| [Chen et al., Device-independent quantification of measurement incompatibility (2021)](https://doi.org/10.1103/PhysRevResearch.3.023143) | Compare quantitative certificates and assumptions; do not describe all incompatibility quantification as new. Full model-by-model comparison remains pending. |
| [Tendick, Budroni and Quintino (2025)](https://arxiv.org/abs/2506.21223) | Distinct notions of measurement reduction and convexification have different meanings. Locate our compatible-pair mixture definition precisely; do not equate it with every notion of needing three measurements. |
| [Navascues and Vertesi](https://arxiv.org/abs/1412.0924), [Navascues et al.](https://arxiv.org/abs/1507.07521) | The sharp bound certifies Schmidt number >= 3 for the supplied behavior. Compare against dimension and entanglement-dimension witnesses. The general method is established; priority of this particular witness is not. |

The highest-value remaining work is now narrow and specific: obtain the displayed definition of
`I3322(η)` and confirm its tilt term is a marginal, and extract the 4422/5522 coefficient
vectors of arXiv:0810.1615 to test `F` under setting identifications. A targeted expert question
should show the coefficient vector, the two positivity identities, and the correlator-support
argument above — not the phrase "two-sided partial locality". No outreach has been performed.

The candidate contribution, stated so that the corollary above cannot be read back into it:

> An exact, dependency-free certificate that a positivity-penalized M3322 functional is
> bounded by 7 for **every Schmidt-number-two quantum behavior**, together with an explicit
> qutrit behavior that exceeds it while satisfying every relabeled ordinary I3322 and M3322
> qubit score threshold.

The partial-locality geometry is a supporting result rather than the headline: derivability of
the inequality's *validity* does not erase the geometric content, and the 13/13/14 face
structure with the two-sided facet emergence stands on its own. No exhaustive novelty audit has
been completed, and neither sentence has been cleared against the dimension-witness literature.
