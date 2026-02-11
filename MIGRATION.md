# Migration Notes

This document is the canonical migration guide for operational and tooling transitions in this repository.

## 2026-Q1 Reliability Migration

### What changed
- Dependency installs are now lockfile-driven (`poetry.lock` committed).
- CI quality checks are enforced as hard gates on pull requests.
- Renovate is the only active dependency updater.

### What contributors need to do
- Recreate local environments after pulling:
  - `poetry install --no-interaction`
- Run the full local quality gate before opening PRs:
  - `poetry run ruff check .`
  - `poetry run ruff format --check .`
  - `poetry run mypy src --ignore-missing-imports`
  - `poetry run pyright src`
  - `poetry run pytest`

### Archived modernization docs
Historical transformation notes are retained for reference only:
- `UPDATED_README.md`
- `ULTRA_MODERNIZATION_2025.md`
- `TRANSFORMATION_COMPLETE.md`
