"""Payments intentionally untested until source equations are verified."""

import pytest
from cls_market.models import Aggregator, Allocation, DSO, MarketScenario
from cls_market.mechanisms.pab import pay_as_bid
from cls_market.mechanisms.uniform import uniform_pricing
from cls_market.mechanisms.uni_sided_vcg import uni_sided_vcg


@pytest.mark.skip(reason="TODO P01-P05: check pay-as-bid equation first")
def test_pay_as_bid_uses_offer_not_actual_cost() -> None:
    a = Aggregator("A", 0.0, 10.0, lambda p: 10.0-p, lambda p: 2.0*(10.0-p))
    case = MarketScenario("pab", (a,), DSO(lambda p: p))
    chosen = Allocation({"A": 6.0}, 0.0)
    payments = pay_as_bid(case, chosen)
    assert payments.to_aggregators_eur["A"] >= 0.0
    # TODO: Replace weak assertion with a hand-derived EUR value.


@pytest.mark.skip(reason="TODO U01-U07: clarify uniform-price convention")
def test_uniform_price_from_original_paper() -> None:
    a = Aggregator("A", 0.0, 10.0, lambda p: 10.0-p, lambda p: 10.0-p)
    case = MarketScenario("uniform", (a,), DSO(lambda p: p))
    payments = uniform_pricing(case, Allocation({"A": 5.0}, 0.0))
    assert "A" in payments.to_aggregators_eur
    # TODO: Independently compute the common price.


@pytest.mark.skip(reason="TODO V01-V11: derive VCG counterfactual payments")
def test_vcg_with_two_aggregators() -> None:
    a = Aggregator("A", 0.0, 10.0, lambda p: 10-p, lambda p: 10-p)
    b = Aggregator("B", 0.0, 10.0, lambda p: 2*(10-p), lambda p: 2*(10-p))
    case = MarketScenario("vcg", (a, b), DSO(lambda p: 20*max(0.0, p-10)))
    chosen = Allocation({"A": 0.0, "B": 10.0}, 10.0)
    payments = uni_sided_vcg(case, chosen)
    assert "A" in payments.to_aggregators_eur
    # TODO: Calculate counterfactual costs and replace with numeric assertion.
