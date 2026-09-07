# Model, geometry, and quantum implications

## 1. Definition

Inputs x,y lie in {0,1,2}; outputs a,b lie in {0,1}. Work in the normalized nonsignaling behavior space, with 15 correlators ordered as

`A0,A1,A2,B0,B1,B2,E00,E01,E02,E10,E11,E12,E20,E21,E22`.

Let H_A be the convex hull of the three classes whose restriction to a designated pair of Alice inputs and all Bob inputs is Bell local. Define H_B by exchanging parties, and H = conv(H_A union H_B). Convex weights are independent of the settings. These are behavior classes, not definitions of quantum joint measurability.

### Symbols, kept distinct

- **H** — the *nonsignaling* partial-local hull defined above: `conv(H_A u H_B)`. This is a
  constraint on behaviors, not on measurements.
- **C** — the *quantum* behaviors arising from setting-independent mixtures of local quantum
  implementations in which, in each component, at least one party has a jointly measurable
  pair. Which party may vary between components.
- **Q** — the local quantum behavior set.

The parent-POVM argument in section 3 establishes `C` is a subset of `H` intersected with
`Q`. **No equality is established, and H is strictly larger than C.** For a concrete
separation take zero local marginals and

    E = [[1,  1, 0],
         [1, -1, 0],
         [1,  1, 0]]

The probabilities are valid and nonsignaling, and Alice's input pair {0,2} is local (take
independent fair signs r, t and set A0 = A2 = B0 = B1 = r, B2 = t), so the behavior lies in
H. But inputs {0,1} on each side give a CHSH value of 4, above the Tsirelson bound, so it is
not quantum and cannot lie in C. The exclusion argument runs one way only: a violation of
F <= 7 puts a behavior outside H, and hence outside C.

