"""Validate the CLS participant and market data contracts."""

from dataclasses import FrozenInstanceError

import pytest

from cls_market.models import Aggregator, DSO, MarketScenario


def test_existing_positional_constructors_and_truthful_costs():
    curve = lambda cap: 10.0 - cap
    agg = Aggregator("A", 0.0, 10.0, curve, curve)
    dso = DSO(lambda total: total)
    market = MarketScenario("baseline", (agg,), dso)
    assert market.aggregators[0].offer_cost(3.0) == 7.0
    assert dso.dso_id == "DSO"
    assert dso.network_limit_kw is None
    assert dso.cost(3.0) == 3.0


def test_dso_profile_metadata_and_independent_cost_curve():
    curve = lambda total: 2.0 * max(0.0, total - 100.0)
    dso = DSO(cost=curve, dso_id="DSO_001", network_limit_kw=100.0)
    assert dso.dso_id == "DSO_001"
    assert dso.network_limit_kw == 100.0
    assert dso.cost(110.0) == 20.0


def test_true_and_offer_costs_can_differ():
    true_cost = lambda cap: cap
    offer_cost = lambda cap: 2.0 * cap
    agg = Aggregator("A", 0.0, 10.0, true_cost, offer_cost)
    assert agg.true_cost(3.0) == 3.0
    assert agg.offer_cost(3.0) == 6.0


@pytest.mark.parametrize("agg_id", ["", "   ", None, 10])
def test_invalid_aggregator_id(agg_id):
    with pytest.raises(ValueError):
        Aggregator(agg_id, 0.0, 10.0, lambda p: p, lambda p: p)


@pytest.mark.parametrize("minimum, nominal", [
    (-1.0, 10.0), (10.0, 10.0), (11.0, 10.0),
    (0.0, 0.0), (float("nan"), 10.0), (0.0, float("inf")),
    (float("-inf"), 10.0), (True, 10.0), (0.0, "10"),
])
def test_invalid_aggregator_power_range(minimum, nominal):
    with pytest.raises(ValueError):
        Aggregator("A", minimum, nominal, lambda p: p, lambda p: p)


@pytest.mark.parametrize("true_cost, offer_cost", [
    (None, lambda p: p), (lambda p: p, 5.0),
])
def test_invalid_aggregator_cost_callables(true_cost, offer_cost):
    with pytest.raises(TypeError):
        Aggregator("A", 0.0, 10.0, true_cost, offer_cost)


@pytest.mark.parametrize("dso_id", ["", "  ", None, 5])
def test_invalid_dso_id(dso_id):
    with pytest.raises(ValueError):
        DSO(lambda total: total, dso_id=dso_id)


@pytest.mark.parametrize("network_limit", [-1.0, float("nan"), float("inf"), "100", True])
def test_invalid_dso_network_capacity(network_limit):
    with pytest.raises(ValueError):
        DSO(lambda total: total, network_limit_kw=network_limit)


def test_invalid_dso_curve():
    with pytest.raises(TypeError):
        DSO(500)


def test_scenario_requires_unique_aggregator_ids():
    curve = lambda p: p
    a = Aggregator("same", 0.0, 10.0, curve, curve)
    b = Aggregator("same", 0.0, 20.0, curve, curve)
    with pytest.raises(ValueError, match="unique"):
        MarketScenario("duplicates", (a, b), DSO(curve))


@pytest.mark.parametrize("name", ["", " ", None, 1])
def test_invalid_scenario_name(name):
    curve = lambda p: p
    a = Aggregator("A", 0.0, 10.0, curve, curve)
    with pytest.raises(ValueError):
        MarketScenario(name, (a,), DSO(curve))


def test_scenario_rejects_empty_or_mutable_aggregator_collection():
    curve = lambda p: p
    a = Aggregator("A", 0.0, 10.0, curve, curve)
    with pytest.raises(ValueError):
        MarketScenario("empty", (), DSO(curve))
    with pytest.raises(ValueError):
        MarketScenario("mutable", [a], DSO(curve))


def test_scenario_rejects_wrong_participant_types():
    curve = lambda p: p
    a = Aggregator("A", 0.0, 10.0, curve, curve)
    with pytest.raises(TypeError):
        MarketScenario("bad agg", (a, "fake"), DSO(curve))
    with pytest.raises(TypeError):
        MarketScenario("bad dso", (a,), curve)


def test_frozen_contracts():
    curve = lambda p: p
    agg = Aggregator("A", 0.0, 10.0, curve, curve)
    with pytest.raises(FrozenInstanceError):
        agg.p_nom_kw = 20.0
