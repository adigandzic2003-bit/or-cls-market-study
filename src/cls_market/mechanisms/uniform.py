"""Uniform pricing specifically for CLS, not a generic power market."""

from ..models import Allocation, MarketScenario, Payments


def uniform_pricing(scenario: MarketScenario, allocation: Allocation) -> Payments:
    """Compute a common CLS marginal price using the original convention.

    TODO U01: Read Heinrich Eq. (5) and its explanatory paragraphs.
    TODO U02: Define a 'unit' of CLS: reduced contractual capacity, not energy.
    TODO U03: Derive the common marginal clearing price.
    TODO U04: Check derivative signs: P_lim and x=P_nom-P_lim point in
               opposite directions; do not silently pay negative prices.
    TODO U05: Decide handling of ties, non-differentiable curves and zero CLS.
    TODO U06: Prove the numerical result in a two-aggregator paper example.
    TODO U07: Document any simplifications relative to the original paper.
    """
    raise NotImplementedError("TODO U01-U07: derive and implement CLS uniform pricing")
