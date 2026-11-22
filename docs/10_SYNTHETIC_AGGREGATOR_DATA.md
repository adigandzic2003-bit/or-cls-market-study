# Synthetic aggregator dataset — provenance, schema and checks

**PROVENANCE WARNING: All 150 profiles and all numerical parameters were generated with AI assistance. They are deliberately synthetic, not observations of German aggregators, not officially verified capacities, and not a statistically representative sample.** Do not present them as German market measurements or use them for real-world grid operation or price forecasts.

The selection of technology archetypes is Germany-*informed*: household heat-pump and EV charging portfolios, commercial buildings, industrial loads, EV charging fleets, and battery *charging* portfolios. This broad coverage is motivated by the German regulator's descriptions of controllable loads under §14a EnWG, and research on flexible commercial, industrial and EV loads. The actual number of profiles per type and every numeric range below are **study design assumptions**, not estimates from the cited sources.

Context links (qualitative only):
- Bundesnetzagentur, controllable consumption / §14a: https://www.bundesnetzagentur.de/DE/Vportal/Energie/SteuerbareVBE/artikel.html
- EnWG §14a: https://www.gesetze-im-internet.de/enwg_2005/__14a.html
- TU Braunschweig flexess use cases: https://www.tu-braunschweig.de/en/elenia/research/research-projects/flexess

## Relational CSV tables

Location: `data/aggregators/` — load into three Pandas DataFrames by `load_aggregator_dataframes()`.

| File | Primary key | Fields |
| --- | --- | --- |
| `catalog.csv` | `aggregator_id` | `portfolio_type`, `setting`, `size_class`, `flexibility_class`, `profile_id`, `case_tag`, `data_origin` |
| `technical.csv` | `aggregator_id` | `p_min_kw`, `p_nom_kw`, `max_flex_kw`, `flexibility_share` |
| `costs.csv` | (`aggregator_id`, `cost_model`) | `full_cost_eur`, `factor`, `a`, `b`, `data_origin` |

Every ID exists **exactly once** in catalog/technical and **twice** in costs (once for each cost model). There are 30 profiles in each of five categories, not population-weighted. Each category has three deliberately repeated *profiles* (same technical/economic parameters but distinct participant IDs). No duplicate participant IDs or duplicate cost-model keys are allowed. Repeated profiles permit controlled comparisons without silently duplicating a participant.

Classification is mechanical: `flexibility_class` uses flexible share `<0.25` low, `<0.55` medium, otherwise high; `size_class` uses nominal capacity `<250` small, `<1000` medium, otherwise large. These are **model tags**, not quality, credit, or regulatory ratings.

## Synthetic generation rules

The profile generator is `scripts/generate_aggregator_data.py`. Its fixed seed (`20261122`) and integer arithmetic produce repeatable nominal capacities and parameter sets. All values are in **kW and EUR for one hypothetical common contract event/horizon**. No €/kWh or duration inference is made. The category ranges below are deliberately illustrative for *aggregated portfolios*, not individual assets.

| Portfolio category | Nominal kW | Flexible share (design bounds) | Full-flex cost €/kW (design bounds) |
| --- | ---: | ---: | ---: |
| `residential_bundle` | 80–800 | 15–45% | 1.80–6.00 |
| `commercial_buildings` | 120–1300 | 10–40% | 2.50–8.00 |
| `industrial_loads` | 300–4000 | 5–30% | 3.50–11.00 |
| `ev_charging_fleets` | 120–1800 | 20–80% | 1.00–5.00 |
| `battery_charging` | 80–1500 | 35–90% | 0.80–4.00 |

Minimum power is `p_min = p_nom - max_flex`. Values `p_min >= 0`, `p_min < p_nom`, `max_flex > 0` are mandatory. A few rows intentionally hit **valid** boundaries of the declared ranges, such as normalized exponent 1 or 3 and the lowest/highest flexible share. These are boundary *cases*, not invalid rows.

Two alternative curve families are provided **per same ID**. Both use the same endpoint cost `B` to facilitate comparisons:

- `normalized`: `C(P_lim) = B * ((P_nom - P_lim)/(P_nom - P_min))**factor`; `factor` in `[1,3]` (unvalidated economic assumption).
- `heinrich_exponential`: `C(P_lim)=a * exp(b*P_lim) - a*exp(b*P_nom)`, `b<0`, `a>0`. The parameters are **AI-generated and numerically calibrated to C(P_min)≈B and C(P_nom)=0**, not Heinrich's empirical coefficients. The two families need not agree away from endpoints.

The CSVs hold **parameters**, not serialized Python callables. `get_aggregator()` builds a valid `Aggregator` instance via the existing `curves.py` factories. Default offers are truthful (`true_cost is offer_cost`). Strategic markups and scenario modifiers belong in the later Scenario Builder and must leave the source CSVs unchanged.

## Validation policy: reject incorrect data, not valid edge cases

Before returning any profile or DataFrame, `load_aggregator_pool()` validates:

- Required columns, completeness, nonempty/unique IDs, joined key sets, exactly one cost row per (ID, model).
- Every numeric field finite; valid min/nominal/flexible shares; class labels match derived numerical values.
- `max_flex_kw = p_nom_kw - p_min_kw`; `flexibility_share ≈ max_flex_kw / p_nom_kw`.
- Cost factory requirements, no negative full-flex cost, both cost families finite at nominal, midpoint and minimum, zero at nominal and matching full-flex cost at minimum.
- Repeated profile IDs must have identical technical and cost parameters; `data_origin` must clearly say synthetic.

A bad CSV edit must raise `ValueError`, **not** silently pass to optimization. The tests in `tests/test_aggregator_data.py` include deliberate corruptions to verify this behavior. This is mathematical/structural validation, **not proof that invented numbers are empirically correct or individually grid-feasible**. Cross-network compatibility, realistic simultaneous demand, stochastic calibration, and physical constraints remain future research and Scenario Builder tasks.

## Use

```python
from cls_market.aggregator_data import (
    load_aggregator_dataframes, select_aggregators, sample_aggregators,
)

catalog_df, technical_df, costs_df = load_aggregator_dataframes()
controlled = select_aggregators(["AGG_001", "AGG_030"], cost_model="normalized")
random_sample = sample_aggregators(12, seed=42, cost_model="heinrich_exponential")
```

`pandas` is included in optional project extra `analysis`, install with `pip install -e ".[analysis,dev]"`. Direct ID lookup and random sampling use only standard Python (plus project cost-curve dependencies). Random sampling is without replacement; record chosen IDs and input version with each experiment for full reproducibility. Future modifications must be scenario-level overlays, not edits to the AI-generated source catalog.
