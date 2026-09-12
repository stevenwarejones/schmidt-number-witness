> **Access/comparison update, 9 September 2026:** the exact GK family comparison is
> complete; Goh Appendix G and Pauwels Appendices A/D have now been inspected in full text.
> Connor's author webpage was read, but the linked full proof was unavailable.
> Current access status is updated below; the extended evidence is in
> [the extended comparison](EXTENDED_COMPARISON.md). None is human expert validation.

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

where `M_A` is obtained from eq. (48) by local input/output relabelings **without party
exchange** — both parties may be relabeled; what matters is that an Alice-partial-local class
is not converted into a Bob-partial-local class — and `M_B` is obtained from eq. (48) by local
relabelings **together with** party exchange.

`M_B` is **not** the bare party swap of this particular `M_A`: the two live in the same
published orbit but need different relabelings. Explicitly, in the repository's ordering,

    M_A       = [1, 0, 1,  0,-1, 1, -1,-1,-1,  0,-1, 1,  1,-1,-1]
    M_B       = [1,-1, 0, -1,-1, 0, -1,-1,-1, -1,-1, 1,  1,-1, 0]
    swap(M_A) = [0,-1, 1,  1, 0, 1, -1, 0, 1, -1,-1,-1, -1, 1,-1]

`proofs/verify_m3322_corollary.py` checks the correct statement — that each lies in the
appropriate half of the orbit — and never claims one is the swap of the other. Setting relabelings map `L^A_2conv` to itself, so `M_A <= 6`
holds throughout `H_A` and `M_B <= 6` throughout `H_B`. With `p >= 0` this gives `F <= 7` on
`H_A`, on `H_B`, and hence on `H = Conv(H_A, H_B)` — in three lines, from a published facet.

Two things are **not** covered by that derivation, and the verifier checks the second of them
explicitly:

- **the sharp Schmidt-number-two bound** (`docs/SCHMIDT_NUMBER_BOUND.md`,
  `proofs/verify_sharp_qubit.py`). That is a penalized statement about quantum
  realizations rather than a statement about `H`, and the displayed partial-local derivation
  does not establish it — that bound uses the separate quantum argument and certificate. No
  universal claim is made about what some *other* partial-local argument might reach.
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

### The correlation-weighted family, over its whole parameter range

The ordinary **I3322** threshold above is the `c = 1` member of a published one-parameter
family — this does not apply to the M3322 or CHSH thresholds, which are not members of it —

    I3322(c) = <A0> + <A1> + <B0> + <B1> - <A0B0> - <A0B1> - <A1B0> - <A1B1>
               + c ( <A0B2> - <A1B2> + <A2B0> - <A2B1> ),

