"""Colorado Public Utilities Commission scraper using Playwright."""

from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Browser, Page
from app.scrapers.base import BaseScraper, ScrapedDocument
from app.config import settings
import structlog
import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

logger = structlog.get_logger()


def _scrape_sync_standalone(base_url: str) -> List[dict]:
    """Standalone scraping function for multiprocessing (must be at module level)."""
    # Import here to avoid issues with multiprocessing
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
    from datetime import datetime
    import structlog
    import time
    
    logger = structlog.get_logger()
    documents = []
    browser = None
    playwright = None
    page = None
    
    try:
        logger.info("_scrape_sync_standalone: Starting")
        # Initialize browser (sync)
        logger.info("_scrape_sync_standalone: Initializing browser")
        playwright = sync_playwright().start()
        logger.info("_scrape_sync_standalone: Playwright started, launching Chromium")
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        logger.info("_scrape_sync_standalone: Browser initialized, creating context")
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        logger.info("_scrape_sync_standalone: Context created, creating page")
        page = context.new_page()
        logger.info("_scrape_sync_standalone: Page created, starting URL scraping")
        
        # URLs to scrape
        urls = [
            f"{base_url}/",
            f"{base_url}/rules-regulations",
            f"{base_url}/orders-decisions",
            f"{base_url}/rulemaking-proceedings",
        ]
        
        for url in urls:
            try:
                logger.info("Scraping CPUC URL", url=url)
                
                # Navigate to page with browser
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(2)  # Wait for JavaScript to load
                
                # Get page content
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract document links - be more flexible
                doc_links = []
                all_links = soup.find_all('a', href=True)
                
                # Also check for content directly on the page (not just links)
                page_has_content = False
                main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': lambda x: x and 'content' in x.lower()})
                if main_content:
                    content_text = main_content.get_text(strip=True)
                    if len(content_text) > 500:  # Has substantial content
                        page_has_content = True
                        # Treat the page itself as a document
                        doc_links.append((url, soup.find('title').get_text(strip=True) if soup.find('title') else "Page Content"))
                
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"{base_url}{href}"
                    elif href.startswith('#'):
                        continue  # Skip anchor links
                    elif not href.startswith('http'):
                        continue
                    
                    # More flexible matching - check for any relevant content
                    href_lower = href.lower()
                    text_lower = text.lower()
                    
                    # Check for document indicators
                    indicators = [
                        'order', 'decision', 'rule', 'regulation', 'docket', 'proceeding',
                        '.pdf', 'doc', 'policy', 'guidance', 'standard', 'requirement',
                        'statute', 'law', 'act', 'bill', 'amendment'
                    ]
                    
                    if any(indicator in href_lower or indicator in text_lower for indicator in indicators):
                        doc_links.append((href, text))
                    # Also include links that look like they might be documents
                    elif any(ext in href_lower for ext in ['.pdf', '.doc', '.docx', '.html']):
                        doc_links.append((href, text))
                    # Include links with substantial text (might be document pages)
                    elif len(text) > 10 and any(word in text_lower for word in ['colorado', 'energy', 'utility', 'commission']):
                        doc_links.append((href, text))
                
                logger.info("Found potential document links", url=url, count=len(doc_links))
                
                # If no links found but page has content, scrape the page itself
                if not doc_links and page_has_content:
                    doc_links.append((url, soup.find('title').get_text(strip=True) if soup.find('title') else "Page Content"))
                
                # Scrape up to 10 documents per page
                for href, link_text in doc_links[:10]:
                    try:
                        # If this is the same URL as current page, use existing content
                        if href == url and page_has_content:
                            # Use content we already have
                            title = soup.find('title') or soup.find('h1')
                            title_text = title.get_text(strip=True) if title else link_text or "Untitled"
                            
                            if main_content:
                                content = main_content.get_text(separator='\n', strip=True)
                            else:
                                body = soup.find('body')
                                content = body.get_text(separator='\n', strip=True) if body else ""
                        else:
                            # Navigate to new page
                            page.goto(href, wait_until='networkidle', timeout=30000)
                            time.sleep(1)
                            content_html = page.content()
                            soup = BeautifulSoup(content_html, 'html.parser')
                            
                            title = soup.find('title') or soup.find('h1')
                            title_text = title.get_text(strip=True) if title else link_text or "Untitled"
                            
                            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': lambda x: x and 'content' in str(x).lower()})
                            if main_content:
                                content = main_content.get_text(separator='\n', strip=True)
                            else:
                                body = soup.find('body')
                                content = body.get_text(separator='\n', strip=True) if body else ""
                        
                        # Only add if content is substantial
                        if len(content) > 200:  # At least 200 characters
                            doc_dict = {
                                'title': title_text[:500],
                                'content': content[:50000],
                                'source_url': href,
                                'document_type': 'regulation',
                                'published_date': None,
                                'source': 'CPUC',
                                'metadata': {'scraped_at': datetime.now().isoformat(), 'link_text': link_text[:200]}
                            }
                            documents.append(doc_dict)
                            logger.debug("Document scraped", title=title_text[:50], content_length=len(content))
                        else:
                            logger.debug("Skipping document - content too short", url=href, length=len(content))
                    except Exception as e:
                        logger.warning("Failed to scrape document", url=href, error=str(e))
                        continue
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error("Error scraping CPUC URL", url=url, error=str(e))
                continue
        
        logger.info("CPUC scraping complete", documents_found=len(documents))
        return documents
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(
            "CPUC scraper error",
            error=str(e),
            error_type=type(e).__name__,
            traceback=error_trace
        )
        return documents
    finally:
        try:
            if page:
                page.close()
            if browser:
                browser.close()
            if playwright:
                playwright.stop()
        except Exception as cleanup_error:
            logger.warning("Error during cleanup", error=str(cleanup_error))


