"""Activate these tests only after independently deriving expected results."""

import math
import pytest
from cls_market.curves import (
    normalized_aggregator_cost, exponential_aggregator_cost, normalized_dso_cost, exponential_dso_cost,
    normalized_aggregator_cap_cost)

# 1. NORMALIZED AGGREGATOR
@pytest.mark.parametrize("q, expected", [
    (0, 0),
    (50, 125),
    (100, 500),])
def test_normalized_aggregator(q, expected):
    curve = normalized_aggregator_cost(100, 500, 2)
    assert curve(q) == pytest.approx(expected)

@pytest.mark.parametrize("q", [-10, 150, float("nan"), float("inf")])
def test_invalid_normalized_aggregator_input(q):
    curve = normalized_aggregator_cost(100, 500, 2)

    with pytest.raises(ValueError):
        curve(q)

@pytest.mark.parametrize("F, B, factor", [
    (0, 500, 2),
    (100, -10, 2),
    (100, 500, 4),
    (100, 500, 0.5),
    (100, 500, float("nan")),])
def test_invalid_normalized_aggregator_parameters(F, B, factor):
    with pytest.raises(ValueError):
        normalized_aggregator_cost(F, B, factor)

# 2. EXPONENTIAL AGGREGATOR (HEINRICH)
@pytest.mark.parametrize("p_lim, expected", [
    (0, 75),
    (10, 25),
    (20, 0),])
def test_exponential_aggregator(p_lim, expected):
    b = -math.log(2) / 10
    curve = exponential_aggregator_cost(100, b, 20, 0)

    assert curve(p_lim) == pytest.approx(expected)

@pytest.mark.parametrize("p_lim", [-1, 21, float("nan"), float("inf")])
def test_invalid_exponential_aggregator_input(p_lim):
    curve = exponential_aggregator_cost(100, -0.1, 20, 0)

    with pytest.raises(ValueError):
        curve(p_lim)

@pytest.mark.parametrize("a, b, p_nom, p_min", [
    (0, -0.1, 20, 0),
    (100, 0, 20, 0),
    (100, -0.1, 20, 20),
    (float("nan"), -0.1, 20, 0),])
def test_invalid_exponential_aggregator_parameters(a, b, p_nom, p_min):
    with pytest.raises(ValueError):
        exponential_aggregator_cost(a, b, p_nom, p_min)


# 3. NORMALIZED DSO
@pytest.mark.parametrize("S, expected", [
    (90, 0),
    (100, 0),
    (105, 125),
    (110, 500),])
def test_normalized_dso(S, expected):
    curve = normalized_dso_cost(100, 10, 500, 2)

    assert curve(S) == pytest.approx(expected)

@pytest.mark.parametrize("S", [-10, float("nan"), float("inf")])
def test_invalid_normalized_dso_input(S):
    curve = normalized_dso_cost(100, 10, 500, 2)

    with pytest.raises(ValueError):
        curve(S)

@pytest.mark.parametrize("K, R, B, factor", [
    (-1, 10, 500, 2),
    (100, 0, 500, 2),
    (100, 10, -500, 2),
    (100, 10, 500, 4),])
def test_invalid_normalized_dso_parameters(K, R, B, factor):
    with pytest.raises(ValueError):
        normalized_dso_cost(K, R, B, factor)

# 4. EXPONENTIAL DSO (HEINRICH)
@pytest.mark.parametrize("S, expected", [
    (0, 10),
    (10, 20),
    (20, 40),])
def test_exponential_dso(S, expected):
    beta = math.log(2) / 10
    curve = exponential_dso_cost(10, beta, 0)

    assert curve(S) == pytest.approx(expected)

@pytest.mark.parametrize("S", [-10, float("nan"), float("inf")])
def test_invalid_exponential_dso_input(S):
    curve = exponential_dso_cost(10, 0.1, 0)

    with pytest.raises(ValueError):
        curve(S)

@pytest.mark.parametrize("alpha, beta, gamma", [
    (0, 0.1, 0),
    (10, -0.1, 0),
    (10, 0.1, float("nan")),])
def test_invalid_exponential_dso_parameters(alpha, beta, gamma):
    with pytest.raises(ValueError):
        exponential_dso_cost(alpha, beta, gamma)

@pytest.mark.parametrize("p_lim_kw, expected", [
    (150, 0),
    (100, 125),
    (50, 500),])
def test_normalized_aggregator_cap_cost(p_lim_kw, expected):
    curve = normalized_aggregator_cap_cost(
        p_nom_kw=150, p_min_kw=50, full_cost_eur=500, factor=2)

    assert curve(p_lim_kw) == pytest.approx(expected)

@pytest.mark.parametrize("p_lim_kw", [
    49, 151, float("nan"), float("inf")])
def test_invalid_normalized_aggregator_cap(p_lim_kw):
    curve = normalized_aggregator_cap_cost(150, 50, 500, 2)

    with pytest.raises(ValueError):
        curve(p_lim_kw)
