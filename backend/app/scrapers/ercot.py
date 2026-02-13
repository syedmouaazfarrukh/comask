"""
ERCOT (Electric Reliability Council of Texas) Scraper.

Fetches ERCOT market rules, nodal protocols, and operating guides.
Source: ERCOT website (www.ercot.com)
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from datetime import date
import asyncio
import re
import structlog

from app.scrapers.base import BaseScraper, ScrapedDocument
from app.config import settings
from app.db.models import AuthorityLevel, JurisdictionType, DocumentType

logger = structlog.get_logger()


class ERCOTScraper(BaseScraper):
    """
    Scraper for ERCOT protocols, market rules, and operating guides.

    ERCOT operates the Texas Interconnection and manages the wholesale
    electricity market for most of Texas.
    """

    BASE_URL = "https://www.ercot.com"

    # Key ERCOT document sections to scrape
    SECTIONS = {
        "protocols": {
            "name": "ERCOT Nodal Protocols",
            "url": "/mktrules/nprotocols/current",
            "description": "Current Nodal Protocol sections governing ERCOT market operations",
        },
        "guides": {
            "name": "ERCOT Operating Guides",
            "url": "/mktrules/guides",
            "description": "Operating guides for market participants",
        },
        "market_rules": {
            "name": "ERCOT Market Rules",
            "url": "/mktrules",
            "description": "Market rules and procedures overview",
        },
    }

    def __init__(self):
        self.source_name = "ERCOT"
        self.base_url = self.BASE_URL
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=15.0),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            follow_redirects=True,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def scrape(self) -> List[ScrapedDocument]:
        """Scrape ERCOT protocols and market rules."""
        documents = []

        for section_key, section_info in self.SECTIONS.items():
            logger.info("Scraping ERCOT section", section=section_key, name=section_info["name"])

            try:
                section_docs = await self._scrape_section(section_key, section_info)
                documents.extend(section_docs)
            except Exception as e:
                logger.error(
                    "Error scraping ERCOT section",
                    section=section_key,
                    error=str(e),
                )
                continue

            await asyncio.sleep(settings.scraper_delay_seconds)

        logger.info("ERCOT scraping complete", total_documents=len(documents))
        return documents

    async def _scrape_section(
        self,
        section_key: str,
        section_info: Dict[str, Any],
    ) -> List[ScrapedDocument]:
        """Scrape an ERCOT section page and extract documents."""
        documents = []

        section_url = f"{self.BASE_URL}{section_info['url']}"

        try:
            response = await self.client.get(section_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract the main page content as a document
            content = self._extract_content(soup)
            if content and len(content) > 200:
                doc = ScrapedDocument(
                    title=section_info["name"],
                    content=content,
                    source_url=section_url,
                    document_type=DocumentType.STANDARD.value,
                    published_date=date.today(),
                    source="ERCOT",
                    metadata={
                        "section": section_key,
                        "description": section_info["description"],
                        "authority_level": AuthorityLevel.REGIONAL.value,
                        "jurisdiction_type": JurisdictionType.ERCOT.value,
                        "hierarchy": ["ERCOT", section_info["name"]],
                    },
                )
                documents.append(doc)

            # Find sub-page links for protocol sections
            page_links = soup.find_all("a", href=True)
            protocol_links = []

            for link in page_links:
                href = link.get("href", "")
                text = link.get_text(strip=True)

                # Look for protocol section links or document links
                if (
                    "/mktrules/" in href
                    and href != section_info["url"]
                    and text
                    and len(text) > 5
                    and not href.endswith((".pdf", ".doc", ".docx", ".zip"))
                ):
                    full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    protocol_links.append((text, full_url))

            # Scrape sub-pages (limit to avoid overwhelming)
            for text, url in protocol_links[:20]:
                try:
                    sub_doc = await self._scrape_sub_page(
                        section_info["name"],
                        text,
                        url,
                    )
                    if sub_doc:
                        documents.append(sub_doc)

                    await asyncio.sleep(settings.scraper_delay_seconds / 2)
                except Exception as e:
                    logger.warning("Error scraping ERCOT sub-page", url=url, error=str(e))
                    continue

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error scraping ERCOT section",
                section=section_key,
                status=e.response.status_code,
            )
        except Exception as e:
            logger.error("Error scraping ERCOT section", section=section_key, error=str(e))

        return documents

    async def _scrape_sub_page(
        self,
        parent_name: str,
        page_title: str,
        page_url: str,
    ) -> Optional[ScrapedDocument]:
        """Scrape an individual ERCOT sub-page."""
        try:
            response = await self.client.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            content = self._extract_content(soup)
            if not content or len(content) < 200:
                return None

            return ScrapedDocument(
                title=f"ERCOT - {page_title}",
                content=content,
                source_url=page_url,
                document_type=DocumentType.STANDARD.value,
                published_date=date.today(),
                source="ERCOT",
                metadata={
                    "parent_section": parent_name,
                    "page_title": page_title,
                    "authority_level": AuthorityLevel.REGIONAL.value,
                    "jurisdiction_type": JurisdictionType.ERCOT.value,
                    "hierarchy": ["ERCOT", parent_name, page_title],
                },
            )

        except Exception as e:
            logger.warning("Error scraping ERCOT page", url=page_url, error=str(e))
            return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from an ERCOT page."""
        content_selectors = [
            "#main-content",
            ".content-area",
            ".main-content",
            "main",
            "article",
            "#content",
        ]

        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                for tag in content_div.select("nav, script, style, header, footer, .nav, .sidebar"):
                    tag.decompose()

                text = content_div.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return self._clean_text(text)

        body = soup.find("body")
        if body:
            for tag in body.select("nav, script, style, header, footer"):
                tag.decompose()
            text = body.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return self._clean_text(text)

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'Skip to .*?content', '', text, flags=re.IGNORECASE)
        return text.strip()

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        return [f"{self.BASE_URL}{info['url']}" for info in self.SECTIONS.values()]