class CPUCScraper(BaseScraper):
    """Scraper for Colorado PUC documents using browser automation."""
    
    def __init__(self):
        super().__init__(
            source_name="CPUC",
            base_url=settings.cpuc_base_url
        )
        self.browser: Optional[Browser] = None
    
    def get_source_urls(self) -> List[str]:
        """Get CPUC URLs to scrape."""
        # Updated URLs based on actual CPUC website structure
        return [
            f"{self.base_url}/",
            f"{self.base_url}/rules-regulations",
            f"{self.base_url}/orders-decisions",
            f"{self.base_url}/rulemaking-proceedings",
        ]
    
    def _init_browser_sync(self):
        """Initialize Playwright browser (sync version for Windows compatibility)."""
        try:
            logger.debug("Starting Playwright browser")
            playwright = sync_playwright().start()
            logger.debug("Playwright started, launching Chromium")
            browser = playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.debug("Chromium browser launched successfully")
            return browser, playwright
        except Exception as e:
            import traceback
            logger.error(
                "Failed to initialize browser",
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc()
            )
            raise
    
    def _close_browser_sync(self, browser: Browser, playwright):
        """Close browser (sync version)."""
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
    
    async def scrape(self) -> List[ScrapedDocument]:
        """Scrape CPUC documents using browser automation."""
        try:
            logger.info("Starting CPUC scrape (async wrapper)")
            # Use ProcessPoolExecutor for Windows compatibility
            # Playwright needs a fresh event loop, which processes provide
            # Set multiprocessing start method for Windows (if not already set)
            import sys
            if sys.platform == 'win32':
                try:
                    multiprocessing.set_start_method('spawn', force=True)
                except RuntimeError:
                    # Already set, ignore
                    pass
            
            loop = asyncio.get_event_loop()
            with ProcessPoolExecutor(max_workers=1) as executor:
                logger.debug("Submitting scrape task to process pool")
                # Use standalone function that can be pickled for multiprocessing
                doc_dicts = await loop.run_in_executor(executor, _scrape_sync_standalone, self.base_url)
            
            # Convert dicts to ScrapedDocument objects
            documents = []
            for doc_dict in doc_dicts:
                try:
                    doc = ScrapedDocument(**doc_dict)
                    documents.append(doc)
                except Exception as e:
                    logger.warning("Failed to create ScrapedDocument", error=str(e))
                    continue
            
            logger.info("CPUC scrape completed", documents_found=len(documents))
            return documents
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(
                "CPUC scraper async error",
                error=str(e) if e else "Unknown error",
                error_type=type(e).__name__ if e else "Unknown",
                traceback=error_trace
            )
            return []
    
    def _scrape_sync(self) -> List[ScrapedDocument]:
        """Synchronous scraping function (runs in thread pool)."""
        documents = []
        browser = None
        playwright = None
        page = None
        
        try:
            logger.info("_scrape_sync: Starting")
            # Initialize browser (sync)
            logger.info("_scrape_sync: Initializing browser")
            browser, playwright = self._init_browser_sync()
            logger.info("_scrape_sync: Browser initialized, creating context")
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            logger.info("_scrape_sync: Context created, creating page")
            page = context.new_page()
            logger.info("_scrape_sync: Page created, starting URL scraping")
            
            urls = self.get_source_urls()
            
            for url in urls:
                try:
                    logger.info("Scraping CPUC URL", url=url)
                    
                    # Navigate to page with browser
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    import time
                    time.sleep(2)  # Wait for JavaScript to load
                    
                    # Get page content
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract document links - look for common patterns
                    doc_links = []
                    
                    # Find links that might be documents
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Make absolute URL
                        if href.startswith('/'):
                            href = f"{self.base_url}{href}"
                        elif not href.startswith('http'):
                            continue
                        
                        # Check if it looks like a document
                        if any(indicator in href.lower() or indicator in text.lower() 
                               for indicator in ['order', 'decision', 'rule', 'regulation', 
                                                'docket', 'proceeding', '.pdf', 'doc']):
                            doc_links.append((href, text))
                    
                    logger.info("Found potential document links", url=url, count=len(doc_links))
                    
                    # Scrape up to 10 documents per page (MVP limit)
                    for href, link_text in doc_links[:10]:
                        try:
                            doc = self._scrape_document_with_browser_sync(page, href, link_text)
                            if doc:
                                documents.append(doc)
                                logger.debug("Document scraped", title=doc.title[:50])
                        except Exception as e:
                            logger.warning("Failed to scrape document", url=href, error=str(e))
                            continue
                    
                    # Respect rate limits
                    import time
                    time.sleep(settings.scraper_delay_seconds)
                    
                except Exception as e:
                    logger.error("Error scraping CPUC URL", url=url, error=str(e))
                    continue
            
            logger.info("CPUC scraping complete", documents_found=len(documents))
            return documents
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(
                "CPUC scraper error",
                error=str(e),
                error_type=type(e).__name__,
                traceback=error_trace
            )
            return documents
        finally:
            # Clean up
            try:
                if page:
                    page.close()
                self._close_browser_sync(browser, playwright)
            except Exception as cleanup_error:
                logger.warning("Error during cleanup", error=str(cleanup_error))
    
    def _scrape_document_with_browser_sync(
        self, 
        page: Page, 
        url: str, 
        link_text: str = ""
    ) -> Optional[ScrapedDocument]:
        """Scrape a single document using browser (sync version)."""
        try:
            # Navigate to document page
            page.goto(url, wait_until='networkidle', timeout=30000)
            import time
            time.sleep(1)  # Wait for content to load
            
            # Get page content
            content_html = page.content()
            soup = BeautifulSoup(content_html, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            if not title:
                title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else link_text or "Untitled Document"
            
            # Extract main content - try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to body text
                body = soup.find('body')
                content = body.get_text(separator='\n', strip=True) if body else ""
            
            # Extract metadata - look for dates
            published_date = None
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'\d{4}-\d{2}-\d{2}',
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ]
            
            import re
            for pattern in date_patterns:
                matches = re.findall(pattern, content[:2000])
                if matches:
                    try:
                        # Try to parse the first date found
                        date_str = matches[0]
                        # Simple parsing - can be improved
                        if '/' in date_str:
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                published_date = datetime(int(parts[2]), int(parts[0]), int(parts[1]))
                        elif '-' in date_str:
                            published_date = datetime.fromisoformat(date_str)
                    except:
                        pass
                    break
            
            # Determine document type from URL or content
            doc_type = "regulation"
            if 'order' in url.lower() or 'order' in title_text.lower():
                doc_type = "order"
            elif 'rule' in url.lower() or 'rule' in title_text.lower():
                doc_type = "regulation"
            elif 'docket' in url.lower():
                doc_type = "docket"
            
            return ScrapedDocument(
                title=title_text[:500],  # Limit title length
                content=content[:50000],  # Limit content size
                source_url=url,
                document_type=doc_type,
                published_date=published_date,
                source="CPUC",
                metadata={
                    "scraped_at": datetime.now().isoformat(),
                    "link_text": link_text[:200]
                }
            )
            
        except Exception as e:
            logger.warning("Failed to scrape document", url=url, error=str(e))
            return None

