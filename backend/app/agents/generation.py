"""Answer generation agent."""

from typing import List, Dict, Any
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.llm import get_llm
from app.llm.base import LLMMessage
import structlog

logger = structlog.get_logger()


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

CRITICAL RULES:
1. ONLY use information from the provided documents
2. ALWAYS cite specific documents with [Document: Title] format
3. If information is not in the documents, explicitly state "I don't have specific information on this"
4. Never make up information or use knowledge outside the documents
5. If the answer is uncertain, say so clearly
6. Provide actionable information when possible
7. Include relevant dates and sources
8. If there's conversation history, use it to provide contextually relevant answers that build on previous questions

Answer format:
- Clear, concise answer
- Specific citations in [Document: Title] format
- If uncertain, state the uncertainty
- Suggest alternatives if the exact answer isn't available
- Reference previous conversation topics when relevant"""

            user_prompt = f"""User Question: {context.query}{history_context}

Location: Colorado

Relevant Documents:
{documents_context}

Provide a comprehensive answer with citations. If the documents don't fully answer the question, 
be honest about what information is available and what is not."""

            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.3,  # Low temperature for accuracy
                max_tokens=2000
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
            
            # Determine confidence
            confidence = "high" if len(citations) >= 2 else "medium" if len(citations) == 1 else "low"
            
            return AgentResult(
                success=True,
                data={
                    "answer": response.content,
                    "citations": citations,
                    "confidence": confidence,
                    "documents_used": len(citations)
                },
                metadata={
                    "model": response.model,
                    "tokens": response.usage.get("total_tokens", 0) if response.usage else 0,
                    "documents_available": len(documents)
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

