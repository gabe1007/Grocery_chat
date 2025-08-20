import asyncio
import logging
from typing import Dict, List
from playwright.async_api import Page
from config_loader import ScraperConfig
from .element_utils import ElementUtils

logger = logging.getLogger(__name__)

class ProductExtractor:
    """
    Handles product search and data extraction.
    """
    
    def __init__(self, config: ScraperConfig):
        self.config = config
    
    async def search_products(self, page: Page, search_term: str):
        """
        Navigate to site and perform a product search.
        """
        await page.goto(self.config.base_url, timeout=self.config.timeouts["page_load"])
        await asyncio.sleep(2)
        
        search_input = await page.wait_for_selector(
            self.config.selectors["search_input"],
            timeout=self.config.timeouts["element_wait"]
        )
        
        await search_input.click()
        await search_input.fill(search_term)
        await page.keyboard.press('Enter')
        
        await page.wait_for_selector(
            self.config.selectors["product_items"],
            timeout=self.config.timeouts["element_wait"]
        )
        await asyncio.sleep(2)
    
    async def load_all_products(self, page: Page):
        """
        Load all products by clicking 'load more' until no more products.
        """
        previous_count = 0
        
        while True:
            current_products = await page.query_selector_all(self.config.selectors["product_items"])
            current_count = len(current_products)
            
            if current_count == previous_count:
                break
            
            previous_count = current_count
            
            load_button = await ElementUtils.find_element(
                page,
                self.config.selectors["load_more"],
                self.config.timeouts["load_more"]
            )
            
            if not load_button:
                break
            
            await load_button.scroll_into_view_if_needed()
            await load_button.click()
            await asyncio.sleep(self.config.timeouts["load_more"] / 1000)
    
    async def extract_product_data(self, product) -> Dict[str, str]:
        """
        Extract product information from a product element.
        """
        name = await ElementUtils.extract_text(product, self.config.selectors["name"])
        price = await ElementUtils.extract_text(product, self.config.selectors["price"])
        unit_price = await ElementUtils.extract_text(product, self.config.selectors["unit_price"])
        
        return {
            "name": name or "Unknown",
            "price": price or "Price not available",
            "unit_price": unit_price if unit_price and unit_price != price else ""
        }
    
    async def extract_all_products(self, page: Page) -> List[Dict[str, str]]:
        """
        Extract data from all product elements on the page.
        """
        products = await page.query_selector_all(self.config.selectors["product_items"])
        product_list = []
        
        for product in products:
            try:
                product_data = await self.extract_product_data(product)
                product_list.append(product_data)
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                continue
        
        return product_list