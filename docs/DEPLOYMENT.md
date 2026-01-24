# Comask Deployment Guide

This document provides step-by-step instructions for deploying Comask to Azure.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Azure Resources Required](#azure-resources-required)
3. [Cost Estimate](#cost-estimate)
4. [Prerequisites](#prerequisites)
5. [Deployment Options](#deployment-options)
6. [Option A: Azure Container Apps (Recommended)](#option-a-azure-container-apps-recommended)
7. [Option B: Azure App Service](#option-b-azure-app-service)
8. [Environment Variables](#environment-variables)
9. [Post-Deployment Steps](#post-deployment-steps)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
                                    ┌─────────────────────────────────────┐
                                    │           Azure Cloud               │
                                    │                                     │
┌──────────┐                        │  ┌─────────────────────────────┐   │
│  Users   │ ───HTTPS───────────────┼─▶│   Azure Container Apps /    │   │
└──────────┘                        │  │   App Service               │   │
                                    │  │                             │   │
                                    │  │  ┌─────────┐  ┌──────────┐  │   │
                                    │  │  │Frontend │  │ Backend  │  │   │
                                    │  │  │ (Next.js│──│ (FastAPI)│  │   │
                                    │  │  │  :3000) │  │  :8000)  │  │   │
                                    │  │  └─────────┘  └────┬─────┘  │   │
                                    │  └────────────────────┼────────┘   │
                                    │                       │            │
                                    │  ┌────────────────────▼────────┐   │
                                    │  │  Azure Database for         │   │
                                    │  │  PostgreSQL (Flexible)      │   │
                                    │  │  + pgvector extension       │   │
                                    │  └─────────────────────────────┘   │
                                    │                                     │
                                    │  ┌─────────────────────────────┐   │
                                    │  │  Azure Cache for Redis      │   │
                                    │  │  (Optional - for sessions)  │   │
                                    │  └─────────────────────────────┘   │
                                    │                                     │
                                    │  ┌─────────────────────────────┐   │
                                    │  │  Azure Container Registry   │   │
                                    │  │  (Store Docker images)      │   │
                                    │  └─────────────────────────────┘   │
                                    └─────────────────────────────────────┘

External APIs:
  - Azure OpenAI (GPT-4o for answers)
  - Voyage AI (Embeddings)
```

---

## Azure Resources Required

| Resource | Purpose | SKU Recommendation |
|----------|---------|-------------------|
| **Azure Container Registry** | Store Docker images | Basic ($5/month) |
| **Azure Container Apps** | Run containers | Consumption plan (pay-per-use) |
| **Azure Database for PostgreSQL** | Database + pgvector | Burstable B1ms ($15/month) |
| **Azure Cache for Redis** | Session caching (optional) | Basic C0 ($16/month) or skip |
| **Azure OpenAI** | Already configured | Pay-per-use |

---

## Cost Estimate

### Minimum Setup (Development/Testing)
| Resource | Monthly Cost |
|----------|-------------|
| Container Registry (Basic) | ~$5 |
| Container Apps (low traffic) | ~$10-20 |
| PostgreSQL Flexible (B1ms) | ~$15 |
| **Total** | **~$30-40/month** |

### Production Setup
| Resource | Monthly Cost |
|----------|-------------|
| Container Registry (Standard) | ~$20 |
| Container Apps (moderate traffic) | ~$50-100 |
| PostgreSQL Flexible (GP_Standard_D2s) | ~$100 |
| Redis Cache (Basic C0) | ~$16 |
| **Total** | **~$185-235/month** |

> Note: Azure OpenAI costs are separate and based on usage (~$0.01-0.03 per query)

---

## Prerequisites

### Tools Required (Install on your machine)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Azure Requirements
- Azure subscription with Owner/Contributor access
- Azure OpenAI resource (you already have this configured)

### Verify Tools
```bash
# Check Azure CLI
az --version

# Check Docker
docker --version

# Login to Azure
az login
```

---

## Deployment Options

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Container Apps** | Serverless, auto-scale, cheaper at low traffic | Newer service | MVP, startups |
| **App Service** | Mature, more features, easier debugging | Fixed pricing | Enterprise |
| **AKS** | Full Kubernetes, maximum control | Complex, overkill for this | Large scale |

**Recommendation**: Start with **Azure Container Apps** for cost efficiency.

---

## Option A: Azure Container Apps (Recommended)

### Step 1: Set Variables (MANUAL - Run in Terminal)

```bash
# Set these variables (customize as needed)
RESOURCE_GROUP="comask-rg"
LOCATION="eastus"
ACR_NAME="comaskacr"  # Must be globally unique, lowercase, no dashes
ENVIRONMENT_NAME="comask-env"
```

### Step 2: Create Resource Group (MANUAL)

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 3: Create Container Registry (MANUAL)

```bash
# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials (save these!)
az acr credential show --name $ACR_NAME
```

**Save the output** - you'll need the username and password.

### Step 4: Create PostgreSQL Database (MANUAL)

```bash
# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name comask-postgres \
  --location $LOCATION \
  --admin-user comaskadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 16 \
  --public-access 0.0.0.0

# Enable pgvector extension
az postgres flexible-server parameter set \
  --resource-group $RESOURCE_GROUP \
  --server-name comask-postgres \
  --name azure.extensions \
  --value vector

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name comask-postgres \
  --database-name comask
```

**Connection string will be**:
```
postgresql+asyncpg://comaskadmin:YourSecurePassword123!@comask-postgres.postgres.database.azure.com:5432/comask?ssl=require
```

### Step 5: Build and Push Docker Images (MANUAL)

```bash
# Navigate to project directory
cd "/Users/mouaazfarrukh/Documents/Work/DashGen Solutions/Comask"

# Login to ACR
az acr login --name $ACR_NAME

# Build and push backend
docker build -t $ACR_NAME.azurecr.io/comask-backend:latest ./backend
docker push $ACR_NAME.azurecr.io/comask-backend:latest

# Build and push frontend
docker build -t $ACR_NAME.azurecr.io/comask-frontend:latest ./frontend
docker push $ACR_NAME.azurecr.io/comask-frontend:latest
```

### Step 6: Create Container Apps Environment (MANUAL)

```bash
# Create Container Apps environment
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 7: Deploy Backend Container App (MANUAL)

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Deploy backend
az containerapp create \
  --name comask-backend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_NAME.azurecr.io/comask-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars \
    "APP_ENV=production" \
    "DATABASE_URL=postgresql+asyncpg://comaskadmin:YourSecurePassword123!@comask-postgres.postgres.database.azure.com:5432/comask?ssl=require" \
    "AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_KEY" \
    "AZURE_OPENAI_ENDPOINT=https://blog-tool-openai.openai.azure.com/" \
    "AZURE_OPENAI_API_VERSION=2024-02-15-preview" \
    "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o" \
    "VOYAGE_API_KEY=YOUR_VOYAGE_API_KEY" \
    "SECRET_KEY=YOUR_SECRET_KEY_HERE"

# Get backend URL
BACKEND_URL=$(az containerapp show --name comask-backend --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "Backend URL: https://$BACKEND_URL"
```

### Step 8: Deploy Frontend Container App (MANUAL)

```bash
# Deploy frontend (use backend URL from previous step)
az containerapp create \
  --name comask-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_NAME.azurecr.io/comask-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars \
    "NEXT_PUBLIC_API_URL=https://$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(az containerapp show --name comask-frontend --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "Frontend URL: https://$FRONTEND_URL"
```

### Step 9: Initialize Database (MANUAL)

```bash
# Connect to PostgreSQL and run init script
# Option 1: Use Azure Portal Query Editor
# Option 2: Use psql locally:
psql "postgresql://comaskadmin:YourSecurePassword123!@comask-postgres.postgres.database.azure.com:5432/comask?sslmode=require"

# Run these SQL commands:
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Then run migrations via backend:
# Access backend container logs to see if migrations ran
az containerapp logs show --name comask-backend --resource-group $RESOURCE_GROUP
```

---

## Option B: Azure App Service

If you prefer App Service, use these commands instead:

### Create App Service Plan and Apps

```bash
# Create App Service Plan
az appservice plan create \
  --name comask-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create backend web app
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan comask-plan \
  --name comask-backend-app \
  --deployment-container-image-name $ACR_NAME.azurecr.io/comask-backend:latest

# Create frontend web app
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan comask-plan \
  --name comask-frontend-app \
  --deployment-container-image-name $ACR_NAME.azurecr.io/comask-frontend:latest

# Configure environment variables (same as Container Apps)
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name comask-backend-app \
  --settings \
    APP_ENV=production \
    DATABASE_URL="postgresql+asyncpg://..." \
    # ... other env vars
```

---

## Environment Variables

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db?ssl=require` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `Eqon1LhX...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://blog-tool-openai.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment name | `gpt-4o` |
| `VOYAGE_API_KEY` | Voyage AI API key | `pa-976q88...` |
| `SECRET_KEY` | JWT secret (generate new for prod!) | Random 64-char string |
| `APP_ENV` | Environment | `production` |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://comask-backend.azurecontainerapps.io` |

### Generate New Secret Key

```bash
# Generate a secure secret key
openssl rand -hex 32
```

---

## Post-Deployment Steps

### 1. Verify Health

```bash
# Check backend health
curl https://<backend-url>/health

# Expected response:
# {"status":"healthy","database":"connected","environment":"production"}
```

### 2. Run Database Migrations

The backend should auto-run migrations on startup. Check logs:

```bash
az containerapp logs show --name comask-backend --resource-group $RESOURCE_GROUP --follow
```

### 3. Seed Initial Data (Optional)

To populate the database with Colorado energy regulations:

```bash
# This needs to be run from inside the backend container or via API
# POST request to start data collection:
curl -X POST https://<backend-url>/api/data/collect?jurisdiction=colorado
```

### 4. Set Up Custom Domain (Optional)

```bash
# Add custom domain to frontend
az containerapp hostname add \
  --name comask-frontend \
  --resource-group $RESOURCE_GROUP \
  --hostname comask.yourdomain.com

# Configure DNS: Add CNAME record pointing to the Container App URL
```

### 5. Enable HTTPS (Auto-enabled for Container Apps)

Container Apps automatically provide HTTPS. For custom domains, you'll need to configure certificates.

---

## Troubleshooting

### Common Issues

#### 1. Container won't start
```bash
# Check logs
az containerapp logs show --name comask-backend --resource-group $RESOURCE_GROUP

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Image pull failed (check ACR credentials)
```

#### 2. Database connection failed
```bash
# Verify PostgreSQL is running
az postgres flexible-server show --name comask-postgres --resource-group $RESOURCE_GROUP

# Check firewall rules
az postgres flexible-server firewall-rule list --resource-group $RESOURCE_GROUP --name comask-postgres

# Add Azure services access
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name comask-postgres \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

#### 3. Frontend can't reach backend
- Ensure backend URL is correct in frontend env vars
- Check CORS settings in backend
- Verify both containers are in same environment

#### 4. pgvector extension not found
```sql
-- Connect to PostgreSQL and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Quick Reference Commands

```bash
# View all resources
az resource list --resource-group $RESOURCE_GROUP --output table

# Restart backend
az containerapp revision restart --name comask-backend --resource-group $RESOURCE_GROUP

# Scale backend
az containerapp update --name comask-backend --resource-group $RESOURCE_GROUP --min-replicas 2 --max-replicas 5

# View logs
az containerapp logs show --name comask-backend --resource-group $RESOURCE_GROUP --follow

# Delete everything (cleanup)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

---

## Deployment Checklist

- [ ] Azure CLI installed and logged in
- [ ] Docker Desktop running
- [ ] Resource group created
- [ ] Container Registry created and credentials saved
- [ ] PostgreSQL Flexible Server created with pgvector enabled
- [ ] Database created
- [ ] Backend image built and pushed
- [ ] Frontend image built and pushed
- [ ] Container Apps environment created
- [ ] Backend deployed with correct environment variables
- [ ] Frontend deployed with correct API URL
- [ ] Health check passes
- [ ] Test a query in the UI

---

## Support

If you encounter issues:
1. Check the logs: `az containerapp logs show --name <app-name> --resource-group $RESOURCE_GROUP`
2. Verify environment variables are set correctly
3. Ensure database is accessible from Container Apps

---

*Last updated: January 2026*
