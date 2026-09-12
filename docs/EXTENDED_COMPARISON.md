# Extended novelty review and completed family comparison

**8 September 2026. Separate handoff for the literature/repository agent.**

## Assessment

The targeted search did not identify an earlier proof of this particular SN2 equality simplex or this particular optimal one-event penalty. That is a bounded negative search, not priority clearance. Broad claims about inventing device-independent Schmidt-number certification, exact qubit bounds, SOS equality analysis, or parameterized 3322 witnesses remain inappropriate.

There is a substantial completed comparison: **the original qutrit behavior Q cannot be certified beyond SN2 by any scalar score from either branch of the full Gigena–Kaniewski family, under any input permutation, output flip, or party exchange.** An exact projected-mixture certificate now closes the eight cases left open in the earlier search. F nevertheless detects Q. This strengthens the specific nonredundancy claim without proving historical novelty.

The mathematical endpoint work is in `docs/PENALTY_RESEARCH.md`. Its interval proof is local, even with complex measurements included; α* is not solved.

## 1. What was actually searched and inspected

The search covered the M3322 lineage, general parameterized I3322-like families, dimension-constrained bounds, equality geometry, zero-event/Hardy faces, penalty/efficiency formulations, and recent I3322 attainment claims. Queries included `3322 one-parameter quantum inequality`, `3322 two-parameter inequality`, `M3322 family`, `Schmidt number Bell penalty`, `I3322 tilted`, `M3322 qubit bound`, and exact-number searches. Sparse M3322-only queries often returned unrelated electrical products; those results provide no evidence of absence.

I followed the dimension-constrained paper's references to the asymmetric-detection papers and inspected the actual functional in Gigena–Kaniewski. I also checked the repo's existing open-comparison list, rather than treating every rediscovered source as new to the project.

| Source | Material inspected in this pass | Consequence |
|---|---|---|
| Gigena–Kaniewski, 2203.01837 | Full-text HTML, especially Eq. (1), Sections II–III and SOS/equality discussion | Full parameter-family comparison completed exactly below |
| Navascués–de la Torre–Vértesi, 1308.3410 | Downloaded PDF, Section IV.A.1 and references 55–56 | Parameterized three-setting dimensional certification is established prior art |
| Brunner et al., quant-ph/0702130 | Full PDF, Eqs. (4)–(5) | Ratio optimization for critical Bell penalties/efficiencies is old |
| Vértesi–Pironio–Brunner, 0909.3171 | Downloaded PDF, Eq. (2) | The relevant efficiency deformation is a marginal penalty |
| Quintino et al., 1902.05841 | Downloaded full text; prior exact Eq. (48) derivation retained | Original H validity remains inherited; no new priority claim |
| Tendick, 2408.08347 | Downloaded PDF, Mnn22 discussion and conclusions | Compatibility/measurement-number interpretation is prior art |
| Goh et al., 1710.05892 | Downloaded PDF, Appendix G and related face discussion | Specific five-local-vertex comparator verified; quantum face differs |
| Pauwels, 2608.29734 | Downloaded PDF, Appendix A and Appendix D, introduction | Exact qubit proposition and stated Lean scope directly inspected |
| Connor | Author's full explanatory webpage; linked full article returned 404 | Full proof remains uninspected; do not upgrade status |
| Apsiape/i3322-exact-wall | Current certificate map; indexed manuscript status warning | Additional unreviewed comparator with explicit superseded claims |
| Araújo et al., 2311.18707 | Abstract and author-hosted PDF sections available through web extraction | KKT-assisted hierarchy is relevant method prior art; not applied here |
| Mukherjee et al., 2502.13296v3 | Full-text HTML introduction and theorem/corollary descriptions | Distinguish fully DI behavior detection from universal state certification |

“Full text available” does not mean every theorem was independently proved. In particular this is not a proof audit of the unrestricted I3322 preprints. Sources and links appear below.

## 2. Completed exact comparison with Gigena–Kaniewski

Their Eq. (1) is the family

$$
\beta=\alpha_1 m_b+c+\alpha_3 d,\qquad b\in\{-1,+1\},
$$

where, using our zero-based setting labels,

$$
m_b=A_0+A_1+b(B_0+B_1),
$$
$$
c=E_{00}+E_{01}+E_{10}+E_{11},\qquad
 d=E_{20}-E_{21}+E_{02}-E_{12}.
$$

