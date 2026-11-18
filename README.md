# CLS Market Study | Operations Research Seminar

**Status:** Educational research scaffold (work in progress). **No auction algorithms have been implemented or scientifically validated yet.**

This repository develops a student-owned Python implementation of the Capacity Limitation Services (CLS) market studied by Heinrich et al. The immediate priority is to reproduce the allocation and payment mechanisms and validate them against hand-solvable examples. Scarcity and supplier concentration are possible later stress tests, not a second energy-market model.

## Scientific scope

- DSO procurement of contractual power-consumption limits from aggregators.
- Common cost-minimizing allocation using reported bid curves and DSO costs.
- Three payment mechanisms: pay-as-bid, CLS uniform pricing, and uni-sided VCG.
- Separation of *true economic costs*, *reported bids*, *monetary payments*, and *profits*.
- Carefully designed and documented edge cases after baseline validation.

**Important:** A contracted power limit is not automatically the same as an observed reduction relative to a consumption baseline. For an aggregator that cannot participate in CLS, its nominal consumption still remains in the DSO cost calculation.

## What's implemented?

The repository contains Python type contracts, function signatures, TODO-rich docstrings, research notes, a small executable smoke test and **skipped** tests for the unfinished algorithms. The solver, cost functions, payments, calibrated inputs, experiments and results are deliberately **not** supplied.

## Getting started

Requirements: Python 3.11 or later.

```bash
git clone https://github.com/adigandzic2003-bit/or-cls-market-study.git
cd or-cls-market-study
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -v
python scripts/run_toy_example.py
```

Initially, the structural smoke test should pass, while research tests remain skipped. **Passing skipped tests is not evidence that the auctions work.** Remove each `@pytest.mark.skip` only once the code and independent hand-calculation are ready.

## Where to start

1. Read [the scope](docs/01_SCOPE.md) and [model specification](docs/02_MODEL_SPEC.md).
2. Work through [the detailed implementation checklist](docs/03_IMPLEMENTATION_TODOS.md).
3. Write independent calculations in [the test notebook](docs/04_HAND_CALCULATIONS.md).
4. Implement cost curves and allocation, followed by each payment rule.
5. Record decisions in [the research log](docs/05_RESEARCH_LOG.md) and AI support in [the AI-use log](docs/06_AI_USAGE.md).
6. Only after validation: run scarcity and concentration experiments.

## Main scientific reference

Heinrich, C. et al. *A Local Flexibility Market Mechanism with Capacity Limitation Services.* Energy Policy, 156, 112335. DOI: https://doi.org/10.1016/j.enpol.2021.112335.

Please verify the exact equations and any claims against the original publication before implementing or citing them. A public copy is linked from: https://orbit.dtu.dk/en/publications/a-local-flexibility-market-mechanism-with-capacity-limitation-ser/

## License and contribution policy

MIT License (see [LICENSE](LICENSE)). The repository is public for transparency and reproducibility. The owner retains write and merge control. Suggestions and forks do not imply permission to push to the default branch. The research model and implementation are incomplete.
