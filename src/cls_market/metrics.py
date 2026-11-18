"""Evaluate outcomes using actual costs and transfers separately."""

from dataclasses import dataclass
from .models import Allocation, MarketScenario, Payments


@dataclass(frozen=True)
class OutcomeMetrics:
    total_payments_eur: float
    total_true_system_cost_eur: float
    dso_total_expense_eur: float
    aggregator_profit_eur: dict[str, float]


def evaluate_outcome(
    scenario: MarketScenario, allocation: Allocation, payments: Payments
) -> OutcomeMetrics:
    """Calculate resource costs, transfers, provider profit and DSO spending.

    TODO M01: Verify payment IDs match aggregator IDs.
    TODO M02: Sum actual aggregator costs using true_cost(P_lim_j).
    TODO M03: Evaluate DSO_cost(sum P_lim_j) once.
    TODO M04: True system cost = actual aggregator costs + DSO cost.
               Payments are transfers and are NOT added again here.
    TODO M05: Aggregator profit = allocated payment - true CLS cost.
    TODO M06: DSO total expense = DSO operating cost + total payments.
    TODO M07: Define DSO net benefit compared to an identical no-CLS case.
    TODO M08: Add robustness for floating-point accuracy and invalid values.
    """
    raise NotImplementedError("TODO M01-M08: implement outcome metrics")
