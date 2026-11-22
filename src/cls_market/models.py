"""Data contracts for CLS markets; auction algorithms live in separate modules."""

from collections.abc import Callable
from dataclasses import dataclass
import math

# Every aggregator curve accepts a contracted power cap [kW] and returns cost [EUR].
# A DSO curve accepts the sum of contracted caps [kW] and returns cost [EUR].
CostCurve = Callable[[float], float]


def _validate_nonnegative_power(name: str, value: float) -> None:
    """Require a finite, nonnegative power value in kW."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite, nonnegative number")
    try:
        valid = math.isfinite(value) and value >= 0
    except (TypeError, ValueError, OverflowError):
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a finite, nonnegative number")


@dataclass(frozen=True)
class Aggregator:
    """One CLS participant with a feasible cap interval and two cost curves.

    true_cost represents actual provision costs; offer_cost is the reported bid
    used by the allocation optimizer. They may coincide in truthful scenarios.
    Each curve takes P_lim [kW] and returns cost [EUR].

    Curve shape, normalization and economic calibration are model assumptions
    validated separately; the data contract checks only structural invariants.
    """

    aggregator_id: str
    p_min_kw: float
    p_nom_kw: float
    true_cost: CostCurve
    offer_cost: CostCurve

    def __post_init__(self) -> None:
        if not isinstance(self.aggregator_id, str) or not self.aggregator_id.strip():
            raise ValueError("aggregator_id must be a nonempty string")
        _validate_nonnegative_power("p_min_kw", self.p_min_kw)
        _validate_nonnegative_power("p_nom_kw", self.p_nom_kw)
        if self.p_min_kw >= self.p_nom_kw:
            raise ValueError("Require 0 <= p_min_kw < p_nom_kw")
        if not callable(self.true_cost) or not callable(self.offer_cost):
            raise TypeError("true_cost and offer_cost must be callable")


@dataclass(frozen=True)
class DSO:
    """Distribution operator for ONE local network segment in a CLS auction.

    cost accepts the sum of all contracted aggregator caps [kW] and returns
    operating costs [EUR] for the common contract horizon.

    network_limit_kw (K) and reference_overload_kw (R) are optional metadata
    describing the local *cost model* reference point S=K+R. K is NOT a hard
    feasibility cap and neither field changes the supplied callable.
    DSO(lambda total: total) remains valid for existing tests and toy cases.
    """

    cost: CostCurve
    dso_id: str = "DSO"
    network_limit_kw: float | None = None
    reference_overload_kw: float | None = None

    def __post_init__(self) -> None:
        if not callable(self.cost):
            raise TypeError("DSO cost must be callable")
        if not isinstance(self.dso_id, str) or not self.dso_id.strip():
            raise ValueError("dso_id must be a nonempty string")
        if self.network_limit_kw is not None:
            _validate_nonnegative_power("network_limit_kw", self.network_limit_kw)
        if self.reference_overload_kw is not None:
            _validate_nonnegative_power("reference_overload_kw", self.reference_overload_kw)
            if self.reference_overload_kw <= 0:
                raise ValueError("reference_overload_kw must be positive")
            if self.network_limit_kw is None:
                raise ValueError("reference_overload_kw requires network_limit_kw")
            if not math.isfinite(self.network_limit_kw + self.reference_overload_kw):
                raise ValueError("Reference total caps exceed numeric limits")

    @property
    def reference_total_caps_kw(self) -> float | None:
        """Reference point K+R, if both metadata values are supplied."""
        if self.network_limit_kw is None or self.reference_overload_kw is None:
            return None
        return self.network_limit_kw + self.reference_overload_kw


@dataclass(frozen=True)
class MarketScenario:
    """One CLS auction with one DSO and an ordered set of aggregators.

    A multi-DSO experiment uses multiple scenarios; modeling more than one
    DSO in the same auction would require a different network allocation model.
    """

    name: str
    aggregators: tuple[Aggregator, ...]
    dso: DSO

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Scenario name must be a nonempty string")
        if not isinstance(self.aggregators, tuple) or not self.aggregators:
            raise ValueError("aggregators must be a nonempty tuple")
        if any(not isinstance(agg, Aggregator) for agg in self.aggregators):
            raise TypeError("All scenario participants must be Aggregator instances")
        ids = [agg.aggregator_id for agg in self.aggregators]
        if len(ids) != len(set(ids)):
            raise ValueError("Aggregator IDs must be unique within a scenario")
        if not isinstance(self.dso, DSO):
            raise TypeError("dso must be a DSO instance")


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
