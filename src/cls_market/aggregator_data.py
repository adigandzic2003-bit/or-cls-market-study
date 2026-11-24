"""Validated, ID-addressable loader for AI-generated synthetic aggregator profiles.

CSV files are the source of truth. No random values are generated at load time.
Do not use these hypothetical profiles as empirical observations of Germany.
"""
from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from .curves import exponential_aggregator_cost, normalized_aggregator_cap_cost
from .models import Aggregator

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "aggregators"
PROVENANCE = "ai_generated_synthetic_not_empirical"
REQUIRED_COLUMNS = {
    "catalog": {"aggregator_id", "portfolio_type", "setting", "size_class",
                "flexibility_class", "profile_id", "case_tag", "data_origin"},
    "technical": {"aggregator_id", "p_min_kw", "p_nom_kw",
                  "max_flex_kw", "flexibility_share"},
    "costs": {"aggregator_id", "cost_model", "full_cost_eur", "factor", "a", "b",
              "data_origin"},
}
MODELS = frozenset({"normalized", "heinrich_exponential"})


def _read_table(directory: Path, stem: str) -> list[dict[str, str]]:
    with (directory / f"{stem}.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not REQUIRED_COLUMNS[stem] <= set(reader.fieldnames):
            raise ValueError(f"Missing required columns in {stem}.csv")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Empty {stem}.csv")
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Malformed records in {stem}.csv")
    return rows


def _finite(row: dict[str, str], field: str) -> float:
    try:
        value = float(row[field])
    except (ValueError, TypeError, KeyError) as error:
        raise ValueError(f"Invalid {field}: {row.get(field)!r}") from error
    if not math.isfinite(value):
        raise ValueError(f"Nonfinite {field}: {value!r}")
    return value


def _unique_by_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in rows:
        identifier = row["aggregator_id"]
        if not identifier or identifier.strip() != identifier or identifier in result:
            raise ValueError(f"Invalid or duplicate aggregator ID in {label}: {identifier!r}")
        result[identifier] = row
    return result


def load_aggregator_pool(directory: Path | None = None) -> dict[str, dict]:
    """Load and validate all linked CSV tables before returning any profiles.

    Results keyed by stable aggregator ID; IDs are never randomly regenerated.
    Repeated technical/cost profiles are allowed, duplicate IDs are not.
    """
    root = Path(directory) if directory is not None else DATA_DIR
    catalog = _unique_by_id(_read_table(root, "catalog"), "catalog")
    technical = _unique_by_id(_read_table(root, "technical"), "technical")
    cost_rows = _read_table(root, "costs")
    if set(catalog) != set(technical):
        raise ValueError("Catalog and technical aggregator IDs do not match")

    costs: dict[tuple[str, str], dict[str, str]] = {}
    for row in cost_rows:
        identifier, model = row["aggregator_id"], row["cost_model"]
        key = identifier, model
        if identifier not in catalog or model not in MODELS or key in costs:
            raise ValueError(f"Unknown/duplicate cost row: {key}")
        if row["data_origin"] != PROVENANCE:
            raise ValueError(f"Missing synthetic-data provenance for {key}")
        costs[key] = row
    if len(costs) != 2 * len(catalog):
        raise ValueError("Each aggregator must have one cost row per model")

    pool = {}
    repeated_profiles = {}
    for identifier, cat in catalog.items():
        if cat["data_origin"] != PROVENANCE:
            raise ValueError(f"Missing synthetic-data provenance for {identifier}")
        if not cat["portfolio_type"] or not cat["profile_id"]:
            raise ValueError(f"Missing category or profile_id for {identifier}")
        tech = technical[identifier]
        p_min, p_nom = _finite(tech, "p_min_kw"), _finite(tech, "p_nom_kw")
        flex, share = _finite(tech, "max_flex_kw"), _finite(tech, "flexibility_share")
        if not (0 <= p_min < p_nom and flex > 0 and 0 < share <= 1):
            raise ValueError(f"Invalid power range or share for {identifier}")
        if not math.isclose(flex, p_nom - p_min, abs_tol=1e-8, rel_tol=1e-10):
            raise ValueError(f"Inconsistent maximum flexibility for {identifier}")
        if not math.isclose(share, flex / p_nom, abs_tol=1e-8, rel_tol=0):
            raise ValueError(f"Inconsistent flexibility share for {identifier}")
        expected_flex_class = "low" if share < .25 else "medium" if share < .55 else "high"
        expected_size_class = "small" if p_nom < 250 else "medium" if p_nom < 1000 else "large"
        if cat["flexibility_class"] != expected_flex_class or cat["size_class"] != expected_size_class:
            raise ValueError(f"Inconsistent class labels for {identifier}")

        norm = costs.get((identifier, "normalized"))
        exp = costs.get((identifier, "heinrich_exponential"))
        if norm is None or exp is None:
            raise ValueError(f"Missing cost model for {identifier}")
        full_cost = _finite(norm, "full_cost_eur")
        factor = _finite(norm, "factor")
        full_cost_exp = _finite(exp, "full_cost_eur")
        a, b = _finite(exp, "a"), _finite(exp, "b")
        if not (full_cost > 0 and 1 <= factor <= 3 and full_cost_exp > 0 and a > 0 and b < 0):
            raise ValueError(f"Invalid cost parameters for {identifier}")
        if not math.isclose(full_cost_exp, full_cost, abs_tol=1e-8):
            raise ValueError(f"Noncomparable baseline costs for {identifier}")
        if any(norm[column] != "" for column in ("a", "b")) or exp["factor"] != "":
            raise ValueError(f"Unexpected cost parameters for {identifier}")
        norm_curve = normalized_aggregator_cap_cost(p_nom, p_min, full_cost, factor)
        exp_curve = exponential_aggregator_cost(a, b, p_nom, p_min)
        for curve in (norm_curve, exp_curve):
            if not math.isclose(curve(p_nom), 0.0, abs_tol=1e-6):
                raise ValueError(f"Nonzero cost at nominal power for {identifier}")
            if not math.isclose(curve(p_min), full_cost, abs_tol=1e-4, rel_tol=1e-8):
                raise ValueError(f"Bad full-flexibility cost calibration for {identifier}")
            mid = (p_min + p_nom) / 2
            if not 0 <= curve(mid) <= full_cost + 1e-5:
                raise ValueError(f"Nonmonotonic or negative midpoint costs for {identifier}")

        # Repeated profiles are intentionally identical, including costs.
        fingerprint = (cat["portfolio_type"], p_nom, p_min, flex, full_cost,
                       factor, a, b)
        existing = repeated_profiles.setdefault(cat["profile_id"], fingerprint)
        if fingerprint != existing:
            raise ValueError(f"Repeated profile has inconsistent values: {cat['profile_id']}")
        pool[identifier] = {"catalog": cat, "technical": tech,
                            "costs": {"normalized": norm, "heinrich_exponential": exp}}
    return pool


def get_aggregator(aggregator_id: str, cost_model: str = "normalized",
                   pool: dict[str, dict] | None = None) -> Aggregator:
    """Create a truthful Aggregator from a fixed ID and chosen curve model."""
    records = load_aggregator_pool() if pool is None else pool
    if cost_model not in MODELS:
        raise ValueError(f"Unknown cost model: {cost_model}")
    row = records[aggregator_id]
    technical, cost = row["technical"], row["costs"][cost_model]
    p_min, p_nom = float(technical["p_min_kw"]), float(technical["p_nom_kw"])
    if cost_model == "normalized":
        curve = normalized_aggregator_cap_cost(
            p_nom, p_min, float(cost["full_cost_eur"]), float(cost["factor"]))
    else:
        curve = exponential_aggregator_cost(
            float(cost["a"]), float(cost["b"]), p_nom, p_min)
    return Aggregator(aggregator_id, p_min, p_nom, curve, curve)


def select_aggregators(aggregator_ids: list[str] | tuple[str, ...],
                       cost_model: str = "normalized",
                       pool: dict[str, dict] | None = None) -> tuple[Aggregator, ...]:
    """Select specific IDs for hand checks and controlled stress scenarios."""
    if len(aggregator_ids) != len(set(aggregator_ids)):
        raise ValueError("Cannot select an aggregator ID twice in the same auction")
    if not aggregator_ids:
        raise ValueError("At least one aggregator is required")
    records = load_aggregator_pool() if pool is None else pool
    return tuple(get_aggregator(identifier, cost_model, records) for identifier in aggregator_ids)


def sample_aggregators(n: int, seed: int = 42, category: str | None = None,
                       cost_model: str = "normalized",
                       pool: dict[str, dict] | None = None) -> tuple[Aggregator, ...]:
    """Reproducible sampling WITHOUT replacement; never invents new IDs."""
    records = load_aggregator_pool() if pool is None else pool
    ids = sorted(identifier for identifier, row in records.items()
                 if category is None or row["catalog"]["portfolio_type"] == category)
    if type(n) is not int or not 1 <= n <= len(ids):
        raise ValueError("n must be between 1 and the number of eligible aggregators")
    selected = random.Random(seed).sample(ids, n)
    return select_aggregators(selected, cost_model, records)


def load_aggregator_dataframes(directory: Path | None = None):
    """Return (catalog_df, technical_df, costs_df); requires pandas analysis extra.

    Validate linked tables before exposing them to data analysis or simulations.
    """
    root = Path(directory) if directory is not None else DATA_DIR
    load_aggregator_pool(root)
    try:
        import pandas as pd
    except ImportError as error:
        raise ImportError('Install pandas: pip install -e ".[analysis]"') from error
    result = []
    for stem in ("catalog", "technical", "costs"):
        result.append(pd.read_csv(root / f"{stem}.csv", dtype={"aggregator_id": "string"}))
    return tuple(result)