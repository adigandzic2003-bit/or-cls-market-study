"""Allocation tests must use paper-calculated optima before activation."""

import pytest
from cls_market.allocation import solve_allocation
from cls_market.models import Aggregator, DSO, MarketScenario


def test_single_aggregator_allocation() -> None:
    """Verify the optimizer against a hand-calculated optimum."""

    curve = lambda p: 2.0 * (10.0 - p)
    agg = Aggregator("A", 0.0, 10.0, curve, curve)

    case = MarketScenario("one", (agg,), DSO(lambda p: 5.0 * max(0.0, p - 6.0)))

    result = solve_allocation(case)

    assert 0.0 <= result.limits_kw["A"] <= 10.0
    assert result.limits_kw["A"] == pytest.approx(6.0, abs=1e-2)
    assert result.reported_objective_eur == pytest.approx(8.0, abs=1e-2)


@pytest.mark.skip(reason="TODO A06: retain consumer load in counterfactual")
def test_no_cls_participation_does_not_remove_consumption() -> None:
    curve = lambda p: 10.0 - p
    a = Aggregator("A", 0.0, 10.0, curve, curve)
    b = Aggregator("B", 0.0, 10.0, curve, curve)
    case = MarketScenario("counterfactual", (a, b), DSO(lambda p: p))
    got = solve_allocation(case, fixed_nominal_ids=frozenset({"A"}))
    assert got.limits_kw["A"] == pytest.approx(10.0)
    # TODO: Verify the DSO still counts A's nominal power.
