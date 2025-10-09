#!/bin/bash
# AI Automation Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: local, staging, production

set -e

ENVIRONMENT=${1:-local}
NAMESPACE="ai-automation"

echo "🚀 AI Automation Deployment Script"
echo "Environment: $ENVIRONMENT"
echo ""

case $ENVIRONMENT in
  local)
    echo "📦 Deploying locally with Docker Compose..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
      echo "⚠️  .env file not found. Creating from example..."
      if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys."
        echo "Press Enter to continue after editing .env..."
        read
      else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
      fi
    fi
    
    # Start services
    echo "🐳 Starting Docker Compose services..."
    docker-compose up -d
    
    echo ""
    echo "✅ Local deployment complete!"
    echo ""
    echo "📍 Access points:"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Postgres: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    ;;
    
  staging|production)
    echo "☸️  Deploying to Kubernetes ($ENVIRONMENT)..."
    
    # Check kubectl is available
    if ! command -v kubectl &> /dev/null; then
      echo "❌ kubectl not found. Please install kubectl first."
      exit 1
    fi
    
    # Check if namespace exists, create if not
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
      echo "📦 Creating namespace: $NAMESPACE"
      kubectl apply -f k8s/namespace.yaml
    fi
    
    # Check if secrets exist
    if ! kubectl get secret ai-automation-secrets -n $NAMESPACE &> /dev/null; then
      echo "⚠️  Secrets not found. Please create secrets first:"
      echo ""
      echo "kubectl create secret generic ai-automation-secrets \\"
      echo "  --namespace=$NAMESPACE \\"
      echo "  --from-literal=database-url='postgresql://...' \\"
      echo "  --from-literal=openai-api-key='sk-...' \\"
      echo "  --from-literal=anthropic-api-key='sk-ant-...' \\"
      echo "  --from-literal=jwt-secret='your-secret-key'"
      echo ""
      exit 1
    fi
    
    # Apply configurations
    echo "📝 Applying ConfigMaps..."
    kubectl apply -f k8s/configmap.yaml
    
    # Deploy databases
    echo "🗄️  Deploying databases..."
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/redis.yaml
    
    # Wait for databases to be ready
    echo "⏳ Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s || true
    
    # Deploy application
    echo "🚀 Deploying application..."
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    
    # Apply ingress for production
    if [ "$ENVIRONMENT" == "production" ]; then
      echo "🌐 Applying ingress..."
      kubectl apply -f k8s/ingress.yaml
    fi
    
    # Wait for deployment to be ready
    echo "⏳ Waiting for deployment to be ready..."
    kubectl wait --for=condition=available deployment/ai-automation -n $NAMESPACE --timeout=300s
    
    # Show status
    echo ""
    echo "✅ Kubernetes deployment complete!"
    echo ""
    echo "📊 Deployment status:"
    kubectl get pods -n $NAMESPACE
    echo ""
    kubectl get services -n $NAMESPACE
    echo ""
    
    if [ "$ENVIRONMENT" == "production" ]; then
      echo "🌐 Ingress:"
      kubectl get ingress -n $NAMESPACE
    fi
    
    echo ""
    echo "View logs: kubectl logs -f deployment/ai-automation -n $NAMESPACE"
    echo "Scale: kubectl scale deployment/ai-automation --replicas=5 -n $NAMESPACE"
    ;;
    
  *)
    echo "❌ Unknown environment: $ENVIRONMENT"
    echo "Usage: ./deploy.sh [local|staging|production]"
    exit 1
    ;;
esac





