import asyncio
import logging
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .config_loader import Config

logger = logging.getLogger(__name__)

class GiassiScraper:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    # Browser lifecycle methods
    async def _initialize_browser(self):
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
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None

    # Low-level utility methods (no dependencies)
    async def _find_element(self, page: Page, selectors: List[str], timeout: int = None) -> Optional[any]:
        timeout = timeout or self.config.timeouts["element_wait"]
        for selector in selectors:
            try:
                return await page.wait_for_selector(selector, timeout=timeout)
            except:
                continue
        return None

    @staticmethod
    async def _extract_text(element, selectors: List[str]) -> Optional[str]:
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
        await page.goto(self.config.base_url, timeout=self.config.timeouts["page_load"])
        await asyncio.sleep(2)
        
        search_input = await page.wait_for_selector(self.config.selectors["search_input"], timeout=self.config.timeouts["element_wait"])
        await search_input.click()
        await search_input.fill(search_term)
        await page.keyboard.press('Enter')
        
        await page.wait_for_selector(self.config.selectors["product_items"], timeout=self.config.timeouts["element_wait"])
        await asyncio.sleep(2)

    # Mid-level methods (depend on utility methods)
    async def _extract_product_data(self, product) -> Dict[str, str]:
        name = await GiassiScraper._extract_text(product, self.config.selectors["name"])
        price = await GiassiScraper._extract_text(product, self.config.selectors["price"])
        unit_price = await GiassiScraper._extract_text(product, self.config.selectors["unit_price"])
        
        return {
            "name": name or "Unknown",
            "price": price or "Price not available",
            "unit_price": unit_price if unit_price and unit_price != price else ""
        }

    async def _load_all_products(self, page: Page):
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
        if not search_term or not search_term.strip():
            return {
                "success": False,
                "error": "Search term cannot be empty",
                "search_term": search_term,
                "total_products": 0,
                "products": []
            }

        # Initialize browser if not already done
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