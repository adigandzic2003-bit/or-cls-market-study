# Synthetic local-DSO reference profiles — scope, data and validation

**PROVENANCE: All 50 DSO profile records, their numeric parameters, and the five archetype proportions were constructed with AI assistance as reproducible synthetic assumptions. They are not measured German network data, not a sample of 50 real operators, and not empirically representative.** They are suitable for controlled *model experiments*, not operational grid decisions.

## What is a "DSO" in this model?

The German Federal Network Agency's *Monitoringbericht 2025* (Table 21) lists **851 registered electricity distribution network operators for 2025**, versus 866 for 2024. Table 22's 2024 network-structure overview also reports 851 operators, including closed distribution networks; these figures use different reference contexts. Our 50 hypothetical `DSO_###` records therefore **do not enumerate German operators**. Each record is a **local network/feeder-segment cost profile under one hypothetical DSO**, at the level appropriate for a local capacity-limitation-service (CLS) auction.

Background: [Bundesnetzagentur / Bundeskartellamt, Monitoringbericht 2025](https://data.bundesnetzagentur.de/Bundesnetzagentur/SharedDocs/Mediathek/Monitoringberichte/MonitoringberichtEnergie2025.pdf). This source informs the institutional background **only**; it does not establish our numeric cost coefficients, feeder sizes, or archetype weights.

The `MarketScenario` dataclass includes one `DSO` and any positive number of `Aggregator` instances. If we need several DSO territories, we run separate scenarios. Coupled multi-DSO network optimization is **not** part of the current model.

## Relational DataFrame architecture

The source of truth is the three CSV files under `data/dsos/`:

| File | Primary key | Purpose |
| --- | --- | --- |
| `catalog.csv` | `dso_id` | Local-feeder archetype, context, derived classes, stable `profile_id`, edge-case tag and AI provenance |
| `technical.csv` | `dso_id` | `network_limit_kw` = K, `reference_overload_kw` = R, `reference_total_caps_kw` = K+R, `reference_overload_ratio` = R/K |
| `costs.csv` | (`dso_id`, `cost_model`) | Reference total cost B in EUR, normalized factor, exponential `alpha`, `beta`, `gamma`, AI provenance |

Each DSO ID occurs once in `catalog.csv`, once in `technical.csv`, and **twice** in `costs.csv`: `normalized` and `heinrich_exponential`. IDs never duplicate. **One repeated parameter profile per archetype** intentionally has two separate IDs, permitting controlled comparisons with identical characteristics.

The `DSO` class holds the cost callable, stable `dso_id`, and optional metadata K and R. `reference_total_caps_kw` is a derived property. Existing calls such as `DSO(lambda s: s)` remain valid.

## Design: five archetypes, ten local feeders each

**All bounds below are arbitrary experimental design parameters, not derived German distributions.** Values refer to a *local segment*, **not** the total capacity of a utility company.

| Archetype | Count | K (reference local capacity, kW) | R/K (reference overload) | B/R (EUR/kW reference overload) |
| --- | ---: | ---: | ---: | ---: |
| `urban_residential` | 10 | 1,000–4,500 | 15–45% | 6.00–15.00 |
| `suburban_mixed` | 10 | 700–3,800 | 20–55% | 5.00–14.00 |
| `rural_feeder` | 10 | 400–2,200 | 15–50% | 7.00–18.00 |
| `industrial_feeder` | 10 | 2,500–15,000 | 10–35% | 4.00–12.00 |
| `charging_cluster` | 10 | 800–5,000 | 20–60% | 8.00–20.00 |

`K` is the cost-function **reference network limit**, not a hard physical feasibility constraint. `R` is a strictly positive *reference overload* used to define a common cost calibration point `K+R`. `B` is the hypothetical total cost **for a single common CLS contract event/horizon**, not electricity price (EUR/kWh), and is generated as `R * penalty_eur_per_kw`. We have not inferred an actual network duration, operating cost or regulatory penalty from it.

Valid edge cases include `factor=1`, `factor=3`, small/large K and low/high R/K. These are explicitly tagged in `case_tag`. All rows have positive K, R and B and finite coefficients. The class accepts optional metadata K=0 for independent toy use, but the CSV design intentionally uses K>0 to support the R/K ratio.

## Two cost-curve models for the same DSO

For contracted total caps `S = sum_j P_lim,j`:

1. **Normalized synthetic overload model:** `C(S)=B * (max(0,S-K)/R)**factor`, factor 1–3 (assumption; not empirically justified). Thus `C(S)=0` at and below K, and `C(K+R)=B`.
2. **Heinrich-style exponential *functional form*:** `C(S)=alpha * exp(beta*S) + gamma`, with `beta>0`, `alpha>0`, `gamma=-alpha`. We calibrate `alpha` so that `C(0)=0` and `C(K+R)≈B`. `beta` is a scaled shape parameter; **these are generated coefficients, NOT Heinrich's reported empirical parameters**.

These families have the same baseline cost at `S=0` and the same cost at `S=K+R`, but **different behavior between those points**: the exponential curve charges some costs below K while the normalized model does not. This is an intended sensitivity comparison, not mathematical equivalence.

The B and R scaling must eventually be sensitivity-tested and justified against observed network data or clearly retained as synthetic assumptions. Unlimited extrapolation to arbitrarily large S is **not** credible and may overflow; scenario compatibility and solver domain checks remain necessary.

## Validation and error policy

`scripts/generate_dso_data.py` deterministically writes the CSV snapshot (`SEED=20261122`). `load_dso_pool()` reads **and validates every record** before making any one profile available. Invalid numeric data is rejected, never silently repaired.

Validation includes schema/key integrity, absence of missing/NaN/Inf values, positive K/R/B, consistent K+R and R/K, valid cost exponents and coefficients, `gamma=-alpha`, `C(0)=0`, nonnegative/nondecreasing sample points, `C(K+R)≈B`, category/class consistency, and repeated-profile equality. Mutations of invalid values are tested in `tests/test_dso_data.py`; constructor metadata is tested in `tests/test_dso_models.py`. The generator's exact CSV snapshot is checked for reproducibility.

This verifies **internal arithmetic and contract correctness**, not German representativeness, physical AC power-flow feasibility, nor validity of a particular set of aggregators under a DSO. **The future Scenario Builder must explicitly compare `sum(P_nom)` to the chosen DSO's K and K+R, flag or control scale mismatches, and apply scenario modifiers only to copies.** Large overloads are allowed for deliberate stress tests but must be tagged and interpreted as such.

## API and DataFrames

```python
from cls_market.dso_data import (
    load_dso_dataframes, get_dso, select_dsos, sample_dso, sample_dsos,
)

catalog_df, technical_df, costs_df = load_dso_dataframes()
fixed = get_dso("DSO_001", cost_model="normalized")
specific = select_dsos(["DSO_003", "DSO_021"], cost_model="heinrich_exponential")
random_one = sample_dso(seed=42, network_profile="rural_feeder")
random_batch = sample_dsos(5, seed=42)
```

`pandas` is an optional analysis dependency (`pip install -e ".[analysis,dev]"`). Direct keyed loading and sampling work without Pandas. For exact experiment replay, retain the **selected IDs, cost-model name, fixed data snapshot/commit SHA, and seed**. DSO and aggregator pools are separately sourced and do not yet constitute an integrated Scenario Builder.