**This transcription is the one literature-dependent input to an otherwise exact verifier.** Everything downstream of it is machine-checked, and the verifier enumerates the relabeling orbit itself rather than trusting the certificate's list — but if these three definitions misread Eq. (1), the comparison closes the wrong family and no verifier fails. The reading above was made in this pass from the full-text HTML; it has not been confirmed by a second reader, and a later review session's own attempt to fetch the source was refused. Anyone holding the paper should check these three lines before relying on §2.

The paper studies exact quantum values and optimal realizations in one branch and numerical behavior in the other. It already uses SOS kernels to analyze equality; neither parameterized boundaries nor that method is new. Its correlator matrix has a structural zero, so direct relabeling to our positive-α nine-correlator family is excluded, but that observation alone does not settle whether its score thresholds detect Q.[^1]

### New certificate and proof of non-detection

For each relabeling of Q and each branch b, project the behavior to the three numbers (m_b,c,d). The full enumeration has **1,152 distinct branch-labeled targets**. For every target the supplied certificate provides an exact convex mixture of genuine qubit strategies with exactly those same three numbers.

Consequently, for every parameter choice, the mixture reproduces that family's scalar score on Q. Its value cannot exceed the SN2 maximum. Indeed at least one component achieves at least the average, so it cannot exceed the genuine two-qubit maximum either, even if one does not allow shared randomness when defining that maximum.

The new verifier reconstructs all 36 probabilities of Q from its complex rational state and rank-one measurement vectors. It reconstructs every qubit strategy from its actual state/measurement parameters, checks convex weights and projected coordinates exactly, and independently enumerates the expected target set. No numerical bound on the family is used.

The old discovery package covered 1,144 targets. A new least-squares search located qubit strategies near the eight remaining targets. Rational neighboring strategies then yielded four-point convex decompositions with exact positive weights. Only these final rational data enter the verifier. All eight gaps are closed.

Files:

- `proofs/gigena_complete_certificate.json`: complete exact data, including the earlier 1,144 cases and the eight additions.
- `proofs/verify_gigena_complete.py`: reconstruction and coverage verifier.
- `tests/test_gigena_mutations.py`: eight corruptions — dropped target, duplicated target, negative weight, unnormalized weights, false projected coordinate, displaced target, a phi direction off the unit circle, and a non-deterministic "local" outcome — each of which must reject with its own diagnostic code and with no other case's code. Three anti-degradation controls sit alongside them: the unmodified certificate must pass in the same staged layout, a verifier that refuses everything must satisfy no case, and a verifier that always prints one code must not stand in for a different case.
- `proofs/qutrit_certificate.json`: original Q, copied from the repo and independently reconstructed.

All pass. This verifier uses SymPy for Born reconstruction and standard-library exact fractions for the mixture identities. The full family remains infinite in its continuous parameters; exact matching of the three coefficient statistics handles them simultaneously.

### Scope boundaries

Different relabelings can use different simulators. This is **not** one SN2 model reproducing the full behavior Q. Such a model would contradict F(Q)>7. Nor does it rule out arbitrary nonlinear joint-score tests, filtering, multi-copy protocols or conditional tradeoffs using additional statistics.

This comparison concerns the **original** Q. The improved qutrit realization giving approximately 1.51% white-noise tolerance was not compared against this full family here. Every strengthened witness F+εp with ε≥0 also detects the original Q, so the original-Q nonredundancy comparison remains relevant to that family.

## 3. Detection-efficiency literature is closer than a title-only comparison suggests

Navascués–de la Torre–Vértesi explicitly analyze a one-parameter three-setting dimension-witness family, with a qubit threshold near η=0.428 subject to numerical solver precision. Their references lead to the asymmetric-detection construction. This directly defeats any broad claim that a tunable 3322 qubit/nonqubit boundary is new.[^2]

Vértesi–Pironio–Brunner write the efficiency deformation as

$$
I_{NN22}(\eta)=I_{NN22}-\frac{1-\eta}{\eta}P(A_1).
$$

It is a marginal penalty. At N=3 its structural missing correlator survives the deformation. Our positive-α functional adds the formerly missing joint correlator, so this displayed family is not directly our one-event family under relabeling and nonzero scaling. That is a coefficient-level comparison, not a complete test of all its detection power.[^3]

