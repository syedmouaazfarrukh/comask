"""
eCFR (Electronic Code of Federal Regulations) API Client.

Fetches federal regulations from the official eCFR API.
Relevant titles:
- Title 18: Conservation of Power and Water Resources
- Title 40: Protection of Environment (energy-related parts)
"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import asyncio
import structlog
from pydantic import BaseModel

from app.scrapers.base import BaseScraper, ScrapedDocument
from app.config import settings
from app.db.models import AuthorityLevel, JurisdictionType, DocumentType

logger = structlog.get_logger()


class ECFRSection(BaseModel):
    """Model for an eCFR section."""
    title_number: int
    title_name: str
    chapter: Optional[str] = None
    part_number: Optional[int] = None
    part_name: Optional[str] = None
    section_number: Optional[str] = None
    section_name: Optional[str] = None
    content: str
    effective_date: Optional[date] = None
    hierarchy: List[str] = []


class ECFRClient:
    """
    Client for the eCFR API.

    API Documentation: https://www.ecfr.gov/developers/documentation/api/v1
    """

    BASE_URL = "https://www.ecfr.gov/api/versioner/v1"

    # Energy-relevant titles and parts
    ENERGY_TITLES = {
        18: {  # Conservation of Power and Water Resources
            "name": "Conservation of Power and Water Resources",
            "parts": [
                (1, 399),  # All parts - FERC regulations
            ]
        },
        40: {  # Protection of Environment
            "name": "Protection of Environment",
            "parts": [
                (60, 99),   # Air quality standards
                (260, 299), # Hazardous waste
            ]
        },
    }

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.ecfr_api_base_url or self.BASE_URL
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            headers={"User-Agent": settings.scraper_user_agent},
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_title_structure(self, title: int) -> Dict[str, Any]:
        """
        Get the structure of a title (chapters, parts, sections).

        Args:
            title: CFR title number

        Returns:
            Title structure as dictionary
        """
        # Use 'current' instead of a specific date to get the most recent version
        url = f"{self.base_url}/structure/current/title-{title}.json"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("eCFR structure request failed", title=title, status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("eCFR structure request error", title=title, error=str(e))
            raise

    async def get_full_text(
        self,
        title: int,
        part: Optional[int] = None,
        section: Optional[str] = None,
        as_of_date: Optional[date] = None,
    ) -> str:
        """
        Get the full text of a title, part, or section.

        Args:
            title: CFR title number
            part: Optional part number
            section: Optional section number (e.g., "1.1")
            as_of_date: Date for historical version (defaults to current)

        Returns:
            Full text content
        """
        # Use 'current' or a specific date
        ref_date = as_of_date.isoformat() if as_of_date else "current"

        # Build the URL path
        path = f"/full/{ref_date}/title-{title}"
        if part:
            path += f"/part-{part}"
            if section:
                path += f"/section-{part}.{section}"

        url = f"{self.base_url}{path}.xml"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("eCFR content not found", title=title, part=part, section=section)
                return ""
            logger.error("eCFR full text request failed", title=title, status=e.response.status_code)
            raise

    async def search(
        self,
        query: str,
        title: Optional[int] = None,
        per_page: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Search eCFR content.

        Args:
            query: Search query
            title: Optional title to limit search
            per_page: Results per page
            page: Page number

        Returns:
            Search results
        """
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
        }
        if title:
            params["title"] = title

        url = f"{self.base_url}/search"

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("eCFR search failed", query=query, error=str(e))
            raise

    async def get_versions(self, title: int, part: int) -> List[Dict[str, Any]]:
        """
        Get version history for a part.

        Args:
            title: CFR title number
            part: Part number

        Returns:
            List of version information
        """
        url = f"{self.base_url}/versions/title-{title}/part-{part}.json"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json().get("content_versions", [])
        except Exception as e:
            logger.error("eCFR versions request failed", title=title, part=part, error=str(e))
            return []


