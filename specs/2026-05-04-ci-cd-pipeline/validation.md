# Validation

## 1. CI workflow fires and passes

- Open a pull request targeting `main`; confirm the `ci` workflow appears in the
  PR checks and all steps pass (lint, format, security, audit, tests × 3 Python versions)
- Push directly to `main`; confirm the same workflow runs and passes
- Introduce a deliberate lint error on a branch; confirm CI fails on that step
  and the failure is clearly identified

## 2. Publish workflow fires on tag push

- Tag a commit: `git tag v0.1.1 && git push origin v0.1.1`
- Confirm the `publish` workflow triggers and completes successfully
- Confirm the new version appears on https://pypi.org/project/global-impact-tracker/
- Confirm `pip install global-impact-tracker==0.1.1` resolves in a clean virtualenv

## 3. Badges render correctly in README

- Open the public GitHub repo page; all four badges are visible below the title
- CI badge shows passing state on `main`
- PyPI version badge shows the current published version
- Python versions badge shows 3.11 | 3.12 | 3.13
- License badge shows Apache 2.0

## Definition of done

All three validation checks pass, the `PYPI_API_TOKEN` secret is set in GitHub
Actions, and no ruff/bandit/pip-audit findings remain unresolved in `src/`.
