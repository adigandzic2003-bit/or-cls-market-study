"""Common allocation optimization. Compare Heinrich et al. Eq. (1)-(3)."""

from .models import Allocation, MarketScenario


def reported_objective(limits_kw: dict[str, float], scenario: MarketScenario) -> float:
    """Calculate total reported market costs."""

    # TODO 1: Initialize total aggregator costs
    aggregator_costs = 0.0

    # TODO 2: Iterate over all aggregators
    for aggregator in scenario.aggregators:

        # TODO 3: Read the power limit by aggregator ID

        # TODO 4: Add the aggregator's offer cost
        ...

    # TODO 5: Sum all contracted power limits
    total_caps_kw = ...

    # TODO 6: Calculate the DSO's operating cost
    dso_cost = ...

    # TODO 7: Return total costs
    ...