More importantly, Brunner et al. optimize a ratio of a Bell value to a failure contribution to obtain a critical efficiency in Eq. (5). Therefore **the ratio/critical-penalty formulation itself is not a new mathematical technique**. The possible contribution is the specific SN2 tradeoff, exact certificates, and face classification. These experiments have different assumptions; no detector-efficiency improvement for our witness follows from this analogy.[^4]

## 4. Equality geometry: what Goh does and does not preempt

The relevant passage of Goh et al. is now directly inspected, not merely reported. Appendix G constructs a positivity-based face with five affinely independent local deterministic points. The associated quantum face contains the nonlocal Hardy point and has dimension five; the local face has dimension four. Earlier parts discuss quantum and local exposed faces coinciding in other examples.[^5]

Thus the number “five vertices” and the general phenomenon of local/quantum face coincidence are not novelty claims. Their Hardy construction does not, by that passage alone, establish our 3322 SN2 equality theorem. In particular its quantum face is not just its local four-simplex. The repo's claim should remain the specific equality `S2 ∩ {F=7}=L_F`, with all model definitions and branches explicit.

The proposed critical-penalty contact picture should likewise be presented as a concrete unresolved instance of supporting-face geometry, not a newly invented phenomenon. The local endpoint candidate does not yet establish an entangled global contact point.

## 5. Recent I3322 comparators: stronger access, cautious conclusions

### Pauwels

The downloaded full PDF's Appendix A, Proposition 1 explicitly states and argues the exact two-qubit I3322 maximum 1/4 for arbitrary binary measurements. Appendix D says the Lean development treats finite-dimensional pure states with binary projective measurements and does **not** formalize the mixed-state/POVM reduction. These details are now directly inspected. I did not build the Lean project or independently validate the full nonattainment theorem.[^6]

This updates an access-status row, not the mathematical validity status of an unrefereed preprint. The repo should neither describe this source as abstract-only nor claim that the entire operational theorem has been machine checked. Exactness/checkability are valuable properties, but were never sufficient novelty claims.

### Connor

The author's webpage states finite-dimensional nonattainment and discusses Schmidt-rank gaps. It links a full article at `/i3322-pra.pdf`, but that link returned 404 in this pass. The webpage is direct evidence of what the author claims; it is not the full proof. I cannot verify the detailed rank-bound formula from that source alone, so the previously quoted ResearchGate corollary remains unverified here.[^7]

### Additional public certificate project

The Apsiape/i3322-exact-wall repository's certificate map distinguishes currently claimed bounds from a historical chain it says was not restored. The indexed manuscript also carries an explicit warning about earlier claims. It is relevant evidence that similar exact-certificate efforts exist, but this pass did not validate its proof chain or establish a publication/priority date for each theorem.[^8]

Do not cite an old headline from this project without a pinned revision and its status warning. Do not infer that several public claims amount to independent validation of one another.

## 6. Other comparators and methodological implications

Quintino's M3322 lineage and Tendick's Mnn22 interpretation remain important motivation. The original partial-local validity of F follows from the already verified M3322-plus-positivity identity. The positive-ε strengthened family fails on the old hull; that counterexample must remain visible. Optimizing the SN2 bound changes the set being separated.[^9][^10]

Moroder et al. provide established device-independent entanglement-quantification context. This pass did not independently certify a particular plotted negativity value; retain the distinction between a numerical curve and an exact lower certificate.[^11]

Mukherjee et al. discuss limitations even for Bell-nonlocal higher-Schmidt-number states and introduce certification with trusted quantum inputs. This is useful context for why our result detects particular behaviors rather than certifying all SN3 states. Their measurement-device-independent construction changes the input assumptions and is not our Bell experiment.[^12]

Araújo et al. develop optimality constraints for noncommutative optimization and apply them to Bell bounds. This suggests an improved global-proof route, but their unrestricted-dimension hierarchy cannot simply be used as an SN2 upper bound. Any adaptation must enforce the appropriate dimension identities and check the stated constraint qualifications.[^13]

## 7. Defensible paper claim

Suggested core statement:

> For a specific positivity-penalized M3322 functional, we characterize the entire Schmidt-number-two equality face as a local four-simplex and certify a nearly optimal one-event penalty. An explicit qutrit behavior violates the resulting SN2 bound. Exact projected simulators show that the original qutrit example is not detected by any scalar score in the full Gigena–Kaniewski family, even after relabeling.

Add the boundary continuation result with its actual scope. State separately that the exact optimal coefficient and its complete equality face remain open. The new interval result establishes a strict local optimum modulo qubit gauge; it should not be the headline of the paper.

