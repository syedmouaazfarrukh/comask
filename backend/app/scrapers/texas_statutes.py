"""
Texas Statutes Scraper.

Fetches Texas state statutes, focusing on the Utilities Code Title 2 (PURA).
Source: Official Texas Legislature (statutes.capitol.texas.gov) via Playwright.
The site uses Angular and requires JS rendering.
"""

import asyncio
from typing import List
from datetime import date
import re
import structlog

from app.scrapers.base import BaseScraper, ScrapedDocument
from app.config import settings
from app.db.models import AuthorityLevel, JurisdictionType, DocumentType

logger = structlog.get_logger()


class TexasStatutesScraper(BaseScraper):
    """
    Scraper for Texas Utilities Code (PURA).

    Uses Playwright to render the Angular-based Texas Legislature website.
    Each chapter is loaded as a single HTML page containing all sections.
    """

    BASE_URL = "https://statutes.capitol.texas.gov/Docs/UT/htm"

    # Key PURA chapters for energy compliance
    TARGET_CHAPTERS = {
        11: "General Provisions",
        12: "Organization of Commission",
        14: "Jurisdiction and Powers of Commission",
        15: "Judicial Review, Enforcement, and Penalties",
        17: "Customer Protection",
        31: "General Provisions (Electric)",
        32: "Jurisdiction and Powers (Electric)",
        35: "Alternative Energy Providers",
        36: "Rates",
        37: "Certificates of Convenience and Necessity",
        38: "Regulation of Electric Services",
        39: "Restructuring of Electric Utility Industry",
        40: "Retail Competition",
        41: "Market Power and Anticompetitive Practices",
        42: "Rate Setting After Competition",
        43: "Electric Cooperative and Municipal Utility Competition",
    }

    def __init__(self):
        self.source_name = "Texas Statutes"
        self.base_url = self.BASE_URL

    async def close(self):
        """No persistent resources to close."""
        pass

    async def scrape(self) -> List[ScrapedDocument]:
        """Scrape Texas Utilities Code chapters using Playwright."""
        documents = []

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed, skipping Texas Statutes scraping")
            return documents

        logger.info("Starting Texas Statutes scraping with Playwright")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                )

                for chapter_num, chapter_name in self.TARGET_CHAPTERS.items():
                    chapter_url = f"{self.BASE_URL}/UT.{chapter_num}.htm"
                    logger.info(
                        "Scraping Texas Utilities Code chapter",
                        chapter=chapter_num,
                        name=chapter_name,
                    )

                    try:
                        chapter_docs = await self._scrape_chapter(
                            context, chapter_num, chapter_name, chapter_url
                        )
                        documents.extend(chapter_docs)
                    except Exception as e:
                        logger.error(
                            "Error scraping chapter",
                            chapter=chapter_num,
                            error=str(e),
                        )

                    await asyncio.sleep(settings.scraper_delay_seconds)

                await browser.close()

        except Exception as e:
            logger.error("Playwright Texas Statutes scraping failed", error=str(e))

        logger.info(
            "Texas statutes scraping complete", total_documents=len(documents)
        )
        return documents

    async def _scrape_chapter(
        self, context, chapter_num: int, chapter_name: str, chapter_url: str
    ) -> List[ScrapedDocument]:
        """Scrape a single chapter page and split into sections."""
        documents = []

        page = await context.new_page()
        try:
            await page.goto(chapter_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)  # Wait for Angular to render

            # Get the full rendered text
            full_text = await page.evaluate("() => document.body.innerText")

            if not full_text or len(full_text) < 500:
                logger.warning("No content for chapter", chapter=chapter_num)
                return documents

            # Split into individual sections
            sections = self._split_into_sections(full_text, chapter_num)

            if sections:
                logger.info(
                    "Found sections in chapter",
                    chapter=chapter_num,
                    count=len(sections),
                )
                for section_num, section_title, section_text in sections:
                    doc = ScrapedDocument(
                        title=f"Tex. Util. Code \u00a7 {section_num} - {section_title}",
                        content=section_text,
                        source_url=chapter_url,
                        document_type=DocumentType.STATUTE.value,
                        published_date=date.today(),
                        source="Texas Utilities Code",
                        metadata={
                            "chapter_number": chapter_num,
                            "chapter_name": chapter_name,
                            "section_number": section_num,
                            "authority_level": AuthorityLevel.STATE.value,
                            "jurisdiction_type": JurisdictionType.TEXAS.value,
                            "citation": f"Tex. Util. Code \u00a7 {section_num}",
                            "hierarchy": [
                                "Texas Utilities Code",
                                "Title 2: Public Utility Regulatory Act",
                                f"Chapter {chapter_num}: {chapter_name}",
                                f"Section {section_num}",
                            ],
                        },
                    )
                    documents.append(doc)
            else:
                # Store as single chapter document
                content = self._clean_text(full_text)
                if len(content) > 200:
                    doc = ScrapedDocument(
                        title=f"Tex. Util. Code Ch. {chapter_num} - {chapter_name}",
                        content=content,
                        source_url=chapter_url,
                        document_type=DocumentType.STATUTE.value,
                        published_date=date.today(),
                        source="Texas Utilities Code",
                        metadata={
                            "chapter_number": chapter_num,
                            "chapter_name": chapter_name,
                            "authority_level": AuthorityLevel.STATE.value,
                            "jurisdiction_type": JurisdictionType.TEXAS.value,
                            "citation": f"Tex. Util. Code Ch. {chapter_num}",
                            "hierarchy": [
                                "Texas Utilities Code",
                                "Title 2: Public Utility Regulatory Act",
                                f"Chapter {chapter_num}: {chapter_name}",
                            ],
                        },
                    )
                    documents.append(doc)

        except Exception as e:
            logger.error(
                "Error rendering chapter page",
                chapter=chapter_num,
                error=str(e),
            )
        finally:
            await page.close()

        return documents

    def _split_into_sections(
        self, text: str, chapter_num: int
    ) -> list:
        """Split chapter text into individual sections."""
        # Pattern: "Sec. 39.001. TITLE TEXT" at start of line
        pattern = rf"(Sec\.\s*{chapter_num}\.\d+[A-Za-z]*\.)\s*([^\n]+)"
        matches = list(re.finditer(pattern, text))

        if not matches:
            return []

        sections = []
        for i, match in enumerate(matches):
            sec_marker = match.group(1)  # "Sec. 39.001."
            sec_title = match.group(2).strip()

            # Extract section number
            num_match = re.search(r"(\d+\.\d+[A-Za-z]*)", sec_marker)
            section_num = num_match.group(1) if num_match else sec_marker

            # Get text until next section or end
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = self._clean_text(text[start:end])

            if len(section_text) > 50:
                sections.append((section_num, sec_title, section_text))

        return sections

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove navigation/boilerplate from beginning
        patterns_to_remove = [
            r"Texas Constitution\s*and Statutes.*?(?=Sec\.|SUBCHAPTER)",
            r"Search Options.*?(?=Sec\.|SUBCHAPTER)",
        ]
        for pattern in patterns_to_remove:
            text = re.sub(pattern, "", text, count=1, flags=re.DOTALL)

        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        return [
            f"{self.BASE_URL}/UT.{ch}.htm" for ch in self.TARGET_CHAPTERS
        ]
