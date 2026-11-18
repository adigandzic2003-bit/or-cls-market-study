"""Smoke test only. A passing result does NOT validate auction algorithms."""

from cls_market.models import Aggregator, DSO, MarketScenario


def test_data_contracts_and_imports() -> None:
    simple = lambda p: float(10.0 - p)
    agg = Aggregator("A", 0.0, 10.0, simple, simple)
    scenario = MarketScenario("smoke", (agg,), DSO(lambda total: total))
    assert scenario.aggregators[0].p_nom_kw == 10.0
    assert scenario.dso.cost(3.0) == 3.0
