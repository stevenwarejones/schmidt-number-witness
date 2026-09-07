---
title: "An exact Schmidt-number-two bound for a probability-penalized M3322 functional"
subtitle: "Updated manuscript draft | Consolidated review handoff"
date: "7 September 2026"
fontsize: 11pt
geometry: margin=0.9in
mainfont: DejaVu Serif
sansfont: DejaVu Sans
monofont: DejaVu Sans Mono
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[L]{\small Schmidt-number witness | Review draft}
  - \fancyfoot[C]{\thepage}
  - \setlength{\headheight}{15pt}
  - \setlength{\emergencystretch}{3em}
---

**Review status.** This is an unpublished draft, not an externally validated paper. The exact certificate chain has been checked computationally; human expert review and historical novelty assessment remain outstanding. The inequality's partial-local validity follows from published M3322 inequalities plus positivity. The proposed contribution centers on the sharp Schmidt-number-two bound, the explicit qutrit separation and their geometric interpretation.

**Statement on AI use.** This manuscript and the artifact it describes were produced by two AI systems working adversarially against each other under the direction of the listed author, who is not a physicist. This draft was written by ChatGPT (OpenAI), working as "Astra"; the repository's verifiers, certificates and tests were written by Claude (Anthropic), which also reviewed this work, and Astra in turn reviewed Claude's. Each system's mathematics was re-derived by the other before being adopted, and the disagreements are recorded in the repository rather than reconciled silently. No claim here has been checked by a human domain expert. It is circulated to invite exactly the scrutiny it has not had.

**For the reviewer.** Please prioritize the exact operator identity and positivity certificate; the extension to arbitrary binary POVMs and Schmidt number two; the prior-art comparison, especially probability-conditioned dimension bounds; and the interpretation of the convex-remainder bound. The mathematical baseline is linked in Section 7. This revision incorporates the detailed novelty audit of 7 September 2026, including its exact one-parameter comparison and explicitly incomplete catalogue audit. This PDF is a manuscript handoff, not a replacement for its machine-readable certificates.

## Abstract

We study a binary-outcome bipartite Bell functional with three measurement settings per party. An exact rational sum-of-squares identity establishes the sharp bound F ≤ 7 for all states of Schmidt number at most two and arbitrary local binary POVMs. A fully specified two-qutrit realization attains F = 7.0129123854899715..., thereby certifying Schmidt number at least three. The functional is a positivity-penalized relabeling of M3322 on either party. Its supporting face has dimension 13 on each one-sided partial-local hull and dimension 14 on their convex union, making it a facet only of the latter among these three sets. Consequently the witness also excludes setting-independent mixtures in which the party supplying a compatible measurement pair may vary between components. The supplied behavior remains below explicit qubit-achievable benchmarks for all relabelings of ordinary I3322 and M3322 and every member of a published correlation-weighted I3322 family with parameter c at least one. A certified unrestricted quantum upper bound yields a lower bound exceeding 31.19% on the quantum remainder outside the convex hull of the Schmidt-number-two and compatible-pair classes for the supplied behavior.

## 1. Scenario and relation to existing inequalities

Let $x,y\in\{0,1,2\}$ and $a,b\in\{0,1\}$. With observable outcomes $(-1)^a$ and $(-1)^b$, define marginal expectations $A_x,B_y$ and correlators $E_{xy}$. Consider

$$
\begin{aligned}
F={}&A_0-A_1+A_2-B_0-B_1+B_2\\
&-E_{00}-E_{01}-E_{02}-E_{10}-E_{11}+E_{12}\\
&+E_{20}-E_{21}-E_{22}.
\end{aligned}
$$

The analysis uses the ordinary local quantum Bell model, $p(ab|xy)=\mathrm{tr}[\rho(M_{a|x}\otimes N_{b|y})]$, and setting-independent convex weights. It concerns certification from probabilities; no hidden signaling or observer-dependent event assumption is imposed.

**Main result.** The functional below has the attained bound F ≤ 7 on all Schmidt-number-two quantum behaviors with arbitrary binary POVMs, while an exact qutrit realization exceeds it. Section 3 proves the bound; Section 4 specifies the separating realization.

