# 🚀 Quick Start Guide - Ultra Modern AI Automation Repo

## ⚡ TL;DR - Get Started in 5 Minutes

### Option 1: Dev Container (Recommended)

```bash
# Open in VS Code
code ai-automation-repo

# Click "Reopen in Container" when prompted
# Wait 5 minutes for initial build
# Everything is ready! Start coding!
```

### Option 2: Local Development

```bash
# 1. Install Task runner
brew install go-task/tap/go-task  # macOS
# or visit https://taskfile.dev/installation/

# 2. Install dependencies
task install

# 3. Run quality checks
task check

# 4. Run tests
task test

# 5. Start development server
task serve:dev
```

---

## 📋 Essential Commands

### Development

```bash
task serve:dev         # Start API server with hot reload
task test              # Run all tests in parallel
task test:watch        # Run tests in watch mode (TDD)
task check             # Run all quality checks (lint + format + typecheck)
```

### Database

```bash
task db:init           # Initialize database
task db:migrate        # Create new migration
task db:upgrade        # Apply migrations
task db:seed           # Add demo data
```

### Quality & Security

```bash
task lint              # Run linter with auto-fix
task format            # Format code with Ruff
task typecheck         # Run MyPy + Pyright
task security          # Run all security scans
```

### Documentation

```bash
task docs:serve        # Serve docs at http://localhost:8000
task docs:build        # Build static site
task docs:deploy       # Deploy to GitHub Pages
```

### Profiling & Analysis

```bash
task profile:cpu       # Profile CPU usage (generates SVG)
task profile:memory    # Profile memory usage
task analyze:dead      # Find unused code
task analyze:complexity # Check code complexity
```

---

## 🎯 What's New?

### 1. **Taskfile** - One Command for Everything

No more remembering complex commands! Just use `task`:

```bash
task --list            # See all available commands
task <command>         # Run any command
```

### 2. **Dev Container** - Zero Setup Development

Open in VS Code → Click "Reopen in Container" → Start coding!

Includes:
- Python 3.13 + Poetry + UV
- PostgreSQL + Redis
- All VS Code extensions
- Pre-configured formatting and linting
- SSH keys and git config mounted

### 3. **Advanced Testing**

```bash
# Run specific test types
task test:unit         # Unit tests only
task test:integration  # Integration tests
task test:benchmark    # Performance benchmarks

# Tests now run in parallel (faster!)
# Tests run in random order (catches bugs!)
# Tests have automatic timeouts (no more hangs!)
```

### 4. **Auto-Generated Documentation**

```bash
task docs:serve
# Opens http://localhost:8000
# Beautiful Material Design theme
# Auto-generated API docs from your code
# Dark mode support
```

### 5. **Automated Security**

Every PR automatically gets:
- CodeQL security scan
- Dependency vulnerability check
- Trivy container scan
- Bandit Python security check

### 6. **Automated Dependency Updates**

Renovate Bot will:
- Check for updates every Monday morning
- Auto-merge minor/patch updates
- Group related packages together
- Alert immediately on security issues

---

## 🏗️ Project Structure

```
ai-automation-repo/
├── .devcontainer/          # Dev container configuration
│   ├── devcontainer.json   # VS Code settings
│   ├── docker-compose.yml  # PostgreSQL + Redis
│   └── Dockerfile          # Dev environment
├── .github/
│   ├── ISSUE_TEMPLATE/     # Bug & feature templates
│   ├── workflows/          # CI/CD pipelines
│   │   ├── ci.yml          # Main CI (10 jobs!)
│   │   ├── docs.yml        # Documentation deployment
│   │   └── release.yml     # Automated releases
│   ├── dependabot.yml      # Dependency updates
│   └── pull_request_template.md
├── docs/                   # MkDocs documentation
│   ├── index.md           # Homepage
│   ├── gen_ref_pages.py   # Auto-generate API docs
│   └── .../               # Guide sections
├── src/                   # Your application code
├── tests/                 # Test suite
├── mkdocs.yml            # Documentation config
├── renovate.json         # Renovate Bot config
├── Taskfile.yml          # Task definitions
├── pyproject.toml        # Python config (enhanced!)
└── ULTRA_MODERNIZATION_2025.md  # Full details
```

---

## 🧪 Testing Best Practices

### Test Markers

```python
import pytest

@pytest.mark.unit
def test_something():
    """Fast unit test"""
    pass

@pytest.mark.integration
def test_integration():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Long-running test"""
    pass

@pytest.mark.benchmark
def test_performance(benchmark):
    """Performance benchmark"""
    result = benchmark(my_function)
```

### Running Tests

