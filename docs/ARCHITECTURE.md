# Comask - System Architecture

**Colorado Energy Compliance Assistant**
*Providing defensible answers with exact sources for energy compliance attorneys*

---

## Overview

Comask is a full-stack AI-powered research assistant that helps attorneys navigate Colorado energy regulations. It retrieves information from authoritative federal and state sources, generates cited answers, and provides transparency into its reasoning process.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              COMASK ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐         ┌──────────────────────────────────────────────┐ │
│  │   Frontend   │         │               Backend (FastAPI)              │ │
│  │   Next.js    │◄───────►│                                              │ │
│  │  React 18    │  REST   │  ┌────────────────────────────────────────┐  │ │
│  │  Tailwind    │   API   │  │           Agentic Pipeline             │  │ │
│  └──────────────┘         │  │                                        │  │ │
│                           │  │  Intent → Extraction → Relevance       │  │ │
│                           │  │     → Generation → Validation          │  │ │
│                           │  │                                        │  │ │
│                           │  └────────────────┬───────────────────────┘  │ │
│                           │                   │                          │ │
│                           │  ┌────────────────┴───────────────────────┐  │ │
│                           │  │                                        │  │ │
│                           │  │   ┌─────────┐       ┌──────────────┐   │  │ │
│                           │  │   │ Claude  │       │  PostgreSQL  │   │  │ │
│                           │  │   │   API   │       │  + pgvector  │   │  │ │
│                           │  │   └─────────┘       └──────────────┘   │  │ │
│                           │  │                                        │  │ │
│                           │  │   ┌─────────┐       ┌──────────────┐   │  │ │
│                           │  │   │ Voyage  │       │   Scrapers   │   │  │ │
│                           │  │   │   AI    │       │ (eCFR, etc.) │   │  │ │
│                           │  │   └─────────┘       └──────────────┘   │  │ │
│                           │  │                                        │  │ │
│                           │  └────────────────────────────────────────┘  │ │
│                           │                                              │ │
│                           └──────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 14 | React server components, routing |
| Language | TypeScript | Type safety |
| Styling | Tailwind CSS | Utility-first CSS |
| Animations | Framer Motion | Smooth UI transitions |
| Markdown | react-markdown | Rendering formatted answers |
| Charts | React Flow | Knowledge graph visualization |

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | Async Python API |
| Language | Python 3.11 | Core backend logic |
| LLM | Claude API | Answer generation (Sonnet/Opus) |
| Embeddings | Voyage AI | Document embeddings (voyage-3) |
| Database | PostgreSQL + pgvector | Document storage, vector search |
| Auth | JWT + bcrypt | User authentication |
| Logging | structlog | Structured JSON logging |
| HTTP | httpx | Async HTTP client for scrapers |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend Hosting | Azure App Service (B1) | Container hosting |
| Backend Hosting | Azure App Service (B1) | Container hosting |
| Database | Azure PostgreSQL Flexible (B1ms) | Managed PostgreSQL with pgvector |
| Container Registry | Docker Hub | Image storage |
| CI/CD | Docker buildx | Multi-platform builds |

---

## Agentic Pipeline

The core innovation of Comask is its 5-stage agentic pipeline that processes every query:

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. INTENT ANALYSIS                                                      │
│    • Classify query type (regulatory_requirement, compliance, etc.)     │
│    • Extract keywords and entities                                      │
│    • Detect if follow-up question                                       │
│    • Determine jurisdiction scope                                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. DOCUMENT EXTRACTION                                                  │
│    • Vector similarity search (pgvector)                                │
│    • Keyword matching fallback                                          │
│    • Filter by jurisdiction (federal, state, regional)                  │
│    • Retrieve top-N candidate documents                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. RELEVANCE SCORING                                                    │
│    • Re-rank documents by relevance                                     │
│    • Apply authority-level weighting (federal > state > regional)       │
│    • Score recency (newer documents prioritized)                        │
│    • Filter to top-5 most relevant                                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. ANSWER GENERATION                                                    │
│    • Claude API generates answer from documents                         │
│    • Enforces inline citations [[cite:N:fact]]                          │
│    • Builds knowledge graph (retrieval flow)                            │
│    • Fallback to general knowledge if no docs found                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. VALIDATION                                                           │
│    • Verify citations match source documents                            │
│    • Check for unsupported claims                                       │
│    • Validate confidence level                                          │
│    • Flag any issues for transparency                                   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
                          Cited Answer
```

---

## Database Schema

### Core Tables

```sql
-- Documents: Source regulatory documents
documents
├── id (UUID, PK)
├── title (VARCHAR)
├── content (TEXT)
├── source (VARCHAR)           -- e.g., "Federal Register - FERC"
├── source_url (VARCHAR)
├── document_type (ENUM)       -- regulation, statute, decision, order
├── authority_level (ENUM)     -- federal, state, regional, utility
├── jurisdiction_type (ENUM)   -- federal, colorado, nerc, wecc, spp
├── published_date (DATE)
├── effective_date (DATE)
├── metadata (JSONB)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Document Chunks: Semantic chunks for retrieval
document_chunks
├── id (UUID, PK)
├── document_id (UUID, FK → documents)
├── content (TEXT)
├── chunk_index (INTEGER)
├── embedding (VECTOR(1024))   -- Voyage AI embeddings
├── metadata (JSONB)
└── created_at (TIMESTAMP)

-- Conversations: Chat session management
conversations
├── id (UUID, PK)
├── user_id (UUID, FK → users, nullable)
├── location (VARCHAR)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Messages: Conversation history
messages
├── id (UUID, PK)
├── conversation_id (UUID, FK → conversations)
├── role (ENUM)                -- user, assistant
├── content (TEXT)
├── metadata (JSONB)
└── created_at (TIMESTAMP)

