# 01 | Research scope

## Seminar core

- One local network constraint, one DSO and several aggregators.
- Contractual power-limit decisions, not assumed physical energy savings.
- Implement Heinrich's allocation and payment rules independently.
- Compare PAB, CLS uniform pricing and uni-sided VCG using controlled inputs.
- Validate first with truthful bids and deterministic, hand-solvable markets.
- Explore market scarcity, concentration and counterfactual edge cases later.

## Deliberately out of scope for now

- Multi-period EV charging optimization or full power-flow simulation.
- Reinforcement learning or a reproduction of Holmberg and Wolak's game.
- A new auction mechanism, or journal-level novelty claims.
- Treating a hard flexibility requirement as if it were Heinrich's DSO cost curve.
- Strategic bidding until the baseline models pass numerical verification.

## Working research question

How do scarcity and aggregator concentration affect payments, true system costs and the DSO's economic benefit in the uni-sided VCG CLS market described by Heinrich et al.?

This is a **working** question. Do not present an unimplemented scenario as an established research result.

## Key quantities

- `P_nom_j`: nominal contractual power (kW).
- `P_min_j`: minimum acceptable power cap (kW).
- `P_lim_j`: decision variable, allocated contractual power cap (kW).
- `F_j = P_nom_j - P_min_j`: maximum possible tightening of contract cap (kW).
- `true_cost_j`: extra economic cost of imposing the contracted cap (EUR).
- `offer_cost_j`: the reported cost curve the market optimizes (EUR).
- `payment_j`: monetary transfer to aggregator j (EUR).

*Do not equate transfers with real resource costs.*
