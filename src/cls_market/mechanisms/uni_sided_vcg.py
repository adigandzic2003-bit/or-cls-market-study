"""Uni-sided VCG transfers. Compare Heinrich et al. Eq. (6)-(11)."""

from ..models import Allocation, MarketScenario, Payments


def uni_sided_vcg(scenario: MarketScenario, allocation: Allocation) -> Payments:
    """Compute each aggregator's externality on the other actors.

    TODO V01: Derive the original allocation and counterfactual mathematically.
    TODO V02: For every aggregator j, run solve_allocation again with j's
               CLS cap fixed at P_nom_j. Its consumption must remain present.
    TODO V03: Calculate other aggregators' offered costs in each allocation.
    TODO V04: Include DSO operating costs in both cases with same cost curve.
    TODO V05: Calculate q_j as the effect on OTHERS (not j's own offer).
    TODO V06: Compare j's payment with a hand-solved two-aggregator example.
    TODO V07: Distinguish aggregator-side VCG from a full VCG payment scheme.
    TODO V08: Check DSO finances the total of all aggregator transfers.
    TODO V09: Treat failed counterfactual solves and ties explicitly.
    TODO V10: Never silently substitute arbitrary large costs for infeasibility.
    TODO V11: State assumptions before testing incentives or individual
               rationality. Numerical examples do not prove truthfulness.
    """
    raise NotImplementedError("TODO V01-V11: implement the counterfactual VCG rule")
