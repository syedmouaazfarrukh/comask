# Comask - Product Features & Data Sources

**Colorado Energy Compliance Assistant**
*Version 1.0 - January 2026*

---

## What We've Built

Comask is a specialized AI research assistant for Colorado energy compliance attorneys. Unlike generic AI chatbots, every answer is:

1. **Sourced** - Drawn from authoritative regulatory documents
2. **Cited** - Every fact includes inline citations to the exact source
3. **Transparent** - Knowledge graphs show the reasoning path
4. **Verified** - Validation agents check claims against sources

---

## User Journey

### 1. Landing Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         ┌─────────────────┐                             │
│                         │   COMASK LOGO   │                             │
│                         └─────────────────┘                             │
│                                                                         │
│               "Your AI Compliance Research Assistant"                   │
│                                                                         │
│                    ┌──────────────────────┐                             │
│                    │   Select Location    │                             │
│                    │   [  Colorado  ▼ ]   │                             │
│                    └──────────────────────┘                             │
│                                                                         │
│                    [ Start Researching →  ]                             │
│                                                                         │
│                  🌐 Interactive Globe Animation                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Users select their jurisdiction (Colorado) and enter the research interface.

### 2. Chat Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ☰  COMASK                                    ☀️/🌙  🔄  📊              │
├─────────────────────────────────────────────────────────────────────────┤
│                                              │                          │
│  👋 Hello! I'm here to help you with         │    📍 Colorado           │
│     Colorado energy regulations.             │                          │
│                                              │    Processing:           │
│  💬 User: What are Colorado's renewable      │    ✓ Intent Analysis     │
│          energy requirements for IOUs?       │    ✓ Source Search       │
│                                              │    ✓ Answer Generation   │
│  🤖 Assistant:                               │    ✓ Validation          │
│                                              │                          │
│     Colorado's Renewable Energy Standard     │    ⏱️ 3.2 seconds        │
│     requires IOUs to generate [[cite:1:      │                          │
│     30% of electricity from renewable        │    📚 Sources Found: 5   │
│     sources]] by 2020...                     │                          │
│                                              │    🎯 Confidence: High   │
│     [View Knowledge Graph]                   │                          │
│                                              │                          │
│     📚 Sources (3)                           │                          │
│     ├─ 1. Colorado RES - CRS 40-2-124       │                          │
│     ├─ 2. PUC Rule 3654                     │                          │
│     └─ 3. FERC Order 2222...                │                          │
│                                              │                          │
├──────────────────────────────────────────────┴──────────────────────────┤
│ [Ask about Colorado energy regulations...                           📤] │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3. Knowledge Graph Visualization

When users click "View Knowledge Graph", they see the retrieval flow:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Knowledge Graph                           [✕]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│         ┌─────────────────────────────────────┐                         │
│         │ 🔍 "What are Colorado's renewable   │                         │
│         │     energy requirements..."          │                         │
│         └────────────────┬────────────────────┘                         │
│                          │                                              │
│            ┌─────────────┼─────────────┐                                │
│            │             │             │                                │
│            ▼             ▼             ▼                                │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐                           │
│     │ Doc 1    │  │ Doc 2    │  │ Doc 3    │                           │
│     │ CRS 40-  │  │ PUC Rule │  │ FERC     │                           │
│     │ 2-124    │  │ 3654     │  │ Order    │                           │
│     │ ⭐ 95%    │  │ ⭐ 87%    │  │ ⭐ 72%    │                           │
│     └────┬─────┘  └────┬─────┘  └────┬─────┘                           │
│          │             │             │                                  │
│          └─────────────┼─────────────┘                                  │
│                        ▼                                                │
│              ┌─────────────────┐                                        │
│              │ 💡 Generated    │                                        │
│              │    Answer       │                                        │
│              └─────────────────┘                                        │
│                                                                         │
│  Legend: ⭐ = Relevance Score                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Features

### 1. Inline Citations

Every factual claim in answers is linked to its source document:

```markdown
Colorado requires IOUs to generate [[cite:1:30% of electricity from
renewable sources]] by 2020, increasing to [[cite:1:100% by 2040]]
under the Clean Energy Plan.
```

Hover over highlighted text to see the exact source excerpt.

### 2. Multi-Source Search

The system searches across multiple data sources in parallel:

| Source Type | Examples |
|-------------|----------|
| Federal Regulations | eCFR Title 18 (FERC), Title 40 (EPA) |
| Federal Register | FERC, EPA, DOE rulemakings |
| Colorado Statutes | CRS Title 40 (Utilities) |
| Colorado Regulations | 4 CCR 723 (PUC Rules) |
| Regional Standards | NERC reliability standards |

### 3. Confidence Scoring

Every answer includes a confidence indicator:

| Level | Meaning | Indicator |
|-------|---------|-----------|
| **High** | 3+ inline citations from authoritative sources | 🟢 |
| **Medium** | 1-2 citations or less authoritative sources | 🟡 |
| **Low** | No matching documents; general knowledge used | 🔴 |

### 4. Processing Pipeline Visibility

The right sidebar shows real-time processing status:

1. **Intent Analysis** - Understanding the question type
2. **Source Search** - Finding relevant documents
3. **Answer Generation** - Creating the response
4. **Validation** - Verifying citations

Each step shows completion time and metadata.

### 5. Conversation Memory

The system maintains context across questions:

- Follow-up questions understand previous context
- "What about municipal utilities?" after an IOU question works correctly
- Conversation history persists in the database

### 6. Dark/Light Mode

Full theme support for comfortable reading in any environment.

---

## Data Sources

### Current Database Status

