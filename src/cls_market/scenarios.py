"""Reproducible toy markets first; controlled scarcity scenarios later."""

from .models import MarketScenario, Aggregator
from .curves import normalized_aggregator_cap_cost, normalized_dso_cost

def make_toy_scenario() -> MarketScenario:
    """Prepare a tiny hand-solvable CLS example.

    TODO S01: Specify two or three aggregators with nominal/minimum caps.
    TODO S02: Choose and justify normalized additional CLS cost curves.
    TODO S03: Use truthful offers for the first validation.
    TODO S04: Record expected optimum in docs/04_HAND_CALCULATIONS.md.
    TODO S05: Keep all inputs deterministic until the basic tests pass.
    """
    a = Aggregator(
        aggregator_id="Agg 1", p_min_kw=100, p_nom_kw=150, true_cost=cost_a, offer_cost=cost_a)
    b = Aggregator(100.0, 150.0, 100.0, 100.0)
    m = MarketScenario()

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
