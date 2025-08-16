import asyncio
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def search_angeloni_products(search_term: str) -> str:
    """Search for products on Angeloni website."""
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
            # Navigate to Angeloni website
            await page.goto("https://www.angeloni.com.br/super/?utm_source=site+eletro&utm_medium=clicks&utm_campaign=Super_Eletro&utm_id=super", timeout=30000)
            await asyncio.sleep(3)
            
            # Try multiple approaches to find the search input
            search_selectors = [
                'input[placeholder="Buscar por categorias, produtos ou marcas"]',
                'input[placeholder*="Buscar"]',
                'input[type="text"]',
                '.vtex-styleguide-9-x-input'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await page.wait_for_selector(selector, timeout=3000)
                    if search_input:
                        break
                except:
                    continue
            
            if not search_input:
                return "❌ Could not find search input on Angeloni website"
            
            # Perform search
            await search_input.click()
            await search_input.fill(search_term)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            
            # Wait for search results
            await asyncio.sleep(5)
            
            # Load all products by handling pagination
            previous_count = 0
            max_iterations = 10
            iteration_count = 0
            
            while iteration_count < max_iterations:
                iteration_count += 1
                
                # Try different product selectors
                product_selectors = [
                    '.vtex-search-result-3-x-galleryItem',
                    '.vtex-product-summary-2-x-container',
                    '.vtex-product-summary-2-x-element',
                    '[data-testid*="product"]',
                    '[class*="product-summary"]',
                    '[class*="galleryItem"]',
                    '[class*="product-item"]',
                    '.shelf-item'
                ]
                
                products = []
                working_selector = None
                
                for selector in product_selectors:
                    products = await page.query_selector_all(selector)
                    if products:
                        working_selector = selector
                        break
                
                current_count = len(products)
                
                # If no new products were loaded, break
                if current_count == previous_count:
                    break
                
                previous_count = current_count
                
                # Look for "Mostrar mais" button
                mostrar_mais_selectors = [
                    'a.vtex-button[rel="next"]:has-text("Mostrar mais")',
                    'a[rel="next"]:has-text("Mostrar mais")',
                    'a.vtex-button:has-text("Mostrar mais")',
                    'a[href*="page="]:has-text("Mostrar mais")'
                ]
                
                mostrar_mais_button = None
                for selector in mostrar_mais_selectors:
                    try:
                        mostrar_mais_button = await page.wait_for_selector(selector, state='visible', timeout=2000)
                        if mostrar_mais_button:
                            break
                    except:
                        continue
                
                if mostrar_mais_button:
                    await mostrar_mais_button.scroll_into_view_if_needed()
                    await mostrar_mais_button.click()
                    await asyncio.sleep(2)
                else:
                    break
            
            # Get final product count
            for selector in product_selectors:
                products = await page.query_selector_all(selector)
                if products:
                    break
            
            if not products:
                return f"❌ No products found for '{search_term}' on Angeloni"
            
            # Extract product information
            result_text = f"🛒 Angeloni Search Results for '{search_term}':\n"
            result_text += f"Total products found: {len(products)}\n\n"
            
            for i, product in enumerate(products):
                try:
                    # Try to find product name
                    name_selectors = [
                        '.vtex-product-summary-2-x-productBrand',
                        '.vtex-product-summary-2-x-productName',
                        '[class*="productBrand"]',
                        '[class*="productName"]',
                        'h1', 'h2', 'h3', 'h4',
                        'a[title]'
                    ]
                    
                    name = "Name not found"
                    for selector in name_selectors:
                        name_element = await product.query_selector(selector)
                        if name_element:
                            name = await name_element.text_content()
                            if name and name.strip():
                                name = name.strip()
                                break
                    
                    # Try to find price
                    price_selectors = [
                        '.vtex-product-price-1-x-currencyInteger',
                        '.vtex-product-price-1-x-currencyInteger--summary',
                        '.vtex-product-summary-2-x-price_sellingPrice',
                        '.vtex-product-price-1-x-sellingPriceValue',
                        '.vtex-product-price-1-x-sellingPrice',
                        '[class*="sellingPrice"]',
                        '[class*="currencyInteger"]',
                        '[class*="price"]',
                        '[class*="Price"]'
                    ]
                    
                    price = "Price not found"
                    for selector in price_selectors:
                        price_element = await product.query_selector(selector)
                        if price_element:
                            price_text = await price_element.text_content()
                            if price_text and price_text.strip():
                                if 'currencyInteger' in selector:
                                    price_container = await price_element.query_selector('xpath=..')
                                    if price_container:
                                        full_price = await price_container.text_content()
                                        if full_price and 'R$' in full_price:
                                            price = full_price.strip()
                                            break
                                    currency_symbol = await product.query_selector('.vtex-product-price-1-x-currencyContainer')
                                    decimal_part = await product.query_selector('.vtex-product-price-1-x-currencyFraction')
                                    
                                    if currency_symbol:
                                        symbol_text = await currency_symbol.text_content()
                                        price = f"{symbol_text} {price_text}"
                                        if decimal_part:
                                            decimal_text = await decimal_part.text_content()
                                            price += f",{decimal_text}"
                                        break
                                    else:
                                        price = f"R$ {price_text}"
                                        break
                                elif 'R$' in price_text or '$' in price_text:
                                    price = price_text.strip()
                                    break
                    
                    # Try to find unit price
                    unit_price_element = await product.query_selector('[class*="unitPrice"], [class*="unit-price"]')
                    unit_price = await unit_price_element.text_content() if unit_price_element else ""
                    
                    product_info = f"{i+1}. {name}\n   Price: {price}"
                    if unit_price and unit_price.strip() and unit_price != price:
                        product_info += f" ({unit_price.strip()})"
                    
                    result_text += product_info + "\n\n"
                    
                except Exception as e:
                    continue
            
            return result_text
                    
        except Exception as e:
            logger.error(f"Angeloni scraping error: {e}")
            return f"❌ Error searching Angeloni: {str(e)}"
        finally:
            await browser.close()
