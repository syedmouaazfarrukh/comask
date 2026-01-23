# Deployment Guide for Colorado Energy Compliance Assistant

## Prerequisites

- Docker and Docker Compose installed
- Azure CLI installed and authenticated (for Azure deployment)
- API keys for Claude and Voyage AI

## Local Development

### Quick Start

1. Copy environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `.env` with your API keys:
   ```
   CLAUDE_API_KEY=your_claude_api_key
   VOYAGE_API_KEY=your_voyage_api_key
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Mode with Hot Reload

The default `docker-compose.yml` includes volume mounts for hot reload:
- Backend code changes are reflected immediately
- Frontend supports Next.js hot module replacement

## Production Deployment

### Building Production Images

1. Make the build script executable:
   ```bash
   chmod +x scripts/build-images.sh
   ```

2. Build images:
   ```bash
   ./scripts/build-images.sh
   ```

   Or with a specific tag:
   ```bash
   ./scripts/build-images.sh v1.0.0
   ```

### Docker Compose Production

1. Copy and configure production environment:
   ```bash
   cp .env.production.example .env.production
   ```

2. Edit `.env.production` with secure values:
   ```
   POSTGRES_PASSWORD=your_secure_database_password
   SECRET_KEY=$(openssl rand -hex 32)
   CLAUDE_API_KEY=your_claude_api_key
   VOYAGE_API_KEY=your_voyage_api_key
   BACKEND_URL=https://your-backend-url
   FRONTEND_URL=https://your-frontend-url
   ```

3. Deploy with production compose file:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
   ```

## Azure App Service Deployment

### Option 1: Azure Container Registry + App Service

1. Create Azure Container Registry:
   ```bash
   az acr create --resource-group myResourceGroup --name mycomaskregistry --sku Basic
   ```

2. Login to ACR:
   ```bash
   az acr login --name mycomaskregistry
   ```

3. Build and push images:
   ```bash
   export DOCKER_REGISTRY=mycomaskregistry.azurecr.io
   ./scripts/build-images.sh v1.0.0
   ```

4. Create App Service Plan:
   ```bash
   az appservice plan create \
     --name comask-plan \
     --resource-group myResourceGroup \
     --is-linux \
     --sku B2
   ```

5. Create Backend Web App:
   ```bash
   az webapp create \
     --resource-group myResourceGroup \
     --plan comask-plan \
     --name comask-backend \
     --deployment-container-image-name mycomaskregistry.azurecr.io/comask-backend:v1.0.0
   ```

6. Create Frontend Web App:
   ```bash
   az webapp create \
     --resource-group myResourceGroup \
     --plan comask-plan \
     --name comask-frontend \
     --deployment-container-image-name mycomaskregistry.azurecr.io/comask-frontend:v1.0.0
   ```

7. Configure environment variables:
   ```bash
   az webapp config appsettings set \
     --resource-group myResourceGroup \
     --name comask-backend \
     --settings \
       DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
       SECRET_KEY="your-secret-key" \
       CLAUDE_API_KEY="your-claude-key" \
       VOYAGE_API_KEY="your-voyage-key"
   ```

### Option 2: Azure Database for PostgreSQL

For production, use Azure Database for PostgreSQL with pgvector:

1. Create PostgreSQL Flexible Server:
   ```bash
   az postgres flexible-server create \
     --resource-group myResourceGroup \
     --name comask-postgres \
     --admin-user comaskadmin \
     --admin-password 'SecurePassword123!' \
     --sku-name Standard_B1ms \
     --tier Burstable \
     --version 16
   ```

2. Enable pgvector extension:
   ```bash
   az postgres flexible-server parameter set \
     --resource-group myResourceGroup \
     --server-name comask-postgres \
     --name azure.extensions \
     --value vector
   ```

3. Update your connection string to use the Azure PostgreSQL instance.

## Environment Variables Reference

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | Yes | JWT signing key (256-bit hex) |
| `CLAUDE_API_KEY` | Yes | Anthropic Claude API key |
| `VOYAGE_API_KEY` | Yes | Voyage AI embeddings API key |
| `APP_ENV` | No | Environment (development/production) |
| `DEBUG` | No | Enable debug mode (true/false) |
| `REDIS_URL` | No | Redis connection string |
| `FRONTEND_URL` | No | Frontend URL for CORS |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |

## Health Checks

Both services include health check endpoints:

- Backend: `GET /health`
- Frontend: `GET /` (returns HTML)

## Monitoring

The backend includes structured logging with structlog. Configure log aggregation in Azure:

```bash
az webapp log config \
  --resource-group myResourceGroup \
  --name comask-backend \
  --docker-container-logging filesystem
```

View logs:
```bash
az webapp log tail \
  --resource-group myResourceGroup \
  --name comask-backend
```

## Security Considerations

1. Always use HTTPS in production
2. Set secure, random values for `SECRET_KEY`
3. Use Azure Key Vault for secrets management
4. Enable Azure DDoS protection
5. Configure firewall rules for PostgreSQL
6. Use managed identities where possible

## Troubleshooting

### Database Connection Issues

1. Check PostgreSQL is running:
   ```bash
   docker-compose logs postgres
   ```

2. Verify pgvector extension:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

### Container Build Failures

1. Check Docker daemon is running
2. Ensure sufficient disk space
3. Review build logs for dependency issues

### Health Check Failures

1. Check container logs:
   ```bash
   docker logs comask-backend
   ```

2. Verify environment variables are set correctly
3. Check database connectivity
