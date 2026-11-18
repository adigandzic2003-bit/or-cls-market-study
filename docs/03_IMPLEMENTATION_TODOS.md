# 03 | Detailed implementation plan (student-owned algorithms)

**Rule:** Do not jump to simulations. For each task, first understand the original equation, predict at least one numeric result without Python, implement it yourself and then enable its test. Use small commits and record important decisions.

## M0 | Environment and mathematical literacy

- [ ] **T00.1 Setup.** Clone the public repository, create a Python 3.11+ virtual environment, install `pip install -e '.[dev]'` and run `pytest -v`. Expect one smoke test to pass and the research tests to be skipped.
- [ ] **T00.2 Research purpose.** Explain in five of your own sentences what the DSO chooses, what an aggregator offers, what the optimization minimizes and what a monetary payment represents.
- [ ] **T00.3 Original equations.** Read Heinrich's allocation and mechanism sections. Copy the relevant equations into your own study notes, label every symbol and unit and identify which quantities are parameters or decision variables.
- [ ] **T00.4 Documentation.** Create your own first research-log entry and log the AI-generated initial architecture. Do not claim skipped tests validate the model.

**Acceptance:** You can verbally distinguish P_nom, P_lim, actual CLS cost, bid, payment and DSO costs.

## M1 | Data and cost curves

- [ ] **C01 Aggregator curve.** In `curves.py`, implement `linear_aggregator_cost`. First derive the relation between a reduction in the allowable cap and the extra contract cost. Check units, nonnegative parameters, the zero-cost nominal cap, and a tighter cap. Specify how invalid cap values are handled. Test at least three independent inputs.
- [ ] **C02 Toy DSO curve.** Choose a finite, nonnegative cost function of total contracted caps with an interpretable reference network limit. Write the exact formula and units into `docs/02_MODEL_SPEC.md`. Test below, at and above the limit. Explicitly label this an illustrative model rather than Heinrich's estimated probabilistic curve.
- [ ] **C03 Input validation.** Detect duplicate aggregator IDs, wrong bounds, negative nominal limits, nonfinite curve outputs and inconsistent allocation keys. Record why each invalid case should fail.

**Acceptance:** Your own table of input caps and EUR costs matches the implementation and all enabled curve tests pass.

## M2 | The allocation optimizer

- [ ] **A01 Objective.** Reconstruct the allocation criterion from Heinrich. The sum of reported aggregator costs and DSO cost is minimized; transfers should not enter this optimization.
- [ ] **A02 Variables.** Build a stable index mapping from aggregator IDs to a vector of decision variables. Every P_lim_j has its own [P_min_j, P_nom_j] interval.
- [ ] **A03 Algorithm choice.** Review SciPy `minimize`, bounds and solver status. Choose a numerical method appropriate to the chosen functions. Discuss corner solutions, potential non-differentiability and whether the objective is convex.
- [ ] **A04 Returned output.** Convert the numerical solution into `Allocation`. Verify status, bound feasibility and the objective independently rather than trusting a reported success flag alone.
- [ ] **A05 Counterfactuals.** For `fixed_nominal_ids`, fix the relevant variables at P_nom. They **remain** consumers within the DSO cost. Add a regression test specifically preventing the removed-load mistake.
- [ ] **A06 Hand verification.** Solve a one-aggregator and a two-aggregator case on paper, including a boundary optimum. Compare with the numerical optimizer and a small brute-force grid when feasible.
- [ ] **A07 Failure handling.** Choose deterministic tolerances, describe what happens for empty markets, malformed IDs or failed optimization, and show a helpful error message.

**Acceptance:** The chosen caps, objective and DSO cost match an independently computed benchmark.

## M3 | Payment mechanisms

- [ ] **P01 Pay-as-bid.** Re-read Heinrich Eq. (4). Implement the transfer using the **offer** curve at the allocated cap, not true_cost. Create a test where the two curves deliberately differ.
- [ ] **U01 Uniform pricing.** Read Heinrich Eq. (5) and surrounding text. Define the marginal unit and common clearing price. Check the sign when differentiating by P_lim versus tightened capacity. Handle equal marginal costs, non-differentiable costs and zero awarded CLS explicitly.
- [ ] **V01 Uni-sided VCG: repeat optimization.** For every aggregator j, solve with j's ability to offer CLS removed, meaning P_lim_j fixed at P_nom_j. Keep its physical load in the DSO function.
- [ ] **V02 Externality calculation.** Compute the change in the DSO costs and **other** aggregators' offered costs between original and counterfactual allocations. Do not subtract j's own bid in the other-actors cost.
- [ ] **V03 DSO financing.** Explain the difference between the aggregator-side VCG externality payment and the DSO's uni-sided financing obligation; compare with Heinrich Eq. (11).
- [ ] **V04 Edge cases.** Test ties, near-zero payments, infeasible hard constraints if separately used, extremely steep costs and optimizer failure. Do not silently insert arbitrary backstop penalties.
- [ ] **V05 Economic claims.** Make no blanket statement about truthfulness, budget balance or individual rationality without specifying the assumptions from the paper.