M3322 originates in nonlocal-resource inequalities [1,2]. One-sided partial-locality and its connection to measurement structure are developed in [3], with a general n-input extension in [4]. Dimension certification and dimension-constrained bounds are established subjects [5-7]. The result considered here is the exact bound for the particular F above together with its two-sided geometric role. Historical originality of this specific bound remains under review.

Define the two relabeled parent functionals by

$$
\begin{aligned}
M_A&=F+A_1+B_0+E_{10},\\
M_B&=F-A_2-B_2+E_{22}.
\end{aligned}
$$

They are respectively a local input/output relabeling without party exchange and a party-exchanged relabeling of the M3322 representative in [3, Eq.48]. The identities

$$
F-7=(M_A-6)-4p(00|10)=(M_B-6)-4p(11|22)
\tag{1}
$$

make their relationship explicit. F is not proposed as an independent parent inequality. Unlike the unpenalized M3322, which admits qubit violations [8], F has the sharp Schmidt-number-two ceiling established below.

## 2. Two-sided partial locality

For each Alice input pair $S$, let $H_{A,S}$ consist of normalized nonsignaling behaviors whose $S\times\{0,1,2\}$ restriction is Bell local. Set

$$
H_A=\mathrm{conv}\bigcup_{|S|=2}H_{A,S},\qquad
H=\mathrm{conv}(H_A\cup H_B),
$$

with $H_B$ defined by exchange of parties.

**Proposition 1.** F ≤ 7 on H. The $F=7$ faces of $H_A,H_B$ and $H$ have affine dimensions 13, 13 and 14, respectively, in an ambient space of dimension 15.

**Proof.** The known inequalities M_A ≤ 6 on $H_A$ and M_B ≤ 6 on $H_B$, together with positivity in (1), establish validity on both hulls and their convex union. Equality on $H_A$ forces p(00|10)=0 in addition to F=7; these are independent affine constraints. Equality on $H_B$ analogously forces p(11|22)=0. Hence each one-sided face has dimension at most 13. Exact rational points in the companion artifact give matching lower bounds and affine rank 14 for the two-sided face. Their membership is certified by the partial-local constraints; a separate 15-point certificate supplies explicit local models on the designated restrictions. Since H contains the full-dimensional local polytope, its dimension is 15. $\square$

This proposition characterizes one face, not the full facet structure of H. Its validity is a corollary of one-sided results; the change in face dimension is a separate property.

Let C be the class of setting-independent mixtures of quantum implementations where at least one party has a jointly measurable pair in each component. The state, measurements, pair, and party may vary between components.

**Proposition 2.** C ⊆ H ∩ Q, and therefore F ≤ 7 on C.

**Proof.** In an Alice-compatible component, write $M_{a|x}=\sum_\lambda p(a|x,\lambda)G_\lambda$. Put $q_\lambda=\mathrm{tr}[\rho(G_\lambda\otimes I)]$ and, for $q_\lambda>0$, $p(b|y,\lambda)=\mathrm{tr}[\rho(G_\lambda\otimes N_{b|y})]/q_\lambda$. These nonnegative normalized responses provide a local decomposition for the pair and every Bob input. The full quantum behavior is nonsignaling. The same argument applies on Bob’s side; setting-independent convexity completes the proof. $\square$

No equality between C and H ∩ Q is assumed. Quantum partial-locality classes and actual compatible-measurement classes are distinguished in [10]; the operational relation between simulability and compatibility mixtures also requires the definitions in [11]. The present inclusion does not claim a new general incompatibility-quantification method.

## 3. Sharp Schmidt-number-two theorem

**Theorem 3.** Every behavior obtained from a state of Schmidt number at most two, using arbitrary local binary POVMs, satisfies F ≤ 7. This holds in arbitrary finite ambient local dimension and under setting-independent shared randomness. The bound is attained.

**Proof.** First take nontrivial projective qubit observables $A_i=u_i\cdot\sigma$ and $B_j=v_j\cdot\sigma$. They satisfy $A_i^2=B_j^2=I$, interparty commutation, and scalar anticommutators

$$
\{A_i,A_j\}=2g^A_{ij}I,\qquad
\{B_i,B_j\}=2g^B_{ij}I.
$$

