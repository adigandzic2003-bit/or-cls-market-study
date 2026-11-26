
"""CLS market allocation based on Heinrich's cost minimization."""

from scipy.optimize import minimize
from .models import Allocation, MarketScenario


def reported_objective(limits_kw: dict[str, float], scenario: MarketScenario) -> float:
    """Calculate total reported market costs."""

    aggregator_costs = 0.0

    for agg in scenario.aggregators:
        p_lim_kw = limits_kw[agg.aggregator_id]
        aggregator_costs += agg.offer_cost(p_lim_kw)

    total_caps_kw = sum(limits_kw.values())

    dso_cost = scenario.dso.cost(total_caps_kw)

    return aggregator_costs + dso_cost



def solve_allocation(scenario: MarketScenario) -> Allocation:
    """Find cost-minimizing contractual power limits."""

    aggregators = scenario.aggregators

    # Preserve a stable order for the optimizer
    ids = [agg.aggregator_id for agg in aggregators]

    # Bounds saves every aggregator's values in a new list -> Searching space for optimization
    bounds = [(agg.p_min_kw, agg.p_nom_kw) for agg in aggregators]

    # Starting point of optimization -> It is also possible to start from p_min_kw :)
    x0 = [agg.p_nom_kw for agg in aggregators]

    # Convert the solver's vector into our dictionary
    def objective(x):
        limits = dict(zip(ids, x))
        return reported_objective(limits, scenario)

    # Numerical optimization
    result = minimize(fun=objective, x0=x0, bounds=bounds, method="SLSQP")

    # Check solver status
    if not result.success:
        raise RuntimeError(result.message)

    # Convert optimized results back into our model
    optimized_limits = dict(zip(ids, result.x))

    # TODO 6: Return an Allocation object
    return ...
