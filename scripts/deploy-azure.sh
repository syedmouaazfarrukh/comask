#!/bin/bash

# =============================================================================
# Comask Azure Deployment Script
# =============================================================================
# This script deploys Comask to Azure Container Apps
# 
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - Docker Desktop running
#   - .env.prod file with production secrets
#
# Usage:
#   ./scripts/deploy-azure.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Configuration - MODIFY THESE VALUES
# -----------------------------------------------------------------------------
RESOURCE_GROUP="${RESOURCE_GROUP:-comask-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-comaskacr}"  # Must be globally unique, lowercase
ENVIRONMENT_NAME="${ENVIRONMENT_NAME:-comask-env}"
POSTGRES_SERVER_NAME="${POSTGRES_SERVER_NAME:-comask-postgres}"
POSTGRES_ADMIN_USER="${POSTGRES_ADMIN_USER:-comaskadmin}"
POSTGRES_ADMIN_PASSWORD="${POSTGRES_ADMIN_PASSWORD:-}"  # Will prompt if empty

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker Desktop."
        exit 1
    fi
    
    # Check if logged into Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Please run: az login"
        exit 1
    fi
    
    log_success "All prerequisites met."
}

prompt_for_password() {
    if [ -z "$POSTGRES_ADMIN_PASSWORD" ]; then
        echo -n "Enter PostgreSQL admin password (min 8 chars, mixed case, number): "
        read -s POSTGRES_ADMIN_PASSWORD
        echo
    fi
}

# -----------------------------------------------------------------------------
# Main Deployment Steps
# -----------------------------------------------------------------------------

echo "=============================================="
echo "  Comask Azure Deployment"
echo "=============================================="
echo ""

check_prerequisites
prompt_for_password

# Step 1: Create Resource Group
log_info "Step 1: Creating resource group '$RESOURCE_GROUP' in '$LOCATION'..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
log_success "Resource group created."

# Step 2: Create Container Registry
log_info "Step 2: Creating Azure Container Registry '$ACR_NAME'..."
az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled true \
    --output none
log_success "Container Registry created."

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

# Step 3: Create PostgreSQL Flexible Server
log_info "Step 3: Creating PostgreSQL Flexible Server..."
az postgres flexible-server create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$POSTGRES_SERVER_NAME" \
    --location "$LOCATION" \
    --admin-user "$POSTGRES_ADMIN_USER" \
    --admin-password "$POSTGRES_ADMIN_PASSWORD" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 16 \
    --public-access 0.0.0.0 \
    --output none
log_success "PostgreSQL server created."

# Enable pgvector extension
log_info "Enabling pgvector extension..."
az postgres flexible-server parameter set \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$POSTGRES_SERVER_NAME" \
    --name azure.extensions \
    --value vector \
    --output none

# Create database
log_info "Creating database..."
az postgres flexible-server db create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$POSTGRES_SERVER_NAME" \
    --database-name comask \
    --output none
log_success "Database created with pgvector enabled."

# Step 4: Build and Push Docker Images
log_info "Step 4: Building and pushing Docker images..."
az acr login --name "$ACR_NAME"

log_info "Building backend image..."
docker build -t "$ACR_NAME.azurecr.io/comask-backend:latest" ./backend
docker push "$ACR_NAME.azurecr.io/comask-backend:latest"
log_success "Backend image pushed."

log_info "Building frontend image..."
docker build -t "$ACR_NAME.azurecr.io/comask-frontend:latest" ./frontend
docker push "$ACR_NAME.azurecr.io/comask-frontend:latest"
log_success "Frontend image pushed."

# Step 5: Create Container Apps Environment
log_info "Step 5: Creating Container Apps environment..."
az containerapp env create \
    --name "$ENVIRONMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none
log_success "Container Apps environment created."

# Step 6: Load environment variables from .env.prod
if [ -f ".env.prod" ]; then
    log_info "Loading environment variables from .env.prod..."
    export $(grep -v '^#' .env.prod | xargs)
fi

# Build database URL
DATABASE_URL="postgresql+asyncpg://${POSTGRES_ADMIN_USER}:${POSTGRES_ADMIN_PASSWORD}@${POSTGRES_SERVER_NAME}.postgres.database.azure.com:5432/comask?ssl=require"

# Step 7: Deploy Backend
log_info "Step 6: Deploying backend container app..."
az containerapp create \
    --name comask-backend \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$ENVIRONMENT_NAME" \
    --image "$ACR_NAME.azurecr.io/comask-backend:latest" \
    --target-port 8000 \
    --ingress external \
    --registry-server "$ACR_NAME.azurecr.io" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars \
        "APP_ENV=production" \
        "DATABASE_URL=$DATABASE_URL" \
        "AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}" \
        "AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}" \
        "AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}" \
        "AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4o}" \
        "VOYAGE_API_KEY=${VOYAGE_API_KEY}" \
        "SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}" \
    --output none

BACKEND_URL=$(az containerapp show --name comask-backend --resource-group "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv)
log_success "Backend deployed at: https://$BACKEND_URL"

# Step 8: Deploy Frontend
log_info "Step 7: Deploying frontend container app..."
az containerapp create \
    --name comask-frontend \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$ENVIRONMENT_NAME" \
    --image "$ACR_NAME.azurecr.io/comask-frontend:latest" \
    --target-port 3000 \
    --ingress external \
    --registry-server "$ACR_NAME.azurecr.io" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars \
        "NEXT_PUBLIC_API_URL=https://$BACKEND_URL" \
    --output none

FRONTEND_URL=$(az containerapp show --name comask-frontend --resource-group "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv)
log_success "Frontend deployed at: https://$FRONTEND_URL"

# Summary
echo ""
echo "=============================================="
echo "  Deployment Complete!"
echo "=============================================="
echo ""
echo -e "${GREEN}Frontend URL:${NC} https://$FRONTEND_URL"
echo -e "${GREEN}Backend URL:${NC}  https://$BACKEND_URL"
echo -e "${GREEN}Backend Health:${NC} https://$BACKEND_URL/health"
echo ""
echo "Next steps:"
echo "  1. Verify health: curl https://$BACKEND_URL/health"
echo "  2. Open the frontend: https://$FRONTEND_URL"
echo "  3. Collect data: curl -X POST https://$BACKEND_URL/api/data/collect?jurisdiction=colorado"
echo ""
echo "To view logs:"
echo "  az containerapp logs show --name comask-backend --resource-group $RESOURCE_GROUP --follow"
echo ""
