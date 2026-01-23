# Environment Setup Guide

## Quick Setup

1. **Copy the template**:
```bash
cp env.template .env
```

2. **Edit `.env` and fill in your values**:
   - `SECRET_KEY`: Generate a random string (min 32 characters)
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name (e.g., `gpt-4-turbo`)

## Required Variables

### Minimum Required for MVP:
- ✅ `SECRET_KEY`
- ✅ `DATABASE_URL`
- ✅ `AZURE_OPENAI_API_KEY`
- ✅ `AZURE_OPENAI_ENDPOINT`
- ✅ `AZURE_OPENAI_DEPLOYMENT_NAME`

### Optional (have defaults):
- `APP_ENV` (default: `development`)
- `DEBUG` (default: `False`)
- `LLM_PROVIDER` (default: `azure_openai`)
- `VECTOR_DB_TYPE` (default: `chroma`)
- All scraper and storage settings

## Generate Secret Key

You can generate a secure secret key using Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

Or using OpenSSL:
```bash
openssl rand -hex 32
```

## Database URL Format

```
postgresql+asyncpg://username:password@host:port/database_name
```

Example:
```
postgresql+asyncpg://postgres:mypassword@localhost:5432/comask_db
```

## Azure OpenAI Setup

1. Go to Azure Portal
2. Create an Azure OpenAI resource
3. Deploy a model (e.g., `gpt-4-turbo`)
4. Get your:
   - API Key (from Keys section)
   - Endpoint URL (from Overview section)
   - Deployment name (the name you gave your model)

## Switching to Groq (Future)

When ready to use Groq:
1. Set `LLM_PROVIDER=groq`
2. Add `GROQ_API_KEY=your-key`
3. Set `GROQ_MODEL=llama-3-70b-8192` (or your preferred model)
4. Restart the application

## Security Notes

⚠️ **Never commit `.env` to git!**

The `.env` file is already in `.gitignore`, but double-check:
- Don't share `.env` files
- Use different keys for development and production
- Rotate keys regularly
- Use environment variables in production (not files)

