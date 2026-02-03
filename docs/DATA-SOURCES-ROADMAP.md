# Comask Data Sources Roadmap

## Current State & Future Direction

This diagram shows our current data sources, what we can add next, and where we need customer direction.

```mermaid
flowchart TB
    subgraph CURRENT["✅ CURRENT SOURCES (66 Documents)"]
        direction TB

        subgraph FED_CURRENT["Federal Sources"]
            FR_DOE["Federal Register - DOE<br/>13 documents"]
            FR_EPA["Federal Register - EPA<br/>17 documents"]
            FR_FERC["Federal Register - FERC<br/>16 documents"]
        end

        subgraph STATE_CURRENT["Colorado State Sources"]
            CRS["Colorado Revised Statutes<br/>Title 40 - Utilities<br/>7 documents"]
            CCR["Colorado Code of Regulations<br/>4 CCR 723 - PUC Rules<br/>4 documents"]
            CO_BILLS["Colorado Legislature Bills<br/>HB22-1362, SB19-077<br/>2 documents"]
            CO_PUC["Colorado PUC Decisions<br/>1 document"]
        end
    end

    subgraph NEXT["🔜 NEXT PHASE (Easy to Add)"]
        direction TB

        subgraph FED_NEXT["Federal - API Available"]
            ECFR["eCFR API<br/>Title 18 (Energy)<br/>Title 40 (Environment)"]
            FERC_ORDERS["FERC Orders<br/>Major rulemakings"]
        end

        subgraph STATE_NEXT["Colorado - Scrapable"]
            PUC_DECISIONS["PUC Recent Decisions<br/>Last 5 years of orders"]
            CEO["Colorado Energy Office<br/>Policy documents"]
        end
    end

    subgraph FUTURE["🎯 FUTURE EXPANSION (Need Direction)"]
        direction TB

        subgraph REGIONAL["Regional Organizations"]
            NERC["NERC Standards<br/>Reliability requirements"]
            WECC["WECC Standards<br/>Western interconnection"]
            SPP["SPP Market Rules<br/>If applicable"]
        end

        subgraph UTILITY["Utility-Specific"]
            XCEL["Xcel Energy Tariffs<br/>Rate schedules"]
            BLACKHILLS["Black Hills Energy<br/>Tariffs & filings"]
            COOPS["Rural Electric Co-ops<br/>Various"]
        end

        subgraph EXTERNAL["External References"]
            NEC["National Electrical Code<br/>Referenced in rules"]
            IEEE["IEEE Standards<br/>Technical requirements"]
            NFPA["NFPA Standards<br/>Safety codes"]
        end
    end

    subgraph DECISION["❓ CUSTOMER DECISION NEEDED"]
        Q1["Which utilities to prioritize?<br/>Xcel vs Black Hills vs Co-ops"]
        Q2["Regional scope?<br/>WECC only or include SPP?"]
        Q3["External standards?<br/>NEC/IEEE - licensed content"]
        Q4["Historical depth?<br/>How far back for decisions?"]
    end

    CURRENT --> NEXT
    NEXT --> FUTURE
    FUTURE --> DECISION

    style CURRENT fill:#d4edda,stroke:#28a745
    style NEXT fill:#fff3cd,stroke:#ffc107
    style FUTURE fill:#cce5ff,stroke:#007bff
    style DECISION fill:#f8d7da,stroke:#dc3545
```

## Source Details

### ✅ Currently Available (66 Documents)

| Source | Type | Count | Coverage |
|--------|------|-------|----------|
| Federal Register - DOE | Federal Regulations | 13 | Energy policy, efficiency |
| Federal Register - EPA | Federal Regulations | 17 | Environmental, air quality |
| Federal Register - FERC | Federal Regulations | 16 | Transmission, markets |
| Colorado Revised Statutes | State Law | 7 | Title 40 utilities law |
| Colorado Code of Regulations | State Rules | 4 | PUC implementation rules |
| Colorado Legislature | State Bills | 2 | Recent energy legislation |
| Colorado PUC | State Decisions | 1 | Commission orders |

### 🔜 Next Phase (2-3 weeks to implement)

| Source | Effort | Value | Notes |
|--------|--------|-------|-------|
| eCFR API | Low | High | Full federal energy regulations |
| FERC Major Orders | Medium | High | Key market/transmission rules |
| PUC Decisions (5yr) | Medium | High | ~500+ relevant decisions |
| Colorado Energy Office | Low | Medium | Policy guidance docs |

### 🎯 Future Expansion (Need customer input)

| Source | Effort | Value | Blocker |
|--------|--------|-------|---------|
| NERC Standards | Medium | High | Which standards apply? |
| WECC Standards | Medium | Medium | Regional scope decision |
| Xcel Tariffs | High | High | PDF parsing complexity |
| Black Hills Tariffs | High | Medium | Lower priority? |
| NEC/IEEE | High | Medium | Licensed content - cost |

## Questions for Sasha

1. **Utility Priority**: Which utility's tariffs matter most?
   - Xcel Energy (largest in Colorado)
   - Black Hills Energy
   - Rural co-ops
   - All of the above?

2. **Regional Scope**: How important are regional standards?
   - NERC (national reliability)
   - WECC (western region)
   - SPP (if any Colorado overlap)

3. **Historical Depth**: For PUC decisions, how far back?
   - Last 2 years (recent precedent)
   - Last 5 years (standard practice)
   - Last 10 years (comprehensive)

4. **External Standards**: Worth the investment?
   - NEC (National Electrical Code) - referenced often
   - IEEE standards - technical specs
   - These are licensed/paid content

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph SOURCES["Data Sources"]
        FED["Federal<br/>APIs & Registers"]
        STATE["State<br/>CRS, CCR, PUC"]
        REG["Regional<br/>NERC, WECC"]
        UTIL["Utility<br/>Tariffs"]
    end

    subgraph PIPELINE["Processing Pipeline"]
        SCRAPE["Scraper<br/>Collect docs"]
        CHUNK["Chunker<br/>Split text"]
        EMBED["Embedder<br/>Voyage AI"]
        STORE["Storage<br/>pgvector"]
    end

    subgraph APP["Application"]
        QUERY["User Query"]
        SEARCH["Vector Search"]
        LLM["Claude LLM"]
        ANSWER["Cited Answer"]
    end

    FED --> SCRAPE
    STATE --> SCRAPE
    REG --> SCRAPE
    UTIL --> SCRAPE

    SCRAPE --> CHUNK --> EMBED --> STORE

    QUERY --> SEARCH
    STORE --> SEARCH
    SEARCH --> LLM --> ANSWER
```

## Recommended Next Steps

Based on attorney use cases, we recommend this priority:

1. **Immediate** (before production)
   - eCFR Title 18 (federal energy regulations)
   - Colorado PUC decisions (last 5 years)

2. **Short-term** (first month)
   - NERC reliability standards
   - Xcel Energy tariffs (if prioritized)

3. **Medium-term** (based on feedback)
   - Additional utilities
   - Regional standards (WECC/SPP)
   - Historical expansion

**The key question for Sasha**: Which direction adds the most value for your practice?
