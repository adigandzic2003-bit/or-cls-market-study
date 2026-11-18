# 08 | GitHub and local development workflow

**Current repository:** https://github.com/adigandzic2003-bit/or-cls-market-study

**Visibility:** Public for reproducibility. The MIT license is at the repository root. Public visibility does **not** give strangers permission to push to your branches. Don't add collaborators unless you want them to have repository permissions.

## First-time local setup (macOS, Linux)

```bash
git clone https://github.com/adigandzic2003-bit/or-cls-market-study.git
cd or-cls-market-study
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -v
```

You may also use your existing Conda environment if Python is 3.11+; avoid installing dependencies in the wrong interpreter.

## Your contribution workflow

1. Read one TODO and the referenced equation.
2. Calculate expected values independently.
3. Write the implementation and activate its test.
4. Commit only the files relevant to that step.
5. Document assumptions and AI assistance.
6. Push your own commit to main.

Example commits:

```text
docs: derive model variables and edge cases
feat: implement student-defined cost curves
feat: implement CLS allocation solver
feat: implement pay as bid payments
feat: implement CLS uniform pricing
feat: implement uni sided VCG counterfactual
test: validate mechanisms with handwritten examples
feat: add controlled scarcity scenarios
```

No PR or self-review is required if you are the sole contributor and your branch rules allow your pushes.

## Important public-repository precautions

- Never commit tokens, passwords, private datasets, correspondence, identifiable participant data or API keys.
- Check file contents and notebook outputs before pushing.
- The MIT license allows others to reuse code subject to its terms, but does not grant them write access to your repository.
