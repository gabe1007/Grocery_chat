import logging
from fastmcp import FastMCP
from giassi.scraper import GiassiScraper
from giassi.formatter import ProductFormatter
from giassi.config import Config
from angeloni.angeloni_scraper import search_angeloni_products

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = Config()

# Create FastMCP server
mcp = FastMCP("Product Search")

@mcp.tool()
async def search_giassi(search_term: str) -> str:
    """
    Search for products on Giassi supermarket website
    Args:
        search_term: Product to search for on Giassi website (e.g., 'arroz', 'leite', 'açúcar')
    Returns:
        Formatted list of products with names and prices
    """
    logger.info(f"Searching for: {search_term}")
    
    scraper = GiassiScraper(config)
    try:
        results = await scraper.scrape_products(search_term.strip())
        return ProductFormatter.format_results(results)
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return f"❌ Error searching for products: {str(e)}"
    finally:
        await scraper.close()  # Always close the browser

@mcp.tool()
async def search_angeloni(search_term: str) -> str:
    """
    Search for products on Angeloni supermarket website
    Args:
        search_term: Product to search for on Angeloni website (e.g., 'arroz', 'leite', 'açúcar')
    Returns:
        Formatted list of products with names and prices
    """
    logger.info(f"Searching Angeloni for: {search_term}")
    try:
        return await search_angeloni_products(search_term.strip())
    except Exception as e:
        logger.error(f"Angeloni tool execution error: {e}")
        return f"❌ Error searching Angeloni: {str(e)}"

if __name__ == "__main__":
    mcp.run()