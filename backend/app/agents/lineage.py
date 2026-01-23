"""Source lineage builder for knowledge graph visualization."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from uuid import uuid4
import re
import structlog

logger = structlog.get_logger()


@dataclass
class GraphNode:
    """Node in the knowledge graph."""
    id: str
    type: str  # 'answer', 'claim', 'source', 'section'
    label: str
    data: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Edge connecting nodes in the knowledge graph."""
    id: str
    source: str  # Node ID
    target: str  # Node ID
    type: str  # 'supports', 'references', 'contains'
    label: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """Complete knowledge graph for an answer."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]

    def to_react_flow(self) -> Dict[str, Any]:
        """Convert to React Flow compatible format."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type,
                    "data": {
                        "label": node.label,
                        **node.data,
                    },
                    "position": node.position or {"x": 0, "y": 0},
                }
                for node in self.nodes
            ],
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "label": edge.label,
                    "data": edge.data,
                    "animated": edge.type == "supports",
                }
                for edge in self.edges
            ],
        }


class LineageBuilder:
    """
    Builds knowledge graphs showing source lineage for answers.

    Creates a visual hierarchy:
    - Answer (root)
      - Claims extracted from answer
        - Sources supporting each claim
          - Sections within sources
    """

    def build(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> KnowledgeGraph:
        """
        Build a knowledge graph for an answer.

        Args:
            answer: The generated answer text
            sources: List of source documents used
            citations: List of citations with claim mappings

        Returns:
            KnowledgeGraph with nodes and edges
        """
        nodes = []
        edges = []

        # Create answer node (root)
        answer_node = GraphNode(
            id="answer",
            type="answer",
            label="Answer",
            data={
                "preview": answer[:200] + "..." if len(answer) > 200 else answer,
                "full_text": answer,
            },
            position={"x": 400, "y": 50},
        )
        nodes.append(answer_node)

        # Extract claims from answer (paragraphs or citation references)
        claims = self._extract_claims(answer, citations)

        # Create claim nodes
        claim_y = 200
        for i, claim in enumerate(claims):
            claim_node = GraphNode(
                id=f"claim_{i}",
                type="claim",
                label=f"Claim {i + 1}",
                data={
                    "text": claim["text"],
                    "preview": claim["text"][:100] + "..." if len(claim["text"]) > 100 else claim["text"],
                },
                position={"x": 200 + (i % 3) * 250, "y": claim_y + (i // 3) * 150},
            )
            nodes.append(claim_node)

            # Connect claim to answer
            edges.append(GraphEdge(
                id=f"answer_to_claim_{i}",
                source="answer",
                target=f"claim_{i}",
                type="contains",
                label="contains",
            ))

        # Create source nodes
        source_y = 450
        source_positions = {}

        for i, source in enumerate(sources):
            source_id = f"source_{i}"
            source_positions[source.get("document_id", str(i))] = source_id

            # Determine node style based on authority level
            authority = source.get("authority_level", "unknown")
            node_style = self._get_authority_style(authority)

            source_node = GraphNode(
                id=source_id,
                type="source",
                label=self._truncate(source.get("title", f"Source {i + 1}"), 40),
                data={
                    "title": source.get("title", "Unknown"),
                    "url": source.get("source_url", "#"),
                    "authority_level": authority,
                    "jurisdiction": source.get("jurisdiction_type", "unknown"),
                    "citation": source.get("citation", ""),
                    "excerpt": source.get("excerpt", "")[:300],
                    "similarity_score": source.get("similarity_score", 0),
                    "style": node_style,
                },
                position={"x": 100 + (i % 4) * 200, "y": source_y + (i // 4) * 150},
            )
            nodes.append(source_node)

        # Connect citations to claims and sources
        for citation in citations:
            claim_idx = citation.get("position_in_answer", 0)
            claim_id = f"claim_{min(claim_idx, len(claims) - 1)}" if claims else None

            # Find matching source
            source_id = None
            doc_id = citation.get("document_id")
            if doc_id and doc_id in source_positions:
                source_id = source_positions[doc_id]
            else:
                # Try to match by title
                for i, source in enumerate(sources):
                    if source.get("title") == citation.get("source_title"):
                        source_id = f"source_{i}"
                        break

            if source_id and claim_id:
                edges.append(GraphEdge(
                    id=f"cite_{uuid4().hex[:8]}",
                    source=claim_id,
                    target=source_id,
                    type="supports",
                    label="supported by",
                    data={
                        "excerpt": citation.get("excerpt", ""),
                        "relevance_score": citation.get("relevance_score", 0),
                    },
                ))
            elif source_id:
                # Connect source directly to answer if no specific claim
                edges.append(GraphEdge(
                    id=f"cite_{uuid4().hex[:8]}",
                    source="answer",
                    target=source_id,
                    type="references",
                    label="references",
                ))

        # Add section nodes if sources have hierarchy
        self._add_section_nodes(nodes, edges, sources, source_positions)

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def _extract_claims(
        self,
        answer: str,
        citations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extract claims/statements from the answer."""
        claims = []

        # Try to split by citation markers first
        citation_pattern = r'\[([^\]]+)\]'
        parts = re.split(citation_pattern, answer)

        current_claim = ""
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Text between citations
                current_claim += part
                if current_claim.strip() and len(current_claim.strip()) > 50:
                    claims.append({"text": current_claim.strip()})
                    current_claim = ""
            # Odd indices are citation matches - skip

        # Add remaining text as a claim
        if current_claim.strip() and len(current_claim.strip()) > 50:
            claims.append({"text": current_claim.strip()})

        # If no claims extracted, split by paragraphs
        if not claims:
            paragraphs = [p.strip() for p in answer.split('\n\n') if p.strip()]
            for p in paragraphs[:5]:  # Limit to 5 claims
                if len(p) > 30:
                    claims.append({"text": p})

        # If still no claims, use the whole answer
        if not claims:
            claims.append({"text": answer[:500]})

        return claims[:5]  # Limit to 5 claims for readability

    def _get_authority_style(self, authority: Any) -> Dict[str, str]:
        """Get visual style based on authority level."""
        styles = {
            "FEDERAL": {"background": "#1e40af", "color": "#ffffff", "border": "#1e3a8a"},
            "STATE": {"background": "#059669", "color": "#ffffff", "border": "#047857"},
            "REGIONAL": {"background": "#7c3aed", "color": "#ffffff", "border": "#6d28d9"},
            "UTILITY": {"background": "#ea580c", "color": "#ffffff", "border": "#c2410c"},
            1: {"background": "#1e40af", "color": "#ffffff", "border": "#1e3a8a"},
            2: {"background": "#059669", "color": "#ffffff", "border": "#047857"},
            3: {"background": "#7c3aed", "color": "#ffffff", "border": "#6d28d9"},
            4: {"background": "#ea580c", "color": "#ffffff", "border": "#c2410c"},
        }
        return styles.get(authority, {"background": "#6b7280", "color": "#ffffff", "border": "#4b5563"})

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def _add_section_nodes(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        sources: List[Dict[str, Any]],
        source_positions: Dict[str, str],
    ):
        """Add section nodes for sources with hierarchy information."""
        section_y = 650

        for i, source in enumerate(sources):
            hierarchy = source.get("section_hierarchy", [])
            if not hierarchy or len(hierarchy) < 2:
                continue

            source_id = f"source_{i}"

            # Add deepest section as a node
            section_text = hierarchy[-1] if hierarchy else ""
            if section_text:
                section_id = f"section_{i}"
                section_node = GraphNode(
                    id=section_id,
                    type="section",
                    label=self._truncate(section_text, 30),
                    data={
                        "hierarchy": hierarchy,
                        "full_path": " > ".join(hierarchy),
                    },
                    position={"x": 100 + (i % 4) * 200, "y": section_y},
                )
                nodes.append(section_node)

                edges.append(GraphEdge(
                    id=f"source_to_section_{i}",
                    source=source_id,
                    target=section_id,
                    type="contains",
                    label="section",
                ))


def build_lineage_graph(
    answer: str,
    sources: List[Dict[str, Any]],
    citations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a knowledge graph for source lineage visualization.

    Args:
        answer: The generated answer
        sources: Source documents
        citations: Citations with claim mappings

    Returns:
        React Flow compatible graph data
    """
    builder = LineageBuilder()
    graph = builder.build(answer, sources, citations)
    return graph.to_react_flow()
