"""Generate repeatable AI-designed synthetic DSO *local network profiles*.

These are NOT empirical German network-operator measurements or full DSO grids.
Run: python scripts/generate_dso_data.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

SEED = 20261122
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "dsos"
SOURCE_LABEL = "ai_generated_synthetic_not_empirical"

# Ten local feeders per archetype, not an estimate of German DSO market shares.
# K in kW, reference overload R/K in percent, reference penalty EUR/kW R.
# All numeric ranges are research assumptions, not observed German values.
ARCHETYPES = (
    ("urban_residential", "urban", 1000, 4500, 15, 45, 600, 1500),
    ("suburban_mixed", "suburban", 700, 3800, 20, 55, 500, 1400),
    ("rural_feeder", "rural", 400, 2200, 15, 50, 700, 1800),
    ("industrial_feeder", "industrial", 2500, 15000, 10, 35, 400, 1200),
    ("charging_cluster", "charging", 800, 5000, 20, 60, 800, 2000),
)


def draw_int(low: int, high: int, archetype: int, slot: int, salt: int) -> int:
    """Stable deterministic draw, with no dependency on global RNG state."""
    key = (SEED + (archetype + 1) * 10007 + (slot + 1) * 7919
           + (slot + 3) * (slot + 5) * 1049 + salt * 65537)
    mixed = (key * 1664525 + 1013904223) % (2 ** 32)
    return low + mixed % (high - low + 1)


def generate_tables() -> tuple[list[dict], list[dict], list[dict]]:
    catalog, technical, costs = [], [], []
    for group, spec in enumerate(ARCHETYPES):
        kind, setting, min_k, max_k, min_ratio, max_ratio, min_rate, max_rate = spec
        profiles = {}
        for slot in range(10):
            dso_id = f"DSO_{group * 10 + slot + 1:03d}"
            if slot == 9:
                # Exactly one intentionally repeated parameter profile per category,
                # but every DSO has a distinct participant ID.
                profile = profiles[8].copy()
                case_tag = "repeated_profile"
            else:
                k = draw_int(min_k, max_k, group, slot, 1)
                overload_pct = draw_int(min_ratio, max_ratio, group, slot, 2)
                rate_cents = draw_int(min_rate, max_rate, group, slot, 3)
                factor_pct = draw_int(120, 280, group, slot, 4)
                shape_pct = draw_int(45, 145, group, slot, 5)
                case_tag = "standard"
                if slot == 0:
                    overload_pct, case_tag = min_ratio, "low_reference_overload_boundary"
                elif slot == 1:
                    overload_pct, case_tag = max_ratio, "high_reference_overload_boundary"
                elif slot == 2:
                    factor_pct, case_tag = 100, "linear_penalty_boundary"
                elif slot == 3:
                    factor_pct, case_tag = 300, "steep_penalty_boundary"
                elif slot == 4:
                    rate_cents, case_tag = min_rate, "low_penalty_boundary"
                elif slot == 5:
                    rate_cents, case_tag = max_rate, "high_penalty_boundary"
                elif slot == 6:
                    k, case_tag = min_k, "small_capacity_boundary"
                elif slot == 7:
                    k, case_tag = max_k, "large_capacity_boundary"
                # Positive reference overload, rounded to full kW.
                r = max(1, (k * overload_pct + 50) // 100)
                anchor = k + r
                full_cost_cents = r * rate_cents
                # Separate exponential DSO curve: C(0)=0, C(K+R)~=B.
                # gamma=-alpha ensures nonnegative operating costs for S>=0.
                beta = round((shape_pct / 100) / anchor, 12)
                assert beta > 0
                alpha = round((full_cost_cents / 100) / math.expm1(beta * anchor), 8)
                assert alpha > 0 and math.isfinite(alpha)
                profile = dict(
                    profile_id=f"PROFILE_{dso_id}", k=k, r=r, anchor=anchor,
                    full_cost_cents=full_cost_cents, factor_pct=factor_pct,
                    alpha=alpha, beta=beta, gamma=-alpha,
                )
                profiles[slot] = profile.copy()
            k, r = profile["k"], profile["r"]
            capacity_class = "small" if k < 1500 else "medium" if k < 5000 else "large"
            overload_ratio = r / k
            overload_class = "low" if overload_ratio < .25 else "medium" if overload_ratio < .45 else "high"
            catalog.append(dict(
                dso_id=dso_id, network_profile=kind, setting=setting,
                asset_scope="local_feeder_segment", capacity_class=capacity_class,
                overload_reference_class=overload_class, profile_id=profile["profile_id"],
                case_tag=case_tag, data_origin=SOURCE_LABEL,
            ))
            technical.append(dict(
                dso_id=dso_id, network_limit_kw=k, reference_overload_kw=r,
                reference_total_caps_kw=profile["anchor"],
                reference_overload_ratio=f"{overload_ratio:.8f}",
            ))
            full_cost = f"{profile['full_cost_cents'] / 100:.2f}"
            costs.append(dict(
                dso_id=dso_id, cost_model="normalized", full_cost_eur=full_cost,
                factor=f"{profile['factor_pct']/100:.2f}",
                alpha="", beta="", gamma="", data_origin=SOURCE_LABEL,
            ))
            costs.append(dict(
                dso_id=dso_id, cost_model="heinrich_exponential", full_cost_eur=full_cost,
                factor="", alpha=f"{profile['alpha']:.8f}",
                beta=f"{profile['beta']:.12f}", gamma=f"{profile['gamma']:.8f}",
                data_origin=SOURCE_LABEL,
            ))
    return catalog, technical, costs


def write_tables(directory: Path = DATA_DIR) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for stem, rows in zip(("catalog", "technical", "costs"), generate_tables()):
        with (directory / f"{stem}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {directory / stem}.csv ({len(rows)} records)")


if __name__ == "__main__":
    write_tables()
