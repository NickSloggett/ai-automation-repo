# ai-automation-repo Upgrade Baseline (2026-Q1)

**Captured:** 2026-02-10

## Dependency State

- **Primary path:** Poetry (pyproject.toml)
- **Lockfile:** poetry.lock — **NOT COMMITTED** (must run `poetry lock` when Poetry available)
- **Python:** 3.11–3.13 per pyproject.toml

## CI State

- **Workflows:** `.github/workflows/ci.yml`, docs.yml, release.yml
- **Issues:**
  - Lint, format, bandit, mypy, pyright, pytest, safety, trivy, SBOM: all use `continue-on-error: true` — quality checks are advisory, not blocking
  - Cache key uses `hashFiles('**/poetry.lock')` — fails/invalid when no lockfile

## Hygiene

- **.gitignore:** Missing
- **Tracked cache:** `src/__pycache__/`, `src/agents/__pycache__/` (Python bytecode)

## Dependency Bots

- **Renovate:** renovate.json (primary, Poetry-aware)
- **Dependabot:** .github/dependabot.yml (pip ecosystem — duplicates Renovate)

## Test / Build

- **Tests:** pytest, coverage, matrix 3.11/3.12/3.13
- **Build:** poetry build, poetry check pass
- **Docker:** Multi-arch build (amd64 for CI)