defined at [arXiv:1507.07521](https://arxiv.org/abs/1507.07521) Eq. (26) and
[arXiv:1808.02412](https://arxiv.org/abs/1808.02412) Eq. (E1).
`proofs/verify_i3322_family.py` settles it for **every** `c >= 1` at once.

It derives the qubit benchmark rather than quoting one: with the maximally entangled two-qubit
state and `A₀ = tX + zZ`, `A₁ = −tX + zZ`, `A₂ = X`, `B₀ = tX − zZ`, `B₁ = −tX − zZ`, `B₂ = X`
on `t² + z² = 1`, the score is `4 − 4t² + 4ct`, giving `4 + c²` at `t = c/2` and `4c` at
`t = 1`. Each relabeling makes `c ↦ I3322(c)(Q)` an affine function, 576 distinct lines in all,
and every one lies strictly below the benchmark on both intervals — smallest margin
`0.5834085189625386` near `c ≈ 1.6027`, decided in exact rational arithmetic.

These are **achievable** qubit scores, i.e. lower witnesses. Nothing here claims they are the
qubit maxima, and the argument does not need that.

### Is F a four-setting inequality with settings identified?

`research/audit_catalog_folds.py` — a **comparison, not a proof gate** — takes the 129
four-setting `J⁽ⁿ⁾₄₄₂₂` inequalities of Pál and Vértesi's Table I
([arXiv:0810.1615](https://arxiv.org/abs/0810.1615)), archived verbatim, and folds each down to
three settings under the 20 surjective reductions per party (12 signed pair identifications, 8
deterministic substitutions):

    129 inequalities  ×  20 Alice maps  ×  20 Bob maps  =  51,600 reductions,  0 matches.

Two integrity checks give that number meaning: every source vector is independently confirmed
to have classical maximum 0 in the source convention — a check on the coefficients, **not**
authentication of which published equation was transcribed — and a positive control lifts `F`
to four settings, by adding an unused all-zero setting, and requires the fold to recover it. A
control that split a nonzero row between two settings would be stronger; this one is not that.

**This covers 129 rows of one table** — not all 241 inequalities of that survey, not all 175
four-setting classes, not five settings, not arbitrary wirings, and not positive combinations
of several inequalities. Zero matches is not evidence of novelty.

### Comparisons that remain open

- the broader Gigena–Kaniewski scalar-score comparison is now **resolved**: all 1,152
  projected targets have exact SN2 simulators. See `proofs/verify_gigena_complete.py` and
  `docs/EXTENDED_COMPARISON.md`. The earlier eight-case gap is superseded.
- the detection-efficiency family's own detection comparison, as opposed to the
  correlator-support argument above.
- the remainder of the complete four-setting catalogue data.
- arbitrary combinations of prior bounds, wirings, filtering, many-copy protocols, and
  conditional or probability-penalized tradeoffs generally.

**Scope.** The score-threshold comparison covers input permutations, output flips and party
exchange of two inequality families, and nothing else: not local preprocessing, filtering, sequential wirings, many-copy
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
correlator `E10` (zero-based, as `docs/THEORY.md` declares) is precisely the single entry
M3322 leaves at zero. The ninth correlator is
what a joint-probability penalty buys and a marginal tilt cannot.

### The Hardy comparator: one paper, and only its exact-zero form is disposed of

Mukherjee, Roy, Bhattacharya, Das, Gazi and Banik appear under two titles that are **versions
of the same work**, not two comparators: *Device independent Schmidt rank witness by using
Hardy paradox* ([arXiv:1407.2146](https://arxiv.org/abs/1407.2146)) and *Hardy's test as a
device-independent dimension witness* (PRA **92**, 022302 (2015),
[doi](https://doi.org/10.1103/PhysRevA.92.022302)). An earlier version of this document listed
them as two distinct open items. It builds on Chen, Cabello, Xu, Su, Wu and Kwek,
[arXiv:1308.4468](https://arxiv.org/abs/1308.4468).

It is the closest comparator found by **claim type**, since it witnesses Schmidt rank rather
than merely dimension.

Disposed of: the **displayed exact-zero test**. It lives in the **(2 settings, 3 outcomes)**
scenario, not (3,3,2,2), and conditions on probabilities vanishing exactly. `Q` has **no exact
zeros** — its smallest probability is `53279182288146183/66660503297129198901092 ≈ 7.99 ×
10⁻⁷` — so that test does not apply to it as written.

**Not** disposed of: any robust, noise-tolerant or transformed version of the same idea, and
the coefficient-level relation of that construction to `F`, which has not been examined.

### Context: the usual I3322 threshold does not detect the supplied qutrit behavior

This is a statement about **`Q`**, established directly by the exact achievable benchmark
above, and it must not be inflated into a general claim about tight 3322 inequalities.

Two qualifications matter, and an earlier version of this document got both wrong:

- Pál and Vértesi ([arXiv:1006.3032](https://arxiv.org/abs/1006.3032)) exhibit a construction
  approaching `0.250875…`, above the qubit value `0.25`, and **conjecture** that the supremum
  is not attained in any finite dimension. That was their conjecture, not a theorem, and this
  document previously cited it as one. As of 30 August 2026 an **unrefereed preprint** claims to
  prove it — see "New comparators" below. This document does not restate it as settled fact, and
  nothing here depends on which way it goes.
- Navascués and Vértesi ([arXiv:1412.0924](https://arxiv.org/abs/1412.0924)) report a
  **numerical** SDP computation, certified to seven significant digits, that the `C³⊗C³`
  maximum is also `0.25`. That is a numerical result, not an exact equality theorem.

Neither qualification weakens anything here, because the non-detection argument needs only the
exact achievable benchmark constructed in the verifier — not any literature maximum.

Separately, Pál and Vértesi's survey of 241 tight two-outcome inequalities up to five settings
per party ([arXiv:0810.1615](https://arxiv.org/abs/0810.1615)) found higher-dimensional
advantage in 43 cases, all at four and five settings, remarking that the simplest three-setting
inequality was "surprisingly" not among them. `F` is **not** a facet of the local polytope, so
it falls outside that survey — which is also why absence from it proves nothing.

### New comparators located in the 7 September 2026 review round

These arrived with the penalty-endpoint package (`docs/CERTIFICATE_PENALTY_ENDPOINT.md`) as
reported findings. They are recorded here with **what was independently checked in this
repository's session and what was not**, because the difference is the whole point of this file.
The rule applied: a comparator is only described by what a source actually seen here says.

| Source | Checked here | Not checked here |
|---|---|---|
| Pauwels, *The quantum supremum of the I3322 Bell inequality is not attained in finite dimension*, [arXiv:2608.29734](https://arxiv.org/abs/2608.29734) | full PDF inspected: Appendix A states and argues the arbitrary-binary-measurement qubit value 1/4; Appendix D limits Lean coverage to finite-dimensional pure-projective strategies | full nonattainment proof not independently validated; Lean project not built; the mixed-state/POVM reduction is explicitly outside its formalized scope |
| Goh et al., *Geometry of the set of quantum correlations*, [arXiv:1710.05892](https://arxiv.org/abs/1710.05892) | Appendix G inspected: the local face has five affinely independent vertices; its quantum face contains the nonlocal Hardy point and has dimension five | no inference that this establishes our particular 3322 SN2 four-simplex classification; broad novelty still unresolved |
| Rai, Duarte, Brito, Chaves, *Geometry of the quantum set on no-signaling faces*, [arXiv:1812.06057](https://arxiv.org/abs/1812.06057) | the listing exists; the abstract does concern faces of the no-signaling set on which every nonlocal correlation is postquantum ("quantum voids"), a full characterization in the simplest Bell scenario, and use as a dimension witness | the full text, and any detailed relation to the forced-zero-probability reasoning used in the endpoint work |
| Connor, *Maximal I3322 Violation Requires Infinite Local Dimension*, [author webpage](https://violet-connor.neocities.org/i3322) | author explanation read; records claims of nonattainment and Schmidt-rank gaps | linked full article returned 404; full proof and detailed rank-bound corollary remain uninspected in this review |

What follows from the part that *is* checked:

- **Do not claim novelty for "an exact, independently checkable bound in this scenario."**
  Pauwels reports a Lean formalization of a pure-projective core for I3322 in (3,3,2,2).
  Its source has not been built in this review. Exact checkability remains valuable in itself — it is why anything
  here can be audited at all — but it does not by itself establish novelty, and it did not
  before this preprint either. The claim this repository can support is about a *specific
  penalized functional*.
- **Do not conflate the two I3322 announcements.** Pauwels and Connor are different names,
  different dates and different venues, with different levels of source access here. This
  document adjudicates neither priority nor correctness between them.
- **Nothing above changes any claim here.** The comparisons in this file rest on *achievable*
  qubit benchmarks constructed inside the verifiers, never on a literature maximum, so a
  resolved or unresolved I3322 supremum leaves them intact.
- The equality-face material is in the repository. Goh Appendix G has now been read;
  detailed Rai comparisons and expert assessment remain separate review tasks.

**Access failure, stated plainly.** arXiv abstract pages were reachable from this session;
the arXiv full-text endpoints (both the PDF and the HTML rendering) were not,
returning HTTP 429 on every attempt across several minutes. So for all three arXiv comparators above, only abstract-level verification was
possible here. That is a limitation of this session, not a statement about the papers.

### Status of each comparison

One table, so that nothing is described as both complete and unperformed. An earlier version
of this document still listed the efficiency equation and the catalogue extraction as never
done, in the same file as the sections reporting them done.

| Comparison | Status | Exact scope | Evidence |
|---|---|---|---|
| ordinary I3322 / M3322 / CHSH score thresholds on `Q` | **resolved** | all relabelings of three functionals, against achievable qubit benchmarks constructed in the verifier | `proofs/verify_novelty_comparison.py` |
| correlation-weighted `I3322(c)`, every `c >= 1` | **resolved** | all relabelings, whole parameter range, exact rational decision | `proofs/verify_i3322_family.py` |
| `F` as a marginal tilt of I3322 or M3322 | **resolved** | correlator support 9 vs 8 across the orbits; excludes every marginal-tilted family at once | `proofs/verify_novelty_comparison.py` |
| the detection-efficiency term's *form* | **resolved from a primary source** | fixed local fallback under independent one-sided loss; not setting-dependent efficiency, not postselection | quant-ph/0702130, quoted above |
| `F` as a four-setting catalogue inequality under setting identification | **partially resolved** | 129 rows of Table I of arXiv:0810.1615, 20 surjective reductions per party, 51,600 folds, zero matches | `research/audit_catalog_folds.py` |
| the rest of that catalogue | **open** | the remaining inequalities of that survey, all 175 four-setting classes, and the 5522 tables | — |
| broader Gigena–Kaniewski family | **resolved for scalar scores on original Q** | both branches, every continuous parameter and every relabeling; different projections may use different simulators | `proofs/verify_gigena_complete.py`: 1,152 exact targets |
| Hardy-type comparators | **partially resolved** | the displayed exact-zero test does not apply to `Q`; robust or transformed variants are untouched | below |
| wirings, filtering, many-copy protocols, combinations of several inequalities, conditional tradeoffs generally | **open** | — | — |
| Pauwels / Goh / Rai | **mixed access; novelty still open** | Pauwels Appendices A/D and Goh Appendix G inspected in full text in the follow-up; Rai full-text reinspection not part of that follow-up | `docs/EXTENDED_COMPARISON.md` |
| Connor's announced I3322 characterization | **full proof uninspected** | author webpage read; linked full article returned 404 | `docs/EXTENDED_COMPARISON.md` |

Searching was English-language web search only, not INSPIRE or full-text scholarly search.
Absence of hits is not evidence of novelty, and none of this was performed by a human expert.

## Still open

| Comparator | Relation to investigate |
| --- | --- |
| [Quintino et al. (2019)](https://arxiv.org/abs/1902.05841) | The inequality is settled above. Whether the **two-sided convexification** and its facet structure appear anywhere in the follow-up literature is not settled. |
| [Chen et al., Device-independent quantification of measurement incompatibility (2021)](https://doi.org/10.1103/PhysRevResearch.3.023143) | Compare quantitative certificates and assumptions; do not describe all incompatibility quantification as new. Full model-by-model comparison remains pending. |
| [Tendick, Budroni and Quintino (2025)](https://arxiv.org/abs/2506.21223) | Distinct notions of measurement reduction and convexification have different meanings. Locate our compatible-pair mixture definition precisely; do not equate it with every notion of needing three measurements. |
| [Navascues and Vertesi](https://arxiv.org/abs/1412.0924), [Navascues et al.](https://arxiv.org/abs/1507.07521) | The sharp bound certifies Schmidt number >= 3 for the supplied behavior. Compare against dimension and entanglement-dimension witnesses. The general method is established; priority of this particular witness is not. |

The highest-value remaining work, per the status table above: the untested remainder of the
four-setting catalogue, joint or conditional extensions beyond the resolved Gigena–Kaniewski
scalar family, and robust forms of the Hardy Schmidt-rank comparator. Full-text access and
proof-validation status are separated in `docs/EXTENDED_COMPARISON.md`. A targeted expert question should show the coefficient vector, the two
positivity identities, and the correlator-support argument — not the phrase "two-sided partial
locality". No outreach has been performed.

The candidate contribution, stated so that the corollary above cannot be read back into it:

> An exact, dependency-free certificate that a positivity-penalized M3322 functional is
> bounded by 7 for **every Schmidt-number-two quantum behavior**, together with an explicit
> qutrit behavior that exceeds it while satisfying every relabeled ordinary I3322 and M3322
> qubit score threshold.

The partial-locality geometry is a supporting result rather than the headline: derivability of
the inequality's *validity* does not erase the geometric content, and the 13/13/14 face
structure with the two-sided facet emergence stands on its own. No exhaustive novelty audit has
been completed, and neither sentence has been cleared against the dimension-witness literature.


## 2026-09-08 follow-up: passages read for the boundary-continuation PR

This dated update supersedes the abstract-only status above for the passages
specified here; it does not upgrade Pauwels or Connor to a proof inspected in
this follow-up.

- **Goh et al.** Section III C 2, equation (26), explicitly gives a quantum
  exposed face equal to its local counterpart. Appendix G 2, equations
  (G1)-(G3), has a five-vertex, four-dimensional local face but a
  five-dimensional quantum face containing a nonlocal Hardy point. Those
  passages were read directly from the [PDF](https://arxiv.org/pdf/1710.05892).
  They establish conceptual prior art, not this specific SN2 classification.
  General local/quantum face coincidence and multiple functionals exposing one
  face are not novelty claims here.
- **Rai et al.** The introduction and stated classification scope were read
  directly from the [PDF](https://arxiv.org/pdf/1812.06057). Their quantum-void
  classification concerns the two-setting CHSH scenario. It is relevant to the
  forced-zero method; this scope check is not a proof that no consequence of
  their work can imply the present three-setting result.
- **Remaining gap.** Targeted searches did not identify this exact equality
  face or critical one-event coefficient. This is a bounded negative search,
  not priority clearance. A parameterized three-setting inequality plus
  positivity could still imply the tradeoff. Rank-one Gram downdates and
  PSD Cauchy-Schwarz are standard tools, not innovations claimed by the new
  continuation.

The candidate contribution is the specific SN2 equality classification and
nearly optimal one-event tradeoff with an explicit qutrit separation.
`docs/CERTIFICATE_PENALTY_BOUNDARY.md` adds a singular-certificate equality
argument and a small quadratic remainder, both awaiting separate review.