The primary comparator likewise distinguishes behavioral partial locality from measurement
compatibility; see the definitions and Appendix F of
[Quintino et al.](https://arxiv.org/html/1902.05841v2).

### Convention

Output 0 maps to +1 and output 1 to -1, and

    P(ab|xy) = [1 + (-1)^a A_x + (-1)^b B_y + (-1)^(a+b) E_xy] / 4.

Define F by the coefficient vector

`[1,-1,1,-1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1]`.

The supplied exact duals prove F <= 7 on each of the six constituent partial-local classes. The supplied points prove that the F=7 face of H has affine dimension 14, while H has dimension 15.

## 2. Exact one-sided face dimensions

Write each constituent polytope's positivity/CHSH inequalities as r_i.(1,v) >= 0. The exact dual certificate writes 7-F(v) as a nonnegative linear combination of these quantities. At a saturating point every row carrying a strictly positive coefficient must vanish.

For each constituent, form the nullspace of those active rows in homogeneous coordinates (1,v). The span of the three nullspaces for one side contains the homogeneous span of its entire saturating face. Its rank is 14, hence the face dimension is at most 13. Explicit nonsignaling points belonging to the designated 2x3-local restrictions give matching affine rank 13. Combining both sides gives affine rank 14.

`proofs/verify_face_dimensions.py` checks the dual identities, nullspaces, membership inequalities and ranks exactly. For binary 2x3 restrictions, positivity and the complete set of 2x2 CHSH inequalities characterize locality; the separate facet verifier also supplies explicit deterministic local models for its 15 points. No claim of exhaustive enumeration of H's facets is made.

Thus F is a facet of H, but not of H_A or H_B. This is a structural distinction; it is not by itself a novelty proof.

It is in fact less than it looks. The *valid inequality* F <= 7 on H is a corollary of eq. (48) of
[Quintino et al.](https://arxiv.org/abs/1902.05841) plus positivity, via the exact identities
F = M_A - 4 p(00|10) + 1 = M_B - 4 p(11|22) + 1 with M_A, M_B relabelings of M3322 valid on H_A and H_B
respectively. `proofs/verify_m3322_corollary.py` proves this; `docs/PRIOR_ART.md` states what
survives it. Only the facet property and the sharp Schmidt-number-two bound of section 3 are outside
that derivation.

## 3. Gate-free quantum implication

Consider any setting-independent mixture of local quantum implementations. In each component, at least one party has a jointly measurable pair among its three binary measurements. The state, POVMs, compatible pair and which party supplies that pair may all vary between components.

**Claim:** every such mixture satisfies F <= 7.

**Proof:** In an Alice-compatible component, let G_lambda be a parent POVM for the designated pair, with classical response p(a|x,lambda). Set

`q(lambda) = tr[(G_lambda tensor I) rho]`

and, when q(lambda)>0,

`p(b|y,lambda) = tr[(G_lambda tensor B_b|y) rho] / q(lambda)`.

These give a local hidden-variable decomposition on that pair and all Bob inputs. The full behavior is nonsignaling by the local quantum construction, so it belongs to the corresponding constituent of H_A. Zero-weight lambda terms can be omitted. The exchanged argument places Bob-compatible components in H_B. Setting-independent mixtures therefore belong to H. The exact validity certificate finishes the proof.

The exact qutrit behavior violates this bound and excludes that entire mixture explanation. The result does not identify an inaccessible mechanism, prove finite-speed influence, or establish that all decompositions contain only incompatible components. It excludes decompositions consisting entirely of the specified compatible components.

## 4. Qubit bound: now proved, with the original optimization reduction

**Theorem (now certified in SCHMIDT_NUMBER_BOUND.md):** every two-qubit behavior with three binary measurements per party satisfies F <= 7, including arbitrary binary POVMs and setting-independent shared randomness.

A maximum can be attained at a pure state and projective binary measurements: the objective is separately affine in the state and each effect, and the extrema of 0 <= M <= I are projections. Qubit dichotomic observables are therefore either +/-I or u.sigma with |u|=1.

If ANY observable is +/-I, it is jointly measurable with another local measurement. The behavior then belongs to H_A or H_B, giving F <= 7 exactly in any dimension. This analytically disposes of every deterministic-measurement case. The numerical rank-pattern search is an implementation cross-check, not needed to prove this special case.

In the remaining case, use local unitaries to write the pure state as

`cos(theta)|00> + sin(theta)|11>`, with 0 <= theta <= pi/4.

Let c=cos(2 theta), s=sin(2 theta), z=(0,0,1), and T=diag(s,-s,1). Let Alice's three Bloch vectors be u_x. Put

```
a = (1,-1,1)
b = (-1,-1,1)
E = [[-1,-1,-1],[-1,-1,1],[1,-1,-1]]
```

Analytic optimization over Bob's nontrivial projective measurements yields

`G(theta,u) = c sum_x a_x u_x,z + sum_y | T sum_x E_xy u_x + c b_y z |`.

A self-contained analytic route would prove G <= 7 for all three unit Bloch vectors and theta in the stated interval. If G>7, the maximizing Bob vectors immediately construct a counterexample. This leaves six real parameters after the common azimuth gauge (theta, three polar angles, two relative azimuths). No coplanarity assumption is made.

The search implementation also allows deterministic Bob outputs by taking, for each y, the maximum of the displayed norm and the absolute scalar response. This makes it cover all binary POVM extremes even outside the analytically reduced sector.

### Exact endpoints

At theta=0 the state is product, so F<=7 by locality.

At theta=pi/4, all nontrivial local marginals vanish and T is orthogonal. The eigenvalues of E E^T are 1,4,4. Therefore

`sum_y |sum_x E_xy u_x| <= sqrt(3 sum_y |sum_x E_xy u_x|^2) <= sqrt(3*4*3) = 6`.

This proves an upper bound of 6 for the all-nontrivial maximally entangled sector. Deterministic-observable cases retain the separate bound of 7. The interior is now covered by the exact sum-of-squares certificate in SCHMIDT_NUMBER_BOUND.md.

### Numerical evidence and its limit

Thirty optimizations found maximum 7 within floating precision; the four fully nontrivial Alice searches approached the product-state endpoint. Nine fixed-theta searches also found no violation. Saved witnesses are evaluated independently by a 4x4 Bell operator. Neither the seeds, successful optimizer exits, nor the sampled entanglement profile certify an upper bound between samples or across unsampled local optima.

Update: `SCHMIDT_NUMBER_BOUND.md` now proves the sharp general bound F <= 7. The earlier dimension interpretation was too weak: Schmidt compression extends a qubit bound to all states of Schmidt number <=2, so the exact qutrit violation certifies Schmidt number >=3 and hence both local dimensions >=3.

## 5. Research note: a polynomial formulation

Retained as a research description. It is superseded by the Gram certificate for the
purpose of establishing the bound.


The original sharp-bound task had the following polynomial formulation, now resolved by the operator certificate. Take c,s >=0 with c^2+s^2=1; three unit vectors u_x; and t_y>=0 with

`t_y^2 = |diag(s,-s,1) sum_x E_xy u_x + c b_y z|^2`.

Prove `7 - c sum_x a_x u_x,z - sum_y t_y >= 0` on this compact domain, or produce a feasible point with negative value. This is suitable for a real-algebraic/SOS or certified branch-and-bound attack. A dimension-unrestricted quantum hierarchy alone cannot certify this qubit statement, because the supplied qutrit realization already violates it.
