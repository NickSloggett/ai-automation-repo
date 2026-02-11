# Changelog

All notable changes to this repository are documented in this file.

## 2026-02-10

### Changed
- Enforced CI quality gates by making Ruff, format check, Bandit, MyPy, Pyright, pytest, and Safety blocking checks.
- Switched security/reporting-only jobs (Trivy and SBOM generation) to explicit informational status labeling.
- Updated OpenTelemetry dependency set to a resolver-compatible configuration and removed unused `autogen` dependency causing lock resolution conflicts.

### Added
- Committed `poetry.lock` for deterministic installs.
- Added root `.gitignore` to prevent cache/build/editor artifacts from being tracked.

### Removed
- Deleted tracked Python bytecode/cache artifacts from `src/__pycache__`.
- Disabled duplicate dependency automation by removing `.github/dependabot.yml` and keeping Renovate as the single updater policy.
