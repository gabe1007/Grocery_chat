import asyncio
import logging
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .config import Config

logger = logging.getLogger(__name__)

class GiassiScraper:
    """
    Web scraper for Giassi supermarket products.
    
    This class provides functionality to scrape product information from Giassi's website
    using Playwright for browser automation. It handles browser lifecycle, product search,
    and data extraction.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the scraper with configuration.
        """
        self.config = config or Config()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def _initialize_browser(self):
        """
        Initialize the browser instance and context.

        Launches a headless Chromium browser with configured arguments and creates a new
        browsing context with specified viewport and user agent. Only initializes if browser
        doesn't already exist.
        """
        if not self.browser:
            self.browser = await (await async_playwright().start()).chromium.launch(
                headless = True,
                args = self.config.browser_args
            )
            self.context = await self.browser.new_context(
                viewport = self.config.viewport,
                user_agent = self.config.user_agent
            )

    async def close(self):
        """
        Close the browser instance and clean up resources.
        
        Closes the browser if it exists and resets browser/context attributes to None.
        Should be called when scraping is complete to free up system resources.
        """
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None

    async def _find_element(self, page: Page, selectors: List[str], timeout: int = None) -> Optional[any]:
        """
        Find the first matching element from a list of selectors.
        Iterates through selectors and returns the first element found within the timeout period.
        """
        timeout = timeout or self.config.timeouts["element_wait"]
        for selector in selectors:
            try:
                return await page.wait_for_selector(selector, timeout=timeout)
            except:
                continue
        return None

    @staticmethod
    async def _extract_text(element, selectors: List[str]) -> Optional[str]:
        """
        Extract text content from an element using multiple selector strategies.
        
        Attempts to extract text from the first matching selector. Handles both single
        string selectors and lists of selectors.
        """
        if isinstance(selectors, str):
            selectors = [selectors]
            
        for selector in selectors:
            el = await element.query_selector(selector)
            if el:
                text = await el.text_content()
                if text and text.strip():
                    return text.strip()
        return None
    
    async def _search_products(self, page: Page, search_term: str):
        """
        Navigate to site and perform a product search.
        
        Loads the base URL, locates the search input, enters the search term,
        and submits the search. Waits for product results to load.
        """
        await page.goto(self.config.base_url, timeout=self.config.timeouts["page_load"])
        await asyncio.sleep(2)
        
        search_input = await page.wait_for_selector(self.config.selectors["search_input"], timeout=self.config.timeouts["element_wait"])
        await search_input.click()
        await search_input.fill(search_term)
        await page.keyboard.press('Enter')
        
        await page.wait_for_selector(self.config.selectors["product_items"], timeout=self.config.timeouts["element_wait"])
        await asyncio.sleep(2)

    async def _extract_product_data(self, product) -> Dict[str, str]:
        """
        Extract product information from a product element.
        
        Retrieves name, price, and unit price from a product container element using
        configured selectors. Provides default values when data is missing.
        """
        name = await GiassiScraper._extract_text(product, self.config.selectors["name"])
        price = await GiassiScraper._extract_text(product, self.config.selectors["price"])
        unit_price = await GiassiScraper._extract_text(product, self.config.selectors["unit_price"])
        
        return {
            "name": name or "Unknown",
            "price": price or "Price not available",
            "unit_price": unit_price if unit_price and unit_price != price else ""
        }

    async def _load_all_products(self, page: Page):
        """
        Load all products by clicking 'load more' until no more products.
        
        Continuously clicks the 'load more' button until no new products are loaded
        or the button disappears. Handles scrolling and waiting between loads.
        """
        previous_count = 0
        while True:
            current_products = await page.query_selector_all(self.config.selectors["product_items"])
            current_count = len(current_products)
            
            if current_count == previous_count:
                break
                
            previous_count = current_count
            
            load_button = await self._find_element(page, self.config.selectors["load_more"], self.config.timeouts["load_more"])
            if not load_button:
                break
                
            await load_button.scroll_into_view_if_needed()
            await load_button.click()
            await asyncio.sleep(self.config.timeouts["load_more"] / 1000)

    async def scrape_products(self, search_term: str) -> Dict[str, any]:
        """
        Main method to scrape products for a given search term.
        
        Orchestrates the entire scraping process:
        1. Validates search term
        2. Initializes browser if needed
        3. Performs product search
        4. Loads all products
        5. Extracts product data
        6. Handles errors and cleanup
        """
        if not search_term or not search_term.strip():
            return {
                "success": False,
                "error": "Search term cannot be empty",
                "search_term": search_term,
                "total_products": 0,
                "products": []
            }
            
        await self._initialize_browser()
            
        try:
            page = await self.context.new_page()
            await self._search_products(page, search_term)
            await self._load_all_products(page)
            
            products = await page.query_selector_all(self.config.selectors["product_items"])
            product_list = []
            
            for product in products:
                try:
                    product_data = await self._extract_product_data(product)
                    product_list.append(product_data)
                except Exception as e:
                    logger.warning(f"Error parsing product: {e}")
                    continue
            
            return {
                "success": True,
                "search_term": search_term,
                "total_products": len(product_list),
                "products": product_list
            }
                    
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return {
                "success": False,
                "error": str(e),
                "search_term": search_term,
                "total_products": 0,
                "products": []
            }
        finally:
            if 'page' in locals():
                await page.close()
                