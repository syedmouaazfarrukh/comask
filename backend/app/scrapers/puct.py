"""
Public Utility Commission of Texas (PUCT) Rules Scraper.

Fetches PUCT substantive rules from the Texas Administrative Code (TAC).
Title 16, Part 2, Chapter 25 - Substantive Rules Applicable to Electric Service Providers.
Source: Texas Secretary of State TAC (texreg.sos.state.tx.us)
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


class PUCTScraper(BaseScraper):
    """
    Scraper for PUCT Substantive Rules (16 TAC Chapter 25).

    The Texas Administrative Code is hosted by the Texas Secretary of State
    at texreg.sos.state.tx.us. PUCT electric rules are in Title 16, Part 2, Chapter 25.
    """

    TAC_BASE = "https://texreg.sos.state.tx.us/public"

    # Key subchapters of 16 TAC Chapter 25
    SUBCHAPTERS = {
        "A": {
            "name": "General Provisions",
            "description": "Definitions, scope, applicability",
            "rule_range": (1, 10),
        },
        "B": {
            "name": "Customer Service and Protection",
            "description": "Customer rights, billing, disconnection, complaints",
            "rule_range": (21, 50),
        },
        "C": {
            "name": "Infrastructure and Reliability",
            "description": "Electric service reliability, infrastructure requirements",
            "rule_range": (51, 62),
        },
        "D": {
            "name": "Records, Reports, and Other Filing Requirements",
            "description": "Filing requirements, record keeping",
            "rule_range": (71, 80),
        },
        "H": {
            "name": "Electrical Planning",
            "description": "Renewable energy, energy efficiency, demand response",
            "rule_range": (173, 182),
        },
        "J": {
            "name": "Costs, Rates, and Tariffs",
            "description": "Rate design, cost allocation, tariff filing",
            "rule_range": (231, 250),
        },
        "R": {
            "name": "Customer Protection for Retail Electric Providers",
            "description": "REP certification, customer protection in competitive market",
            "rule_range": (471, 500),
        },
        "S": {
            "name": "Wholesale Markets",
            "description": "Wholesale market oversight, ERCOT market rules",
            "rule_range": (501, 515),
        },
    }

    def __init__(self):
        self.source_name = "PUCT"
        self.base_url = self.TAC_BASE
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
        """Scrape PUCT substantive rules from the Texas Administrative Code."""
        documents = []

        # First try to get the chapter index page
        logger.info("Scraping PUCT rules from TAC", title=16, part=2, chapter=25)

        for subch_code, subch_info in self.SUBCHAPTERS.items():
            logger.info(
                "Scraping TAC subchapter",
                subchapter=subch_code,
                name=subch_info["name"],
            )

            try:
                subch_docs = await self._scrape_subchapter(subch_code, subch_info)
                documents.extend(subch_docs)
            except Exception as e:
                logger.error(
                    "Error scraping subchapter",
                    subchapter=subch_code,
                    error=str(e),
                )
                continue

            await asyncio.sleep(settings.scraper_delay_seconds)

        logger.info("PUCT rules scraping complete", total_documents=len(documents))
        return documents

    async def _scrape_subchapter(
        self,
        subch_code: str,
        subch_info: Dict[str, Any],
    ) -> List[ScrapedDocument]:
        """Scrape all rules in a subchapter."""
        documents = []

        # TAC URL for subchapter listing
        subch_url = (
            f"{self.TAC_BASE}/readtac$ext.ViewTAC"
            f"?tac_view=5&ti=16&pt=2&ch=25&sch={subch_code}&rl=Y"
        )

        try:
            response = await self.client.get(subch_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find links to individual rules
            rule_links = soup.find_all("a", href=re.compile(r"TacPage.*rl=\d+"))

            if rule_links:
                for link in rule_links:
                    href = link.get("href", "")
                    rule_text = link.get_text(strip=True)

                    # Build full URL
                    rule_url = f"{self.TAC_BASE}/{href}" if not href.startswith("http") else href

                    rule_doc = await self._scrape_rule(
                        subch_code,
                        subch_info["name"],
                        rule_text,
                        rule_url,
                    )
                    if rule_doc:
                        documents.append(rule_doc)

                    await asyncio.sleep(settings.scraper_delay_seconds / 2)
            else:
                # Fallback: try scraping individual rules by number range
                start_rule, end_rule = subch_info["rule_range"]
                for rule_num in range(start_rule, end_rule + 1):
                    rule_url = (
                        f"{self.TAC_BASE}/readtac$ext.TacPage"
                        f"?sl=R&app=9&p_dir=&p_rloc=&p_tloc=&p_ploc=&pg=1"
                        f"&p_tac=&ti=16&pt=2&ch=25&rl={rule_num}"
                    )

                    rule_doc = await self._scrape_rule(
                        subch_code,
                        subch_info["name"],
                        f"Rule 25.{rule_num}",
                        rule_url,
                    )
                    if rule_doc:
                        documents.append(rule_doc)

                    await asyncio.sleep(settings.scraper_delay_seconds / 2)

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error scraping subchapter",
                subchapter=subch_code,
                status=e.response.status_code,
            )
        except Exception as e:
            logger.error(
                "Error scraping subchapter from TAC",
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
        """Scrape a single PUCT rule."""
        try:
            response = await self.client.get(rule_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            content = self._extract_tac_content(soup)
            if not content or len(content) < 100:
                return None

            # Extract rule number
            rule_match = re.search(r'25\.(\d+)', rule_name)
            rule_num = rule_match.group(0) if rule_match else rule_name

            # Try to get the rule title from the page
            title_elem = soup.find("b") or soup.find("strong")
            rule_title = title_elem.get_text(strip=True) if title_elem else rule_name

            return ScrapedDocument(
                title=f"16 TAC \u00a7 {rule_num} - {rule_title}",
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
                    "rule_number": rule_num,
                    "authority_level": AuthorityLevel.STATE.value,
                    "jurisdiction_type": JurisdictionType.TEXAS.value,
                    "citation": f"16 TAC \u00a7 {rule_num}",
                    "hierarchy": [
                        "Title 16: Economic Regulation",
                        "Part 2: Public Utility Commission of Texas",
                        "Chapter 25: Substantive Rules",
                        f"Subchapter {subch_code}: {subch_name}",
                        f"Rule {rule_num}",
                    ],
                },
            )

        except Exception as e:
            logger.warning("Error scraping PUCT rule", rule=rule_name, error=str(e))
            return None

    def _extract_tac_content(self, soup: BeautifulSoup) -> str:
        """Extract content from a TAC rule page."""
        # TAC pages use specific HTML structure
        content_selectors = [
            "td.textbody",
            ".textbody",
            "td[class*='text']",
            "body",
        ]

        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                for tag in content_div.select("script, style"):
                    tag.decompose()

                text = content_div.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return self._clean_text(text)

        # Fallback: get all text
        body = soup.find("body")
        if body:
            for tag in body.select("script, style"):
                tag.decompose()
            text = body.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return self._clean_text(text)

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'Next Rule.*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Previous Rule.*', '', text, flags=re.IGNORECASE)
        return text.strip()

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        urls = [
            f"{self.TAC_BASE}/readtac$ext.ViewTAC?tac_view=4&ti=16&pt=2&ch=25",
        ]
        for subch_code in self.SUBCHAPTERS:
            urls.append(
                f"{self.TAC_BASE}/readtac$ext.ViewTAC?tac_view=5&ti=16&pt=2&ch=25&sch={subch_code}&rl=Y"
            )
        return urls
