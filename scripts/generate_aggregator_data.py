"""Generate a deterministic, AI-designed *synthetic* CLS aggregator catalog.

All numbers are illustrative model assumptions, not measured German market data.
Run: python scripts/generate_aggregator_data.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

SEED = 20261122
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "aggregators"
SOURCE_LABEL = "ai_generated_synthetic_not_empirical"

# Bounds are illustrative for *aggregated portfolios*, not individual appliances.
# The balanced category counts are experimental design, not German market shares.
CATEGORIES = (
    ("residential_bundle", "suburban", 80, 800, 15, 45, 180, 600),
    ("commercial_buildings", "urban", 120, 1300, 10, 40, 250, 800),
    ("industrial_loads", "industrial", 300, 4000, 5, 30, 350, 1100),
    ("ev_charging_fleets", "mixed", 120, 1800, 20, 80, 100, 500),
    ("battery_charging", "mixed", 80, 1500, 35, 90, 80, 400),
)


def draw_int(low: int, high: int, category: int, slot: int, salt: int) -> int:
    """Stable pseudo-random-looking integer (independent of Python RNG versions)."""
    key = (SEED + (category + 1) * 10007 + (slot + 1) * 7919
           + (slot + 3) * (slot + 5) * 1049 + salt * 65537)
    mixed = (key * 1664525 + 1013904223) % (2 ** 32)
    return low + mixed % (high - low + 1)


def generate_tables() -> tuple[list[dict], list[dict], list[dict]]:
    catalog, technical, costs = [], [], []
    previous_profiles: dict[int, dict] = {}
    for category_index, spec in enumerate(CATEGORIES):
        category, setting, min_nom, max_nom, min_share, max_share, min_rate, max_rate = spec
        previous_profiles = {}
        for slot in range(30):
            aggregator_id = f"AGG_{category_index * 30 + slot + 1:03d}"
            if slot in (9, 19, 29):
                # Separate participants with identical profiles; NEVER duplicate IDs.
                profile = previous_profiles[slot - 1].copy()
                case_tag = "repeated_profile"
            else:
                p_nom = draw_int(min_nom, max_nom, category_index, slot, 1)
                share_pct = draw_int(min_share, max_share, category_index, slot, 2)
                rate_cents = draw_int(min_rate, max_rate, category_index, slot, 3)
                factor_pct = draw_int(120, 280, category_index, slot, 4)
                curvature_pct = draw_int(70, 180, category_index, slot, 5)
                case_tag = "standard"
                if slot == 0:
                    share_pct, case_tag = min_share, "low_flex_boundary"
                elif slot == 1:
                    share_pct, case_tag = max_share, "high_flex_boundary"
                elif slot == 2:
                    factor_pct, case_tag = 100, "linear_cost_boundary"
                elif slot == 3:
                    factor_pct, case_tag = 300, "steep_cost_boundary"
                elif slot == 4:
                    rate_cents, case_tag = min_rate, "low_cost_boundary"
                elif slot == 5:
                    rate_cents, case_tag = max_rate, "high_cost_boundary"
                elif slot == 6:
                    p_nom, case_tag = min_nom, "small_size_boundary"
                elif slot == 7:
                    p_nom, case_tag = max_nom, "large_size_boundary"
                # Positive, finite, strictly smaller than nominal by construction.
                max_flex = max(1, (p_nom * share_pct + 50) // 100)
                p_min = p_nom - max_flex
                full_cost_cents = max_flex * rate_cents
                shape = curvature_pct / 100
                # Dimensionless shape / power normalizes b across portfolio sizes.
                b = -math.floor(shape / p_nom * 10_000_000 + 0.5) / 10_000_000
                assert b < 0
                denom = math.exp(b * p_min) - math.exp(b * p_nom)
                a = math.floor(((full_cost_cents / 100) / denom) * 1_000_000 + 0.5) / 1_000_000
                assert math.isfinite(a) and a > 0
                profile = dict(
                    profile_id=f"PROFILE_{aggregator_id}", p_nom=p_nom,
                    p_min=p_min, max_flex=max_flex, full_cost_cents=full_cost_cents,
                    factor_pct=factor_pct, a=a, b=b,
                )
                previous_profiles[slot] = profile.copy()

            share = profile["max_flex"] / profile["p_nom"]
            flex_class = "low" if share < .25 else "medium" if share < .55 else "high"
            size_class = "small" if profile["p_nom"] < 250 else "medium" if profile["p_nom"] < 1000 else "large"
            catalog.append(dict(
                aggregator_id=aggregator_id,
                portfolio_type=category,
                setting=setting,
                size_class=size_class,
                flexibility_class=flex_class,
                profile_id=profile["profile_id"],
                case_tag=case_tag,
                data_origin=SOURCE_LABEL,
            ))
            technical.append(dict(
                aggregator_id=aggregator_id,
                p_min_kw=profile["p_min"],
                p_nom_kw=profile["p_nom"],
                max_flex_kw=profile["max_flex"],
                flexibility_share=f"{share:.8f}",
            ))
            full_cost_eur = f"{profile['full_cost_cents'] / 100:.2f}"
            costs.append(dict(
                aggregator_id=aggregator_id,
                cost_model="normalized",
                full_cost_eur=full_cost_eur,
                factor=f"{profile['factor_pct'] / 100:.2f}",
                a="", b="", data_origin=SOURCE_LABEL,
            ))
            costs.append(dict(
                aggregator_id=aggregator_id,
                cost_model="heinrich_exponential",
                full_cost_eur=full_cost_eur,
                factor="",
                a=f"{profile['a']:.6f}",
                b=f"{profile['b']:.7f}",
                data_origin=SOURCE_LABEL,
            ))
    return catalog, technical, costs


def write_tables(directory: Path = DATA_DIR) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, rows in zip(("catalog.csv", "technical.csv", "costs.csv"), generate_tables()):
        with (directory / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {directory / name} ({len(rows)} records)")


if __name__ == "__main__":
    write_tables()
