"""Confidence scoring system for answer quality assessment."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import structlog

from app.db.models import AuthorityLevel

logger = structlog.get_logger()


class ConfidenceLevel(Enum):
    """Confidence levels for answers."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ConfidenceFactor:
    """Individual factor contributing to confidence score."""
    name: str
    score: float  # 0.0 - 1.0
    weight: float  # How much this factor matters
    explanation: str


@dataclass
class ConfidenceScore:
    """Complete confidence assessment."""
    level: ConfidenceLevel
    score: float  # 0.0 - 1.0
    factors: List[ConfidenceFactor]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "level": self.level.value,
            "score": round(self.score, 2),
            "factors": [
                {
                    "name": f.name,
                    "score": round(f.score, 2),
                    "weight": f.weight,
                    "explanation": f.explanation,
                }
                for f in self.factors
            ],
            "explanation": self.explanation,
        }


class ConfidenceScorer:
    """
    Calculates confidence scores for answers based on multiple factors.

    Factors considered:
    1. Source authority (federal > state > regional > utility)
    2. Source recency (newer is better)
    3. Source quantity (multiple corroborating sources)
    4. Query-source similarity (how well sources match the query)
    5. Source agreement (do sources agree or conflict)
    6. Citation coverage (how much of the answer is cited)
    """

    # Thresholds for confidence levels
    HIGH_THRESHOLD = 0.75
    MEDIUM_THRESHOLD = 0.45

    def score(
        self,
        sources: List[Dict[str, Any]],
        query_similarities: List[float],
        answer_has_citations: bool = True,
        sources_agree: bool = True,
    ) -> ConfidenceScore:
        """
        Calculate confidence score for an answer.

        Args:
            sources: List of source documents with metadata
            query_similarities: Similarity scores between query and each source
            answer_has_citations: Whether the answer includes citations
            sources_agree: Whether the sources provide consistent information

        Returns:
            ConfidenceScore with level, score, and explanation
        """
        factors = []

        # Factor 1: Source Authority
        authority_factor = self._score_authority(sources)
        factors.append(authority_factor)

        # Factor 2: Source Recency
        recency_factor = self._score_recency(sources)
        factors.append(recency_factor)

        # Factor 3: Source Quantity
        quantity_factor = self._score_quantity(sources)
        factors.append(quantity_factor)

        # Factor 4: Query-Source Similarity
        similarity_factor = self._score_similarity(query_similarities)
        factors.append(similarity_factor)

        # Factor 5: Source Agreement
        agreement_factor = self._score_agreement(sources_agree)
        factors.append(agreement_factor)

        # Factor 6: Citation Coverage
        citation_factor = self._score_citations(answer_has_citations, len(sources))
        factors.append(citation_factor)

        # Calculate weighted average
        total_weight = sum(f.weight for f in factors)
        weighted_score = sum(f.score * f.weight for f in factors) / total_weight if total_weight > 0 else 0

        # Determine level
        if weighted_score >= self.HIGH_THRESHOLD:
            level = ConfidenceLevel.HIGH
        elif weighted_score >= self.MEDIUM_THRESHOLD:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        # Generate explanation
        explanation = self._generate_explanation(level, factors, sources)

        return ConfidenceScore(
            level=level,
            score=weighted_score,
            factors=factors,
            explanation=explanation,
        )

    def _score_authority(self, sources: List[Dict[str, Any]]) -> ConfidenceFactor:
        """Score based on source authority levels."""
        if not sources:
            return ConfidenceFactor(
                name="Source Authority",
                score=0.0,
                weight=0.25,
                explanation="No sources found",
            )

        # Map authority levels to scores
        authority_scores = {
            AuthorityLevel.FEDERAL.value: 1.0,
            AuthorityLevel.STATE.value: 0.8,
            AuthorityLevel.REGIONAL.value: 0.6,
            AuthorityLevel.UTILITY.value: 0.4,
            1: 1.0,  # FEDERAL enum value
            2: 0.8,  # STATE enum value
            3: 0.6,  # REGIONAL enum value
            4: 0.4,  # UTILITY enum value
        }

        scores = []
        for source in sources:
            authority = source.get("authority_level")
            if authority is not None:
                scores.append(authority_scores.get(authority, 0.5))
            else:
                scores.append(0.5)  # Unknown authority

        avg_score = sum(scores) / len(scores) if scores else 0.5

        # Determine explanation
        has_federal = any(
            source.get("authority_level") in [AuthorityLevel.FEDERAL.value, 1]
            for source in sources
        )
        has_state = any(
            source.get("authority_level") in [AuthorityLevel.STATE.value, 2]
            for source in sources
        )

        if has_federal:
            explanation = "Includes federal regulations (highest authority)"
        elif has_state:
            explanation = "Based on Colorado state sources"
        else:
            explanation = "Based on regional or utility sources"

        return ConfidenceFactor(
            name="Source Authority",
            score=avg_score,
            weight=0.25,
            explanation=explanation,
        )

    def _score_recency(self, sources: List[Dict[str, Any]]) -> ConfidenceFactor:
        """Score based on how recent the sources are."""
        if not sources:
            return ConfidenceFactor(
                name="Source Recency",
                score=0.0,
                weight=0.15,
                explanation="No sources to evaluate",
            )

        from datetime import date

        today = date.today()
        scores = []
        most_recent = None

        for source in sources:
            pub_date = source.get("published_date")
            if pub_date:
                if isinstance(pub_date, str):
                    try:
                        pub_date = date.fromisoformat(pub_date.split("T")[0])
                    except:
                        continue

                days_old = (today - pub_date).days
                # Score decays over 2 years
                score = max(0, 1.0 - (days_old / 730))
                scores.append(score)

                if most_recent is None or pub_date > most_recent:
                    most_recent = pub_date

        if not scores:
            return ConfidenceFactor(
                name="Source Recency",
                score=0.5,
                weight=0.15,
                explanation="Publication dates not available",
            )

        avg_score = sum(scores) / len(scores)

        if most_recent:
            days_ago = (today - most_recent).days
            if days_ago < 30:
                explanation = "Sources are very recent (within 30 days)"
            elif days_ago < 180:
                explanation = "Sources are relatively recent (within 6 months)"
            elif days_ago < 365:
                explanation = "Sources are from the past year"
            else:
                explanation = f"Most recent source is {days_ago // 365} year(s) old"
        else:
            explanation = "Source dates unknown"

        return ConfidenceFactor(
            name="Source Recency",
            score=avg_score,
            weight=0.15,
            explanation=explanation,
        )

    def _score_quantity(self, sources: List[Dict[str, Any]]) -> ConfidenceFactor:
        """Score based on number of corroborating sources."""
        count = len(sources)

        if count == 0:
            score = 0.0
            explanation = "No sources found"
        elif count == 1:
            score = 0.4
            explanation = "Based on a single source"
        elif count == 2:
            score = 0.7
            explanation = "Supported by 2 sources"
        elif count <= 4:
            score = 0.85
            explanation = f"Supported by {count} corroborating sources"
        else:
            score = 1.0
            explanation = f"Strongly supported by {count} sources"

        return ConfidenceFactor(
            name="Source Quantity",
            score=score,
            weight=0.20,
            explanation=explanation,
        )

    def _score_similarity(self, similarities: List[float]) -> ConfidenceFactor:
        """Score based on query-source similarity."""
        if not similarities:
            return ConfidenceFactor(
                name="Query Match",
                score=0.0,
                weight=0.20,
                explanation="Could not match query to sources",
            )

        avg_similarity = sum(similarities) / len(similarities)
        max_similarity = max(similarities)

        if max_similarity >= 0.9:
            explanation = "Excellent match between query and sources"
        elif max_similarity >= 0.75:
            explanation = "Good match between query and sources"
        elif max_similarity >= 0.6:
            explanation = "Moderate match between query and sources"
        else:
            explanation = "Weak match - sources may not directly address query"

        return ConfidenceFactor(
            name="Query Match",
            score=avg_similarity,
            weight=0.20,
            explanation=explanation,
        )

    def _score_agreement(self, sources_agree: bool) -> ConfidenceFactor:
        """Score based on whether sources agree."""
        if sources_agree:
            return ConfidenceFactor(
                name="Source Agreement",
                score=1.0,
                weight=0.10,
                explanation="Sources provide consistent information",
            )
        else:
            return ConfidenceFactor(
                name="Source Agreement",
                score=0.3,
                weight=0.10,
                explanation="Sources may have conflicting information",
            )

    def _score_citations(self, has_citations: bool, source_count: int) -> ConfidenceFactor:
        """Score based on citation coverage."""
        if not has_citations:
            return ConfidenceFactor(
                name="Citation Coverage",
                score=0.2,
                weight=0.10,
                explanation="Answer lacks specific citations",
            )

        if source_count >= 3:
            score = 1.0
            explanation = "Answer is well-cited with multiple sources"
        elif source_count >= 1:
            score = 0.7
            explanation = "Answer includes citations"
        else:
            score = 0.3
            explanation = "Limited citation coverage"

        return ConfidenceFactor(
            name="Citation Coverage",
            score=score,
            weight=0.10,
            explanation=explanation,
        )

    def _generate_explanation(
        self,
        level: ConfidenceLevel,
        factors: List[ConfidenceFactor],
        sources: List[Dict[str, Any]],
    ) -> str:
        """Generate a human-readable confidence explanation."""
        # Find strongest and weakest factors
        sorted_factors = sorted(factors, key=lambda f: f.score, reverse=True)
        strongest = sorted_factors[0]
        weakest = sorted_factors[-1]

        if level == ConfidenceLevel.HIGH:
            explanation = (
                f"High confidence: {strongest.explanation}. "
                f"Answer is based on {len(sources)} authoritative source(s)."
            )
        elif level == ConfidenceLevel.MEDIUM:
            explanation = (
                f"Medium confidence: {strongest.explanation}, "
                f"but {weakest.explanation.lower()}."
            )
        else:
            explanation = (
                f"Low confidence: {weakest.explanation}. "
                "Consider verifying with official sources."
            )

        return explanation


# Convenience function
def calculate_confidence(
    sources: List[Dict[str, Any]],
    similarities: List[float],
    answer_has_citations: bool = True,
    sources_agree: bool = True,
) -> ConfidenceScore:
    """Calculate confidence score for an answer."""
    scorer = ConfidenceScorer()
    return scorer.score(sources, similarities, answer_has_citations, sources_agree)
