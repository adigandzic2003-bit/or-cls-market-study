# 04 | Hand calculations (student worksheet)

**Do not fill these expected results from the program itself.** Solve them independently and then use them as test fixtures.

## Case 1 | One aggregator, piecewise optimum

```text
P_min = 0 kW, P_nom = 10 kW
Aggregator offer = true cost = 2 * (10 - P_lim) EUR
DSO operating cost = 5 * max(0, P_lim - 6) EUR
```

- [ ] Plot or describe each segment of the objective.
- [ ] Find the exact optimal contracted cap and corresponding cost.
- [ ] Explain why this is an interior or boundary optimum.
- [ ] Compare with SciPy and a coarse grid search.

## Case 2 | Two aggregators with different marginal CLS costs

- [ ] Choose nominal/minimum caps and two non-identical true curves.
- [ ] Start with offers equal to true costs.
- [ ] Compute the optimal limits and pay-as-bid payments manually.
- [ ] Repeat one allocation with a different OFFER cost, holding true cost fixed.

## Case 3 | VCG counterfactual with physical load retained

```text
A: P_nom = 10, P_min = 0, offer = true = (10 - P_lim_A) EUR
B: P_nom = 10, P_min = 0, offer = true = 2 * (10 - P_lim_B) EUR
DSO: cost = 20 * max(0, P_lim_A + P_lim_B - 10) EUR
```

- [ ] Derive the optimum with A and B participating.
- [ ] Derive the optimum with A not offering CLS, i.e. P_lim_A fixed at 10.
- [ ] Keep A's nominal load in the DSO objective.
- [ ] Calculate others' cost differences and VCG payment to A.
- [ ] Repeat for B and compare actual system costs with monetary payments.

## Case 4 | Equal bids and ties

- [ ] Design a pair of identical offer curves.
- [ ] Identify multiple optimal allocations and define consistent tie behavior.
- [ ] Test whether your payment result depends on tie selection.

## Case 5 | Scarcity and concentration

- [ ] Define a primary scarcity metric explicitly.
- [ ] Compare markets with identical total available flexibility but different shares.
- [ ] Control additional parameters and explain remaining differences.
- [ ] Compute one counterfactual VCG example for each market.

| Case | Hand solution | Python assertion active | Passed | Notes |
|---|---|---|---|---|
| 1 | [ ] | [ ] | [ ] | |
| 2 | [ ] | [ ] | [ ] | |
| 3 | [ ] | [ ] | [ ] | |
| 4 | [ ] | [ ] | [ ] | |
| 5 | [ ] | [ ] | [ ] | |
