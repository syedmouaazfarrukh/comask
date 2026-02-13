"""
ERCOT (Electric Reliability Council of Texas) Scraper.

Fetches ERCOT market rules, nodal protocols, and operating guides.
ERCOT.com blocks automated HTTP requests, so this scraper uses Playwright
(headless browser) to access the site, similar to the CPUC scraper.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import date
import re
import structlog

from app.scrapers.base import BaseScraper, ScrapedDocument
from app.config import settings
from app.db.models import AuthorityLevel, JurisdictionType, DocumentType

logger = structlog.get_logger()


class ERCOTScraper(BaseScraper):
    """
    Scraper for ERCOT protocols, market rules, and operating guides.

    Uses Playwright headless browser since ERCOT.com returns 403 for
    standard HTTP clients. Falls back gracefully if Playwright is unavailable.
    """

    BASE_URL = "https://www.ercot.com"

    # ERCOT pages to scrape
    PAGES = [
        {
            "url": "/mktrules",
            "name": "ERCOT Market Rules Overview",
            "description": "Overview of ERCOT market rules and protocols",
        },
        {
            "url": "/mktrules/nprotocols/current",
            "name": "ERCOT Nodal Protocols (Current)",
            "description": "Current Nodal Protocol sections governing ERCOT market operations",
        },
        {
            "url": "/mktrules/guides",
            "name": "ERCOT Market Guides",
            "description": "Operating and market guides for market participants",
        },
        {
            "url": "/mktrules/guides/noperating/current",
            "name": "ERCOT Operating Guides (Current)",
            "description": "Current ERCOT operating guides and procedures",
        },
        {
            "url": "/about/governance",
            "name": "ERCOT Governance",
            "description": "ERCOT governance structure and board oversight",
        },
    ]

    def __init__(self):
        self.source_name = "ERCOT"
        self.base_url = self.BASE_URL

    async def close(self):
        """No persistent resources to close."""
        pass

    async def scrape(self) -> List[ScrapedDocument]:
        """Scrape ERCOT pages using Playwright headless browser."""
        documents = []

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed, skipping ERCOT scraping")
            return documents

        logger.info("Starting ERCOT scraping with Playwright")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                )

                for page_info in self.PAGES:
                    page_url = f"{self.BASE_URL}{page_info['url']}"
                    logger.info("Scraping ERCOT page", url=page_url, name=page_info["name"])

                    try:
                        page_docs = await self._scrape_page(
                            context, page_info, page_url
                        )
                        documents.extend(page_docs)
                    except Exception as e:
                        logger.error(
                            "Error scraping ERCOT page",
                            url=page_url,
                            error=str(e),
                        )

                    await asyncio.sleep(settings.scraper_delay_seconds)

                await browser.close()

        except Exception as e:
            logger.error("Playwright ERCOT scraping failed", error=str(e))

        logger.info("ERCOT scraping complete", total_documents=len(documents))
        return documents

    async def _scrape_page(
        self,
        context,
        page_info: Dict[str, Any],
        page_url: str,
    ) -> List[ScrapedDocument]:
        """Scrape a single ERCOT page and its sub-links."""
        documents = []

        page = await context.new_page()
        try:
            await page.goto(page_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Wait for dynamic content

            # Extract page content
            content = await page.evaluate("() => document.body.innerText")

            if content and len(content) > 200:
                content = self._clean_text(content)
                doc = ScrapedDocument(
                    title=page_info["name"],
                    content=content,
                    source_url=page_url,
                    document_type=DocumentType.STANDARD.value,
                    published_date=date.today(),
                    source="ERCOT",
                    metadata={
                        "description": page_info["description"],
                        "authority_level": AuthorityLevel.REGIONAL.value,
                        "jurisdiction_type": JurisdictionType.ERCOT.value,
                        "hierarchy": ["ERCOT", page_info["name"]],
                    },
                )
                documents.append(doc)

            # Find sub-page links for market rules content
            links = await page.evaluate("""() => {
                const anchors = document.querySelectorAll('a[href*="/mktrules/"]');
                return Array.from(anchors).map(a => ({
                    text: a.textContent.trim(),
                    href: a.href
                })).filter(l => l.text.length > 5 && !l.href.match(/\\.(pdf|doc|docx|zip)$/));
            }""")

            # Scrape unique sub-pages
            seen_urls = {page_url}
            for link in links[:15]:
                link_url = link["href"]
                if link_url in seen_urls:
                    continue
                seen_urls.add(link_url)

                try:
                    sub_doc = await self._scrape_sub_page(
                        context, page_info["name"], link["text"], link_url
                    )
                    if sub_doc:
                        documents.append(sub_doc)
                    await asyncio.sleep(settings.scraper_delay_seconds / 2)
                except Exception as e:
                    logger.warning(
                        "Error scraping ERCOT sub-page",
                        url=link_url,
                        error=str(e),
                    )

        finally:
            await page.close()

        return documents

    async def _scrape_sub_page(
        self,
        context,
        parent_name: str,
        page_title: str,
        page_url: str,
    ) -> Optional[ScrapedDocument]:
        """Scrape an individual ERCOT sub-page."""
        page = await context.new_page()
        try:
            await page.goto(page_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            content = await page.evaluate("() => document.body.innerText")

            if not content or len(content) < 200:
                return None

            content = self._clean_text(content)

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
        finally:
            await page.close()

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"Skip to .*?content", "", text, flags=re.IGNORECASE)
        # Remove cookie/consent banners
        text = re.sub(r"We use cookies.*?\n", "", text, flags=re.IGNORECASE)
        return text.strip()

    def get_source_urls(self) -> List[str]:
        """Get list of source URLs."""
        return [f"{self.BASE_URL}{p['url']}" for p in self.PAGES]
