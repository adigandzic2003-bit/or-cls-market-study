from numpy._core import printoptions

from cls_market.scenarios import make_random_scenario
from cls_market.models import MarketScenario, DSO, Aggregator


def test_random_scenario():

    # 1. Create a random market
    market = make_random_scenario(seed=187)

    # 2. Check if the returned object is a MarketScenario
    assert isinstance(market, MarketScenario)

    # 3. Check number of aggregators
    for agg in market.aggregators:
        assert isinstance(agg, Aggregator)

    assert 1 <= len(market.aggregators) <= 25

    # 4. Check the DSO
    assert isinstance(market.dso, DSO)

    # 5. Check the aggregator IDs
    for agg in market.aggregators:
        print(agg.aggregator_id)

    # 6. Check for reproducing results
    m1 = make_random_scenario(seed=187)
    m2 = make_random_scenario(seed=187)

    assert len(m1.aggregators) == len(m2.aggregators)

    for no in range(len(m1.aggregators)):
        assert m1.aggregators[no].aggregator_id == m2.aggregators[no].aggregator_id

    assert m1.dso.dso_id == m2.dso.dso_id