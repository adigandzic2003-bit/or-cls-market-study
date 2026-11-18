"""Toy cost-curve factories. Their economic specification is student work."""

from .models import CostCurve


def linear_aggregator_cost(p_nom_kw: float, marginal_eur_per_kw: float) -> CostCurve:
    """Return a simplified cost of tightening a contractual power cap.

    TODO C01:
    1. Derive c(P_lim) = marginal_cost * (P_nom - P_lim) on paper.
    2. Verify units: EUR/kW times kW equals EUR.
    3. Validate both parameters and decide how to handle invalid caps.
    4. Check the nominal cap gives zero cost and tighter caps cost more.
    5. Explain why this is NOT Heinrich's optimized EV charging-cost curve.
    6. Implement the returned callable and test three hand-calculated cases.
    """
    raise NotImplementedError("TODO C01: implement the toy aggregator cost curve")


def example_dso_cost(network_limit_kw: float, penalty_eur_per_kw: float) -> CostCurve:
    """Finite-penalty toy DSO cost function, not Heinrich's calibrated function.

    TODO C02:
    1. Write and justify the function in docs/02_MODEL_SPEC.md first.
    2. Decide how costs depend on the sum of contracted power caps.
    3. Interpret network_limit_kw and penalty_eur_per_kw correctly.
    4. Check costs below, exactly at, and above the reference limit.
    5. Document that a finite cost is different from a hard grid constraint.
    6. Implement only after your paper derivation and independent test values.
    """
    raise NotImplementedError("TODO C02: specify and implement a toy DSO cost")