The companion rational certificate specifies 84 operator words W_i of length at most three, an integer 84×70 matrix P, and a symmetric rational 70×70 matrix X. For $J_j=\sum_iP_{ij}W_i$, it verifies

$$
7I-\mathcal B_F=\sum_{j,k}X_{jk}J_j^\dagger J_k,
\qquad X\succ0.
\tag{2}
$$

The identity is exact in the polynomial algebra defined by the displayed relations. Positivity follows from strictly positive rational LDL pivots; every polynomial residual coefficient vanishes. Equation (2) therefore proves the bound for every state in the nontrivial projective qubit sector. Sampled Bloch-vector evaluations are cross-checks, not the proof.

Every binary qubit effect has an explicit convex decomposition. If its eigenvalues are $0\le\lambda_-\le\lambda_+\le1$ and $\Pi$ projects onto a maximal-eigenvalue eigenvector, then

$$
M=\lambda_-I+(\lambda_+-\lambda_-)\Pi+(1-\lambda_+)0.
\tag{2a}
$$

The coefficients are nonnegative and sum to one. Decompose each of the six effects in this way, and independently sample its component before the inputs are selected. The product of the six weights is setting independent. This expresses the original behavior as a convex mixture of implementations in which every binary measurement is projective or deterministic. A deterministic observable $\pm I$ is jointly measurable with any other measurement on its party; Proposition 2 bounds every component containing one. Equation (2) bounds every remaining component. Thus the result includes arbitrary binary qubit POVMs and mixed two-qubit states.

For a pure state $|\psi\rangle$ of Schmidt rank $r\le2$, choose local isometries $V_A,V_B$ onto its Schmidt supports and write $|\psi\rangle=(V_A\otimes V_B)|\widetilde\psi\rangle$. Define

$$
\widetilde M_{a|x}=V_A^\dagger M_{a|x}V_A,\qquad
\widetilde N_{b|y}=V_B^\dagger N_{b|y}V_B.
$$

These effects are positive and sum to the identity on their respective supports. Moreover,

$$
\langle\psi|M_{a|x}\otimes N_{b|y}|\psi\rangle
=\langle\widetilde\psi|\widetilde M_{a|x}\otimes
\widetilde N_{b|y}|\widetilde\psi\rangle.
$$

Rank-one supports can be embedded in qubits with arbitrary valid effects on the unused dimension. Compression need not preserve projectivity: that is why the binary-POVM step precedes compression. For a mixed state of Schmidt number at most two, apply this argument separately to every pure state in a Schmidt-rank-at-most-two decomposition and average. The compressed effects may differ between components; the bound holds for each of them. Linearity also includes setting-independent mixtures of implementations.

Finally, the product state $|00\rangle$, $A_0=A_1=A_2=Z$ and $B_0=B_1=B_2=-Z$ gives F=7, establishing sharpness. $\square$

## 4. Exact qutrit separation

An explicit pure state and six binary measurements give

$$
\begin{aligned}
F(Q)&=\frac{6492685621097725532153123325014736141211841649692233}
{925818727541981220573252742087143961265664549902695}\\
&=7.0129123854899715\ldots.
\end{aligned}\tag{3}
$$

For a self-contained specification, normalize the following Gaussian-integer vector in the basis |00$\rangle$, |01$\rangle$, ..., |22$\rangle$:

$$
\begin{aligned}
v=(&4826,-564-4361i,-3959-63i,\\
&-2206-2587i,-527+2563i,1347-2509i,\\
&1226-1212i,24-1993i,1646+2349i).
\end{aligned}
$$

Each row below specifies a vector $v$ and the outcome $r$ with effect $|v\rangle\langle v|/\langle v|v\rangle$. The other effect is its complement. Each vector is normalized separately by that formula.

| Party/input | r | v |
|---|---:|---|
| A0 | 1 | (1280, 4956+4498i, 6992−2164i) |
| A1 | 0 | (7901, −5596+1614i, 1905+167i) |
| A2 | 1 | (2488, 1818+6169i, 5871+4240i) |
| B0 | 0 | (−6034, 3073−4406i, 875+5828i) |
| B1 | 0 | (6800, 1653+7141i, 129+90i) |
| B2 | 0 | (4148, −1407+8707i, 2157+596i) |

