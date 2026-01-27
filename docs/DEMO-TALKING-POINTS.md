# Demo Talking Points for Sasha Meeting

**Comask - Colorado Energy Compliance Assistant**
**Prepared for:** Initial Customer Demo
**Version:** First Draft MVP

---

## Opening (2 minutes)

> "We've built a working prototype that demonstrates our core value proposition: ask a Colorado energy compliance question, get a cited answer from authoritative sources. This is our first version, and we're here to get your feedback to make sure we're building the right product."

**Key Message:** This is a working demo, not a finished product. We want input before building more.

---

## What This Demo Shows

### ✅ What Works Well

1. **Ask questions in natural language**
   - "What are Colorado's renewable energy requirements?"
   - "What is FERC Order 2222?"
   - "What are the emission standards for power plants?"

2. **Get cited answers**
   - Every claim is linked to a source document
   - Hover over highlighted text to see the exact source
   - Click to view the original document

3. **See the reasoning path**
   - "View Knowledge Graph" shows which documents were used
   - Confidence indicator (High/Medium/Low)
   - Processing breakdown in sidebar

4. **Conversation memory**
   - Follow-up questions work
   - "What about municipal utilities?" after an IOU question

### ⚠️ What to Acknowledge

1. **Data coverage is limited**
   - 69 documents from 9 sources
   - Heavy on Federal Register (recent EPA, FERC, DOE documents)
   - Colorado statutes and PUC rules included but not comprehensive
   - **NOT included:** Utility tariffs, full PUC docket archive, WECC/SPP

2. **Some source links may not open directly**
   - Federal Register links: Work perfectly
   - Colorado leg.gov PDFs: May require navigation to site
   - We have the content; the link is for verification

3. **This is optimized for demo, not production load**
   - Single user at a time
   - Response time: 3-10 seconds typical

---

## Demo Script

### Demo 1: Simple Question (shows basic flow)

**Type:** "What is Colorado's renewable energy standard?"

**Expected:** Answer with citations to C.R.S. § 40-2-124, including:
- 30% requirement for IOUs by 2020
- Different requirements for munis and co-ops
- Sources panel with clickable citations

**Talk through:**
- "Notice the inline citations - hover to see the source"
- "These are from Colorado Revised Statutes"
- "Click 'View Knowledge Graph' to see how we found this"

### Demo 2: Federal Question (shows Federal Register data)

**Type:** "What recent FERC regulations affect Colorado utilities?"

**Expected:** Answer citing Federal Register documents, FERC orders

**Talk through:**
- "Our Federal Register data is very current - scraped from the official API"
- "These links will open directly to the government source"

### Demo 3: Follow-up Question (shows conversation memory)

**After Demo 1, type:** "What about for cooperative utilities?"

**Expected:** Contextual answer about co-op RES requirements

**Talk through:**
- "Notice it understood we were still talking about RES"
- "This is the conversation memory feature"

### Demo 4: Edge Case (shows honest limitations)

**Type:** "What are Xcel Energy's current rates for commercial customers?"

**Expected:** Answer acknowledging we don't have utility tariff data

**Talk through:**
- "This is important - we don't make things up"
- "We clearly say we don't have this data yet"
- "This is where we need your input: should we prioritize utility tariffs?"

---

## Questions to Ask Sasha

### Data Priorities
1. "What sources do you use most frequently in your work?"
2. "Which Colorado PUC docket types matter most to you?"
3. "Do you need utility tariff data? Which utilities?"
4. "How important are WECC and SPP regional standards?"

### Workflow Understanding
1. "Walk us through a typical research question you'd ask"
2. "What makes you trust a source enough to cite it to a client?"
3. "How current does information need to be? Days? Weeks?"

### Feature Priorities
1. "Is the citation format useful as shown?"
2. "Would you use the knowledge graph visualization?"
3. "What would make this tool save you the most time?"

### Deal Breakers
1. "What would make this tool unusable for your work?"
2. "Are there compliance requirements for tools you use?"

---

## Handling Tough Questions

### "Why don't some links work?"

> "Great catch. Some state government sites have restrictions on direct linking. We have the actual document content and can show you the source - you may just need to navigate to their site directly for the PDF. Our Federal Register links work perfectly since they have a proper API."

### "How do I know the information is current?"

> "Currently, our Federal Register data is scraped from the official government API and is up-to-date as of last week. For Colorado statutes, we loaded the 2023 version. This is exactly why we're talking to you - we need to understand how critical freshness is and which sources to prioritize for regular updates."

### "Can this replace Westlaw/LexisNexis?"

> "Not today, and maybe not ever for case law research. But for regulatory research across federal, state, and regional sources - where information is scattered across many government websites - we think we can be significantly faster and more comprehensive. We're focused on regulatory compliance, not litigation research."

### "What about accuracy? This is for legal work."

> "We've built the system to never make things up. If we don't have information, we say so clearly. Every claim is tied to a specific source you can verify. We show confidence levels so you know when to dig deeper. But you're right - for legal work, this should be a research accelerator, not a replacement for attorney judgment."

---

## Closing (2 minutes)

> "What we've shown you today is a working foundation. The pipeline works - you can ask questions and get cited answers. But we deliberately stopped here because we didn't want to build features you don't need or index documents you don't use.

> "The most valuable thing you can give us today is feedback on:
> 1. Does this solve a real problem for you?
> 2. What sources should we prioritize next?
> 3. What features would make this actually useful for your daily work?

> "We'd rather build exactly what you need than guess and get it wrong."

---

## After Demo: Next Steps

If positive feedback:
1. Schedule follow-up for detailed requirements gathering
2. Share list of specific data sources to prioritize
3. Discuss trial period for real-work testing

If concerns:
1. Document specific issues raised
2. Determine if fixable or fundamental
3. Decide whether to pivot or iterate

---

## Technical Backup Info

**URLs (if needed):**
- Live app: https://comask-frontend-app.azurewebsites.net
- API docs: https://comask-backend-app.azurewebsites.net/docs

**Database Stats:**
- 69 documents
- 81 chunks
- 9 source types
- All chunks have vector embeddings

**Response Time:**
- Simple questions: 3-5 seconds
- Complex questions: 5-10 seconds

---

*Talking points prepared: January 27, 2026*
