"""Validated ID-addressable loader for AI-generated synthetic DSO local feeders.

The CSVs are the immutable source of truth for experiments. These are NOT
measurements of German DSOs or hard electrical feeder constraints.
"""

from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from .curves import exponential_dso_cost, normalized_dso_cost
from .models import DSO

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "dsos"
PROVENANCE = "ai_generated_synthetic_not_empirical"
MODELS = frozenset({"normalized", "heinrich_exponential"})
PROFILE_SETTINGS = {
    "urban_residential": "urban",
    "suburban_mixed": "suburban",
    "rural_feeder": "rural",
    "industrial_feeder": "industrial",
    "charging_cluster": "charging",
}
PROFILES = frozenset(PROFILE_SETTINGS)
CASE_TAGS = frozenset({
    "standard", "repeated_profile", "low_reference_overload_boundary",
    "high_reference_overload_boundary", "linear_penalty_boundary",
    "steep_penalty_boundary", "low_penalty_boundary", "high_penalty_boundary",
    "small_capacity_boundary", "large_capacity_boundary",
})
REQUIRED_COLUMNS = {
    "catalog": {"dso_id", "network_profile", "setting", "asset_scope", "capacity_class",
                "overload_reference_class", "profile_id", "case_tag", "data_origin"},
    "technical": {"dso_id", "network_limit_kw", "reference_overload_kw",
                  "reference_total_caps_kw", "reference_overload_ratio"},
    "costs": {"dso_id", "cost_model", "full_cost_eur", "factor",
              "alpha", "beta", "gamma", "data_origin"},
}


def _read_table(directory: Path, stem: str) -> list[dict[str, str]]:
    with (directory / f"{stem}.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        if (fields is None or len(fields) != len(set(fields))
                or not REQUIRED_COLUMNS[stem] <= set(fields)):
            raise ValueError(f"Invalid columns in {stem}.csv")
        rows = list(reader)
    if not rows or any(None in row or any(value is None for value in row.values())
                       for row in rows):
        raise ValueError(f"Empty or malformed records in {stem}.csv")
    return rows


def _unique_by_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in rows:
        identifier = row["dso_id"]
        if not identifier or identifier.strip() != identifier or identifier in result:
            raise ValueError(f"Missing or duplicate DSO ID in {label}: {identifier!r}")
        result[identifier] = row
    return result


def _finite(row: dict[str, str], name: str) -> float:
    try:
        result = float(row[name])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid DSO numeric field {name}: {row.get(name)!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"Nonfinite DSO numeric field {name}")
    return result


def load_dso_pool(directory: Path | None = None) -> dict[str, dict]:
    """Validate ALL linked CSV records before exposing any DSO to simulations.

    Every ID must have one technical and one row per cost family. Several
    different DSO IDs may intentionally share the same parameter profile.
    """
    root = Path(directory) if directory is not None else DATA_DIR
    catalog = _unique_by_id(_read_table(root, "catalog"), "catalog")
    technical = _unique_by_id(_read_table(root, "technical"), "technical")
    cost_rows = _read_table(root, "costs")
    if set(catalog) != set(technical):
        raise ValueError("Catalog and technical DSO IDs do not match")

    costs: dict[tuple[str, str], dict[str, str]] = {}
    for row in cost_rows:
        key = (row["dso_id"], row["cost_model"])
        if (key[0] not in catalog or key[1] not in MODELS or key in costs
                or row["data_origin"] != PROVENANCE):
            raise ValueError(f"Invalid or duplicate DSO cost row: {key}")
        costs[key] = row
    if len(costs) != 2 * len(catalog):
        raise ValueError("Each DSO needs exactly one row per cost model")

    pool: dict[str, dict] = {}
    fingerprints = {}
    for dso_id, cat in catalog.items():
        if (cat["data_origin"] != PROVENANCE or cat["network_profile"] not in PROFILES
                or cat["asset_scope"] != "local_feeder_segment" or not cat["profile_id"]
                or cat["setting"] != PROFILE_SETTINGS[cat["network_profile"]]
                or cat["case_tag"] not in CASE_TAGS):
            raise ValueError(f"Invalid DSO classification or provenance: {dso_id}")
        tech = technical[dso_id]
        k = _finite(tech, "network_limit_kw")
        r = _finite(tech, "reference_overload_kw")
        anchor = _finite(tech, "reference_total_caps_kw")
        ratio = _finite(tech, "reference_overload_ratio")
        if not (k > 0 and r > 0 and anchor > 0 and ratio > 0):
            raise ValueError(f"Nonpositive DSO reference value: {dso_id}")
        if not math.isclose(k + r, anchor, rel_tol=1e-12, abs_tol=1e-8):
            raise ValueError(f"Inconsistent DSO reference point: {dso_id}")
        if not math.isclose(r / k, ratio, rel_tol=0, abs_tol=1e-8):
            raise ValueError(f"Inconsistent DSO reference overload ratio: {dso_id}")
        cap_class = "small" if k < 1500 else "medium" if k < 5000 else "large"
        overload_class = "low" if ratio < .25 else "medium" if ratio < .45 else "high"
        if (cat["capacity_class"] != cap_class
                or cat["overload_reference_class"] != overload_class):
            raise ValueError(f"Incorrect DSO classification: {dso_id}")

        norm = costs.get((dso_id, "normalized"))
        exp = costs.get((dso_id, "heinrich_exponential"))
        if norm is None or exp is None:
            raise ValueError(f"Missing DSO cost family: {dso_id}")
        b_cost = _finite(norm, "full_cost_eur")
        factor = _finite(norm, "factor")
        b_cost_exp = _finite(exp, "full_cost_eur")
        alpha = _finite(exp, "alpha")
        beta = _finite(exp, "beta")
        gamma = _finite(exp, "gamma")
        if not (b_cost > 0 and b_cost_exp > 0 and 1 <= factor <= 3
                and alpha > 0 and beta > 0 and gamma < 0):
            raise ValueError(f"Invalid DSO cost parameters: {dso_id}")
        if not math.isclose(b_cost, b_cost_exp, rel_tol=0, abs_tol=1e-8):
            raise ValueError(f"DSO cost families have unequal reference costs: {dso_id}")
        if gamma != -alpha:
            raise ValueError(f"DSO exponential curve not normalized at zero: {dso_id}")
        if (any(norm[column] != "" for column in ("alpha", "beta", "gamma"))
                or exp["factor"] != ""):
            raise ValueError(f"DSO cost columns in wrong model: {dso_id}")

        normalized = normalized_dso_cost(k, r, b_cost, factor)
        exponential = exponential_dso_cost(alpha, beta, gamma)
        for model, curve in (("normalized", normalized), ("heinrich_exponential", exponential)):
            try:
                points = (0.0, k / 2, k, k + r / 2, anchor, anchor + r)
                values = [curve(p) for p in points]
            except (OverflowError, ValueError, FloatingPointError) as exc:
                raise ValueError(f"Cost curve invalid at reference points: {dso_id}") from exc
            if (not all(math.isfinite(value) and value >= -1e-7 for value in values)
                    or any(left > right + 1e-7 for left, right in zip(values, values[1:]))):
                raise ValueError(f"Nonfinite, negative or decreasing DSO costs: {dso_id}")
            if not math.isclose(values[0], 0.0, rel_tol=0, abs_tol=1e-7):
                raise ValueError(f"Nonzero DSO cost at zero load: {dso_id}")
            if not math.isclose(values[4], b_cost, rel_tol=1e-9, abs_tol=1e-3):
                raise ValueError(f"Miscalibrated DSO cost at K+R: {dso_id}")
            if model == "normalized" and not math.isclose(values[2], 0.0, abs_tol=1e-7):
                raise ValueError(f"DSO normalized curve must be zero at K: {dso_id}")

        # Same profile_id means intentionally identical technical/economic data.
        fingerprint = (cat["network_profile"], k, r, anchor, b_cost, factor,
                       alpha, beta, gamma)
        previous = fingerprints.setdefault(cat["profile_id"], fingerprint)
        if fingerprint != previous:
            raise ValueError(f"DSO repeated profile is inconsistent: {cat['profile_id']}")
        pool[dso_id] = {"catalog": cat, "technical": tech,
                        "costs": {"normalized": norm, "heinrich_exponential": exp}}
    return pool