Avoid: “first DI SN3 witness,” “first exact qubit bound,” “first computer-checkable Bell proof,” “new ratio method,” “all previous witnesses fail,” or “optimal penalty determined.”

## 8. Integration and review checklist

1. Review and integrate the complete GK certificate as a separate change. Replace the existing “eight uncovered targets / inconclusive” status with the precise theorem and verifier command. Keep the older attempted search in historical material, labeled superseded.
2. Wire the exact verifier and its rejection mutations into an appropriate validation tier. Validate from a clean export. It must compare the expected target set, not merely count 1,152 entries. (Done: the verifier enumerates the relabeling orbit itself and asserts set equality, and the mutation suite carries anti-degradation controls.)
3. Keep discovery and verification separate. Numerical optimization was used to find the eight additions; it is not a dependency of the acceptance proof.
4. Update Goh and Pauwels access rows to “relevant full-text passages inspected.” Keep proof-validation status separate. Connor remains full-proof-uninspected in this pass.
5. Cite Eq. (1) of Gigena–Kaniewski, Eq. (2) of the 2010 efficiency paper, Eq. (5) of the 2007 asymmetric paper, Goh Appendix G, and Pauwels Appendices A/D precisely.
6. Retain open status for arbitrary modified joint-coefficient families, joint nonlinear tradeoffs, remaining catalogue reductions and protocol transformations. A finite list of excluded families cannot establish priority.
7. Have a human specialist review the intended contribution sentence against the literature. Supply the functional coefficients, model class and exact comparison theorem, not a general request to endorse novelty.

## Sources

[^1]: N. Gigena and J. Kaniewski, *Quantum value for a family of I3322-like Bell functionals*, [full text, Eq. (1)](https://arxiv.org/html/2203.01837v1), 2022.
[^2]: M. Navascués, G. de la Torre and T. Vértesi, *Characterization of Quantum Correlations with Local Dimension Constraints and Its Device-Independent Applications*, [full text](https://arxiv.org/pdf/1308.3410), Section IV.A.1.
[^3]: T. Vértesi, S. Pironio and N. Brunner, *Closing the Detection Loophole in Bell Experiments Using Qudits*, [full text](https://arxiv.org/pdf/0909.3171), Eq. (2).
[^4]: N. Brunner, N. Gisin, V. Scarani and C. Simon, *Detection Loophole in Asymmetric Bell Experiments*, [full text](https://arxiv.org/pdf/quant-ph/0702130), Eqs. (4)–(5).
[^5]: K. T. Goh et al., *Geometry of the set of quantum correlations*, [full text](https://arxiv.org/pdf/1710.05892), especially Appendix G.
[^6]: J. Pauwels, *The quantum supremum of the I3322 Bell inequality is not attained in finite dimension*, [preprint PDF](https://arxiv.org/pdf/2608.29734), Appendices A and D. Unrefereed; full theorem not independently validated in this review.
[^7]: V. Connor, [author's I3322 explanation](https://violet-connor.neocities.org/i3322). Author-claimed results; linked full article unavailable in this pass.
[^8]: Apsiape/i3322-exact-wall, [certificate map](https://github.com/Apsiape/i3322-exact-wall/blob/main/paper/CERTIFICATE-MAP.md) and [manuscript status](https://github.com/Apsiape/i3322-exact-wall/blob/main/paper/MANUSCRIPT.md). Public repository claims, not independently validated here.
[^9]: M. T. Quintino et al., *Device-Independent Tests of Structures of Measurement Incompatibility*, [full text](https://arxiv.org/pdf/1902.05841), Eq. (48).
[^10]: L. Tendick, *Quantum correlations cannot be reproduced with a finite number of measurements*, [full text](https://arxiv.org/pdf/2408.08347).
[^11]: T. Moroder et al., *Device-independent entanglement quantification and related applications*, [paper listing](https://arxiv.org/abs/1302.1336).
[^12]: S. Mukherjee et al., *Measurement-Device-Independent Schmidt Number Certification of All Entangled States*, [full text, v3](https://arxiv.org/html/2502.13296v3), Sections III–IV.
[^13]: M. Araújo, I. Klep, A. J. P. Garner, T. Vértesi and M. Navascués, *First-order optimality conditions for non-commutative optimization problems*, [paper listing](https://arxiv.org/abs/2311.18707) and [author-hosted text](https://igorklep.github.io/files/KKT2.pdf).
