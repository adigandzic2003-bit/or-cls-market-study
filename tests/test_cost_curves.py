"""Activate these tests only after independently deriving expected results."""

import pytest
from cls_market.curves import normalized_aggregator_cost, example_dso_cost


@pytest.mark.parametrize("q_kw", [-10, -1, 101, 150])
def test_invalid_flexibility(q_kw):
    curve = normalized_aggregator_cost(100, 500, 2)

    with pytest.raises(ValueError):
        curve(q_kw)

@pytest.mark.parametrize("q_kw, expected_cost", [
    (0, 0), (50, 125), (100, 500),])
def test_normalized_cost(q_kw, expected_cost):

    curve = normalized_aggregator_cost(100, 500, 2)

    assert curve(q_kw) == pytest.approx(expected_cost)

@pytest.mark.parametrize("F, B, factor", [
    (0, 500, 2),
    (100, -10, 2),
    (100, 500, 0.5),
    (100, 500, 4),
])
def test_invalid_parameters(F, B, factor):
    with pytest.raises(ValueError):
        normalized_aggregator_cost(F, B, factor)

@pytest.mark.skip(reason="TODO C02: derive your OWN toy DSO curve first")
def test_dso_cost_below_at_and_above_limit() -> None:
    curve = example_dso_cost(10.0, 4.0)
    assert callable(curve)
    # TODO: Insert expected EUR values computed on paper.