```bash
# Run all tests
task test

# Run only unit tests
task test:unit

# Run without slow tests
poetry run pytest -m "not slow"

# Run with coverage
task test:cov

# Run benchmarks only
task test:benchmark
```

---

## 🔒 Security Checklist

Before every release, run:

```bash
task security          # Runs all security checks

# Includes:
# ✓ Bandit (Python security linting)
# ✓ Safety (known vulnerabilities)
# ✓ pip-audit (dependency auditing)
```

CI automatically runs:
- CodeQL (advanced static analysis)
- Trivy (vulnerability scanning)
- Dependency review (on PRs)

---

## 📊 CI/CD Pipeline

### On Every Push

1. **Lint & Format Check** - Ruff + Bandit
2. **Type Checking** - MyPy + Pyright
3. **Tests** - Python 3.11, 3.12, 3.13
4. **Security** - Safety + Trivy
5. **Build Check** - Poetry build
6. **Docker Build** - Multi-arch (AMD64/ARM64)
7. **CodeQL** - Security analysis
8. **SBOM** - Supply chain transparency
9. **Dependency Review** - On PRs only

### On Version Tag

1. Build distribution packages
2. Generate SBOM
3. Create GitHub Release
4. Build multi-arch Docker images
5. Push to GitHub Container Registry

---

## 🐳 Docker Commands

### Development

```bash
task docker:build      # Build image
task docker:run        # Run container
task docker:compose:up # Start all services
```

### Production

```bash
# Build multi-arch image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ai-automation:latest \
  .
```

---

## 📚 Documentation

### Local Development

```bash
# Serve docs locally
task docs:serve

# Opens at http://localhost:8000
# Auto-reloads on changes
```

### Deployment

```bash
# Deploy to GitHub Pages
task docs:deploy

# Accessible at:
# https://nicksloggett.github.io/ai-automation-repo/
```

### Auto-Generated API Docs

API documentation is automatically generated from your Python docstrings using Google-style format:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.

    Longer description with more details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Examples:
        >>> my_function("test", 42)
        True
    """
    pass
```

---

## 🎨 Code Style

### Automatic Formatting

Code is automatically formatted on save in VS Code. You can also run:

```bash
task format            # Format all files
task format:check      # Check without formatting
```

### Linting

```bash
task lint              # Lint and auto-fix
task lint:ruff         # Ruff only
task lint:bandit       # Security linting
```

### Type Checking

```bash
task typecheck         # Run both
task typecheck:mypy    # MyPy only
task typecheck:pyright # Pyright only
```

---

## 🔧 Troubleshooting

### Dev Container Issues

**Container fails to build:**
```bash
# Rebuild without cache
Cmd/Ctrl + Shift + P → "Dev Containers: Rebuild Container"
```

**Extensions not working:**
```bash
# Reload window
Cmd/Ctrl + Shift + P → "Developer: Reload Window"
```

### Task Issues

**Task not found:**
```bash
# Update Task to latest version
brew upgrade go-task/tap/go-task

# Or reinstall
brew uninstall go-task && brew install go-task/tap/go-task
```

### Poetry Issues

**Lock file out of sync:**
```bash
poetry lock --no-update
```

**Dependencies conflict:**
```bash
poetry update
```

---

## 📞 Getting Help

1. **Documentation**: [Full docs](https://nicksloggett.github.io/ai-automation-repo/)
2. **Issues**: [GitHub Issues](https://github.com/NickSloggett/ai-automation-repo/issues)
3. **Discussions**: [GitHub Discussions](https://github.com/NickSloggett/ai-automation-repo/discussions)
4. **Task Help**: `task --help`

---

## ✨ Pro Tips

1. **Use the dev container** - Best experience, everything pre-configured
2. **Run `task --list`** - See all available commands
3. **Use test markers** - Run only the tests you need
4. **Enable auto-save** - Code formats automatically
5. **Use `task ci`** - Run full CI pipeline locally before pushing
6. **Profile regularly** - `task profile:cpu` to find bottlenecks
7. **Check complexity** - `task analyze:complexity` to maintain quality
8. **Update deps** - Renovate Bot handles it, just review PRs

---

## 🎯 Next Steps

1. ✅ Set up dev container or install Task
2. ✅ Run `task install` to install dependencies
3. ✅ Run `task check` to verify everything works
4. ✅ Run `task test` to run the test suite
5. ✅ Run `task serve:dev` to start development
6. ✅ Browse docs at `http://localhost:8000` (after `task docs:serve`)
7. ✅ Read `ULTRA_MODERNIZATION_2025.md` for full details

**Happy coding! 🚀**