| Source | Documents | Description |
|--------|-----------|-------------|
| Federal Register - EPA | 20 | Environmental regulations affecting energy |
| Federal Register - FERC | 20 | Federal energy regulatory orders |
| Federal Register - DOE | 13 | Department of Energy rulemakings |
| Colorado Revised Statutes / PUC Rules | 10 | State utility regulations |
| Colorado Revised Statutes | 2 | CRS Title 40 sections |
| Colorado Code of Regulations | 1 | 4 CCR 723 rules |
| NERC | 1 | Reliability standards |
| Colorado PUC | 1 | Commission decisions |
| FERC | 1 | Federal orders |
| **Total** | **69** | Indexed documents |

### Data Acquisition Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATA ACQUISITION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │   Scrapers   │────►│  Processing  │────►│   Storage    │           │
│   │              │     │              │     │              │           │
│   │ • eCFR API   │     │ • Chunking   │     │ • PostgreSQL │           │
│   │ • Fed Reg    │     │   (semantic) │     │ • pgvector   │           │
│   │ • CO CRS     │     │              │     │              │           │
│   │ • CO PUC     │     │ • Voyage AI  │     │ • Metadata   │           │
│   │ • NERC       │     │   Embeddings │     │   JSONB      │           │
│   └──────────────┘     └──────────────┘     └──────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Scrapers Implemented:**
- `ecfr.py` - eCFR API for federal regulations (Title 18, 40)
- `colorado_crs.py` - Colorado Revised Statutes scraper
- `cpuc.py` - Colorado PUC decisions

**Processing:**
- Semantic chunking (target ~500 tokens per chunk)
- Voyage AI embeddings (voyage-3 model, 1024 dimensions)
- Metadata extraction (authority level, jurisdiction, dates)

---

## Question Types Supported

| Intent | Example Questions |
|--------|-------------------|
| **Regulatory Requirements** | "What are the RES requirements for IOUs?" |
| **Compliance Questions** | "How do utilities comply with emission standards?" |
| **Definitions** | "What is a Qualifying Facility under PURPA?" |
| **Process/How-To** | "How does a rate case proceed at the CPUC?" |
| **Deadlines** | "When must utilities file integrated resource plans?" |
| **Eligibility** | "Who qualifies for net metering in Colorado?" |
| **Comparisons** | "How do IOU vs muni requirements differ?" |
| **Penalties** | "What are penalties for RES non-compliance?" |
| **Exemptions** | "Are co-ops exempt from Colorado's RES?" |

---

## Deployment Status

### Production URLs
- **Frontend**: https://comask-frontend-app.azurewebsites.net
- **Backend API**: https://comask-backend-app.azurewebsites.net
- **API Docs**: https://comask-backend-app.azurewebsites.net/docs

### Health Monitoring
```bash
# Check backend health
curl https://comask-backend-app.azurewebsites.net/health
# Returns: {"status":"healthy","database":"connected","environment":"production"}
```

---

## What's Next (Roadmap)

### Phase 2 - Enhanced Data
- [ ] Xcel Energy tariffs
- [ ] Black Hills Energy tariffs
- [ ] More Colorado PUC decisions (5+ years)
- [ ] WECC regional standards
- [ ] SPP market rules

### Phase 3 - Advanced Features
- [ ] Real-time docket monitoring
- [ ] PDF/Word export of research
- [ ] Saved searches
- [ ] Citation bookmarks
- [ ] Multi-jurisdiction support

### Phase 4 - Enterprise
- [ ] SSO integration
- [ ] Team workspaces
- [ ] Audit logging
- [ ] Custom data sources

---

## Sample Interactions

### Example 1: RES Requirements

**User**: What are Colorado's renewable energy standard requirements?

**Assistant**: Colorado's Renewable Energy Standard (RES) is established under [[cite:1:CRS 40-2-124]]. The requirements vary by utility type:

**Investor-Owned Utilities (IOUs)**:
- [[cite:1:30% renewable energy by 2020]]
- [[cite:2:100% clean energy by 2040]] under the Clean Energy Plan

**Municipal Utilities (serving 40,000+ customers)**:
- [[cite:1:10% renewable energy by 2020]]

**Cooperative Electric Associations**:
- [[cite:1:20% renewable energy by 2020]]

*[View Knowledge Graph]* | *Sources: 3*

---

### Example 2: Follow-up Question

**User**: What about smaller municipal utilities?

**Assistant**: Smaller municipal utilities with fewer than 40,000 customers have different requirements under [[cite:1:CRS 40-2-124(1)(c)(V)]]:

- They are [[cite:1:encouraged but not mandated]] to participate in the RES
- Those that voluntarily participate can opt into [[cite:1:the 10% standard]]

The Colorado PUC provides guidance for voluntary participation in [[cite:2:4 CCR 723-3-3652]].

*[View Knowledge Graph]* | *Sources: 2*

---

## Technical Achievements

### Performance
- Average query response: **3-5 seconds**
- Vector search latency: **<100ms**
- Concurrent users supported: **10+**

### Reliability
- Health checks on both services
- Database connection retry on startup
- Graceful degradation when database unavailable
- Request timeouts prevent hanging

### Code Quality
- Multi-agent code review conducted (15 issues found, 8 fixed)
- Production secret validation
- Structured logging (JSON format)
- Type safety (TypeScript + Pydantic)

---

## Getting Started

### For Attorneys
1. Navigate to https://comask-frontend-app.azurewebsites.net
2. Select "Colorado" as your jurisdiction
3. Click "Start Researching"
4. Type your compliance question
5. Review the cited answer and source documents
6. Click "View Knowledge Graph" to see the reasoning path

### For Developers
```bash
# Clone the repository
git clone https://github.com/your-org/comask.git

# Start local development
docker-compose up -d

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

*Product documentation last updated: 2026-01-25*