Exact Born evaluation gives (3). This is an existence construction, not a claim to maximize F over qutrits or unrestricted quantum systems. By Theorem 3 it certifies Schmidt number at least three; by Proposition 2 it also excludes C.


## 5. Comparison with ordinary dimension thresholds

For the same behavior Q, exhaustive input/output/party relabeling gives the following scalar maxima. Values are rounded for display; the comparison uses rational arithmetic.

| Functional | Relabelings | Maximum on Q | Qubit benchmark |
|:--|--:|--:|:--|
| I3322 | 576 | 4.1403881794 | Achievable 5 |
| M3322 | 2304 | 6.0221540522 | Achievable 6.0243205028 |
| CHSH | 72 | 2.0876402763 | Ceiling $2\sqrt{2}$ |
| F | Shipped orientation | 7.0129123855 | Sharp ceiling 7 |

The I3322 representative has marginal coefficients $(-1,-1,0)$ and $(1,1,0)$ and correlation matrix

$$
C_I=\begin{pmatrix}1&1&1\\1&1&-1\\1&-1&0\end{pmatrix}.
$$

It is [3, Eq. (75)] in zero-based input notation. A qubit benchmark of 5 is achieved exactly on $|\phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2$ by

$$
A_0=B_0=\frac{\sqrt3X+Z}{2},\quad
A_1=B_1=\frac{\sqrt3X-Z}{2},\quad A_2=B_2=Z.
$$

All marginals vanish and direct evaluation gives $I=5$. This achievable benchmark alone suffices: the best relabeled score on $Q$ is smaller than a score achievable with qubits. The comparison therefore does not require a literature upper bound on I3322. For reference, its probability form is $I=4J+4$, where

$$
J=\sum_{x,y}(C_I)_{xy}p(00|xy)-2p_A(0|0)-p_A(0|1)-p_B(0|0).
$$

For M3322 the same lower-benchmark argument applies: an explicit qubit realization gives a rational score above 6.023, while every relabeling on $Q$ is below 6.023. The reported approximate qubit score in [8] is contextual, not a premise of this comparison.

Thus F detects entanglement dimension on data for which neither ordinary relabeled I3322 nor M3322 scalar thresholds do so. This does not establish superiority for every behavior or novelty against probability-conditioned tradeoffs. The comparison includes relabelings, not arbitrary preprocessing, filters or multiple-copy wirings. Both parent inequalities do detect nonlocality in Q; the distinction concerns dimension certification.

For an exact M3322 qubit lower witness, normalize the real vector

$$
\psi=(64474,73134,17575,-13624)
$$

in the basis $|00\rangle,|01\rangle,|10\rangle,|11\rangle$. For each setting, outcome 0 has effect $|v\rangle\langle v|/\langle v|v\rangle$, and outcome 1 its complement. Alice's vectors are (100000,312), (98313,18289), (94227,-33485); Bob's are (64814,76152), (-35243,93584), (-11537,-99332). With marginal coefficients (1,1,0) on both sides and correlation matrix

$$
\begin{pmatrix}1&-1&1\\1&-1&-1\\1&1&0\end{pmatrix},
$$

exact Born evaluation gives 6.024320502752555..., an achievable value rather than a certified maximum.


### 5.1 A continuum of correlation-weighted I3322 comparisons

Consider the published family [12, Eq. (26); 13, Eq. (E1)]

$$
\begin{aligned}
I_c={}&A_0+A_1+B_0+B_1-(A_0+A_1)(B_0+B_1)\\
&+c[(A_0-A_1)B_2+A_2(B_0-B_1)],\qquad c\ge1.
\end{aligned}
\tag{4}
$$

Products in this equation denote bipartite correlators. Its parameter changes correlation coefficients; it is distinct from the efficiency-dependent marginal tilt discussed below.

**Proposition 4 (comparison on the supplied behavior).** For every input/output relabeling and party exchange, and every $c\ge1$, the score $I_c(Q)$ is strictly below a value achievable by two qubits.

