"""Pay-as-bid. Read Heinrich et al. Eq. (4) before implementing."""

from ..models import Allocation, MarketScenario, Payments


def pay_as_bid(scenario: MarketScenario, allocation: Allocation) -> Payments:
    """Compute transfers based on bids at the allocated contractual caps.

    TODO P01: Write Heinrich's exact payment rule in your own notation.
    TODO P02: Distinguish offer_cost from true_cost.
    TODO P03: Verify which baseline is subtracted, if any.
    TODO P04: Validate matching scenario/allocation IDs.
    TODO P05: Check against your own numeric example before enabling tests.
    """
    raise NotImplementedError("TODO P01-P05: implement pay-as-bid payments")
