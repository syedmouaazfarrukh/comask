"""
Colorado Revised Statutes (CRS) Scraper.

Fetches Colorado state statutes, focusing on Title 40 (Utilities).
Source: Colorado General Assembly website
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


class ColoradoCRSScraper(BaseScraper):
    """
    Scraper for Colorado Revised Statutes.

    Focuses on Title 40 - Utilities (Regulation of Utilities)
    and related energy statutes.
    """

    # Colorado Legislature website
    BASE_URL = "https://leg.colorado.gov"

    # Justia as alternative source (often more accessible)
    JUSTIA_BASE = "https://law.justia.com/codes/colorado"

    # Relevant titles for energy compliance
    ENERGY_TITLES = {
        40: {
            "name": "Utilities",
            "description": "Public Utilities Commission, rate regulation, service requirements",
            "articles": list(range(1, 20)),  # Articles 1-19
        },
        24: {
            "name": "Government - State",
            "description": "Includes Colorado Energy Office provisions",
            "articles": [38],  # Article 38: Energy
        },
    }

    def __init__(self):
        self.source_name = "Colorado CRS"
        self.base_url = self.BASE_URL
        # Use a more browser-like user agent to avoid being blocked
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            follow_redirects=True,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def scrape(self) -> List[ScrapedDocument]:
        """
        Scrape Colorado energy-related statutes.

        Returns:
            List of scraped documents
        """
        documents = []

        for title_num, title_info in self.ENERGY_TITLES.items():
            logger.info(
                "Scraping CRS title",
                title=title_num,
                name=title_info["name"]
            )

            try:
                # Scrape from Justia (more accessible API)
                title_docs = await self._scrape_title_from_justia(
                    title_num,
                    title_info
                )
                documents.extend(title_docs)

            except Exception as e:
                logger.error(
                    "Error scraping CRS title",
                    title=title_num,
                    error=str(e)
                )
                continue

        logger.info("CRS scraping complete", total_documents=len(documents))
        return documents

    async def _scrape_title_from_justia(
        self,
        title_num: int,
        title_info: Dict[str, Any],
    ) -> List[ScrapedDocument]:
        """
        Scrape a title from Justia's Colorado Code database.

        Args:
            title_num: Title number
            title_info: Title metadata

        Returns:
            List of scraped documents
        """
        documents = []

        # Get the title index page
        title_url = f"{self.JUSTIA_BASE}/title-{title_num}"

        try:
            response = await self.client.get(title_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Find all article links
            article_links = soup.select("a[href*='/article-']")

            for link in article_links:
                href = link.get("href", "")
                article_text = link.get_text(strip=True)

                # Extract article number
                article_match = re.search(r'article-(\d+)', href)
                if not article_match:
                    continue

                article_num = int(article_match.group(1))

                # Check if this article is in our target list
                if title_info["articles"] and article_num not in title_info["articles"]:
                    continue

                # Scrape the article
                article_docs = await self._scrape_article(
                    title_num,
                    title_info["name"],
                    article_num,
                    article_text,
                    href if href.startswith("http") else f"{self.JUSTIA_BASE}{href}"
                )
                documents.extend(article_docs)

                # Respect rate limits
                await asyncio.sleep(settings.scraper_delay_seconds)

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error scraping CRS title",
                title=title_num,
                status=e.response.status_code
            )
        except Exception as e:
            logger.error(
                "Error scraping CRS title from Justia",
                title=title_num,
                error=str(e)
            )

        return documents

    async def _scrape_article(
        self,
        title_num: int,
        title_name: str,
        article_num: int,
        article_name: str,
        article_url: str,
    ) -> List[ScrapedDocument]:
        """
        Scrape an article and its sections.

        Args:
            title_num: Title number
            title_name: Title name
            article_num: Article number
            article_name: Article name
            article_url: URL to article page

        Returns:
            List of scraped documents (one per section)
        """
        documents = []

        try:
            response = await self.client.get(article_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Find section links
            section_links = soup.select("a[href*='/section-']")

            if section_links:
                # Scrape each section
                for link in section_links[:50]:  # Limit to avoid overwhelming
                    href = link.get("href", "")
                    section_text = link.get_text(strip=True)

                    section_url = href if href.startswith("http") else f"{self.JUSTIA_BASE}{href}"

                    section_doc = await self._scrape_section(
                        title_num,
                        title_name,
                        article_num,
                        article_name,
                        section_text,
                        section_url,
                    )
                    if section_doc:
                        documents.append(section_doc)

                    await asyncio.sleep(settings.scraper_delay_seconds / 2)
            else:
                # No sections found, scrape the article as a whole
                content = self._extract_content(soup)
                if content:
                    doc = ScrapedDocument(
                        title=f"C.R.S. Title {title_num}, Article {article_num} - {article_name}",
                        content=content,
                        source_url=article_url,
                        document_type=DocumentType.STATUTE.value,
                        published_date=date.today(),
                        source="Colorado Revised Statutes",
                        metadata={
                            "title_number": title_num,
                            "title_name": title_name,
                            "article_number": article_num,
                            "article_name": article_name,
                            "authority_level": AuthorityLevel.STATE.value,
                            "jurisdiction_type": JurisdictionType.COLORADO.value,
                            "citation": f"C.R.S. § {title_num}-{article_num}",
                            "hierarchy": [
                                f"Title {title_num}: {title_name}",
                                f"Article {article_num}: {article_name}",
                            ],
                        }
                    )
                    documents.append(doc)

        except Exception as e:
            logger.error(
                "Error scraping CRS article",
                title=title_num,
                article=article_num,
                error=str(e)
            )

        return documents

    async def _scrape_section(
        self,
        title_num: int,
        title_name: str,
        article_num: int,
        article_name: str,
        section_name: str,
        section_url: str,
    ) -> Optional[ScrapedDocument]:
        """
        Scrape a single section.

        Args:
            title_num: Title number
            title_name: Title name
            article_num: Article number
            article_name: Article name
            section_name: Section name/number
            section_url: URL to section

        Returns:
            Scraped document or None
        """
        try:
            response = await self.client.get(section_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            content = self._extract_content(soup)
            if not content:
                return None

            # Extract section number from name
            section_match = re.search(r'(\d+-\d+-\d+)', section_name)
            section_num = section_match.group(1) if section_match else section_name

            return ScrapedDocument(
                title=f"C.R.S. § {section_num} - {section_name}",
                content=content,
                source_url=section_url,
                document_type=DocumentType.STATUTE.value,
                published_date=date.today(),
                source="Colorado Revised Statutes",
                metadata={
                    "title_number": title_num,
                    "title_name": title_name,
                    "article_number": article_num,
                    "article_name": article_name,
                    "section_number": section_num,
                    "authority_level": AuthorityLevel.STATE.value,
                    "jurisdiction_type": JurisdictionType.COLORADO.value,
                    "citation": f"C.R.S. § {section_num}",
                    "hierarchy": [
                        f"Title {title_num}: {title_name}",
                        f"Article {article_num}: {article_name}",
                        f"Section {section_num}",
                    ],
                }
            )

        except Exception as e:
            logger.warning(
                "Error scraping CRS section",
                section=section_name,
                error=str(e)
            )
            return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main content from a statute page.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            Cleaned text content
        """
        # Try different content containers
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
                # Remove navigation, scripts, etc.
                for tag in content_div.select("nav, script, style, .nav, .navigation"):
                    tag.decompose()

                text = content_div.get_text(separator="\n", strip=True)
                if len(text) > 100:  # Minimum content threshold
                    return self._clean_text(text)

        # Fallback: get body text
        body = soup.find("body")
        if body:
            for tag in body.select("nav, script, style, header, footer"):
                tag.decompose()
            return self._clean_text(body.get_text(separator="\n", strip=True))

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        # Remove common boilerplate
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
        urls = []
        for title_num in self.ENERGY_TITLES:
            urls.append(f"{self.JUSTIA_BASE}/title-{title_num}")
            urls.append(f"{self.BASE_URL}/colorado-revised-statutes/title-{title_num}")
        return urls


async def fetch_colorado_statutes() -> List[ScrapedDocument]:
    """
    Convenience function to fetch Colorado statutes.

    Returns:
        List of scraped documents
    """
    scraper = ColoradoCRSScraper()
    try:
        return await scraper.scrape()
    finally:
        await scraper.close()