**Proof.** On $|\phi^+\rangle$, choose real projective observables

$$
\begin{aligned}
A_0&=tX+zZ,& A_1&=-tX+zZ,& A_2&=X,\\
B_0&=tX-zZ,& B_1&=-tX-zZ,& B_2&=X,
\end{aligned}
$$

where $0\le t\le1$ and $z=\sqrt{1-t^2}$. All marginals vanish and direct Born evaluation gives $I_c=4(1-t^2)+4ct$. Consequently the following scores are achievable:

$$
q_{\mathrm{ach}}(c)=\begin{cases}4+c^2,&1\le c\le2,\\4c,&c\ge2.\end{cases}
\tag{5}
$$

For each relabeling the rational behavior Q gives $I_c(Q)=a+bc$ with rational a,b. Exhaustive enumeration yields 576 distinct lines. For each line the accompanying exact comparison verifies

$$
4+t_*^2-a-bt_*>0,\qquad
 t_*=\max(1,\min(2,b/2)),
$$

and $b\le4$, $8-a-2b>0$. The first inequality is the minimum of $4+c^2-a-bc$ on $[1,2]$. The last two prove positivity of $4c-a-bc$ on $[2,\infty)$. The smallest first-interval gap is approximately 0.5834085189625386. Every comparison is rational; the printed decimal is not a numerical tolerance. This proves the assertion without claiming that (5) is the optimal qubit value. $\square$

### 5.2 Prior-art scope and remaining comparisons

The efficiency family of [14, Eq. (2)] is

$$
I_{NN22}(\eta_B)=I_{NN22}
-\frac{1-\eta_B}{\eta_B}p_A(+1|1)
\tag{6}
$$

in that source's one-based input and signed-outcome notation. For N=3 this is an I3322 marginal penalty; it is used for dimension analysis in [15]. After normalization, its correlator support remains at most eight entries. F has nine. Thus direct equivalence under relabeling, nonzero scaling and an added constant is excluded, even allowing arbitrary marginal tilts. This support argument does not rule out derivations from several inequalities or establish non-detection of Q for all efficiencies.

The broader Gigena-Kaniewski family [16, Eq. (1)] likewise has at most eight nonzero correlators and is not directly equivalent to F. Proposition 4 does not cover that entire family: its additional parameter and branch choices require separate detection comparisons. No conclusion is drawn from incomplete finite-library searches for projected qubit simulators.

An exact supplementary comparison extracted the 129 J4422 coefficient vectors printed in [17, Table I], verified every local bound by deterministic enumeration, and tested 20 reductions per party: 12 signed pair identifications and eight deterministic substitutions. None of the resulting 51,600 functionals matches the 2304-element F orbit up to a positive scale and a constant. This is a direct-reduction audit of that table, not all 241 inequalities in the survey, the complete 175-class four-setting catalogue [18], or arbitrary combinations and wirings.

The exact-zero Hardy dimension test [19] does not apply to Q directly as written; Q has strictly positive probabilities. This does not exclude robust Hardy penalties or transformed tests. Ordinary I3322 has a history of higher-dimensional advantage [20], so the scalar non-detection comparison above must not be paraphrased as saying I3322 is not a dimension witness.

These checks narrow several concrete equivalence questions. They do not establish historical priority of the conditional Schmidt-number-two tradeoff $M_A\le6+4p(00|10)$. That particular bound remains the proposed contribution requiring expert prior-art assessment.

## 6. A joint convex-class consequence

Let $Q_2$ denote the behaviors realizable with Schmidt number at most two, including setting-independent mixtures, and define

$$
K=\mathrm{conv}(Q_2\cup C).
$$

**Corollary 5.** F ≤ 7 on K. Thus a violation excludes even mixtures which alternate between low-Schmidt-number components and compatible-pair components, with no requirement that the same explanation be used in every component.

This follows immediately from Propositions 1-2, Theorem 3 and convexity. It does not characterize K completely.

A separate exact certificate establishes the dimension-unrestricted quantum upper bound

$$
F\le U=\frac{7041387041}{10^9}=7.041387041.
$$

