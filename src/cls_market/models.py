
"""Data contracts for the CLS market; not the auction algorithms."""

from collections.abc import Callable
from dataclasses import dataclass

CostCurve = Callable[[float], float]


@dataclass(frozen=True)
class Aggregator:
    """One aggregator participating in the CLS market.

    TODO M01: Validate p_min_kw < p_nom_kw.
    TODO M02: Validate finite and nonnegative power values.
    TODO M03: Distinguish true costs from reported offers.
    TODO M04: Verify cost curve behavior and units.
    """
    aggregator_id: str
    p_min_kw: float
    p_nom_kw: float
    true_cost: CostCurve
    offer_cost: CostCurve


@dataclass(frozen=True)
class DSO:
    """Distribution system operator.

    TODO M05: Document network capacity assumptions.
    TODO M06: Verify DSO cost curve behavior.
    """
    cost: CostCurve


@dataclass(frozen=True)
class MarketScenario:
    """One market scenario with any number of aggregators.

    TODO M07: Require at least one aggregator.
    TODO M08: Check unique aggregator IDs.
    TODO M09: Validate scenario consistency.
    """
    name: str
    aggregators: tuple[Aggregator, ...]
    dso: DSO


@dataclass(frozen=True)
class Allocation:
    """Optimized power limits.

    TODO M10: Check allocation feasibility.
    TODO M11: Ensure deterministic aggregator mapping.
    """
    limits_kw: dict[str, float]
    reported_objective_eur: float
    solver_message: str = ""


@dataclass(frozen=True)
class Payments:
    """Payments to participating aggregators.

    TODO M12: Validate payment IDs and finite values.
    """
    to_aggregators_eur: dict[str, float]