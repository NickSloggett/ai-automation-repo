# 🤝 Contributing to AI Automation Boilerplate

Thank you for your interest in contributing to the AI Automation Boilerplate! This document provides guidelines for contributing to this project.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community Guidelines](#community-guidelines)

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Poetry** (for dependency management)
- **Git** (for version control)
- **Docker** (optional, for containerized development)

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ai-automation-boilerplate.git
   cd ai-automation-boilerplate
   ```
3. **Install dependencies**:
   ```bash
   poetry install
   ```
4. **Set up pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```
5. **Create a virtual environment** (optional):
   ```bash
   poetry shell
   ```

### Verify Setup

```bash
# Run tests
poetry run pytest

# Check code formatting
poetry run black --check src/
poetry run isort --check-only src/
poetry run flake8 src/

# Type checking
poetry run mypy src/
```

## 🔄 Development Process

### Branch Strategy

We follow a **feature-branch workflow**:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features or enhancements
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes for production

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write code** following our [Code Standards](#code-standards)
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Run the full test suite**:
   ```bash
   poetry run pytest --cov=src
   ```

### Committing Changes

We follow [Conventional Commits](https://conventionalcommits.org/) format:

```bash
# Feature commits
git commit -m "feat: add new agent type for X"

# Bug fixes
git commit -m "fix: resolve issue with Y"

# Documentation
git commit -m "docs: update README with new examples"

# Refactoring
git commit -m "refactor: improve agent error handling"
```

## 📝 Code Standards

### Python Style Guide

- **PEP 8**: Follow Python Enhancement Proposal 8
- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting and organization
- **Type Hints**: Use comprehensive type annotations
- **Docstrings**: Google-style docstrings for all public functions

### Code Quality Tools

```bash
# Format code
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Lint code
poetry run flake8 src/ tests/

# Type check
poetry run mypy src/

# Security scan
poetry run bandit -r src/
```

### Best Practices

#### Agent Development
```python
from typing import Dict, Any, Optional
from pydantic import BaseModel
from src.agents.base import BaseAgent, AgentConfig, AgentResult

class MyAgent(BaseAgent):
    """Custom agent implementation."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Custom initialization

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main logic."""
        # Implementation here
        pass
```

#### Error Handling
```python
import structlog

logger = structlog.get_logger(__name__)

try:
    result = await some_async_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        operation="some_async_operation",
        error=str(e),
        exc_info=True
    )
    raise
```

#### Configuration
```python
from pydantic import BaseSettings, Field

class MySettings(BaseSettings):
    """Configuration for my component."""

    api_key: str = Field(..., env="MY_API_KEY")
    timeout: int = Field(default=30, env="MY_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False
```

## 🧪 Testing Guidelines

### Testing Philosophy

- **Test-Driven Development (TDD)**: Write tests before implementation
- **Comprehensive Coverage**: Aim for >90% test coverage
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Test Structure

```
tests/
├── test_agents/
│   ├── test_base.py        # Base agent tests
│   ├── test_task.py        # Task agent tests
│   └── test_decision.py    # Decision agent tests
├── test_config/
│   └── test_settings.py    # Configuration tests
├── test_database/
│   └── test_connection.py  # Database tests
├── test_integration/
│   └── test_workflows.py   # Workflow integration tests
└── test_performance/
    └── test_scaling.py     # Performance tests
```

### Writing Tests

```python
import pytest
from src.agents.task import TaskAgent, TaskConfig

class TestMyAgent:
    """Test cases for MyAgent."""

    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        config = TaskConfig(
            name="test_agent",
            description="Test agent",
            max_retries=1,
            timeout=10
        )
        return TaskAgent(config)

    @pytest.mark.asyncio
    async def test_agent_execution_success(self, agent):
        """Test successful agent execution."""
        input_data = {"test": "data"}
        result = await agent.execute(input_data)

        assert result.success is True
        assert "data" in result.data

    @pytest.mark.asyncio
    async def test_agent_execution_failure(self, agent):
        """Test agent execution failure."""
        input_data = {"invalid": "data"}
        result = await agent.execute(input_data)

        assert result.success is False
        assert result.error is not None
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_agents/test_task.py

# Run with verbose output
poetry run pytest -v --tb=short

# Run performance tests
poetry run pytest tests/test_performance/ -m performance
```

## 📚 Documentation

### Documentation Structure

```
docs/
├── api/                    # API documentation
├── guides/                 # User guides
│   ├── quickstart.md      # Quick start guide
│   ├── deployment.md      # Deployment guide
│   └── customization.md   # Customization guide
├── examples/              # Code examples
└── reference/             # API reference
```

### Writing Documentation

- **Clear and Concise**: Use simple language
- **Code Examples**: Include practical examples
- **Screenshots**: Add visuals where helpful
- **Cross-References**: Link related sections

### Building Documentation

```bash
# Install documentation dependencies
poetry install --with docs

# Build HTML documentation
poetry run sphinx-build docs/ docs/_build/html

# Serve documentation locally
poetry run sphinx-autobuild docs/ docs/_build/html
```

## 🔄 Submitting Changes

### Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. **Run tests**:
   ```bash
   poetry run pytest --cov=src
   ```

3. **Check code quality**:
   ```bash
   poetry run pre-commit run --all-files
   ```

4. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

### Pull Request Requirements

- **Clear Title**: Use conventional commit format
- **Detailed Description**: Explain what and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs if needed
- **Breaking Changes**: Clearly mark breaking changes

### Review Process

- **Automated Checks**: CI/CD pipeline runs automatically
- **Code Review**: Maintainers review changes
- **Approval**: Requires maintainer approval
- **Merge**: Squash and merge to maintain clean history

## 🏗️ Community Guidelines

### Communication

- **GitHub Issues**: Use for bug reports and feature requests
- **GitHub Discussions**: Use for questions and discussions
- **Discord**: Join our community chat
- **Email**: Contact maintainers for private matters

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.

### Recognition

Contributors are recognized through:
- **GitHub Contributors** page
- **Release Notes** mentions
- **Community Spotlights** in our newsletter

## 🛠️ Development Tools

### Essential Tools

- **Poetry**: Dependency management
- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **MyPy**: Type checking
- **pytest**: Testing framework

### Optional Tools

- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Sentry**: Error monitoring
- **Grafana**: Metrics visualization
- **Jupyter**: Interactive development

### IDE Configuration

#### VS Code
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## 🔍 Debugging

### Common Issues

1. **Import Errors**: Check virtual environment activation
2. **Type Errors**: Run MyPy for detailed type checking
3. **Test Failures**: Use `-v --tb=short` for detailed output
4. **Performance Issues**: Use profiling tools

### Debugging Tools

```python
# Add debug logging
logger = structlog.get_logger(__name__)
logger.debug("Debug information", key=value)

# Use Python debugger
import pdb; pdb.set_trace()

# Profile performance
import cProfile
cProfile.run('main()')
```

## 📈 Performance Guidelines

### Benchmarks

- **Startup Time**: < 5 seconds
- **Memory Usage**: < 100MB baseline
- **Response Time**: < 1 second for API endpoints
- **Throughput**: > 100 requests/second

### Optimization Tips

1. **Async/Await**: Use async programming for I/O operations
2. **Caching**: Implement appropriate caching strategies
3. **Database**: Use connection pooling and prepared statements
4. **Monitoring**: Track performance metrics continuously

## 🎯 Project Roadmap

### Current Priorities

- [ ] Enhanced agent templates
- [ ] Improved error handling
- [ ] Better documentation
- [ ] Performance optimizations

### Future Enhancements

- [ ] Plugin system for custom tools
- [ ] Multi-language support
- [ ] Advanced monitoring dashboards
- [ ] Mobile app integration

---

Thank you for contributing to the AI Automation Boilerplate! Your contributions help make this project better for everyone. 🚀
