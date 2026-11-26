"""Unit tests for CLS market scenario generation."""

from cls_market.scenarios import make_random_scenario, make_compatible_scenario, is_compatible
from cls_market.models import MarketScenario, DSO, Aggregator

def test_random_scenario():
    """
    Validate the structure and reproducibility of a random CLS market.

    Check that the scenario contains valid aggregator and DSO objects,
    that participant counts stay within the defined range, and that
    identical random seeds produce identical market selections.
    """

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

        if total_minimum_kw <= network_limit_kw <= total_nominal_kw:
            break

        seed += 1

    print(seed)

def test_compatible_scenario():
    """
    Verify that a capacity-compatible CLS market can be generated.

    Ensure the returned scenario is valid and that the DSO reference
    capacity lies between the aggregated minimum and nominal power
    limits of the participating aggregators.
    """

    market = make_compatible_scenario(seed=0)
    assert isinstance(market, MarketScenario)
    assert is_compatible(market)

def test_default_seed():
    """Default scenario seed with 35 for reproducibility."""
    market1 = make_random_scenario()
    market2 = make_random_scenario(seed=35)

    ids1 = [agg.aggregator_id for agg in market1.aggregators]
    ids2 = [agg.aggregator_id for agg in market2.aggregators]

    assert ids1 == ids2
    assert market1.dso.dso_id == market2.dso.dso_id