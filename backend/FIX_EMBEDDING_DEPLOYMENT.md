# Fix Embedding Deployment Error

## Current Issue

The backend is trying to generate embeddings but getting this error:
```
DeploymentNotFound: The API deployment for this resource does not exist.
```

## Root Cause

Azure OpenAI requires a **deployment name** for embeddings, not just a model name. You need to create a deployment in your Azure OpenAI resource.

## Solution

### Option 1: Create Embedding Deployment (Recommended)

1. **Go to Azure Portal**
   - Navigate to your Azure OpenAI resource: `blog-tool-openai`
   - URL: https://portal.azure.com

2. **Create Embedding Deployment**
   - Go to **"Deployments"** or **"Model deployments"** section
   - Click **"+ Create"** or **"Deploy model"**
   - Select model: **"text-embedding-3-large"** or **"text-embedding-ada-002"**
   - Give it a deployment name (e.g., `text-embedding-3-large` or `embeddings`)
   - Click **Create**

3. **Update `.env` file**
   ```env
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-deployment-name-here
   ```

4. **Restart the backend**
   ```bash
   # Stop current server (Ctrl+C)
   uvicorn app.main:app --reload
   ```

### Option 2: Use Same Deployment (If Compatible)

If your `gpt-4o` deployment also supports embeddings (unlikely), you can use:
```env
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=gpt-4o
```

### Option 3: Continue Without Embeddings (Temporary)

The system will now work without embeddings, but vector search won't be available. The extraction agent will use keyword-based search instead.

**Note**: The backend has been updated to handle missing embeddings gracefully, so it will continue working but with limited search capabilities.

## Quick Fix

Add this to your `.env` file in the `backend/` directory:

```env
# If you have an embedding deployment:
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# If you don't have one yet, leave it empty and the system will work without embeddings:
# AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
```

## Verify

After setting up the deployment, test it:
```bash
# The backend should start without embedding errors
# When you submit a query, it should work (with or without embeddings)
```

## Next Steps

1. Create the embedding deployment in Azure Portal
2. Add `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` to your `.env`
3. Restart the backend
4. Test a query - embeddings should work now

