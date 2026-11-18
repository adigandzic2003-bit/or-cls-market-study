"""Separate controlled experiments from core allocation and payment code."""

from .models import MarketScenario


def run_comparison(scenarios: list[MarketScenario]) -> list[dict[str, object]]:
    """Run identical scenario inputs through comparable payment mechanisms.

    TODO E01: Decide whether the same offers apply under each mechanism.
    TODO E02: Call the common allocation function for each scenario.
    TODO E03: Apply PAB, uniform pricing and uni-sided VCG separately.
    TODO E04: Calculate REAL costs using true_cost, not bids.
    TODO E05: Store all caps, transfers, parameters and convergence status.
    TODO E06: Write data only after active unit tests pass.
    TODO E07: Compare paired markets at constant total flexibility.
    TODO E08: Only then produce plots and discuss sensitivity and limits.
    """
    raise NotImplementedError("TODO E01-E08: implement controlled experiments")