This certificate uses interparty commutation and projective involutions without qubit anticommutators, a positive rational Gram matrix, and an explicitly bounded residual. General binary POVMs are included by extremal effects. U is certified but not claimed sharp.

For any decomposition P=(1−t)$P_K$+tP_Q, with $P_K$ ∈ K and $P_Q$ quantum,

$$
F(P)\le7(1-t)+Ut,\qquad
 t\ge\frac{F(P)-7}{U-7}\quad(F(P)>7).
\tag{7}
$$

For (3), the right side is 0.3119910285437303... >31.19%. This bounds the quantum remainder in every such decomposition. It also bounds a decomposition with a Schmidt-number-two first component alone, since $Q_2\subseteq K$. The same numeric U must not be used for an arbitrary nonsignaling remainder. It is not an exact resource cost, nor does it identify accessible labels on individual runs. Applied to mixtures of implementations, components outside the specified easy classes must carry at least this weight; the inequality does not determine their individual states or measurements.

## 7. Limits and reproducibility

For uniform-output admixture $Q_\eta$=(1−η)Q+ηP_uniform, all uniform correlators and marginals vanish. Hence F($Q_\eta$)=(1−η)F(Q), and the supplied realization violates 7 for

$$
\eta<1-7/F(Q)=0.0018412301167041293\ldots.
$$

The corresponding tolerance is approximately 0.1841%. This is a particular probability-noise model, not a detector-efficiency threshold or an experimental feasibility analysis.

The sharp lower-dimensional ceiling is proved, while the unrestricted quantum maximum, optimal remainder cost, and complete facet description of H remain undetermined. Experimental validation and assessment of novelty relative to equivalent witnesses remain separate tasks.

