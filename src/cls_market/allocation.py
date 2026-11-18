"""Common allocation optimization. Compare Heinrich et al. Eq. (1)-(3)."""

from .models import Allocation, MarketScenario


def solve_allocation(
    scenario: MarketScenario,
    fixed_nominal_ids: frozenset[str] = frozenset(),
) -> Allocation:
    """Optimize contracted capacity limits from REPORTED offers.

    TODO A01: Reconstruct Heinrich's allocation objective from the paper.
    TODO A02: Map each aggregator ID to one P_lim_j decision variable.
    TODO A03: Objective = sum_j offer_j(P_lim_j) + DSO_cost(sum_j P_lim_j).
               Do not insert transfers or true costs in this objective.
    TODO A04: Enforce P_min_j <= P_lim_j <= P_nom_j for every aggregator.
    TODO A05: Choose and explain an optimizer (e.g., SciPy minimize) and bounds.
    TODO A06: In a counterfactual, FIX P_lim_j = P_nom_j for every excluded
               CLS participant. Its LOAD remains in the DSO cost calculation.
               Never make the network cheaper by removing the consumer.
    TODO A07: Validate input IDs, bounds and nonfinite cost outputs.
    TODO A08: Inspect solver success and objective, record tolerances.
    TODO A09: Compare an interior optimum and a boundary optimum by hand.
    TODO A10: Return Allocation with deterministic ID mapping and solver note.
    """
    raise NotImplementedError("TODO A01-A10: implement and validate allocation")
