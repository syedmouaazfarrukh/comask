"""
Texas Statutes Scraper.

Fetches Texas state statutes, focusing on the Utilities Code (Title 2 - PURA).
Primary source: Justia (more accessible)
Fallback: Texas Legislature (statutes.capitol.texas.gov)
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


class TexasStatutesScraper(BaseScraper):
    """
    Scraper for Texas Statutes.

    Focuses on the Utilities Code Title 2 (Public Utility Regulatory Act - PURA)
    and related energy statutes.
    """

    # Justia mirror (more accessible for scraping)
    JUSTIA_BASE = "https://law.justia.com/codes/texas"

    # Official Texas Legislature
    OFFICIAL_BASE = "https://statutes.capitol.texas.gov"

    # Key chapters in the Texas Utilities Code for energy compliance
    ENERGY_CHAPTERS = {
        "utilities-code": {
            "name": "Texas Utilities Code",
            "chapters": {
                11: "General Provisions",
                12: "Public Utility Commission of Texas",
                13: "Jurisdiction and Powers of Municipality",
                14: "Jurisdiction of PUCT",
                15: "Judicial Review and Enforcement",
                17: "Consumer Protection",
                25: "Electric Substantive Rules (PUCT)",
                31: "Texas Electric Choice",
                32: "Transmission and Distribution Utilities",
                35: "Electric Cooperatives",
                36: "Rate Regulation",
                37: "Certificates of Convenience and Necessity",
                38: "Reports, Records, and Information",
                39: "Restructuring of Electric Utility Industry",
                40: "Retail Competition",
                41: "Market Power and Anticompetitive Practices",
                42: "Rate Setting After Competition",
                43: "Electric Cooperative and Municipal Utility Competition",
            },
        },
    }

    def __init__(self):
        self.source_name = "Texas Statutes"
        self.base_url = self.JUSTIA_BASE
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
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
        """Scrape Texas energy-related statutes."""
        documents = []

        for code_key, code_info in self.ENERGY_CHAPTERS.items():
            logger.info("Scraping Texas code", code=code_key, name=code_info["name"])

            try:
                code_docs = await self._scrape_code_from_justia(code_key, code_info)
                documents.extend(code_docs)
            except Exception as e:
                logger.error("Error scraping Texas code", code=code_key, error=str(e))
                continue

        logger.info("Texas statutes scraping complete", total_documents=len(documents))
        return documents

    async def _scrape_code_from_justia(
        self,
        code_key: str,
        code_info: Dict[str, Any],
    ) -> List[ScrapedDocument]:
        """Scrape chapters from Justia's Texas Code database."""
        documents = []

        code_url = f"{self.JUSTIA_BASE}/{code_key}"

        try:
            response = await self.client.get(code_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Find chapter links
            chapter_links = soup.select("a[href*='/chapter-']")

            for link in chapter_links:
                href = link.get("href", "")
                chapter_text = link.get_text(strip=True)

                chapter_match = re.search(r'chapter-(\d+)', href)
                if not chapter_match:
                    continue

                chapter_num = int(chapter_match.group(1))

                # Only scrape our target chapters
                if chapter_num not in code_info["chapters"]:
                    continue

                chapter_url = href if href.startswith("http") else f"{self.JUSTIA_BASE}{href}"

                chapter_docs = await self._scrape_chapter(
                    code_info["name"],
                    chapter_num,
                    code_info["chapters"].get(chapter_num, chapter_text),
                    chapter_url,
                )
                documents.extend(chapter_docs)

                await asyncio.sleep(settings.scraper_delay_seconds)

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error scraping Texas code", status=e.response.status_code)
        except Exception as e:
            logger.error("Error scraping Texas code from Justia", error=str(e))

        return documents

    async def _scrape_chapter(
        self,
        code_name: str,
        chapter_num: int,
        chapter_name: str,
        chapter_url: str,
    ) -> List[ScrapedDocument]:
        """Scrape a chapter and its sections."""
        documents = []

        try:
            response = await self.client.get(chapter_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Find section links
            section_links = soup.select("a[href*='/section-']")

            if section_links:
                for link in section_links[:50]:  # Limit per chapter
                    href = link.get("href", "")
                    section_text = link.get_text(strip=True)

                    section_url = href if href.startswith("http") else f"{self.JUSTIA_BASE}{href}"

                    section_doc = await self._scrape_section(
                        code_name,
                        chapter_num,
                        chapter_name,
                        section_text,
                        section_url,
                    )
                    if section_doc:
                        documents.append(section_doc)

                    await asyncio.sleep(settings.scraper_delay_seconds / 2)
            else:
                # No sections found, scrape chapter as a whole
                content = self._extract_content(soup)
                if content:
                    doc = ScrapedDocument(
                        title=f"Tex. Util. Code Ch. {chapter_num} - {chapter_name}",
                        content=content,
                        source_url=chapter_url,
                        document_type=DocumentType.STATUTE.value,
                        published_date=date.today(),
                        source="Texas Utilities Code",
                        metadata={
                            "code_name": code_name,
                            "chapter_number": chapter_num,
                            "chapter_name": chapter_name,
                            "authority_level": AuthorityLevel.STATE.value,
                            "jurisdiction_type": JurisdictionType.TEXAS.value,
                            "citation": f"Tex. Util. Code Ch. {chapter_num}",
                            "hierarchy": [
                                f"{code_name}",
                                f"Chapter {chapter_num}: {chapter_name}",
                            ],
                        },
                    )
                    documents.append(doc)

        except Exception as e:
            logger.error("Error scraping Texas chapter", chapter=chapter_num, error=str(e))

        return documents

    async def _scrape_section(
        self,
        code_name: str,
        chapter_num: int,
        chapter_name: str,
        section_name: str,
        section_url: str,
    ) -> Optional[ScrapedDocument]:
        """Scrape a single section."""
        try:
            response = await self.client.get(section_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            content = self._extract_content(soup)
            if not content:
                return None

            # Extract section number from name
            section_match = re.search(r'(\d+\.\d+)', section_name)
            section_num = section_match.group(1) if section_match else section_name

            return ScrapedDocument(
                title=f"Tex. Util. Code \u00a7 {section_num} - {section_name}",
                content=content,
                source_url=section_url,
                document_type=DocumentType.STATUTE.value,
                published_date=date.today(),
                source="Texas Utilities Code",
                metadata={
                    "code_name": code_name,
                    "chapter_number": chapter_num,
                    "chapter_name": chapter_name,
                    "section_number": section_num,
                    "authority_level": AuthorityLevel.STATE.value,
                    "jurisdiction_type": JurisdictionType.TEXAS.value,
                    "citation": f"Tex. Util. Code \u00a7 {section_num}",
                    "hierarchy": [
                        f"{code_name}",
                        f"Chapter {chapter_num}: {chapter_name}",
                        f"Section {section_num}",
                    ],
                },
            )

        except Exception as e:
            logger.warning("Error scraping Texas section", section=section_name, error=str(e))
            return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from a statute page."""
        content_selectors = [
            ".codes-content",
            ".statute-content",
            "#content",
            "article",
            "main",
        ]

        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                for tag in content_div.select("nav, script, style, .nav, .navigation"):
                    tag.decompose()

                text = content_div.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return self._clean_text(text)

        body = soup.find("body")
        if body:
            for tag in body.select("nav, script, style, header, footer"):
                tag.decompose()
            return self._clean_text(body.get_text(separator="\n", strip=True))

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        boilerplate_patterns = [
            r'Skip to main content',
            r'Search.*?Search',
            r'Share this page',
            r'Print this page',
        ]
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text.strip()

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        urls = [f"{self.JUSTIA_BASE}/utilities-code"]
        for chapter_num in self.ENERGY_CHAPTERS["utilities-code"]["chapters"]:
            urls.append(f"{self.OFFICIAL_BASE}/docs/ut/htm/ut.{chapter_num}.htm")
        return urls
