"""Toy cost-curve factories. Their economic specification is student work."""
from .models import CostCurve
import numpy as np

def normalized_aggregator_cost(
    max_flex_kw: float, full_cost_eur: float, factor: float) -> CostCurve:
    """Create a nonlinear cost function for an aggregator.

    Costs increase with the contracted flexibility q according to
    C(q) = B * (q / F) ** factor.

    F: Maximum available flexibility (kW).
    B: Cost of providing full flexibility (EUR).
    factor: Cost curve exponent (1 to 3).
        -> TODO: Validate requirement factor between 1 and 3!

    Returns a callable that calculates costs for 0 <= q <= F.
    """

    if max_flex_kw <= 0 or full_cost_eur < 0 or (factor < 1 or factor > 3):
        raise ValueError("Invalid cost parameters!")

    def cost(q_kw: float) -> float:
        """Calculate the aggregator's cost for a given flexibility quantity.

        Args:
            q_kw: Contracted flexibility in kW (0 <= q_kw <= max_flex_kw).

        Returns:
            Total flexibility provision cost in EUR.

        Raises:
            ValueError: If q_kw exceeds the available flexibility range.
        """
        if q_kw < 0 or q_kw > max_flex_kw:
            raise ValueError("Invalid cost parameters!")
        else:
            return full_cost_eur * (q_kw/max_flex_kw)**factor

    return cost


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
