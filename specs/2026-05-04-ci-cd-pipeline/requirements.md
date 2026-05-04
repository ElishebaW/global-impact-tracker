# Requirements

## Goal

Add a GitHub Actions CI pipeline that enforces code quality and security on every
PR and push to main, and a separate publish workflow that uploads to PyPI on a
version tag push. Add badges to the README reflecting live CI and package status.

## Current state

- No CI pipeline exists; quality checks and publishing are manual
- `ruff`, `bandit`, and `pip-audit` are not installed or enforced
- PyPI publish is done manually via `twine upload`
- README has no status badges

## Decisions

- **CI triggers: PR + push to main.** Every pull request and every push to main
  runs the full check suite. Pushes to feature branches are not checked by CI —
  that would be covered if/when branch protection is added.
- **Publish trigger: tag push matching `v*`.** Pushing a tag like `v0.2.0`
  automatically builds and uploads to PyPI. No manual dispatch step required for
  normal releases.
- **Test matrix: Python 3.11, 3.12, 3.13.** Matches the classifiers in
  `pyproject.toml` and the `requires-python = ">=3.11"` constraint.
- **Four check steps in CI:** lint (`ruff`), format (`ruff format --check`),
  security (`bandit`), dependency audit (`pip-audit`). Each runs as a separate
  step within one job so failures are individually identifiable.
- **`PYPI_API_TOKEN` stored as a GitHub Actions secret.** The publish workflow
  reads it from `secrets.PYPI_API_TOKEN` and passes it to twine via env var.
- **Four badges in README:** CI status, PyPI version, Python versions, License
  (Apache 2.0). All sourced from shields.io or the GitHub Actions badge URL.
- **No TestPyPI step in the publish workflow.** TestPyPI was the manual
  validation gate for v0.1.0. Automated publish goes straight to PyPI on tag;
  pre-release validation is the responsibility of the CI checks and a local
  `twine check dist/*` before tagging.

## Out of scope

- Branch protection rules (GitHub settings, not code)
- Code coverage reporting or coverage badge
- Docker or containerized test environments
- Deployment beyond PyPI (no hosted service in this phase)
- Gemini proxy or any MCP server changes