def get_dso(dso_id: str, cost_model: str = "normalized",
            pool: dict[str, dict] | None = None) -> DSO:
    """Instantiate one DSO from a stable profile ID with a selected curve."""
    records = load_dso_pool() if pool is None else pool
    if cost_model not in MODELS:
        raise ValueError(f"Unknown DSO cost model: {cost_model}")
    row = records[dso_id]
    tech, cost = row["technical"], row["costs"][cost_model]
    k = float(tech["network_limit_kw"])
    r = float(tech["reference_overload_kw"])
    if cost_model == "normalized":
        curve = normalized_dso_cost(k, r, float(cost["full_cost_eur"]),
                                    float(cost["factor"]))
    else:
        curve = exponential_dso_cost(float(cost["alpha"]), float(cost["beta"]),
                                     float(cost["gamma"]))
    return DSO(cost=curve, dso_id=dso_id, network_limit_kw=k, reference_overload_kw=r)


def select_dsos(dso_ids: list[str] | tuple[str, ...],
                cost_model: str = "normalized",
                pool: dict[str, dict] | None = None) -> tuple[DSO, ...]:
    """Return listed DSO profiles in requested order for batch experiments."""
    if not dso_ids or len(dso_ids) != len(set(dso_ids)):
        raise ValueError("Require nonempty, unique DSO IDs")
    records = load_dso_pool() if pool is None else pool
    return tuple(get_dso(identifier, cost_model, records) for identifier in dso_ids)


def sample_dsos(n: int, seed: int = 42, network_profile: str | None = None,
                cost_model: str = "normalized",
                pool: dict[str, dict] | None = None) -> tuple[DSO, ...]:
    """Select n distinct DSOs reproducibly, without replacement."""
    records = load_dso_pool() if pool is None else pool
    ids = sorted(identifier for identifier, row in records.items()
                 if network_profile is None or row["catalog"]["network_profile"] == network_profile)
    if type(n) is not int or not 1 <= n <= len(ids):
        raise ValueError("n must be between 1 and eligible DSO count")
    selected = random.Random(seed).sample(ids, n)
    return select_dsos(selected, cost_model, records)


def sample_dso(seed: int = 42, network_profile: str | None = None,
               cost_model: str = "normalized",
               pool: dict[str, dict] | None = None) -> DSO:
    """One seeded DSO, suitable for a single existing MarketScenario."""
    return sample_dsos(1, seed, network_profile, cost_model, pool)[0]


def load_dso_dataframes(directory: Path | None = None):
    """Return (catalog_df, technical_df, costs_df), validated before exposure."""
    root = Path(directory) if directory is not None else DATA_DIR
    load_dso_pool(root)
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError('Install pandas: pip install -e ".[analysis]"') from exc
    return tuple(pd.read_csv(root / f"{stem}.csv", dtype={"dso_id": "string"})
                 for stem in ("catalog", "technical", "costs"))
