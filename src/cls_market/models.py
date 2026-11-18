"""Data contracts for the CLS market; not the auction algorithms."""

from collections.abc import Callable
from dataclasses import dataclass

# Every cost curve takes a contracted power cap [kW] and returns cost [EUR].
CostCurve = Callable[[float], float]


@dataclass(frozen=True)
class Aggregator:
    """Aggregator with nominal and minimum contractual limits and two cost curves.

    TODO: Explain why actual costs and reported bids must be separate.
    TODO: Decide whether cost curves are monotone and zero at nominal power.
    """

    aggregator_id: str
    p_min_kw: float
    p_nom_kw: float
    true_cost: CostCurve
    offer_cost: CostCurve


@dataclass(frozen=True)
class DSO:
    """DSO operating cost as a function of the SUM of contracted power caps.

    Network capacity may enter this cost function, but is not automatically
    a hard feasibility constraint. See docs/02_MODEL_SPEC.md.
    """

    cost: CostCurve


@dataclass(frozen=True)
class MarketScenario:
    """One CLS auction and one common contract horizon."""

    name: str
    aggregators: tuple[Aggregator, ...]
    dso: DSO


@dataclass(frozen=True)
class Allocation:
    """Chosen power caps keyed by aggregator ID."""

    limits_kw: dict[str, float]
    reported_objective_eur: float
    solver_message: str = ""


@dataclass(frozen=True)
class Payments:
    """Positive values mean payment to an aggregator, in EUR."""

    to_aggregators_eur: dict[str, float]
