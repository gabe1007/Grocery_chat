import asyncio
import logging
from typing import Dict, List
from playwright.async_api import Page, ElementHandle
from config_loader import ScraperConfig
from .element_utils import ElementUtils

logger = logging.getLogger(__name__)

class ProductExtractor:
    """
    Handles product search and data extraction for Angeloni.
    """
    def __init__(self, config: ScraperConfig):
        self.config = config
    
    async def search_products(self, page: Page, search_term: str):
        """
        Navigate to site and perform a product search.
        """
        await page.goto(self.config.base_url, timeout=self.config.timeouts["page_load"])
        await asyncio.sleep(3)
        
        search_input = await ElementUtils.find_element(
            page, 
            self.config.selectors["search_input"], 
            self.config.timeouts["element_wait"]
        )
        
        if not search_input:
            raise Exception("Could not find search input on Angeloni website")
        
        await search_input.click()
        await search_input.fill(search_term)
        await asyncio.sleep(0.5)
        await page.keyboard.press('Enter')
        
        await asyncio.sleep(5)
    
    async def load_all_products(self, page: Page):
        """
        Load all products by clicking 'Mostrar mais' until no more products.
        """
        previous_count = 0
        max_iterations = 10
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            
            products = await ElementUtils.find_elements(
                page, 
                self.config.selectors["product_items"]
            )
            
            current_count = len(products)
            
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
            await asyncio.sleep(2)
    
    async def extract_product_data(self, product: ElementHandle) -> Dict[str, str]:
        """
        Extract product information from a product element.
        """
        name = await ElementUtils.extract_text(product, self.config.selectors["name"])
        
        price = await ElementUtils.extract_text(product, self.config.selectors["price"])
        
        # Special handling for price since it might need to be constructed from multiple elements
        if price == "Price not found":
            # Try to find price components and construct the full price
            currency_integer = await product.query_selector('.vtex-product-price-1-x-currencyInteger')
            if currency_integer:
                integer_text = await currency_integer.text_content()
                
                currency_symbol = await product.query_selector('.vtex-product-price-1-x-currencyContainer')
                decimal_part = await product.query_selector('.vtex-product-price-1-x-currencyFraction')
                
                if currency_symbol:
                    symbol_text = await currency_symbol.text_content()
                    price = f"{symbol_text} {integer_text}"
                    if decimal_part:
                        decimal_text = await decimal_part.text_content()
                        price += f",{decimal_text}"
                else:
                    price = f"R$ {integer_text}"
        
        unit_price = await ElementUtils.extract_text(product, self.config.selectors["unit_price"])
        
        return {
            "name": name or "Name not found",
            "price": price or "Price not found",
            "unit_price": unit_price if unit_price and unit_price != price else ""
        }
    
    async def extract_all_products(self, page: Page) -> List[Dict[str, str]]:
        """
        Extract data from all product elements on the page.
        """
        products = await ElementUtils.find_elements(
            page, 
            self.config.selectors["product_items"]
        )
        
        product_list = []
        
        for product in products:
            try:
                product_data = await self.extract_product_data(product)
                product_list.append(product_data)
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                continue
        
        return product_list