"""
Public Utility Commission of Texas (PUCT) Rules Scraper.

Fetches PUCT substantive rules from the Texas Administrative Code (TAC).
Title 16, Part 2, Chapter 25 - Substantive Rules Applicable to Electric Service Providers.
Source: Cornell Law Institute mirror of TAC (law.cornell.edu)
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import date
import asyncio
import re
import structlog

from app.scrapers.base import BaseScraper, ScrapedDocument
from app.config import settings
from app.db.models import AuthorityLevel, JurisdictionType, DocumentType

logger = structlog.get_logger()


class PUCTScraper(BaseScraper):
    """
    Scraper for PUCT Substantive Rules (16 TAC Chapter 25).

    Uses the Cornell Law Institute mirror of the Texas Administrative Code,
    which provides reliable static HTML access organized by subchapter.
    """

    CORNELL_BASE = "https://www.law.cornell.edu"
    CHAPTER_URL = "https://www.law.cornell.edu/regulations/texas/title-16/part-2/chapter-25"

    # All subchapters in TAC Chapter 25
    SUBCHAPTERS = [
        ("A", "General Provisions"),
        ("B", "Customer Service and Protection"),
        ("C", "Infrastructure and Reliability"),
        ("D", "Records, Reports, and Other Required Information"),
        ("E", "Certification, Licensing and Registration"),
        ("F", "Metering"),
        ("G", "Submetering"),
        ("H", "Electrical Planning"),
        ("I", "Transmission and Distribution"),
        ("J", "Costs, Rates and Tariffs"),
        ("K", "Relationships with Affiliates"),
        ("L", "Nuclear Decommissioning"),
        ("M", "Competitive Metering"),
        ("N", "Energy Efficiency and Customer-Owned Resources"),
        ("O", "Unbundled Network Elements"),
        ("P", "Renewable Energy"),
        ("Q", "Wholesale Market Design"),
        ("R", "Customer Protection Rules for Retail Electric Service"),
        ("S", "Wholesale Market Oversight"),
    ]

    def __init__(self):
        self.source_name = "PUCT"
        self.base_url = self.CORNELL_BASE
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
        """Scrape PUCT substantive rules from Cornell Law TAC mirror."""
        documents = []

        logger.info("Scraping PUCT rules from Cornell Law TAC")

        for subch_code, subch_name in self.SUBCHAPTERS:
            subch_url = f"{self.CHAPTER_URL}/subchapter-{subch_code}"
            logger.info(
                "Scraping TAC subchapter",
                subchapter=subch_code,
                name=subch_name,
            )

            try:
                subch_docs = await self._scrape_subchapter(
                    subch_code, subch_name, subch_url
                )
                documents.extend(subch_docs)
            except Exception as e:
                logger.error(
                    "Error scraping subchapter",
                    subchapter=subch_code,
                    error=str(e),
                )

            await asyncio.sleep(settings.scraper_delay_seconds)

        logger.info("PUCT rules scraping complete", total_documents=len(documents))
        return documents

    async def _scrape_subchapter(
        self, subch_code: str, subch_name: str, subch_url: str
    ) -> List[ScrapedDocument]:
        """Scrape all rules in a subchapter."""
        documents = []

        try:
            response = await self.client.get(subch_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find individual section links (pattern: /regulations/texas/16-Tex-Admin-Code-SS-25-N)
            rule_links = soup.find_all(
                "a", href=re.compile(r"/regulations/texas/16-Tex-Admin-Code-SS-25")
            )

            logger.info(
                "Found rule links in subchapter",
                subchapter=subch_code,
                count=len(rule_links),
            )

            for link in rule_links:
                href = link.get("href", "")
                rule_text = link.get_text(strip=True)
                rule_url = (
                    href
                    if href.startswith("http")
                    else f"{self.CORNELL_BASE}{href}"
                )

                try:
                    rule_doc = await self._scrape_rule(
                        subch_code, subch_name, rule_text, rule_url
                    )
                    if rule_doc:
                        documents.append(rule_doc)
                except Exception as e:
                    logger.warning(
                        "Error scraping rule",
                        rule=rule_text,
                        error=str(e),
                    )

                await asyncio.sleep(settings.scraper_delay_seconds)

        except Exception as e:
            logger.error(
                "Error fetching subchapter page",
                subchapter=subch_code,
                error=str(e),
            )

        return documents

    async def _scrape_rule(
        self,
        subch_code: str,
        subch_name: str,
        rule_name: str,
        rule_url: str,
    ) -> Optional[ScrapedDocument]:
        """Scrape a single PUCT rule from Cornell Law."""
        try:
            response = await self.client.get(rule_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            content = self._extract_content(soup)
            if not content or len(content) < 100:
                return None

            # Extract rule number (e.g., "§ 25.5 - Definitions" -> "25.5")
            rule_match = re.search(r"25\.(\d+)", rule_name)
            rule_num_str = f"25.{rule_match.group(1)}" if rule_match else rule_name
            rule_num = int(rule_match.group(1)) if rule_match else 0

            # Extract title
            title_match = re.search(r"\u00a7\s*25\.\d+\s*-\s*(.*)", rule_name)
            rule_title = title_match.group(1).strip() if title_match else rule_name

            return ScrapedDocument(
                title=f"16 TAC \u00a7 {rule_num_str} - {rule_title}",
                content=content,
                source_url=rule_url,
                document_type=DocumentType.RULE.value,
                published_date=date.today(),
                source="PUCT Substantive Rules",
                metadata={
                    "tac_title": 16,
                    "tac_part": 2,
                    "tac_chapter": 25,
                    "subchapter": subch_code,
                    "subchapter_name": subch_name,
                    "rule_number": rule_num_str,
                    "authority_level": AuthorityLevel.STATE.value,
                    "jurisdiction_type": JurisdictionType.TEXAS.value,
                    "citation": f"16 TAC \u00a7 {rule_num_str}",
                    "hierarchy": [
                        "Title 16: Economic Regulation",
                        "Part 2: Public Utility Commission of Texas",
                        "Chapter 25: Substantive Rules",
                        f"Subchapter {subch_code}: {subch_name}",
                        f"Rule {rule_num_str}",
                    ],
                },
            )

        except Exception as e:
            logger.warning("Error scraping PUCT rule", rule=rule_name, error=str(e))
            return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract regulation text from a Cornell Law page."""
        for tag in soup.select("nav, script, style, header, footer, .sidebar, #sidebar"):
            tag.decompose()

        body = soup.find("body")
        if not body:
            return ""

        text = body.get_text(separator="\n", strip=True)

        # Find the actual regulation content
        match = re.search(
            r"(16 Tex\. Admin\. Code \u00a7.*|In this chapter.*|The following .*)",
            text,
            re.DOTALL,
        )
        if match:
            text = match.group(1)

        # Remove Cornell boilerplate
        text = re.sub(r"Please help us improve our site.*?\n", "", text)
        text = re.sub(r"×\s*No thank you\s*", "", text)
        text = re.sub(r"State Regulations\s*Compare\s*", "", text)
        text = re.sub(r"About LII.*$", "", text, flags=re.DOTALL)
        text = re.sub(r"Cornell Law School.*$", "", text, flags=re.DOTALL)

        return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        return [self.CHAPTER_URL]
