import asyncio
import logging
from playwright.async_api import async_playwright
from fastmcp import FastMCP

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Giassi Product Search")

async def scrape_giassi_products(search_term: str) -> dict:
    """Search for products on Giassi website."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            await page.goto("https://www.giassi.com.br/", timeout=30000)
            await asyncio.sleep(2)
            
            search_input = await page.wait_for_selector('input[placeholder*="Pesquise"]', timeout=5000)
            await search_input.click()
            await search_input.fill(search_term)
            await page.keyboard.press('Enter')
            
            await page.wait_for_selector('.vtex-search-result-3-x-galleryItem', timeout=15000)
            await asyncio.sleep(2)
            
            previous_count = 0
            while True:
                current_products = await page.query_selector_all('.vtex-search-result-3-x-galleryItem')
                current_count = len(current_products)
                
                if current_count == previous_count:
                    break
                
                previous_count = current_count
                
                mostrar_mais_selectors = [
                    'a:has-text("Mostrar mais")',
                    'a[rel="next"]',
                    '.vtex-button:has-text("Mostrar mais")',
                    'a.vtex-button'
                ]
                
                mostrar_mais_link = None
                for selector in mostrar_mais_selectors:
                    try:
                        mostrar_mais_link = await page.wait_for_selector(selector, state='visible', timeout=3000)
                        if mostrar_mais_link:
                            break
                    except:
                        continue
                
                if mostrar_mais_link:
                    await mostrar_mais_link.scroll_into_view_if_needed()
                    await mostrar_mais_link.click()
                    await asyncio.sleep(3)
                else:
                    break
            
            products = await page.query_selector_all('.vtex-search-result-3-x-galleryItem')
            
            product_list = []
            for product in products:
                try:
                    name_element = await product.query_selector('.vtex-product-summary-2-x-productBrand')
                    
                    price_selectors = [
                        '.vtex-product-summary-2-x-price_sellingPrice',
                        '.vtex-product-price-1-x-sellingPriceValue',
                        '.vtex-product-price-1-x-sellingPrice',
                        '[class*="price"]',
                        '[class*="Price"]',
                        '.giassi-apps-custom-0-x-priceTotalUnita'
                    ]
                    
                    price_element = None
                    price = "Price not found"
                    
                    for selector in price_selectors:
                        price_element = await product.query_selector(selector)
                        if price_element:
                            price = await price_element.text_content()
                            if price and price.strip() and 'R$' in price:
                                break
                    
                    unit_price_element = await product.query_selector('.giassi-apps-custom-0-x-priceTotalUnita')
                    
                    name = await name_element.text_content() if name_element else "Name not found"
                    unit_price = await unit_price_element.text_content() if unit_price_element else ""
                    
                    product_data = {
                        "name": name.strip() if name else "Unknown",
                        "price": price.strip() if price else "Price not available",
                        "unit_price": unit_price.strip() if unit_price and unit_price != price else ""
                    }
                    
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
            await browser.close()

@mcp.tool()
async def search_giassi(search_term: str) -> str:
    """
    Search for products on Giassi supermarket website
    
    Args:
        search_term: Product to search for on Giassi website (e.g., 'arroz', 'leite', 'açúcar')
    
    Returns:
        Formatted list of products with names and prices
    """
    if not search_term or not search_term.strip():
        return "Error: Search term cannot be empty"
    
    logger.info(f"Searching for: {search_term}")
    
    try:
        result = await scrape_giassi_products(search_term.strip())
        
        if result["success"]:
            response_text = f"🛒 Search Results for '{result['search_term']}':\n"
            response_text += f"📊 Total products found: {result['total_products']}\n\n"
            
            for i, product in enumerate(result["products"], 1):
                response_text += f"{i}. 🏷️ {product['name']}\n"
                response_text += f"   💰 Price: {product['price']}\n"
                if product['unit_price']:
                    response_text += f"   📏 Unit Price: {product['unit_price']}\n"
                response_text += "\n"
                
            if result['total_products'] == 0:
                response_text += "❌ No products found for this search term."
        else:
            response_text = f"❌ Search failed for '{result['search_term']}':\n"
            response_text += f"Error: {result.get('error', 'Unknown error')}"
        
        return response_text
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return f"❌ Error searching for products: {str(e)}"

if __name__ == "__main__":
    mcp.run()
