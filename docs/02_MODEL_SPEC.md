# 02 | Model specification and assumptions to verify

Primary source: Heinrich et al., *A Local Flexibility Market Mechanism with Capacity Limitation Services*, DOI https://doi.org/10.1016/j.enpol.2021.112335.

**Status:** Draft transcription and interface design. The student must check equation numbering, signs, normalization and assumptions against the original PDF before marking any mechanism correct.

## Players, variables, constraints

Aggregators are indexed by j. The decision variable is the CLS cap P_lim_j in kW.
For every j:

```text
P_min_j <= P_lim_j <= P_nom_j
```

A cap is an upper bound on consumption, not proof of a baseline-adjusted reduction.

## Common allocation rule

Working representation of the allocation objective:

```text
minimize over P_lim:
    sum_j offer_cost_j(P_lim_j)
    + DSO_cost(sum_j P_lim_j)
```

The objective uses bids, not true aggregator costs, and does not add auction transfers.

## Payment functions

- Pay-as-bid: consult Heinrich Eq. (4) and specify the baseline and normalization.
- CLS uniform pricing: consult Eq. (5); carefully check derivative signs under P_lim versus reduction F.
- Uni-sided VCG: consult Eqs. (6), (7) and (11); compute bidder-side externalities through new optimization runs.

### Crucial VCG counterfactual

When aggregator j does not offer CLS, fix its limit at P_nom_j and **keep that load inside** the sum passed to the DSO cost curve. Excluding an aggregator from a market is not removing its consumers from the network.

## Economics

- Real system cost = sum of aggregators' actual CLS costs + DSO operating costs.
- DSO expense = DSO operating costs + total paid to aggregators.
- Aggregator profit = payment received - actual CLS cost.
- Avoid adding transfers again when computing social resource costs.

## Things the student must decide and document

- [ ] Source-accurate model equations and interpretation of every variable.
- [ ] Which toy cost curves to use, and why they are only simplifications.
- [ ] Whether bid and true cost curves are identical in the truthful benchmark.
- [ ] Numerical optimizer, constraints, tolerances and solver failure handling.
- [ ] Marginal-price sign convention and tie handling for uniform pricing.
- [ ] How DSO net benefit is benchmarked against no participation.
- [ ] Definition of scarcity in a finite DSO cost framework.
- [ ] Whether/how to use a technical pivotality threshold with explicit R.
- [ ] Which sensitivity cases Heinrich already studied; avoid claiming novelty.
- [ ] Economic significance of counterfactual infeasibility or steep DSO costs.

## Provenance

| Element | Origin | Current status |
|---|---|---|
| CLS cap variable and allocation | Heinrich | Reproduce and validate |
| PAB, uniform and uni-sided VCG | Heinrich | Not implemented |
| Simple linear aggregator curve | Didactic toy assumption | To derive |
| Finite toy DSO overload cost | Didactic toy assumption | To derive |
| Scarcity/concentration scenario matrix | Proposed extension | After baseline |
| Pivotality as explicit R-threshold | Optional conceptual measure | Not an original hard constraint |
