# Comask Quick Deployment Guide

This is a quick reference for deploying Comask to Azure. For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## Prerequisites

1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Install Docker Desktop: https://www.docker.com/products/docker-desktop
3. Login to Azure: `az login`

## Quick Deploy (5 Steps)

### Step 1: Create .env.prod file

```bash
cp .env.prod.example .env.prod
# Edit .env.prod with your API keys
```

**Required values in .env.prod:**
```
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=https://blog-tool-openai.openai.azure.com/
VOYAGE_API_KEY=<your-key>
SECRET_KEY=<generate-with: openssl rand -hex 32>
```

### Step 2: Run Deployment Script

```bash
cd "/Users/mouaazfarrukh/Documents/Work/DashGen Solutions/Comask"
./scripts/deploy-azure.sh
```

The script will:
- Create Azure resource group
- Create Container Registry
- Create PostgreSQL database with pgvector
- Build and push Docker images
- Deploy to Azure Container Apps

### Step 3: Wait for Deployment (~10-15 minutes)

The script will output the URLs when complete.

### Step 4: Verify Deployment

```bash
curl https://<backend-url>/health
# Should return: {"status":"healthy","database":"connected","environment":"production"}
```

### Step 5: Open the App

Navigate to `https://<frontend-url>` in your browser.

## Manual Deployment

If you prefer manual control, follow these individual commands:

```bash
# Variables
RESOURCE_GROUP="comask-rg"
LOCATION="eastus"
ACR_NAME="comaskacr"

# 1. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create container registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# 3. Create PostgreSQL (see DEPLOYMENT.md for full command)

# 4. Build and push images
az acr login --name $ACR_NAME
docker build -t $ACR_NAME.azurecr.io/comask-backend:latest ./backend
docker push $ACR_NAME.azurecr.io/comask-backend:latest
docker build -t $ACR_NAME.azurecr.io/comask-frontend:latest ./frontend
docker push $ACR_NAME.azurecr.io/comask-frontend:latest

# 5. Deploy containers (see DEPLOYMENT.md for full commands)
```

## Cost Estimate

| Setup | Monthly Cost |
|-------|-------------|
| Development | ~$30-40 |
| Production | ~$185-235 |

## Troubleshooting

```bash
# View logs
az containerapp logs show --name comask-backend --resource-group comask-rg --follow

# Restart container
az containerapp revision restart --name comask-backend --resource-group comask-rg

# Delete everything
az group delete --name comask-rg --yes
```

## Need Help?

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions and troubleshooting.
