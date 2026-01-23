# Quick Start Guide - Full Implementation

## ✅ What's Been Done

All mock data has been removed and replaced with **fully functional** real data processing:

1. ✅ **Vector Database** (ChromaDB) - Stores document embeddings
2. ✅ **Document Storage** (MongoDB) - Stores full documents
3. ✅ **Real Document Search** - Vector + keyword search
4. ✅ **Data Collection** - Scrapers populate database
5. ✅ **Real Citations** - All citations from actual documents
6. ✅ **No Mock Data** - Everything uses real data

## 🚀 Getting Started

### Step 1: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Step 2: Collect Data (IMPORTANT!)

Before queries will work, you need to collect data:

```bash
# Collect from all Colorado sources
curl -X POST "http://localhost:8000/api/data/collect?jurisdiction=colorado"

# Or use the API docs at http://localhost:8000/docs
```

**Note**: This will take a few minutes as it scrapes Colorado sources.

### Step 3: Check Data Collection Status

```bash
# Check how many documents were collected
curl "http://localhost:8000/api/data/stats?jurisdiction=colorado"
```

### Step 4: Test a Query

```bash
curl -X POST http://localhost:8000/api/queries \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can I install solar panels in Colorado?",
    "location": "colorado"
  }'
```

Or use the frontend at `http://localhost:3000`

## 📊 API Endpoints

### Data Collection
- `POST /api/data/collect` - Collect from all sources
- `POST /api/data/collect/{source}` - Collect from specific source (e.g., "CPUC")
- `GET /api/data/stats` - Get document statistics

### Queries
- `POST /api/queries` - Submit a query
- `GET /health` - Health check

## 🔄 Data Flow

1. **Collection**: Scrapers → MongoDB + ChromaDB
2. **Query**: User question → Intent → Vector Search → Relevance → Generation → Answer
3. **Response**: Answer + Real citations from actual documents

## 📝 Notes

- **First Time**: Run data collection before queries
- **Embeddings**: If not configured, system uses keyword search (still works!)
- **Scrapers**: Currently CPUC is implemented, add more as needed
- **Storage**: 
  - MongoDB: Full documents
  - ChromaDB: Embeddings (local `./chroma_db` folder)

## 🐛 Troubleshooting

- **No results**: Run data collection first
- **Empty answers**: Check if documents were collected successfully
- **Slow queries**: First query may be slower (embedding generation)
- **Scraper errors**: Check logs for specific source issues

## 📚 Documentation

- `IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `FIX_EMBEDDING_DEPLOYMENT.md` - Embedding setup guide
- API docs: `http://localhost:8000/docs`

