# Task Groups

## 1. Add CI checks workflow

Create `.github/workflows/ci.yml`:

- Trigger on `pull_request` targeting `main` and `push` to `main`
- Single job with steps:
  1. Checkout code
  2. Set up Python (matrix: 3.11, 3.12, 3.13)
  3. Install dev dependencies (`pip install -e ".[dev]"` + `ruff`, `bandit`, `pip-audit`)
  4. Lint: `ruff check src/ tests/`
  5. Format check: `ruff format --check src/ tests/`
  6. Security scan: `bandit -r src/`
  7. Dependency audit: `pip-audit`
  8. Tests: `pytest tests/ -v`
- Add `ruff` and `bandit` and `pip-audit` to `[project.optional-dependencies] dev`
  in `pyproject.toml`

## 2. Add publish workflow

Create `.github/workflows/publish.yml`:

- Trigger on `push` to tags matching `v*`
- Steps:
  1. Checkout code
  2. Set up Python 3.13
  3. Install `build` and `twine`
  4. Build: `python -m build`
  5. Check: `python -m twine check dist/*`
  6. Upload: `python -m twine upload dist/*` using `PYPI_API_TOKEN` from secrets
- Document that `PYPI_API_TOKEN` must be set in the repo's GitHub Actions secrets

## 3. Fix any lint/format/security findings

- Run `ruff check src/ tests/` locally and fix all findings
- Run `ruff format src/ tests/` to auto-format
- Run `bandit -r src/` and resolve any medium/high findings
- Run `pip-audit` and address any known vulnerabilities in dependencies

## 4. Add README badges

Add four shields.io badges to the top of `README.md`, just below the title:

- CI status: GitHub Actions workflow badge for `ci.yml` on `main`
- PyPI version: `https://img.shields.io/pypi/v/global-impact-tracker`
- Python versions: `https://img.shields.io/pypi/pyversions/global-impact-tracker`
- License: `https://img.shields.io/badge/license-Apache%202.0-blue`
