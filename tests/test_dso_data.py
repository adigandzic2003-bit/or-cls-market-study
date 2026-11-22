"""Structural, economic-reference and mutation tests for the synthetic DSO catalog."""

import csv
from collections import Counter
from pathlib import Path
import shutil

import pytest

from cls_market.dso_data import (
    DATA_DIR, get_dso, load_dso_dataframes, load_dso_pool,
    sample_dso, sample_dsos, select_dsos,
)
from cls_market.models import DSO, MarketScenario, Aggregator


def test_full_dataset_and_no_duplicate_ids():
    pool = load_dso_pool()
    assert len(pool) == 50
    assert len(set(pool)) == 50
    assert Counter(row["catalog"]["network_profile"] for row in pool.values()) == {
        "urban_residential": 10,
        "suburban_mixed": 10,
        "rural_feeder": 10,
        "industrial_feeder": 10,
        "charging_cluster": 10,
    }
    assert all(row["catalog"]["data_origin"] == "ai_generated_synthetic_not_empirical"
               for row in pool.values())


def test_one_intentional_repeat_per_category():
    pool = load_dso_pool()
    for category in {row["catalog"]["network_profile"] for row in pool.values()}:
        members = [row for row in pool.values()
                   if row["catalog"]["network_profile"] == category]
        counts = Counter(row["catalog"]["profile_id"] for row in members)
        assert sum(n - 1 for n in counts.values()) == 1
        assert max(counts.values()) == 2


def test_every_model_is_nondecreasing_nonnegative_and_calibrated():
    pool = load_dso_pool()
    for dso_id, row in pool.items():
        k = float(row["technical"]["network_limit_kw"])
        r = float(row["technical"]["reference_overload_kw"])
        assert k > 0 and r > 0
        for model in ("normalized", "heinrich_exponential"):
            dso = get_dso(dso_id, model, pool)
            assert isinstance(dso, DSO)
            assert dso.reference_total_caps_kw == pytest.approx(k + r)
            expected = float(row["costs"][model]["full_cost_eur"])
            values = [dso.cost(point) for point in (0, k/2, k, k+r/2, k+r, k+2*r)]
            assert values[0] == pytest.approx(0, abs=1e-7)
            assert values[4] == pytest.approx(expected, abs=1e-3)
            assert all(v >= -1e-7 for v in values)
            assert all(left <= right + 1e-7 for left, right in zip(values, values[1:]))
            if model == "normalized":
                assert values[2] == 0


def test_fixed_ids_seed_and_network_profile_filter():
    pool = load_dso_pool()
    selected = select_dsos(["DSO_010", "DSO_001"], pool=pool)
    assert [dso.dso_id for dso in selected] == ["DSO_010", "DSO_001"]
    a = sample_dsos(7, seed=91, pool=pool)
    b = sample_dsos(7, seed=91, pool=pool)
    assert [x.dso_id for x in a] == [x.dso_id for x in b]
    assert len({x.dso_id for x in a}) == 7
    rural = sample_dsos(5, seed=3, network_profile="rural_feeder", pool=pool)
    assert all(pool[x.dso_id]["catalog"]["network_profile"] == "rural_feeder"
               for x in rural)
    assert isinstance(sample_dso(seed=4, pool=pool), DSO)


def test_dso_works_with_existing_market_scenario():
    curve = lambda p: 100.0 - p
    aggregator = Aggregator("A", 0, 100, curve, curve)
    market = MarketScenario("one-feeder", (aggregator,), sample_dso(seed=4))
    assert market.dso.dso_id.startswith("DSO_")
    assert market.dso.cost(0) == pytest.approx(0, abs=1e-7)


@pytest.mark.parametrize("ids", [[], ["DSO_001", "DSO_001"]])
def test_duplicate_or_empty_selections_rejected(ids):
    with pytest.raises(ValueError):
        select_dsos(ids)


def test_unknown_id_and_invalid_sampling_count_rejected():
    with pytest.raises(KeyError):
        get_dso("DSO_UNKNOWN")
    with pytest.raises(ValueError):
        sample_dsos(51)
    with pytest.raises(ValueError):
        sample_dsos(11, network_profile="urban_residential")
    with pytest.raises(ValueError):
        get_dso("DSO_001", cost_model="unknown")


def test_read_linked_dataframes():
    pytest.importorskip("pandas")
    catalog, technical, costs = load_dso_dataframes()
    assert (len(catalog), len(technical), len(costs)) == (50, 50, 100)
    assert catalog.dso_id.is_unique
    assert technical.dso_id.is_unique
    assert not costs.duplicated(["dso_id", "cost_model"]).any()


def test_snapshot_generator_matches_committed_csvs():
    # scripts/ isn't an installed Python package; load the snapshot generator by path.
    import importlib.util
    script = DATA_DIR.parents[1] / "scripts" / "generate_dso_data.py"
    spec = importlib.util.spec_from_file_location("dso_generator_snapshot", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated = module.generate_tables()
    for file_name, expected_rows in zip(("catalog.csv", "technical.csv", "costs.csv"), generated):
        with (DATA_DIR / file_name).open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == len(expected_rows)
        assert rows == [{key: str(value) for key, value in row.items()} for row in expected_rows]


@pytest.mark.parametrize("file_name, dso_id, model, field, invalid", [
    ("technical.csv", "DSO_001", None, "network_limit_kw", "-2"),
    ("technical.csv", "DSO_001", None, "reference_overload_kw", "0"),
    ("technical.csv", "DSO_001", None, "reference_total_caps_kw", "9999"),
    ("technical.csv", "DSO_001", None, "reference_overload_ratio", "NaN"),
    ("costs.csv", "DSO_001", "normalized", "factor", "4"),
    ("costs.csv", "DSO_001", "normalized", "full_cost_eur", "-3"),
    ("costs.csv", "DSO_001", "heinrich_exponential", "alpha", "Inf"),
    ("costs.csv", "DSO_001", "heinrich_exponential", "gamma", "0"),
    ("costs.csv", "DSO_001", "heinrich_exponential", "beta", "0.03"),
    ("catalog.csv", "DSO_001", None, "data_origin", "empirical"),
    ("catalog.csv", "DSO_001", None, "capacity_class", "invalid"),
])
def test_corrupt_data_rejected(tmp_path: Path, file_name: str, dso_id: str,
                               model: str | None, field: str, invalid: str):
    for name in ("catalog.csv", "technical.csv", "costs.csv"):
        shutil.copyfile(DATA_DIR / name, tmp_path / name)
    path = tmp_path / file_name
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames, rows = reader.fieldnames, list(reader)
    for row in rows:
        if row["dso_id"] == dso_id and (model is None or row.get("cost_model") == model):
            row[field] = invalid
            break
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError):
        load_dso_pool(tmp_path)


def test_duplicate_dso_id_rejected(tmp_path: Path):
    for name in ("catalog.csv", "technical.csv", "costs.csv"):
        shutil.copyfile(DATA_DIR / name, tmp_path / name)
    path = tmp_path / "catalog.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames, rows = reader.fieldnames, list(reader)
    rows[1]["dso_id"] = rows[0]["dso_id"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError):
        load_dso_pool(tmp_path)
