import asyncio
import logging
from typing import Dict, List
from playwright.async_api import Page
from .browser_manager import BrowserManager
from .product_extractor import ProductExtractor
from .formatter import ProductFormatter
from .config import AngeloniConfig

logger = logging.getLogger(__name__)

class AngeloniScraper:
    """
    Main scraper class that coordinates the scraping process.
    """
    def __init__(self, config: AngeloniConfig = None):
        self.config = config or AngeloniConfig()
        self.browser_manager = BrowserManager(self.config)
        self.product_extractor = ProductExtractor(self.config)
    
    async def scrape_products(self, search_term: str) -> Dict:
        """
        Scrape products from Angeloni website based on search term.
        
        Args:
            search_term: The product to search for
            
        Returns:
            Dictionary containing scraping results
        """
        try:
            page = await self.browser_manager.new_page()
            
            # Search for products
            await self.product_extractor.search_products(page, search_term)
            
            # Load all products
            await self.product_extractor.load_all_products(page)
            
            # Extract product data
            products = await self.product_extractor.extract_all_products(page)
            
            return {
                "success": True,
                "search_term": search_term,
                "total_products": len(products),
                "products": products
            }
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return {
                "success": False,
                "search_term": search_term,
                "error": str(e)
            }
    
    async def close(self):
        """
        Close the browser and clean up resources.
        """
        await self.browser_manager.close()

async def search_angeloni_products(search_term: str) -> str:
    """Search for products on Angeloni website."""
    config = AngeloniConfig()
    scraper = AngeloniScraper(config)
    
    try:
        results = await scraper.scrape_products(search_term.strip())
        return ProductFormatter.format_results(results)
    except Exception as e:
        logger.error(f"Angeloni scraping error: {e}")
        return f"❌ Error searching Angeloni: {str(e)}"
    finally:
        await scraper.close()
        