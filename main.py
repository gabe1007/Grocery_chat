import logging
import asyncio
from fastmcp import FastMCP
from giassi.scraper import GiassiScraper
from utils.formatter import Formatter
from angeloni.scraper import AngeloniScraper
from config_loader import ScraperConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configurations
giassi_config = ScraperConfig('giassi_config.yaml')
angeloni_config = ScraperConfig('angeloni_config.yaml')

# Create FastMCP server
mcp = FastMCP("Product Search")

@mcp.tool()
async def search_products(search_term: str) -> str:
    """
    Search for products on both Giassi and Angeloni supermarket websites concurrently
    
    Args:
        search_term: Product to search for (e.g., 'arroz', 'leite', 'açúcar')
    
    Returns:
        Formatted list of products from both stores with names and prices
    """
    logger.info(f"Searching both stores for: {search_term}")
    
    # Create scrapers
    giassi_scraper = GiassiScraper(giassi_config)
    angeloni_scraper = AngeloniScraper(angeloni_config)
    
    async def search_giassi():
        try:
            results = await giassi_scraper.scrape_products(search_term.strip())
            return ("Giassi", results)
        except Exception as e:
            logger.error(f"Giassi search error: {e}")
            return ("Giassi", f"Error: {str(e)}")
        finally:
            await giassi_scraper.close()
    
    async def search_angeloni():
        try:
            results = await angeloni_scraper.scrape_products(search_term.strip())
            return ("Angeloni", results)
        except Exception as e:
            logger.error(f"Angeloni search error: {e}")
            return ("Angeloni", f"Error: {str(e)}")
        finally:
            await angeloni_scraper.close()
    
    try:
        # Run both searches concurrently
        giassi_result, angeloni_result = await asyncio.gather(
            search_giassi(),
            search_angeloni(),
            return_exceptions=True
        )
        
        # Format combined results
        formatted_output = []
        
        # Handle Giassi results
        store_name, results = giassi_result
        if isinstance(results, str) and results.startswith("Error"):
            formatted_output.append(f"\n=== {store_name} ===\n{results}")
        else:
            formatted_giassi = Formatter.format_results(results)
            formatted_output.append(f"\n=== {store_name} ===\n{formatted_giassi}")
        
        # Handle Angeloni results
        store_name, results = angeloni_result
        if isinstance(results, str) and results.startswith("Error"):
            formatted_output.append(f"\n=== {store_name} ===\n{results}")
        else:
            formatted_angeloni = Formatter.format_results(results)
            formatted_output.append(f"\n=== {store_name} ===\n{formatted_angeloni}")

        logger.info("\n".join(formatted_output))

        return "\n".join(formatted_output)
        
    except Exception as e:
        logger.error(f"Concurrent search error: {e}")
        return f"Error during concurrent search: {str(e)}"

if __name__ == "__main__":
    mcp.run()