-- Users: Authentication
users
├── id (UUID, PK)
├── email (VARCHAR, UNIQUE)
├── password_hash (VARCHAR)
├── full_name (VARCHAR)
├── is_active (BOOLEAN)
├── is_verified (BOOLEAN)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

---

## API Endpoints

### Queries
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/queries` | Submit question, get cited answer |

### Conversations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/conversations/create` | Create new conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |

### Data Collection
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/data/collect` | Trigger full data collection |
| POST | `/api/data/collect/{source}` | Collect from specific source |
| GET | `/api/data/stats` | Get document statistics |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create user account |
| POST | `/auth/login` | Get access token |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Invalidate token |
| GET | `/auth/me` | Get current user |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Database + app health |
| GET | `/` | API information |

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            AZURE DEPLOYMENT                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                        Docker Hub                                │   │
│   │   ┌─────────────────┐         ┌─────────────────┐               │   │
│   │   │ smf777/comask-  │         │ smf777/comask-  │               │   │
│   │   │ frontend:v1.0.1 │         │ backend:v1.0.1  │               │   │
│   │   └────────┬────────┘         └────────┬────────┘               │   │
│   └────────────┼───────────────────────────┼────────────────────────┘   │
│                │                           │                            │
│                ▼                           ▼                            │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                   Azure Resource Group                           │   │
│   │                                                                  │   │
│   │   ┌─────────────────────┐     ┌─────────────────────┐           │   │
│   │   │   App Service       │     │   App Service       │           │   │
│   │   │   (Frontend)        │────►│   (Backend)         │           │   │
│   │   │   B1 Linux          │     │   B1 Linux          │           │   │
│   │   │   comask-frontend-  │     │   comask-backend-   │           │   │
│   │   │   app.azurewebsites │     │   app.azurewebsites │           │   │
│   │   └─────────────────────┘     └──────────┬──────────┘           │   │
│   │                                          │                       │   │
│   │                                          ▼                       │   │
│   │                               ┌─────────────────────┐           │   │
│   │                               │  PostgreSQL         │           │   │
│   │                               │  Flexible Server    │           │   │
│   │                               │  B1ms               │           │   │
│   │                               │  + pgvector ext     │           │   │
│   │                               │  comask-db.postgres │           │   │
│   │                               └─────────────────────┘           │   │
│   │                                                                  │   │
│   └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Estimated Monthly Cost: ~$28 (B1 App Service × 2 + B1ms PostgreSQL)
```

---

## Security Measures

### Authentication
- JWT tokens with HS256 signing
- bcrypt password hashing (configurable rounds)
- Token expiration: 24h access, 7d refresh
- Production SECRET_KEY validation (fails if default)

### CORS
- Explicit origin allowlist (no wildcards in production)
- Restricted headers: `Authorization`, `Content-Type`, `Accept`, `Origin`, `X-Requested-With`
- Credentials support for cross-origin requests

### API Security
- Request timeouts (30s default) prevent hanging
- Rate limiting via Azure App Service
- Input validation via Pydantic models
- SQL injection prevention via SQLAlchemy ORM

### Production Validation
```python
@model_validator(mode='after')
def validate_production_settings(self) -> 'Settings':
    if self.app_env == 'production':
        if self.secret_key == 'change-me-in-production':
            raise ValueError('SECRET_KEY must be set to a secure value')
```

---

## Key Files Reference

```
Comask/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, middleware, routers
│   │   ├── config.py            # Pydantic settings, env vars
│   │   ├── agents/              # Agentic pipeline
│   │   │   ├── intent.py        # Query intent analysis
│   │   │   ├── extraction.py    # Document retrieval
│   │   │   ├── relevance.py     # Document ranking
│   │   │   ├── generation.py    # Answer generation
│   │   │   └── validation.py    # Citation validation
│   │   ├── api/                  # API endpoints
│   │   │   ├── queries.py       # Query orchestration
│   │   │   ├── conversations.py # Chat management
│   │   │   └── auth.py          # Authentication
│   │   ├── db/
│   │   │   ├── database.py      # SQLAlchemy + pgvector
│   │   │   └── models.py        # ORM models
│   │   ├── llm/
│   │   │   ├── claude.py        # Anthropic Claude client
│   │   │   └── embeddings.py    # Voyage AI embeddings
│   │   ├── scrapers/            # Data acquisition
│   │   │   ├── ecfr.py          # Federal regulations
│   │   │   ├── colorado_crs.py  # Colorado statutes
│   │   │   └── cpuc.py          # Colorado PUC decisions
│   │   └── services/            # Business logic
│   │       ├── auth_service.py  # JWT, password hashing
│   │       └── conversation_service.py
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── login/page.tsx       # Auth pages
│   │   └── layout.tsx           # Root layout
│   ├── components/
│   │   ├── ChatInterface.tsx    # Main chat UI
│   │   ├── ChatMessage.tsx      # Message rendering
│   │   ├── KnowledgeGraph.tsx   # Source visualization
│   │   └── MapVisualization.tsx # Processing sidebar
│   ├── lib/
│   │   └── api.ts               # API client
│   └── Dockerfile
└── docs/
    ├── ARCHITECTURE.md          # This file
    └── PRODUCT-FEATURES.md      # Features & user guide
```

---

## Environment Variables

### Backend (Required)
```bash
APP_ENV=production
SECRET_KEY=<32+ char secret>
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
CLAUDE_API_KEY=<anthropic-api-key>
VOYAGE_API_KEY=<voyage-ai-key>
```

### Frontend (Build-time)
```bash
NEXT_PUBLIC_API_URL=https://backend-url.azurewebsites.net
```

---

*Architecture document last updated: 2026-01-25*
