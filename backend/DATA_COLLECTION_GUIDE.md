# Data Collection Guide

## ⚠️ IMPORTANT: Collect Data First!

The system needs data before it can answer questions. You must run data collection first.

## How to Collect Data

### Option 1: Using API (Recommended)

```bash
# Collect from all Colorado sources
curl -X POST "http://localhost:8000/api/data/collect?jurisdiction=colorado"
```

This will:
1. Scrape Colorado Public Utilities Commission (CPUC)
2. Store documents in MongoDB
3. Generate embeddings and store in ChromaDB
4. Take 5-10 minutes depending on source size

### Option 2: Using API Docs

1. Go to `http://localhost:8000/docs`
2. Find `POST /api/data/collect`
3. Click "Try it out"
4. Set `jurisdiction` to `colorado`
5. Click "Execute"

### Option 3: Using Python Script

```python
import asyncio
from app.services.data_collection import DataCollectionService

async def collect():
    service = DataCollectionService()
    results = await service.collect_all_sources("colorado")
    print(results)

asyncio.run(collect())
```

## Check Collection Status

```bash
# Get statistics
curl "http://localhost:8000/api/data/stats?jurisdiction=colorado"
```

Response:
```json
{
  "jurisdiction": "colorado",
  "document_count": 42,
  "sources": ["CPUC"]
}
```

## What Gets Collected

Currently implemented:
- ✅ **CPUC (Colorado Public Utilities Commission)**
  - Orders
  - Rulemakings
  - Dockets

Coming soon:
- ⏳ **CEO (Colorado Energy Office)**
- ⏳ **Colorado State Legislature**

## Where Data is Stored

1. **MongoDB (Cosmos DB)**: Full document content
   - Collection: `documents`
   - Fields: title, content, source_url, source, published_date, etc.

2. **ChromaDB**: Document embeddings
   - Location: `./chroma_db/` (local folder)
   - Collection: `comask_documents`
   - Used for vector search

## Troubleshooting

### No Documents Found

**Problem**: Queries return "I don't have specific information"

**Solution**: 
1. Run data collection: `POST /api/data/collect`
2. Wait for completion (check logs)
3. Verify with: `GET /api/data/stats`

### Scraper Errors

**Problem**: Some sources fail to scrape

**Solution**:
1. Check logs for specific errors
2. Verify source URLs are accessible
3. Check network connectivity
4. Some sites may block scrapers (add delays/headers)

### Embedding Errors

**Problem**: "DeploymentNotFound" errors

**Solution**: 
- System will use keyword search as fallback
- See `FIX_EMBEDDING_DEPLOYMENT.md` to set up embeddings

## Automated Collection (Future)

For production, set up scheduled collection:
- Daily at 2 AM
- Weekly full refresh
- On-demand triggers

## Next Steps

1. ✅ Run data collection
2. ✅ Verify documents were collected
3. ✅ Test queries
4. ✅ Monitor collection logs

