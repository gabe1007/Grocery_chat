import logging
from typing import Dict
from .config import GiassiConfig
from .browser_manager import BrowserManager
from .product_extractor import ProductExtractor

logger = logging.getLogger(__name__)


class GiassiScraper:
    """
    Web scraper for Giassi supermarket products.
    
    Orchestrates the scraping process using specialized components for
    browser management and product extraction.
    """

    def __init__(self, config: GiassiConfig = None):
        """
        Initialize the scraper with configuration and components.
        """
        self.config = config or GiassiConfig()
        self.browser_manager = BrowserManager(self.config)
        self.product_extractor = ProductExtractor(self.config)
    
    async def close(self):
        """
        Close the browser instance and clean up resources.
        """
        await self.browser_manager.close()
    
    async def scrape_products(self, search_term: str) -> Dict[str, any]:
        """
        Main method to scrape products for a given search term.
        
        Orchestrates the entire scraping process using specialized components.
        """
        if not search_term or not search_term.strip():
            return {
                "success": False,
                "error": "Search term cannot be empty",
                "search_term": search_term,
                "total_products": 0,
                "products": []
            }
        
        page = None
        try:
            page = await self.browser_manager.new_page()
            
            await self.product_extractor.search_products(page, search_term)
            await self.product_extractor.load_all_products(page)
            
            product_list = await self.product_extractor.extract_all_products(page)
            
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
            if page:
                await page.close()
                