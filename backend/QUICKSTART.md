# Quick Start Guide

## Prerequisites

- Python 3.11+
- PostgreSQL (for database)
- Azure OpenAI API key (or Groq for future)

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
Create a `.env` file with:
```env
# Required
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/comask_db
SECRET_KEY=your-secret-key-here
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo

# Optional
LLM_PROVIDER=azure_openai  # or 'groq' for future
DEBUG=True
```

3. **Initialize database**:
```bash
# Create database first
createdb comask_db

# Run migrations (when Alembic is set up)
alembic upgrade head
```

4. **Run scrapers** (first time):
```bash
python scripts/run_scrapers.py
```

5. **Start server**:
```bash
uvicorn app.main:app --reload
```

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Submit a query
curl -X POST http://localhost:8000/api/queries \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can I install solar panels in Colorado?",
    "location": "colorado"
  }'
```

## Project Structure

- `app/main.py` - FastAPI application
- `app/agents/` - Agentic framework (5 agents)
- `app/scrapers/` - Data collection scrapers
- `app/processing/` - Data processing pipeline
- `app/llm/` - LLM abstraction layer
- `app/api/` - API endpoints
- `app/models/` - Pydantic models
- `app/db/` - Database models

## Key Features

✅ Agentic architecture with 5 specialized agents  
✅ LLM provider abstraction (Azure OpenAI / Groq)  
✅ Scraping system for Colorado sources  
✅ Accurate answers with citations  
✅ "I don't know" when information unavailable  
✅ Easy to extend and modify  

