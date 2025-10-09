#!/bin/bash
# Initialize secrets for Kubernetes deployment

set -e

NAMESPACE="ai-automation"

echo "🔐 AI Automation - Secret Initialization"
echo "This script will help you create Kubernetes secrets"
echo ""

# Check kubectl
if ! command -v kubectl &> /dev/null; then
  echo "❌ kubectl not found. Please install kubectl first."
  exit 1
fi

# Prompt for secrets
echo "Please enter your credentials (they won't be displayed):"
echo ""

read -sp "PostgreSQL Password: " POSTGRES_PASSWORD
echo ""

read -sp "OpenAI API Key: " OPENAI_KEY
echo ""

read -sp "Anthropic API Key (optional): " ANTHROPIC_KEY
echo ""

read -sp "Groq API Key (optional): " GROQ_KEY
echo ""

read -sp "JWT Secret Key (or press Enter to generate): " JWT_SECRET
echo ""

# Generate JWT secret if not provided
if [ -z "$JWT_SECRET" ]; then
  JWT_SECRET=$(openssl rand -hex 32)
  echo "✅ Generated JWT secret key"
fi

# Build database URL
read -p "Database Host (default: postgres-service): " DB_HOST
DB_HOST=${DB_HOST:-postgres-service}

read -p "Database Name (default: ai_automation): " DB_NAME
DB_NAME=${DB_NAME:-ai_automation}

read -p "Database User (default: ai_user): " DB_USER
DB_USER=${DB_USER:-ai_user}

DATABASE_URL="postgresql+asyncpg://${DB_USER}:${POSTGRES_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"

# Create namespace if it doesn't exist
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
  echo "📦 Creating namespace: $NAMESPACE"
  kubectl create namespace $NAMESPACE
fi

# Delete existing secret if it exists
if kubectl get secret ai-automation-secrets -n $NAMESPACE &> /dev/null; then
  echo "⚠️  Existing secret found. Deleting..."
  kubectl delete secret ai-automation-secrets -n $NAMESPACE
fi

# Create secret
echo "🔐 Creating Kubernetes secret..."

kubectl create secret generic ai-automation-secrets \
  --namespace=$NAMESPACE \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=postgres-password="$POSTGRES_PASSWORD" \
  --from-literal=openai-api-key="$OPENAI_KEY" \
  --from-literal=anthropic-api-key="${ANTHROPIC_KEY:-}" \
  --from-literal=groq-api-key="${GROQ_KEY:-}" \
  --from-literal=jwt-secret="$JWT_SECRET"

echo ""
echo "✅ Secrets created successfully!"
echo ""
echo "Secret name: ai-automation-secrets"
echo "Namespace: $NAMESPACE"
echo ""
echo "View secret: kubectl describe secret ai-automation-secrets -n $NAMESPACE"
echo "Next step: ./deploy.sh staging (or production)"





