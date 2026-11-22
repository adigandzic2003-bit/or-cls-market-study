"""Toy cost-curve factories. Their economic specification is student work."""
from .models import CostCurve
import numpy as np
import math


def normalized_aggregator_cost(
    max_flex_kw: float, full_cost_eur: float, factor: float) -> CostCurve:
    """Create a nonlinear cost function for an aggregator.

    Costs increase with the contracted flexibility q according to
    C(q) = B * (q / F) ** factor.

    F: Maximum available flexibility (kW).
    B: Cost of providing full flexibility (EUR).
    factor: Cost curve exponent (1 to 3).
        -> TODO: Validate requirement factor between 1 and 3!

    Returns a callable that calculates costs for 0 <= q <= F.
    """

    validate_finite(max_flex_kw=max_flex_kw, full_cost_eur=full_cost_eur, factor=factor)
    if max_flex_kw <= 0 or full_cost_eur < 0 or (factor < 1 or factor > 3):
        raise ValueError("Invalid cost parameters!")

    def cost(q_kw: float) -> float:
        """Calculate the aggregator's cost for a given flexibility quantity.

        Args:
            q_kw: Contracted flexibility in kW (0 <= q_kw <= max_flex_kw).

        Returns:
            Total flexibility provision cost in EUR.

        Raises:
            ValueError: If q_kw exceeds the available flexibility range.
        """

        validate_finite(q_kw=q_kw)
        if q_kw < 0 or q_kw > max_flex_kw:
            raise ValueError("Invalid cost parameters!")
        else:
            return full_cost_eur * (q_kw/max_flex_kw)**factor

    return cost


def exponential_aggregator_cost(
    a: float, b: float, p_nom_kw: float, p_min_kw: float) -> CostCurve:
    """Create an exponential aggregator cost curve based on Heinrich et al. (Eq. 16).

    C(P_lim) = a * exp(b * P_lim) + c
    c = -a * exp(b * P_nom)

    Args:
        a: Positive cost scaling parameter (EUR).
        b: Negative curvature parameter (1/kW).
        p_nom_kw: Nominal power capacity (kW).
        p_min_kw: Minimum contractual power limit (kW).

    Returns:
        Callable calculating costs in EUR for a given power cap.
    """

    validate_finite(a=a, b=b, p_nom_kw=p_nom_kw, p_min_kw=p_min_kw)
    if a <= 0 or b >= 0 or not (0 <= p_min_kw < p_nom_kw):
        raise ValueError("Invalid aggregator parameters!")

    c = -a * np.exp(b * p_nom_kw)

    def cost(p_lim_kw: float) -> float:

        validate_finite(p_lim_kw=p_lim_kw)
        if p_lim_kw < p_min_kw or p_lim_kw > p_nom_kw:
            raise ValueError("Invalid capacity limit!")

        result = float(a * np.exp(b * p_lim_kw) + c)
        validate_finite(result=result)
        return result

    return cost


def normalized_aggregator_cap_cost(
    p_nom_kw: float, p_min_kw: float,
    full_cost_eur: float, factor: float) -> CostCurve:
    """Adapt normalized flexibility costs to a power-cap input."""

    validate_finite(p_nom_kw=p_nom_kw, p_min_kw=p_min_kw)

    if not (0 <= p_min_kw < p_nom_kw):
        raise ValueError("Invalid power limits!")

    max_flex_kw = p_nom_kw - p_min_kw

    flex_cost = normalized_aggregator_cost(
        max_flex_kw, full_cost_eur, factor
    )

    def cost(p_lim_kw: float) -> float:
        validate_finite(p_lim_kw=p_lim_kw)

        if not (p_min_kw <= p_lim_kw <= p_nom_kw):
            raise ValueError("Invalid capacity limit!")

        q_kw = p_nom_kw - p_lim_kw

        return flex_cost(q_kw)

    return cost


def normalized_dso_cost(
    network_limit_kw: float, reference_overload_kw: float, full_cost_eur: float,
        factor: float) -> CostCurve:
    """Create a nonlinear DSO overload cost function.

    C(S) = B * (max(0, S - K) / R) ** factor

    Args:
        network_limit_kw: Reference network capacity K (kW).
        reference_overload_kw: Reference overload R (kW).
        full_cost_eur: Cost B at reference overload R (EUR).
        factor: Cost curve exponent (assumed range: 1 to 3).

    Returns:
        Callable calculating DSO overload costs in EUR.

    Note:
        Synthetic cost model, not Heinrich's calibrated DSO curve.
        TODO: Justify exponent range and parameter assumptions.
    """

    validate_finite(network_limit_kw=network_limit_kw, reference_overload_kw=reference_overload_kw,
        full_cost_eur=full_cost_eur,factor=factor)

    if (network_limit_kw < 0 or reference_overload_kw <= 0 or full_cost_eur < 0
        or (factor < 1 or factor > 3)):
        raise ValueError("Invalid DSO parameters!")

    def cost(total_caps_kw: float) -> float:
        """Calculate overload costs for total contracted power caps.

        Args:
            total_caps_kw: Sum of contracted power caps S (kW).

        Returns:
            DSO overload costs in EUR.

        Raises:
            ValueError: If the input is invalid.
        """

        validate_finite(total_caps_kw=total_caps_kw)
        if total_caps_kw < 0:
            raise ValueError("Invalid total capacity!")

        #C(S) = B * (max(0, S - K) / R) ** factor
        curve = full_cost_eur * ((max(0, total_caps_kw - network_limit_kw)) / reference_overload_kw)**factor
        validate_finite(curve=curve)
        return float(curve)

    return cost


def exponential_dso_cost(alpha: float, beta: float, gamma: float) -> CostCurve:
    """Create an exponential DSO cost curve based on Heinrich et al. (Eq. 17).

    C(S) = alpha * exp(beta * S) + gamma

    Args:
        alpha: Positive cost scaling parameter.
        beta: Positive growth parameter (1/kW).
        gamma: Cost curve offset (EUR).

    Returns:
        Callable calculating DSO operating costs in EUR.
    """

    validate_finite(alpha=alpha, beta=beta, gamma=gamma)

    if alpha <= 0 or beta <= 0:
        raise ValueError("Invalid DSO parameters!")

    def cost(total_caps_kw: float) -> float:
        """Calculate DSO costs for the sum of contracted power caps."""

        validate_finite(total_caps_kw=total_caps_kw)

        if total_caps_kw < 0:
            raise ValueError("Invalid total capacity!")

        result = alpha * np.exp(beta * total_caps_kw) + gamma

        validate_finite(result=result)
        return float(result)

    return cost


def validate_finite(**parameters: float) -> None:
    """Reject NaN and infinite parameter values."""

    for name, value in parameters.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number!")