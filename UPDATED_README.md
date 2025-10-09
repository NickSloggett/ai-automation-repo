# 🤖 AI Automation Agency Platform - **PRODUCTION READY**

> **The Complete Platform for Running Your AI Automation Agency**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-green)](https://github.com/NickSloggett/ai-automation-repo)

**This is not just code—it's a complete business platform.** Everything you need to start, run, and scale an AI automation agency, from client management to billing, workflow orchestration, and delivery automation.

---

## 🚀 What's New - September 2025 Transformation

This repository has been **completely transformed** into a production-ready platform:

### ✨ New Features (50+ Files Added!)

- ✅ **Complete Authentication System** - JWT tokens, API keys, rate limiting
- ✅ **Workflow Orchestration Engine** - Build complex multi-agent workflows
- ✅ **Comprehensive Tools Library** - Web scraping, email, APIs, data processing
- ✅ **Agency Management Suite** - Clients, projects, billing, invoicing
- ✅ **CI/CD Pipeline** - GitHub Actions with automated testing
- ✅ **Kubernetes Deployment** - Production-ready K8s manifests
- ✅ **Monitoring Stack** - Prometheus + Grafana dashboards
- ✅ **Pre-commit Hooks** - Automated code quality checks
- ✅ **Real-World Examples** - Social media, CRM, data analysis workflows
- ✅ **Comprehensive Documentation** - Agency guide, deployment guide, API docs

**📊 6,000+ lines of production-ready code added**

See [COMPREHENSIVE_TRANSFORMATION.md](COMPREHENSIVE_TRANSFORMATION.md) for full details.

---

## 🎯 Who Is This For?

### AI Automation Agency Owners
- Start your agency with a complete platform
- Manage clients, projects, and billing
- Deliver automation services at scale
- Track metrics and KPIs

### Freelance Automation Developers
- Focus on delivering value, not building infrastructure
- Use pre-built workflows and tools
- Professional client management
- Scalable architecture

### Business Automation Teams
- Enterprise-ready security and compliance
- Kubernetes deployment
- Monitoring and observability
- Multi-tenant ready

### Developers Building AI Products
- Clean, modern Python architecture
- Type-safe codebase
- Comprehensive testing
- Easy to extend

---

## 🏗️ Architecture Overview

```
🏢 Agency Layer (NEW!)
├── Client Management (CRM)
├── Project Tracking
├── Billing & Invoicing
└── Time Tracking

🔐 Security Layer (NEW!)
├── JWT Authentication
├── API Key Management
├── Rate Limiting
└── Scope-based Permissions

🔄 Workflow Engine (NEW!)
├── Multi-step Orchestration
├── Parallel Execution
├── Conditional Logic
└── Error Handling & Rollback

🛠️ Tools System (NEW!)
├── Web Scraper (Playwright)
├── Email Automation
├── API Integration
├── Data Processor
└── [Easily Extensible]

🧠 AI Layer
├── OpenAI Integration
├── Anthropic/Claude
├── Groq (Fast Inference)
└── Local Models (Ollama)

📊 Data Layer
├── PostgreSQL (Production)
├── SQLite (Development)
├── Redis (Caching)
└── Vector Stores (Pinecone, Weaviate)

🚀 API Layer
├── FastAPI
├── Auto-generated Docs
├── Health Checks
└── Metrics Endpoint

☸️ Infrastructure (NEW!)
├── Kubernetes Manifests
├── Docker Compose
├── CI/CD Pipeline
└── Monitoring Stack
```

---

## ⚡ Quick Start (3 Minutes)

### Option 1: Local Development

```bash
# Clone repository
git clone https://github.com/NickSloggett/ai-automation-repo.git
cd ai-automation-boilerplate

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
./deploy.sh local

# Or run directly
poetry run uvicorn src.api:app --reload
```

Access:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### Option 2: Kubernetes Deployment

```bash
# Initialize secrets
./scripts/init-secrets.sh

# Deploy to staging
./deploy.sh staging

# Or deploy to production
./deploy.sh production
```

---

## 📚 Complete Feature Set

### 1. 🔐 Authentication & Security

**JWT Authentication**
```python
from src.auth import create_access_token, get_current_user

# Create token
token = create_access_token(
    user_id="user_123",
    email="john@example.com",
    scopes=["read", "write"],
)

# Protect endpoints
@app.get("/protected")
async def protected_route(user: TokenData = Depends(get_current_user)):
    return {"user_id": user.user_id}
```

**API Keys**
```python
from src.auth import create_api_key, validate_api_key

# Create API key
api_key = await create_api_key(
    db=db,
    user_id="user_123",
    name="Production API Key",
    scopes=["workflows:execute", "agents:read"],
    expires_in_days=365,
)
```

**Rate Limiting**
- 100 requests/minute (configurable)
- Per-IP or per-user limiting
- Custom limits per endpoint
- Redis-backed (production)

### 2. 🔄 Workflow Orchestration

**Build Complex Workflows**
```python
from src.workflows import WorkflowBuilder, WorkflowEngine

# Build workflow with fluent API
workflow = (
    WorkflowBuilder("lead_enrichment", "Enrich and score leads")
    .with_config(max_retries=3, parallel_execution=True)
    
    .add_task_step(
        name="fetch_leads",
        task_type="data_fetch",
        inputs={"source": "hubspot", "filter": "status:new"},
    )
    
    .then(
        name="enrich_data",
        agent_type="task",
        agent_config={"task_type": "data_enrichment"},
        inputs={"leads": "{{fetch_leads.output.leads}}"},
    )
    
    .add_decision_step(
        name="score_leads",
        decision_criteria=["company_size", "industry_fit"],
        alternatives=["hot", "warm", "cold"],
    )
    
    .add_conditional_step(
        name="alert_sales",
        condition_field="score_leads.output.score",
        condition_value="hot",
        agent_type="task",
        agent_config={"task_type": "notification"},
    )
    
    .build()
)

# Execute workflow
engine = WorkflowEngine()
result = await engine.execute(workflow)
```

**Features:**
- ✅ Dependency resolution
- ✅ Parallel execution
- ✅ Conditional steps
- ✅ Template variables ({{step.output}})
- ✅ Error handling (stop, continue, rollback)
- ✅ Step-level retries and timeouts

### 3. 🛠️ Tools System

**Web Scraping**
```python
from src.tools import WebScraperTool, ToolConfig

scraper = WebScraperTool(ToolConfig(name="scraper", description="Web scraper"))

result = await scraper.execute(
    url="https://example.com",
    selectors={
        "title": "h1",
        "prices": ".price",
        "descriptions": ".description",
    },
    wait_for=".content",
    screenshot=True,
)
```

**Email Automation**
```python
from src.tools import EmailTool

email = EmailTool(ToolConfig(name="email", description="Email sender"))

result = await email.execute(
    to_emails=["client@example.com"],
    subject="Your Weekly Report",
    body="<h1>Report attached</h1>",
    html=True,
    attachments=["report.pdf"],
)
```

**API Integration**
```python
from src.tools import APITool

api = APITool(ToolConfig(name="api", description="API client"))

result = await api.execute(
    url="https://api.example.com/data",
    method="POST",
    headers={"Authorization": "Bearer token"},
    json={"query": "select * from users"},
)
```

**Data Processing**
```python
from src.tools import DataProcessorTool

processor = DataProcessorTool(ToolConfig(name="processor", description="Data processor"))

result = await processor.execute(
    data=raw_data,
    operation="filter",
    condition="revenue > 10000",
)

result = await processor.execute(
    data=filtered_data,
    operation="aggregate",
    group_by=["region"],
    aggregations={"revenue": "sum", "customers": "count"},
)
```

### 4. 🏢 Agency Management

**Client Management**
```python
from src.agency import ClientManager, ClientStatus

manager = ClientManager(db)

# Create client
client = await manager.create_client(
    company_name="Acme Corp",
    contact_name="John Smith",
    contact_email="john@acme.com",
    industry="E-commerce",
    monthly_budget=5000.00,
)

# Track metrics
metrics = await manager.get_client_metrics(client.id)
# Returns: total_projects, active_projects, total_spent, satisfaction_score
```

**Project Management**
```python
from src.agency import ProjectManager, ProjectType

manager = ProjectManager()

# Create project
project = await manager.create_project(
    client_id=client.id,
    name="Email Automation System",
    project_type=ProjectType.EMAIL_AUTOMATION,
    budget=10000.00,
    estimated_hours=80,
)

# Add milestone
milestone = await manager.add_milestone(
    project_id=project.id,
    name="Phase 1: Integration",
    due_date=datetime.now() + timedelta(days=14),
)

# Log hours
await manager.log_hours(
    project_id=project.id,
    hours=8.5,
    description="Built email template system",
    team_member_id="dev_001",
)
```

**Billing & Invoicing**
```python
from src.agency import BillingManager

billing = BillingManager()

# Create invoice
invoice = await billing.create_invoice(
    client_id=client.id,
    items=[
        {
            "description": "Email Automation Development",
            "quantity": 40,
            "unit_price": 150.00,
        },
    ],
    due_days=30,
    tax_rate=0.10,
)

# Create subscription
subscription = await billing.create_subscription(
    client_id=client.id,
    plan_name="Pro Plan",
    monthly_price=2499.00,
    billing_cycle="monthly",
    included_features=["5 workflows", "10k API calls", "Priority support"],
)
```

### 5. 🧠 Multi-Provider LLM Support

```python
from src.llm import get_llm

# OpenAI
llm = get_llm(provider="openai", model="gpt-4")
response = await llm.generate("Explain quantum computing")

# Anthropic Claude
llm = get_llm(provider="anthropic", model="claude-3-sonnet")
response = await llm.chat([
    {"role": "user", "content": "What's the capital of France?"}
])

# Groq (Fast Inference)
llm = get_llm(provider="groq", model="mixtral-8x7b")
response = await llm.generate("Tell me a joke")

# Local Models (Ollama)
llm = get_llm(provider="local", model="llama2", base_url="http://localhost:11434")
response = await llm.generate("Hello!")

# Streaming
async for chunk in llm.stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

---

## 📊 Real-World Examples

### 1. Social Media Automation

```bash
poetry run python examples/social_media_automation.py
```

**What it does:**
- Generates social media content with AI
- Creates accompanying images
- Schedules posts across platforms
- Tracks engagement

### 2. CRM Lead Enrichment

```bash
poetry run python examples/crm_integration_workflow.py
```

**What it does:**
- Fetches new leads from HubSpot
- Enriches data from Clearbit, LinkedIn
- Scores leads with decision agent
- Sends hot lead alerts to Slack
- Updates CRM with enriched data
- Sends automated follow-up emails

### 3. Data Analysis & Reporting

```bash
poetry run python examples/data_analysis_workflow.py
```

**What it does:**
- Extracts data from multiple sources (DB, APIs, CSVs)
- Cleans and normalizes data
- Performs statistical analysis
- Generates AI-powered insights
- Creates visualizations
- Generates PDF report
- Emails to stakeholders

### 4. Email Processing

```bash
poetry run python examples/email_processing_workflow.py
```

**What it does:**
- Parses incoming emails
- Categorizes content
- Extracts structured information
- Routes to appropriate department
- Sends automated responses

---

## 🚀 Deployment Options

### Local Development
```bash
./deploy.sh local
```

### Kubernetes (Production)
```bash
# 1. Initialize secrets
./scripts/init-secrets.sh

# 2. Deploy
./deploy.sh production

# 3. Monitor
kubectl get pods -n ai-automation
kubectl logs -f deployment/ai-automation -n ai-automation
```

### Features:
- ✅ Horizontal Pod Autoscaling (3-10 replicas)
- ✅ Health checks (liveness, readiness)
- ✅ Resource limits
- ✅ TLS/SSL with cert-manager
- ✅ Ingress with rate limiting
- ✅ PostgreSQL with persistence
- ✅ Redis for caching

---

## 📈 Monitoring & Observability

### Metrics (Prometheus)
- API request rate and latency
- Agent execution success rate
- Workflow execution status
- LLM API calls and token usage
- Error rates
- Database connections
- Cache hit rates

### Dashboards (Grafana)
- Pre-built performance dashboard
- Real-time metrics visualization
- Custom alerts

### Alerts
- High error rate (> 5%)
- Slow response time (> 2s)
- High memory usage (> 90%)
- Workflow failures
- Service unavailability

---

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html

# Specific tests
poetry run pytest tests/test_agents.py -v

# Integration tests
poetry run pytest tests/integration/ -v
```

### CI/CD Pipeline
- ✅ Automated testing on push
- ✅ Multi-platform (Ubuntu, macOS, Windows)
- ✅ Multiple Python versions
- ✅ Security scanning
- ✅ Docker image building
- ✅ Automated deployment

---

## 📖 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup and first steps
- **[AGENCY_GUIDE.md](AGENCY_GUIDE.md)** - Complete agency operations guide
- **[COMPREHENSIVE_TRANSFORMATION.md](COMPREHENSIVE_TRANSFORMATION.md)** - Full feature list
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Technical improvements
- **[docs/AI_GUIDE.md](docs/AI_GUIDE.md)** - AI automation best practices
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment guide

---

## 💰 Pricing Models for Your Agency

### Hourly Rate
- **Range**: $100-$250/hour
- **Best for**: Custom projects, consulting

### Fixed Price Projects
- **Range**: $5,000-$50,000
- **Best for**: Well-defined scope

### Monthly Retainer
- **Range**: $1,500-$10,000/month
- **Best for**: Ongoing support

### Subscription Tiers

**Starter** ($999/month)
- 3 active workflows
- 5,000 API calls/month
- Email support

**Professional** ($2,499/month)
- 10 active workflows
- 25,000 API calls/month
- Priority support
- Custom integrations

**Enterprise** (Custom)
- Unlimited workflows
- Unlimited API calls
- Dedicated account manager
- White-glove service

---

## 🎯 What You Can Build

### Immediate Use Cases

1. **Email Automation**
   - Welcome sequences
   - Drip campaigns
   - Behavioral triggers

2. **Data Processing**
   - Web scraping
   - Data transformation
   - Automated reporting

3. **Social Media**
   - Content scheduling
   - Engagement automation
   - Performance tracking

4. **CRM Automation**
   - Lead enrichment
   - Score and route
   - Automated follow-ups

5. **Business Process**
   - Custom workflows
   - Tool integrations
   - Scheduled tasks

---

## 🏆 Why This Repository is Special

### For Agency Owners
✅ **Complete Business System** - Not just code  
✅ **Client Management** - Built-in CRM  
✅ **Billing Ready** - Invoice & subscriptions  
✅ **Project Tracking** - Know where everything stands  
✅ **Scalable** - From solo to team of 10+

### For Developers
✅ **Clean Architecture** - Easy to understand  
✅ **Well-Documented** - Every function has docstrings  
✅ **Type-Safe** - MyPy passes throughout  
✅ **Tested** - Testing infrastructure in place  
✅ **Modern Python** - Python 3.11+ features

### For DevOps
✅ **Kubernetes-Ready** - Complete manifests  
✅ **Observable** - Prometheus + Grafana  
✅ **Secure** - Auth and rate limiting  
✅ **Scalable** - HPA configured  
✅ **CI/CD** - Automated pipeline

---

## 🤝 Contributing

We welcome contributions! Areas to contribute:

- **Tools**: Add new automation tools
- **Workflows**: Share workflow patterns
- **Examples**: Real-world use cases
- **Documentation**: Help others succeed
- **Integrations**: Connect to more services

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🚀 Ready to Start Your Agency?

### Next Steps

1. ✅ **Clone and setup** (3 minutes)
2. ✅ **Configure API keys** (5 minutes)
3. ✅ **Run example workflow** (2 minutes)
4. ✅ **Create first client** (5 minutes)
5. ✅ **Deliver first automation** (1-2 days)
6. ✅ **Scale and grow!** (Ongoing)

### Get Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and community
- **Documentation**: Comprehensive guides
- **Examples**: Working code samples

---

## 🙏 Acknowledgments

Built with industry-leading tools:
- **FastAPI** - Modern web framework
- **Poetry** - Dependency management
- **Playwright** - Web automation
- **OpenAI, Anthropic, Groq** - AI providers
- **Prometheus & Grafana** - Monitoring
- **Kubernetes** - Orchestration

---

**This is not just a boilerplate—it's a complete business platform. Start building your AI automation agency today!** 🚀

*Last Updated: September 29, 2025*  
*Version: 2.0.0*  
*Status: Production-Ready*





