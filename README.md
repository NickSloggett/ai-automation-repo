# 🤖 AI Automation Boilerplate

> **Turnkey AI automation projects for immediate client implementation**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/your-username/ai-automation-boilerplate/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-username/ai-automation-boilerplate/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/your-username/ai-automation-boilerplate/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/ai-automation-boilerplate)
[![Documentation Status](https://readthedocs.org/projects/ai-automation-boilerplate/badge/?version=latest)](https://ai-automation-boilerplate.readthedocs.io/?badge=latest)

A comprehensive, production-ready boilerplate for AI automation projects featuring modular agents, workflow orchestration, vector stores, monitoring, and turnkey deployment configurations. Built with modern Python best practices and designed for rapid client onboarding.

## ✅ Implementation Status

**Core Infrastructure: 95% Complete**
- ✅ Configuration system with nested settings
- ✅ Database layer with async SQLAlchemy & Alembic migrations
- ✅ CLI with database management commands
- ✅ FastAPI application with health checks
- ✅ Comprehensive API routers (agents, workflows, tasks, monitoring)

**Agent System: 80% Complete**
- ✅ Base agent abstraction with retry & timeout
- ✅ Task agents with multi-step execution
- ✅ Decision agents for workflow logic
- ✅ Agent execution tracking & history
- ⏳ Tool registry enhancement (partial)

**Production Features: 90% Complete**
- ✅ Alembic database migrations
- ✅ Pre-commit hooks (Black, isort, Ruff, MyPy, Bandit)
- ✅ GitHub Actions CI/CD pipeline
- ✅ Docker multi-stage builds
- ✅ Structured logging & monitoring hooks
- ✅ Cost tracking system
- ⏳ Authentication & authorization (JWT structure ready)

**Integration Points: 70% Complete**
- ✅ LLM base abstractions (OpenAI, Anthropic, Groq, Local)
- ✅ Vector store base (in-memory implementation)
- ✅ Caching layer (Redis/in-memory)
- ✅ Secrets management (Vault, AWS, env)
- ⏳ Pinecone & Weaviate adapters (structure ready)

## 🚀 Features

### Core AI Automation
- **Modular Agent System**: Base agent classes with task and decision agents
- **Workflow Orchestration**: Multi-step automation with error handling and retries
- **Vector Store Integration**: Support for Pinecone, Weaviate, and in-memory storage
- **LLM Integration**: OpenAI, Anthropic, Groq, and local model support

### Enterprise-Ready
- **Comprehensive Monitoring**: Prometheus metrics, Sentry error tracking, structured logging
- **Security**: JWT authentication, Auth0 integration, environment-based configuration
- **Database Support**: SQLAlchemy with async support, Prisma ORM integration
- **API Framework**: FastAPI with automatic documentation and CORS support

### Developer Experience
- **Poetry Dependency Management**: Modern Python packaging with virtual environments
- **Pre-commit Hooks**: Black, Flake8, MyPy, and comprehensive linting
- **CI/CD Pipeline**: GitHub Actions with testing, coverage, and automated deployment
- **Docker & Kubernetes**: Containerization and orchestration support

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Configuration](#configuration)
- [Core Components](#core-components)
- [Examples](#examples)
- [Deployment](#deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Poetry (package manager)
- Git

### 1. Navigate to Package

```bash
cd packages/ai-automation
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Initialize Database

```bash
poetry run python -m src.cli db init
poetry run python -m src.cli db seed  # Optional: Add demo data
```

### 4. Start API Server

```bash
poetry run python -m src.cli serve
# Or directly with uvicorn:
# poetry run uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### 5. Explore API

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

### CLI Commands

```bash
# Database management
poetry run python -m src.cli db init       # Initialize database
poetry run python -m src.cli db migrate -m "message"  # Create migration
poetry run python -m src.cli db upgrade    # Apply migrations
poetry run python -m src.cli db seed       # Seed demo data
poetry run python -m src.cli db reset      # Reset database

# Server
poetry run python -m src.cli serve         # Start API server
poetry run python -m src.cli version       # Show version
```

## 🏗️ Architecture Overview

```
ai-automation-boilerplate/
├── src/                          # Core application code
│   ├── agents/                   # Agent implementations
│   │   ├── base.py              # Base agent class
│   │   ├── task.py              # Task-based agents
│   │   └── decision.py          # Decision-making agents
│   ├── config/                  # Configuration management
│   ├── database/                # Database connections
│   ├── logging/                 # Structured logging
│   ├── monitoring/              # Metrics and monitoring
│   ├── vector_store/            # Vector database integration
│   └── api.py                   # FastAPI application
├── tests/                       # Test suite
├── docs/                        # Documentation
├── examples/                    # Example workflows
├── config/                      # Configuration files
├── scripts/                     # Deployment scripts
├── .github/                     # GitHub Actions workflows
├── docker/                      # Docker configurations
├── k8s/                         # Kubernetes manifests
└── pyproject.toml              # Poetry configuration
```

## ⚙️ Configuration

### Environment Variables

Key configuration options (see `.env.example` for full list):

```bash
# Core Settings
ENVIRONMENT=development
DEBUG=true

# API Keys (Required for production)
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key

# Database
DATABASE_URL=sqlite:///./ai_automation.db

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_GATEWAY=your-prometheus-gateway
```

### Agent Configuration

```python
from src.agents.task import TaskAgent, TaskConfig

config = TaskConfig(
    name="my_task_agent",
    description="Custom automation task",
    max_retries=3,
    timeout=300,
    required_tools=["tool1", "tool2"]
)

agent = TaskAgent(config)
```

## 🧩 Core Components

### Agent System

#### Base Agent
All agents inherit from `BaseAgent` providing:
- Async execution with timeout handling
- Automatic retry logic with exponential backoff
- Structured logging and monitoring
- Input validation and error handling

#### Task Agent
For structured, multi-step automation tasks:
```python
from src.agents.task import TaskAgent, TaskConfig, TaskStep

class EmailProcessor(TaskAgent):
    async def _get_task_steps(self, input_data):
        return [
            TaskStep(
                name="parse_email",
                description="Parse email content",
                tool="email_parser",
                parameters={"email_id": input_data["email_id"]}
            ),
            TaskStep(
                name="categorize",
                description="Categorize email",
                tool="categorizer",
                parameters={"content": "{{parse_email.result.content}}"}
            )
        ]
```

#### Decision Agent
For intelligent decision-making workflows:
```python
from src.agents.decision import DecisionAgent, DecisionConfig

config = DecisionConfig(
    name="priority_decider",
    decision_criteria=["urgency", "impact", "resources"],
    confidence_threshold=0.8
)

agent = DecisionAgent(config)
```

### Vector Store Integration

```python
from src.vector_store import get_vector_store

vector_store = get_vector_store()

# Store documents
await vector_store.store_document(
    id="doc_001",
    content="Sample document content",
    metadata={"author": "John Doe", "category": "example"}
)

# Search for similar documents
results = await vector_store.search_similar("similar content query", limit=5)
```

### Monitoring & Logging

```python
from src.logging import get_logger, setup_logging
from src.monitoring import track_performance, track_agent_execution

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Track performance
@track_performance
async def my_function():
    return "result"

# Track agent executions
track_agent_execution("my_agent", success=True)
```

## 📚 Examples

### Email Processing Workflow
```bash
poetry run python examples/email_processing_workflow.py
```

### Social Media Bot
```bash
poetry run python examples/social_media_bot.py
```

### Report Generation
```bash
poetry run python examples/report_generator.py
```

### CRM Integration
```bash
poetry run python examples/crm_integration.py
```

## 🚢 Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Scale the deployment
kubectl scale deployment ai-automation --replicas=3
```

### Serverless (AWS Lambda)

```bash
# Deploy to AWS Lambda
./scripts/deploy_lambda.sh

# Update Lambda function
./scripts/update_lambda.sh
```

### Vercel/Netlify

```bash
# Deploy to Vercel
vercel --prod

# Deploy to Netlify
netlify deploy --prod --dir=.
```

## 📊 Monitoring & Observability

### Metrics
- **Prometheus**: `/metrics` endpoint for application metrics
- **Custom Metrics**: Agent executions, task durations, error rates
- **Grafana Dashboards**: Pre-configured dashboards included

### Logging
- **Structured JSON Logging**: Environment-aware log formatting
- **Log Aggregation**: Compatible with ELK stack, Splunk, etc.
- **Error Tracking**: Sentry integration for production error monitoring

### Health Checks
- **Readiness Probe**: `/health/ready`
- **Liveness Probe**: `/health/live`
- **Database Connectivity**: Automatic health checks

## 🛡️ Security

### Authentication
- **JWT Tokens**: Stateless authentication
- **Auth0 Integration**: Social login and SSO
- **API Key Management**: Secure key storage and rotation

### Compliance
- **GDPR Ready**: Data processing and retention controls
- **HIPAA Considerations**: PHI handling guidelines
- **Audit Logging**: Comprehensive audit trails

### Best Practices
- **Secret Management**: Environment variable encryption
- **Input Validation**: Pydantic model validation
- **Rate Limiting**: Built-in API rate limiting

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_agents.py

# Run with verbose output
poetry run pytest -v --tb=short
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install dependencies: `poetry install`
4. Make your changes
5. Run tests: `poetry run pytest`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style
- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting
- **Flake8**: Linting with bugbear, comprehensions, and simplify plugins
- **MyPy**: Type checking
- **Pre-commit**: Automated code quality checks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Poetry](https://python-poetry.org/) for dependency management
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Monitoring with [Prometheus](https://prometheus.io/) and [Sentry](https://sentry.io/)
- AI capabilities from [OpenAI](https://openai.com/), [Anthropic](https://anthropic.com/), and [LangChain](https://langchain.com/)

## 📞 Support

- **Documentation**: [https://ai-automation-boilerplate.readthedocs.io/](https://ai-automation-boilerplate.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/your-username/ai-automation-boilerplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-automation-boilerplate/discussions)

---

**Ready to automate?** This boilerplate provides everything you need to build and deploy AI automation solutions for your clients. Get started today! 🚀
