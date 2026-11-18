"""System costs are NOT the same as monetary transfers."""

import pytest
from cls_market.metrics import evaluate_outcome
from cls_market.models import Aggregator, Allocation, DSO, MarketScenario, Payments


@pytest.mark.skip(reason="TODO M01-M08: independently derive cost and profit")
def test_transfers_are_not_social_costs() -> None:
    curve = lambda p: 10.0-p
    agg = Aggregator("A", 0.0, 10.0, curve, curve)
    case = MarketScenario("economic", (agg,), DSO(lambda total: total))
    allocation = Allocation({"A": 5.0}, 10.0)
    payments = Payments({"A": 100.0})
    got = evaluate_outcome(case, allocation, payments)
    assert got.total_true_system_cost_eur != 100.0
    # TODO: Add expected true cost, DSO expense and profit assertions.
