import logging
import asyncio
import json
from fastmcp import FastMCP
from giassi.scraper import GiassiScraper
from utils.formatter import Formatter
from utils.product_list import ProductList
from angeloni.scraper import AngeloniScraper
from config_loader import ScraperConfig
from utils.calc_distance import FindDistance
from utils.price_calculator import sum_prices_by_store

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configurations
giassi_config = ScraperConfig('giassi_config.yaml')
angeloni_config = ScraperConfig('angeloni_config.yaml')

# Create FastMCP server
mcp = FastMCP("Product Search")

# Initialize product list manager
product_list = ProductList()

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

@mcp.tool()
async def add_to_list(unidades: str, product_name: str, store: str, price: str) -> str:
    """
    Add a product to your shopping list
    
    Args:
        product_name: Name of the product
        store: Store name (e.g., 'Giassi', 'Angeloni')
        price: Price of the product
    
    Returns:
        Confirmation message
    """
    return product_list.add_product(unidades, product_name, store, price)

@mcp.tool()
async def view_list() -> str:
    """
    View all products in your shopping list
    
    Returns:
        Formatted list of all products
    """
    return product_list.view_products()

@mcp.tool()
async def remove_from_list(product_name: str) -> str:
    """
    Remove a product from your shopping list
    
    Args:
        product_name: Name of the product to remove
    
    Returns:
        Confirmation message
    """
    return product_list.remove_product(product_name)

@mcp.tool()
async def update_unidades(product_name: str, new_unidades: str) -> str:
    """
    Update the unidades value for a product in your shopping list
    
    Args:
        product_name: Name of the product to update
        new_unidades: New unidades value
    
    Returns:
        Confirmation message
    """
    return product_list.update_unidades(product_name, new_unidades)

@mcp.tool()
async def find_nearest_supermarket(address: str) -> str:
    """
    Find the closest supermarket to a given address
    
    Args:
        address: The user's address (e.g., 'Rua das Flores, 123, Joinville, SC')
    
    Returns:
        Information about the closest supermarket including name, address, and distance
    """
    finder = FindDistance()
    try:
        result = finder.find_closest_supermarket(address)

        if result is None:
            return f"Could not find location for address: {address}. Please check the address and try again."
        
        return (f"Closest supermarket to your address:\n"
               f"📍 {result['name']}\n"
               f"📋 Address: {result['address']}\n"
               f"📏 Distance: {result['distance_km']} km")
        
    except Exception as e:
        logger.error(f"Error finding closest supermarket: {e}")
        return f"Error finding closest supermarket: {str(e)}"

@mcp.tool()
async def calculate_shopping_totals() -> str:
    """
    Calculate the total price of products in the shopping list grouped by supermarket
    
    Returns:
        Total prices separated by supermarket with grand total
    """
    return sum_prices_by_store()

if __name__ == "__main__":
    mcp.run()