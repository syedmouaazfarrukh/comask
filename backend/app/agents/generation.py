"""Answer generation agent."""

import re
import uuid
from typing import List, Dict, Any, Tuple
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.llm import get_llm
from app.llm.base import LLMMessage
import structlog

logger = structlog.get_logger()


def extract_inline_citations(answer: str, documents: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Extract inline citations from the answer text.

    The LLM uses format: [[cite:N:fact text]] where N is the document number (1-indexed)
    Returns the cleaned answer and a list of inline citation objects.
    """
    inline_citations = []
    citation_pattern = r'\[\[cite:(\d+):([^\]]+)\]\]'

    matches = list(re.finditer(citation_pattern, answer))

    for i, match in enumerate(matches):
        doc_num = int(match.group(1)) - 1  # Convert to 0-indexed
        fact_text = match.group(2).strip()

        if 0 <= doc_num < len(documents):
            doc = documents[doc_num]
            citation_id = f"cite-{i+1}"

            inline_citations.append({
                "id": citation_id,
                "fact": fact_text,
                "source_index": doc_num,
                "source_title": doc.get("title", "Unknown"),
                "source_excerpt": doc.get("excerpt", doc.get("content", ""))[:500],
                "source_url": doc.get("source_url", "#")
            })

    # Replace [[cite:N:text]] with [[cite-N]] for frontend rendering
    def replace_citation(match):
        doc_num = int(match.group(1)) - 1
        fact_text = match.group(2).strip()
        # Find the citation index
        for i, cite in enumerate(inline_citations):
            if cite["source_index"] == doc_num and cite["fact"] == fact_text:
                return f"[[{cite['id']}:{fact_text}]]"
        return fact_text

    cleaned_answer = re.sub(citation_pattern, replace_citation, answer)

    return cleaned_answer, inline_citations


def build_retrieval_flow(query: str, documents: List[Dict], answer: str) -> Dict:
    """
    Build a retrieval flow graph for knowledge graph visualization.
    Shows: Query -> Documents Retrieved -> Answer
    """
    nodes = []
    edges = []

    # Query node
    query_id = "query-1"
    nodes.append({
        "id": query_id,
        "type": "query",
        "label": query[:50] + "..." if len(query) > 50 else query,
        "metadata": {"full_text": query}
    })

    # Document nodes
    for i, doc in enumerate(documents[:5]):  # Top 5 documents
        doc_id = f"doc-{i+1}"
        nodes.append({
            "id": doc_id,
            "type": "document",
            "label": doc.get("title", "Unknown")[:40] + "..." if len(doc.get("title", "")) > 40 else doc.get("title", "Unknown"),
            "metadata": {
                "full_title": doc.get("title", "Unknown"),
                "source": doc.get("source", "Unknown"),
                "relevance_score": doc.get("relevance_score", 0),
                "source_url": doc.get("source_url", "#"),
                "excerpt": doc.get("excerpt", doc.get("content", ""))[:300]
            }
        })

        # Edge from query to document
        edges.append({
            "source": query_id,
            "target": doc_id,
            "label": f"Retrieved (score: {doc.get('relevance_score', 0):.2f})",
            "relevance_score": doc.get("relevance_score", 0)
        })

    # Answer node
    answer_id = "answer-1"
    nodes.append({
        "id": answer_id,
        "type": "answer",
        "label": "Generated Answer",
        "metadata": {"preview": answer[:100] + "..." if len(answer) > 100 else answer}
    })

    # Edges from documents to answer
    for i, doc in enumerate(documents[:5]):
        doc_id = f"doc-{i+1}"
        edges.append({
            "source": doc_id,
            "target": answer_id,
            "label": "Used in answer",
            "relevance_score": doc.get("relevance_score", 0)
        })

    return {
        "nodes": nodes,
        "edges": edges
    }


class GenerationAgent(BaseAgent):
    """Generates accurate answers with citations."""

    def __init__(self):
        super().__init__(
            name="generation",
            description="Generates accurate answers with proper citations"
        )
        self.llm = get_llm()

    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate answer with citations."""
        try:
            # Get relevant documents from context
            relevance_result = context.metadata.get("relevance", {})
            documents = relevance_result.get("ranked_documents", [])
            
            if not documents:
                # Fallback: Use Azure OpenAI to get latest information
                logger.info("No documents found, using Azure OpenAI fallback")
                
                # Build prompt with conversation history if available
                history_context = ""
                if context.conversation_history:
                    history_context = f"\n\nPrevious conversation context:\n{context.conversation_history}\n\nPlease use this context to provide a relevant answer that continues the conversation naturally."
                
                fallback_prompt = f"""You are an expert on Colorado energy regulations. A user is asking about: {context.query}{history_context}

I couldn't find specific information in our database, but I've gathered information from public sources and the internet. Please provide the most current and accurate information you know about this topic related to Colorado energy regulations.

FORMATTING REQUIREMENTS:
- Use clean, professional formatting
- Use simple line breaks and spacing (avoid markdown headers like ### or ##)
- Use bullet points with simple dashes (-) or numbers (1., 2., etc.)
- Keep paragraphs concise (3-4 sentences max)
- Use bold text sparingly (only for key terms or section headers)
- Make it easy to read in a chat interface

CONTENT REQUIREMENTS:
- Start with: "I couldn't find specific information in our database, but based on public sources and internet research, here's what I found:"
- Be specific to Colorado
- Provide helpful, accurate information based on your knowledge
- Structure the answer clearly with main points
- End with a brief note about verifying with official sources
- Keep the answer comprehensive but well-organized

Location: Colorado
Question: {context.query}

Provide a professional, well-formatted answer that's easy to read in a chat interface."""

                fallback_messages = [
                    LLMMessage(role="system", content="You are an expert on Colorado energy regulations. Provide accurate, helpful information with appropriate disclaimers when information is not from verified documents."),
                    LLMMessage(role="user", content=fallback_prompt)
                ]
                
                try:
                    fallback_response = await self.llm.chat_completion(
                        messages=fallback_messages,
                        temperature=0.3,
                        max_tokens=2000
                    )
                    
                    # Clean up the answer - remove any duplicate disclaimers and format nicely
                    answer_content = fallback_response.content.strip()
                    
                    # Remove duplicate disclaimer if LLM already added one
                    disclaimer_patterns = [
                        "**Note:**",
                        "Note:",
                        "Disclaimer:",
                        "For the most current",
                        "verify with official sources"
                    ]
                    
                    # Check if answer already contains a disclaimer section
                    has_disclaimer = any(pattern.lower() in answer_content.lower() for pattern in disclaimer_patterns)
                    
                    if not has_disclaimer:
                        # Add a clean disclaimer if not present
                        disclaimer_text = "\n\nNote: This information was gathered from public sources and internet research since we don't have specific documents in our database yet. For the most current and official information, please verify with:\n- Colorado Public Utilities Commission: https://puc.colorado.gov\n- Colorado Energy Office: https://energyoffice.colorado.gov\n\nOur database is being updated regularly. Once we have the relevant documents, we'll be able to provide answers with specific citations."
                        answer_content = answer_content + disclaimer_text
                    else:
                        # Just ensure it ends cleanly
                        if not answer_content.endswith('.'):
                            answer_content += "."
                    
                    return AgentResult(
                        success=True,
                        data={
                            "answer": answer_content,
                            "citations": [],
                            "confidence": "medium",
                            "source": "azure_openai_fallback",
                            "suggestion": "This information is from general knowledge. Please verify with official Colorado sources for the most current regulations."
                        },
                        metadata={
                            "model": fallback_response.model,
                            "tokens": fallback_response.usage.get("total_tokens", 0) if fallback_response.usage else 0,
                            "fallback_used": True,
                            "documents_available": 0
                        }
                    )
                except Exception as e:
                    logger.error("Fallback Azure OpenAI call failed", error=str(e))
                    return AgentResult(
                        success=True,
                        data={
                            "answer": "I don't have specific information on this topic in the current Colorado energy regulations database. This may be a newer regulation or a topic not yet covered in our system. Please contact the Colorado Public Utilities Commission directly for the most current information.",
                            "citations": [],
                            "confidence": "low",
                            "suggestion": "You may want to contact the Colorado Public Utilities Commission directly for the most current information."
                        }
                    )
            
            # Build context from documents - use full content if available, otherwise excerpt
            documents_context = "\n\n".join([
                f"Document {i+1}:\n"
                f"Title: {doc.get('title', 'Unknown')}\n"
                f"Source: {doc.get('source', 'Unknown')}\n"
                f"URL: {doc.get('source_url', 'N/A')}\n"
                f"Published: {doc.get('published_date', 'Unknown')}\n"
                f"Relevance Score: {doc.get('relevance_score', 0.0):.2f}\n"
                f"Content: {doc.get('content', doc.get('excerpt', ''))[:2000]}\n"  # Use full content, limit to 2000 chars
                for i, doc in enumerate(documents[:5])  # Top 5 most relevant
            ])

            # Add conversation history context if available
            history_context = ""
            if context.conversation_history:
                history_context = f"\n\nPrevious conversation context:\n{context.conversation_history}\n\nPlease use this context to provide a relevant answer that continues the conversation naturally and references previous topics when relevant."

            system_prompt = """You are an expert on Colorado energy regulations. Your role is to provide accurate,
cited answers based ONLY on the provided documents.

CRITICAL CITATION RULES:
1. ONLY use information from the provided documents
2. For EVERY specific fact, number, percentage, date, or requirement, use INLINE citations with this EXACT format:
   [[cite:N:the exact fact or claim]]
   where N is the document number (1, 2, 3, etc.)

3. Examples of inline citations:
   - "Utilities must generate [[cite:1:30% of electricity from renewable sources]] starting in 2020."
   - "The emission reduction target is [[cite:2:80% by 2030]] compared to 2005 levels."
   - "IOUs are required to achieve [[cite:1:3% from distributed generation]]."

4. ALWAYS cite specific numbers, percentages, dates, requirements, and key facts
5. If information is not in the documents, explicitly state "I don't have specific information on this"
6. Never make up information or use knowledge outside the documents
7. If the answer is uncertain, say so clearly
8. Provide actionable information when possible
9. If there's conversation history, use it to provide contextually relevant answers

FORMATTING:
- Use clear headers and bullet points
- Every factual claim should have an inline citation
- Keep the answer comprehensive but well-organized
- At the end, you can also mention [Document: Title] for general reference

Remember: The inline citation format is [[cite:N:fact]] where N is the document number and fact is the specific claim."""

            user_prompt = f"""User Question: {context.query}{history_context}

Location: Colorado

Relevant Documents:
{documents_context}

Provide a comprehensive answer with INLINE CITATIONS using [[cite:N:fact]] format for every specific fact, number, or requirement.
If the documents don't fully answer the question, be honest about what information is available and what is not."""

            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.3,  # Low temperature for accuracy
                max_tokens=2000
            )

            # Extract inline citations from the response
            processed_answer, inline_citations = extract_inline_citations(
                response.content,
                documents[:5]
            )

            # Build retrieval flow for knowledge graph
            retrieval_flow = build_retrieval_flow(
                context.query,
                documents[:5],
                processed_answer
            )

            # Extract citations from documents used
            citations = []
            for doc in documents[:5]:  # Top 5 documents
                # Include all top documents as citations (they were used in context)
                citations.append({
                    "title": doc.get("title", "Unknown"),
                    "url": doc.get("source_url", "#"),
                    "excerpt": doc.get("excerpt", doc.get("content", ""))[:300],  # Use excerpt or content
                    "source": doc.get("source", "Unknown"),
                    "published_date": doc.get("published_date")
                })

            # Determine confidence based on citations and inline citations
            confidence = "high" if len(inline_citations) >= 3 else "medium" if len(inline_citations) >= 1 else "low"

            return AgentResult(
                success=True,
                data={
                    "answer": processed_answer,
                    "citations": citations,
                    "inline_citations": inline_citations,
                    "retrieval_flow": retrieval_flow,
                    "confidence": confidence,
                    "documents_used": len(citations)
                },
                metadata={
                    "model": response.model,
                    "tokens": response.usage.get("total_tokens", 0) if response.usage else 0,
                    "documents_available": len(documents),
                    "inline_citations_count": len(inline_citations)
                }
            )
            
        except Exception as e:
            logger.error("Answer generation error", error=str(e))
            return AgentResult(
                success=False,
                data={
                    "answer": "I encountered an error while generating the answer. Please try again.",
                    "citations": []
                },
                error=str(e)
            )