class ECFRScraper(BaseScraper):
    """
    Scraper for eCFR federal regulations.

    Focuses on energy-related titles:
    - Title 18: FERC regulations
    - Title 40: EPA environmental regulations (energy parts)
    """

    def __init__(self):
        self.source_name = "eCFR"
        self.base_url = "https://www.ecfr.gov"
        self.client = ECFRClient()

    async def scrape(self) -> List[ScrapedDocument]:
        """
        Scrape energy-related federal regulations from eCFR.

        Returns:
            List of scraped documents
        """
        documents = []

        for title_num, title_info in ECFRClient.ENERGY_TITLES.items():
            logger.info("Scraping eCFR title", title=title_num, name=title_info["name"])

            try:
                # Get title structure
                structure = await self.client.get_title_structure(title_num)

                # Process each relevant part
                for part_range in title_info["parts"]:
                    start_part, end_part = part_range
                    parts = self._extract_parts_from_structure(structure, start_part, end_part)

                    for part in parts:
                        part_docs = await self._scrape_part(title_num, title_info["name"], part)
                        documents.extend(part_docs)

                        # Respect rate limits
                        await asyncio.sleep(settings.scraper_delay_seconds)

            except Exception as e:
                logger.error("Error scraping eCFR title", title=title_num, error=str(e))
                continue

        logger.info("eCFR scraping complete", total_documents=len(documents))
        return documents

    def _extract_parts_from_structure(
        self,
        structure: Dict[str, Any],
        start_part: int,
        end_part: int,
    ) -> List[Dict[str, Any]]:
        """Extract parts within range from title structure."""
        parts = []

        def find_parts(node: Dict[str, Any]):
            if node.get("type") == "part":
                try:
                    part_num = int(node.get("identifier", "0"))
                    if start_part <= part_num <= end_part:
                        parts.append(node)
                except (ValueError, TypeError):
                    pass

            for child in node.get("children", []):
                find_parts(child)

        find_parts(structure)
        return parts

    async def _scrape_part(
        self,
        title_num: int,
        title_name: str,
        part: Dict[str, Any],
    ) -> List[ScrapedDocument]:
        """Scrape a single part and its sections."""
        documents = []

        part_num = part.get("identifier")
        part_name = part.get("label", f"Part {part_num}")

        logger.debug("Scraping eCFR part", title=title_num, part=part_num)

        try:
            # Get full text for the part
            content = await self.client.get_full_text(title_num, int(part_num))

            if content:
                # Create document for the part
                doc = ScrapedDocument(
                    title=f"{title_num} CFR Part {part_num} - {part_name}",
                    content=self._clean_xml_content(content),
                    source_url=f"https://www.ecfr.gov/current/title-{title_num}/part-{part_num}",
                    document_type=DocumentType.REGULATION.value,
                    published_date=date.today(),
                    effective_date=date.today(),
                    source="eCFR",
                    metadata={
                        "title_number": title_num,
                        "title_name": title_name,
                        "part_number": part_num,
                        "part_name": part_name,
                        "authority_level": AuthorityLevel.FEDERAL.value,
                        "jurisdiction_type": JurisdictionType.FEDERAL.value,
                        "citation": f"{title_num} CFR Part {part_num}",
                    }
                )
                documents.append(doc)

        except Exception as e:
            logger.error("Error scraping eCFR part", title=title_num, part=part_num, error=str(e))

        return documents

    def _clean_xml_content(self, xml_content: str) -> str:
        """Extract text content from XML, removing tags."""
        import re

        # Remove XML tags but keep content
        text = re.sub(r'<[^>]+>', ' ', xml_content)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        urls = []
        for title_num in ECFRClient.ENERGY_TITLES:
            urls.append(f"https://www.ecfr.gov/current/title-{title_num}")
        return urls


async def fetch_ecfr_regulations(
    titles: Optional[List[int]] = None,
) -> List[ScrapedDocument]:
    """
    Convenience function to fetch eCFR regulations.

    Args:
        titles: Optional list of title numbers (defaults to energy titles)

    Returns:
        List of scraped documents
    """
    scraper = ECFRScraper()
    try:
        return await scraper.scrape()
    finally:
        await scraper.client.close()
