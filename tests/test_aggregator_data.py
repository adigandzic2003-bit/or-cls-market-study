"""Checks for integrity of the complete AI-generated synthetic aggregator dataset."""

import csv
from collections import Counter
from pathlib import Path
import shutil

import pytest

from cls_market.aggregator_data import (
    DATA_DIR, get_aggregator, load_aggregator_pool,
    load_aggregator_dataframes, sample_aggregators, select_aggregators,
)


def test_full_dataset_is_valid_and_category_balanced():
    pool = load_aggregator_pool()
    assert len(pool) == 150
    assert len({key for key in pool}) == 150
    counts = Counter(profile["catalog"]["portfolio_type"] for profile in pool.values())
    assert counts == {
        "residential_bundle": 30,
        "commercial_buildings": 30,
        "industrial_loads": 30,
        "ev_charging_fleets": 30,
        "battery_charging": 30,
    }
    assert all(profile["catalog"]["data_origin"] == "ai_generated_synthetic_not_empirical"
               for profile in pool.values())


def test_every_category_has_three_intentionally_repeated_profiles():
    pool = load_aggregator_pool()
    for category in {row["catalog"]["portfolio_type"] for row in pool.values()}:
        rows = [row for row in pool.values() if row["catalog"]["portfolio_type"] == category]
        groups = Counter(row["catalog"]["profile_id"] for row in rows)
        assert sum(repeats - 1 for repeats in groups.values()) == 3
        assert max(groups.values()) == 2


def test_both_cost_models_are_constructible_and_calibrated():
    pool = load_aggregator_pool()
    for identifier, profile in pool.items():
        for cost_model in ("normalized", "heinrich_exponential"):
            agg = get_aggregator(identifier, cost_model, pool)
            full_cost = float(profile["costs"][cost_model]["full_cost_eur"])
            assert agg.true_cost is agg.offer_cost
            assert agg.true_cost(agg.p_nom_kw) == pytest.approx(0, abs=1e-6)
            assert agg.true_cost(agg.p_min_kw) == pytest.approx(full_cost, abs=1e-4)


def test_selection_by_id_and_seed_is_reproducible():
    pool = load_aggregator_pool()
    chosen = select_aggregators(["AGG_020", "AGG_001"], pool=pool)
    assert [agg.aggregator_id for agg in chosen] == ["AGG_020", "AGG_001"]
    a = sample_aggregators(10, seed=42, pool=pool)
    b = sample_aggregators(10, seed=42, pool=pool)
    assert [agg.aggregator_id for agg in a] == [agg.aggregator_id for agg in b]
    assert len({agg.aggregator_id for agg in a}) == 10
    industrial = sample_aggregators(5, category="industrial_loads", pool=pool)
    assert all(pool[agg.aggregator_id]["catalog"]["portfolio_type"] == "industrial_loads"
               for agg in industrial)


def test_selection_rejects_invalid_or_duplicate_ids():
    pool = load_aggregator_pool()
    with pytest.raises(ValueError):
        select_aggregators(["AGG_001", "AGG_001"], pool=pool)
    with pytest.raises(KeyError):
        select_aggregators(["AGG_NOT_FOUND"], pool=pool)
    with pytest.raises(ValueError):
        sample_aggregators(151, pool=pool)


def test_dataframe_tables_read_correctly():
    pytest.importorskip("pandas")
    catalog, technical, costs = load_aggregator_dataframes()
    assert (len(catalog), len(technical), len(costs)) == (150, 150, 300)
    assert catalog.aggregator_id.is_unique
    assert technical.aggregator_id.is_unique
    assert not costs.duplicated(["aggregator_id", "cost_model"]).any()


@pytest.mark.parametrize("file_name, agg_id, column, invalid", [
    ("technical.csv", "AGG_001", "p_min_kw", "999999"),
    ("technical.csv", "AGG_001", "max_flex_kw", "999"),
    ("technical.csv", "AGG_001", "flexibility_share", "NaN"),
    ("costs.csv", "AGG_001", "factor", "4"),
    ("costs.csv", "AGG_001", "a", "Inf"),
    ("catalog.csv", "AGG_001", "data_origin", "empirical"),
])
def test_corrupt_data_is_rejected(tmp_path: Path, file_name: str, agg_id: str,
                                  column: str, invalid: str):
    for name in ("catalog.csv", "technical.csv", "costs.csv"):
        shutil.copyfile(DATA_DIR / name, tmp_path / name)
    path = tmp_path / file_name
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    for row in rows:
        if row["aggregator_id"] == agg_id and (file_name != "costs.csv" or
              (column == "factor" and row["cost_model"] == "normalized") or
              (column == "a" and row["cost_model"] == "heinrich_exponential")):
            row[column] = invalid
            break
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError):
        load_aggregator_pool(tmp_path)