The companion artifact reviewed here is pinned to [commit 522bfcf](https://github.com/stevenwarejones/schmidt-number-witness/tree/522bfcfd3ef5a414f8de668439c17fb740b2ff55). The exact chain passes at this snapshot. All active certificates are in `proofs/`: `proofs/verify_sharp_qubit.py` checks (2), `proofs/verify_quantum_upper.py` checks $U$, and `proofs/verify_qutrit.py` reconstructs the qutrit probabilities. The historical routing calculation that certificate originated from has been moved to `research/legacy/` and is not a premise of this paper.

The comparisons of Section 5 are integrated as `proofs/verify_i3322_family.py`, which derives its qubit benchmarks symbolically and then decides the continuum comparison in exact rational arithmetic, and `research/audit_catalog_folds.py`, a scoped comparison rather than a proof gate. `tests/test_comparison_acceptance.py` corrupts the qutrit behaviour and the catalogue data in turn and requires both to be rejected.

The manuscript supplies the POVM and Schmidt-compression reductions explicitly. Its I3322 benchmark and the local-model construction below supplement the repository's proof presentation. They do not modify its certificate data. Discovery-path tests and prior-art prose have outstanding corrections recorded in the accompanying review; neither is used as a mathematical premise here.

## Appendix A. Why the binary 2-by-3 locality test is complete

For a normalized nonsignaling behavior with two Alice settings and any finite number of Bob settings, locality is equivalent to positivity and all 2-by-2 CHSH inequalities. The following interval construction explains the reduction to Fine's theorem [9].

For each Bob setting $y$ and outcome $b$, put $r_b=p_B(b|y)$, $u_b=p(1b|0y)$ and $v_b=p(1b|1y)$. In a candidate joint distribution for counterfactual outcomes $A_0,A_1,B_y$, the number $t_b=p(A_0=1,A_1=1,B_y=b)$ must lie between

$$
\ell_b=\max(0,u_b+v_b-r_b),\qquad h_b=\min(u_b,v_b).
$$

Conversely, each choice in these intervals gives a nonnegative joint distribution by filling its four entries with $t_b,u_b-t_b,v_b-t_b,r_b-u_b-v_b+t_b$. Thus the common parameter $t=p(A_0=1,A_1=1)$ is feasible for setting $y$ precisely when

$$
t\in I_y=[\ell_0+\ell_1,h_0+h_1].
$$

Fine's theorem applied to each two-setting Bob restriction gives pairwise intersection of these intervals under the CHSH assumptions. A finite collection of real intervals with pairwise intersection has a common intersection. Choose $t$ there and construct a joint distribution $q_y(a_0,a_1,b)$ for each $y$. Nonsignaling makes their $(a_0,a_1)$ marginal $\pi$ identical. For $\pi>0$, the joint extension

$$
p(a_0,a_1,b_0,\ldots,b_{n-1})
=\pi(a_0,a_1)\prod_y\frac{q_y(a_0,a_1,b_y)}{\pi(a_0,a_1)}
$$

is a nonnegative normalized distribution reproducing every observed pair; zero-$\pi$ terms contribute zero. It is an explicit local model. This construction independently verifies membership of the supplied face points using rational arithmetic.

Completeness is relevant to a membership test. The upper-bound dual certificates have a weaker dependency: a positive combination of necessary positivity and CHSH inequalities already proves validity, whether or not those inequalities give a complete description.

\clearpage

## References

1. N. Brunner, N. Gisin and V. Scarani, [Entanglement and non-locality are different resources](https://arxiv.org/abs/quant-ph/0412109).
2. N. Brunner, V. Scarani and N. Gisin, [Bell-type inequalities for non-local resources](https://arxiv.org/abs/quant-ph/0603094).
3. M. T. Quintino, C. Budroni, E. Woodhead, A. Cabello and D. Cavalcanti, [Device-independent tests of structures of measurement incompatibility](https://arxiv.org/abs/1902.05841).
4. L. Tendick, [Quantum correlations cannot be reproduced with a finite number of measurements in any no-signaling theory](https://arxiv.org/abs/2408.08347).
5. N. Brunner et al., [Testing the Hilbert space dimension](https://arxiv.org/abs/0802.0760).
6. T. Moroder et al., [Device-independent entanglement quantification and related applications](https://arxiv.org/abs/1302.1336).
7. M. Navascués and T. Vértesi, [Bounding the set of finite dimensional quantum correlations](https://arxiv.org/abs/1412.0924).
8. B. G. Christensen et al., [Exploring the Limits of Quantum Nonlocality with Entangled Photons](https://arxiv.org/abs/1506.01649).

9. A. Fine, [Hidden Variables, Joint Probability, and the Bell Inequalities](https://doi.org/10.1103/PhysRevLett.48.291), Physical Review Letters 48, 291-295 (1982).

10. S.-L. Chen, N. Miklin, C. Budroni and Y.-N. Chen, [Device-independent quantification of measurement incompatibility](https://arxiv.org/abs/2010.08456).
11. L. Tendick, C. Budroni and M. T. Quintino, [Strict hierarchy between n-wise measurement simulability, compatibility structures, and multi-copy compatibility](https://arxiv.org/abs/2506.21223).
12. M. Navascués, A. Feix, M. Araújo and T. Vértesi, [Characterizing finite-dimensional quantum behavior](https://arxiv.org/abs/1507.07521).
13. A. Tavakoli, D. Rosset and M.-O. Renou, [Enabling computation of correlation bounds for finite-dimensional quantum systems via symmetrisation](https://arxiv.org/abs/1808.02412).
14. T. Vértesi, S. Pironio and N. Brunner, [Closing the detection loophole in Bell experiments using qudits](https://arxiv.org/abs/0909.3171).
15. M. Navascués, G. de la Torre and T. Vértesi, [Characterization of quantum correlations with local dimension constraints and its device-independent applications](https://arxiv.org/abs/1308.3410).
16. N. Gigena and J. Kaniewski, [Quantum value for a family of I3322-like Bell functionals](https://arxiv.org/abs/2203.01837).
17. K. F. Pál and T. Vértesi, [Quantum bounds on Bell inequalities](https://arxiv.org/abs/0810.1615).
18. E. Zambrini Cruzeiro and N. Gisin, [Complete list of Bell inequalities with four binary settings](https://arxiv.org/abs/1811.11820).
19. A. Mukherjee et al., [Device independent Schmidt rank witness by using Hardy paradox](https://arxiv.org/abs/1407.2146).
20. K. F. Pál and T. Vértesi, [Maximal violation of the I3322 inequality using infinite dimensional quantum systems](https://arxiv.org/abs/1006.3032).
