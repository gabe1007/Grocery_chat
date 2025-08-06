import logging
from fastmcp import FastMCP
from giassi.scraper import GiassiScraper
from giassi.formatter import ProductFormatter
from giassi.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = Config()

# Create FastMCP server
mcp = FastMCP("Giassi Product Search")

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

if __name__ == "__main__":
    mcp.run()