**Acceptance:** Three mechanisms produce understandable transfers on 2–3 provider toy cases and match your paper calculations.

## M4 | Evaluation metrics

- [ ] **M01 Procurement payments.** Sum transfers to aggregators in EUR.
- [ ] **M02 Actual CLS costs.** Evaluate true_cost for the chosen contractual cap.
- [ ] **M03 DSO operations.** Evaluate the DSO cost at the total selected caps.
- [ ] **M04 Real system costs.** Add actual CLS costs and DSO operating costs, **not** monetary payments.
- [ ] **M05 Profits and net benefit.** Compute each provider's payment minus actual cost and the DSO expense relative to a clearly defined no-CLS counterfactual.
- [ ] **M06 Efficiency.** Define a true-cost optimum benchmark and compare it with the offered-cost allocation. Explain your chosen efficiency metric and any solver tolerance.

**Acceptance:** Your accounting table demonstrates that cash transfers can differ significantly from actual social costs.

## M5 | Testing, replication and reproducibility

- [ ] **T01 Hand cases.** Create 3–5 complete test cases with input curves, bounds, optimum, cost breakdown and mechanism payments written down before testing.
- [ ] **T02 Independent expectations.** Replace skipped assertions with independently computed expected values; never turn on tests by merely accepting the program's outputs as expected values.
- [ ] **T03 Input and boundary testing.** Cover zero available flexibility, ties, identical bids, steep DSO penalties, tiny payment differences and failure states.
- [ ] **T04 Source comparison.** Contrast your results with Heinrich's theoretical/qualitative properties. If exact reported outcomes cannot be replicated using toy curves, state so rather than implying full replication.
- [ ] **T05 Release gate.** Only start the scenario sweep once allocation, payment and metrics tests are genuinely enabled and pass.

**Acceptance:** A reviewer can reproduce every reported figure from saved parameters and code.

## M6 | Controlled research extension (only after M5)

- [ ] **S01 Scarcity definition.** Specify whether scarcity is a benchmark requirement relative to total available contractual flexibility or a parameterization through the DSO cost function. Do not silently merge these frameworks.
- [ ] **S02 Matched scenarios.** Change the capacities of individual aggregators while holding the sum of available capacity and, as far as possible, the relevant cost parameters fixed.
- [ ] **S03 Concentration.** Describe how capacity shares change and which variables are controlled so observed effects can be associated with concentration rather than different cost curves.
- [ ] **S04 Loss of participation.** Re-solve the market when each aggregator in turn offers no CLS. Compare counterfactual objectives, VCG payments and DSO net benefit.
- [ ] **S05 Robustness.** Vary network limits, cost-curve slope, aggregator count and numerical tolerances in small, interpretable steps.
- [ ] **S06 Optional strategy.** If the timetable allows, use transparent, predeclared markup scenarios. Do NOT describe such scenarios as learned or Nash-equilibrium strategies.
- [ ] **S07 Outputs.** Save full scenario parameters, failures, caps, payments, true system costs and DSO benefit in readable files. Create plots only from validated runs.

**Acceptance:** A clearly labeled comparison supports one modest, defensible empirical conclusion.

## M7 | Scientific ownership

- [ ] **D01 Research log.** Record assumptions, what you derived, which algorithm you wrote, tests and open uncertainties.
- [ ] **D02 Source attribution.** Mark equations inherited from Heinrich separately from toy curves, new scenario design and numerical implementation.
- [ ] **D03 AI support.** Record use by category and specific accepted code suggestions if those occur. Initial skeleton and signatures were generated with ChatGPT.
- [ ] **D04 Explainability.** Be ready to derive the optimal allocation objective and one VCG payment on a whiteboard without the assistant.
- [ ] **D05 Paper structure.** Prepare Methods, Verification, Scenarios, Results, Discussion and Limitations, separating replication from extension.

## Work cycle for every numbered TODO

1. **Understand:** derive or paraphrase the relevant mathematical rule.
2. **Predict:** calculate at least one expected result with pen and paper.
3. **Implement:** write one small function and a corresponding active unit test.
4. **Review:** inspect bounds, signs, counterfactuals and numerical tolerances.
5. **Commit:** describe what YOU changed in Git and record any AI help.
