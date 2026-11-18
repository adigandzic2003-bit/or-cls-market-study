"""Activate these tests only after independently deriving expected results."""

import pytest
from cls_market.curves import linear_aggregator_cost, example_dso_cost


@pytest.mark.skip(reason="TODO C01: write, calculate and test the cost curve")
def test_linear_cost_at_three_caps() -> None:
    curve = linear_aggregator_cost(10.0, 2.0)
    assert curve(10.0) == pytest.approx(0.0)
    assert curve(5.0) == pytest.approx(10.0)
    # TODO: Derive the minimum cap and invalid-input cases yourself.


@pytest.mark.skip(reason="TODO C02: derive your OWN toy DSO curve first")
def test_dso_cost_below_at_and_above_limit() -> None:
    curve = example_dso_cost(10.0, 4.0)
    assert callable(curve)
    # TODO: Insert expected EUR values computed on paper.
