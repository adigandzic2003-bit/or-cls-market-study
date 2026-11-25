from numpy._core import printoptions

from cls_market.scenarios import make_random_scenario
from cls_market.models import MarketScenario, DSO, Aggregator


def test_random_scenario():
    # 1. Create a random market
    seed = 0
    while 1==1:
        market = make_random_scenario(seed)

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

        # 7. Check market capacity
        total_nominal_kw = sum(agg.p_nom_kw for agg in market.aggregators)
        total_minimum_kw = sum(agg.p_min_kw for agg in market.aggregators)
        network_limit_kw = market.dso.network_limit_kw

        print("Total nominal power:", total_nominal_kw)
        print("Total minimal power:", total_minimum_kw)
        print("DSO network limit:", network_limit_kw)

        if total_minimum_kw <= network_limit_kw and network_limit_kw <= total_nominal_kw:
            break

        seed += 1

    print(seed)