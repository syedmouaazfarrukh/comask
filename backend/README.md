# Comask Backend

Agentic backend for the Energy Compliance Checker, built with FastAPI, Pydantic, and an agentic framework.

## Architecture

### Agentic Framework
- **Intent Analysis Agent**: Analyzes user queries to understand intent
- **Data Extraction Agent**: Retrieves relevant documents from vector DB
- **Relevance Agent**: Scores and ranks document relevance
- **Answer Generation Agent**: Generates accurate answers with citations
- **Validation Agent**: Ensures answers are grounded in source documents

### Core Components
- **Scrapers**: Automated data collection from Colorado sources
- **Data Pipeline**: Processing, categorization, and embedding generation
- **Vector DB**: Semantic search for relevant regulations
- **LLM Abstraction**: Easy switching between Azure OpenAI and Groq

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database**:
```bash
alembic upgrade head
```

4. **Run scrapers** (first time):
```bash
python -m scripts.run_scrapers
```

5. **Start server**:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration (Pydantic Settings)
│   ├── database.py            # Database connection
│   │
│   ├── api/                   # API routes
│   │   ├── auth.py
│   │   ├── queries.py
│   │   └── documents.py
│   │
│   ├── agents/                # Agentic framework
│   │   ├── base.py           # Base agent class
│   │   ├── intent.py         # Intent analysis
│   │   ├── extraction.py    # Document extraction
│   │   ├── relevance.py      # Relevance scoring
│   │   ├── generation.py     # Answer generation
│   │   └── validation.py    # Answer validation
│   │
│   ├── scrapers/             # Data collection
│   │   ├── base.py          # Base scraper
│   │   ├── cpuc.py          # Colorado PUC
│   │   ├── ceo.py           # Colorado Energy Office
│   │   └── legislature.py   # State Legislature
│   │
│   ├── processing/           # Data processing
│   │   ├── parser.py        # Document parsing
│   │   ├── categorizer.py   # Data categorization
│   │   ├── embedder.py      # Embedding generation
│   │   └── pipeline.py      # Processing pipeline
│   │
│   ├── llm/                  # LLM abstraction
│   │   ├── base.py          # Base LLM interface
│   │   ├── azure_openai.py  # Azure OpenAI implementation
│   │   └── groq.py          # Groq implementation (future)
│   │
│   ├── models/               # Pydantic models
│   │   ├── query.py
│   │   ├── document.py
│   │   └── response.py
│   │
│   └── db/                   # Database models
│       ├── models.py
│       └── schemas.py
│
├── scripts/                  # Utility scripts
│   └── run_scrapers.py
│
└── tests/                    # Tests
```

## Key Features

- **Agentic Architecture**: Multiple specialized agents working together
- **LLM Abstraction**: Easy switching between providers
- **Accurate Answers**: Only answers with verified citations
- **Transparency**: Shows exactly where information came from
- **Colorado Focus**: Deep coverage of Colorado energy regulations

