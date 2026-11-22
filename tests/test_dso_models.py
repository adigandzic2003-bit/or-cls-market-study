"""DSO constructor invariants and backwards compatibility with existing models."""

import pytest
from cls_market.models import DSO


def test_legacy_constructor_and_optional_metadata():
    a = DSO(lambda s: s)
    assert a.dso_id == "DSO" and a.network_limit_kw is None
    assert a.reference_total_caps_kw is None
    b = DSO(lambda s: s, "DSO_A", 100)
    assert b.reference_total_caps_kw is None
    c = DSO(lambda s: s, "DSO_B", 100, 20)
    assert c.reference_total_caps_kw == 120


@pytest.mark.parametrize("r", [0, -1, float("nan"), float("inf"), "3", True])
def test_bad_reference_overload_rejected(r):
    with pytest.raises(ValueError):
        DSO(lambda s: s, network_limit_kw=100, reference_overload_kw=r)


def test_reference_overload_requires_network_limit():
    with pytest.raises(ValueError):
        DSO(lambda s: s, reference_overload_kw=20)


def test_reference_total_must_not_overflow():
    with pytest.raises(ValueError):
        DSO(lambda s: s, network_limit_kw=1e308, reference_overload_kw=1e308)
