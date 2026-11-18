# 07 | Requirements and acceptance evidence

This page maps the current research roadmap to source files and validation activities. It is NOT a substitute for official grading criteria; update after checking seminar instructions.

| Intended seminar requirement | Repo area | Evidence before completion |
|---|---|---|
| Reconstruct Heinrich CLS allocation | src/cls_market/allocation.py | Mathematical explanation and manually checked solver examples |
| Implement PAB, UP and uni-sided VCG independently | src/cls_market/mechanisms/ | Original-equation derivations and activated numeric tests |
| Model real costs versus bids and monetary transfers | models.py; metrics.py | Accounting checks with known numbers |
| Investigate counterfactual market absence | allocation.py; uni_sided_vcg.py | Test that absent CLS provider's physical load remains in network |
| Validate small cases | tests/; docs/04_HAND_CALCULATIONS.md | Independent hand calculations before assertions |
| Research extension and robustness | scenarios.py; experiments.py | Controlled scenario inputs and comparable costs |
| Reproducibility and scientific transparency | README; docs/05_RESEARCH_LOG.md | Explicit parameters, seed, data provenance and uncertainty |
| Document AI support | docs/06_AI_USAGE.md | Actual contributions and independent checking recorded |
| Paper and presentation | outside this package | Later written outputs and defense |

## Suggested checkpoints (not official deadlines)

- Late November: mathematical model and validated toy implementations.
- December: controlled stress tests and first figures.
- January: robustness, interpretation, seminar paper and presentation.

**Scope note:** The original roadmap included strategic markups as a potential extension. The current priority is the verified Heinrich baseline and its limits; strategic behavior is optional.
