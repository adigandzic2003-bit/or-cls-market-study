"""Reproducible toy markets first; controlled scarcity scenarios later."""

import random
from operator import truediv

from .models import MarketScenario
from .aggregator_data import sample_aggregators
from .dso_data import sample_dso

def make_toy_scenario() -> MarketScenario:
    """Prepare a tiny hand-solvable CLS example.

    TODO S01: Specify two or three aggregators with nominal/minimum caps.
    TODO S02: Choose and justify normalized additional CLS cost curves.
    TODO S03: Use truthful offers for the first validation.
    TODO S04: Record expected optimum in docs/04_HAND_CALCULATIONS.md.
    TODO S05: Keep all inputs deterministic until the basic tests pass.
    """

def make_random_scenario(seed: int = 187) -> MarketScenario:
    """
    Generate a reproducible random CLS market scenario.

    Randomly selects 1–25 aggregators and one DSO from the
    synthetic datasets, including their respective cost curves.

    Args:
        seed (int): Random seed for reproducible market selection.

    Returns:
        MarketScenario: A market containing the selected
        aggregators and DSO.
    """

    value = random.Random(seed).randint(1, 25)

    aggregators = sample_aggregators(value, seed=seed)
    dso = sample_dso(seed=seed)

    return MarketScenario("Test scenario", aggregators, dso)

def make_scarcity_scenarios() -> list[MarketScenario]:
    """Change market concentration and flexibility while controlling costs.

    TODO S06: Define the primary scarcity measure before generating scenarios.
    TODO S07: Calculate F_j = P_nom_j - P_min_j as max contractual tightening.
    TODO S08: Compare markets with equal sum(F_j) and unequal concentration.
    TODO S09: If using a threshold R, define it separately from Heinrich's
               DSO cost function and explain technical pivotality.
    TODO S10: Keep network costs and provider costs comparable across cases.
    TODO S11: Save inputs and random seeds before running any large study.
    """
    raise NotImplementedError("TODO S06-S11: build controlled scenario pairs")

def is_compatible(market: MarketScenario) -> bool:
    """Check whether a market scenario is compatible based on capacities"""

    total_nominal_kw = sum(agg.p_nom_kw for agg in market.aggregators)
    total_minimum_kw = sum(agg.p_min_kw for agg in market.aggregators)
    network_limit_kw = market.dso.network_limit_kw

    print("Total nominal power:", total_nominal_kw)
    print("Total minimal power:", total_minimum_kw)
    print("DSO network limit:", network_limit_kw)

    return total_minimum_kw <= network_limit_kw <= total_nominal_kw