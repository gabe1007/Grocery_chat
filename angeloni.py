import asyncio
from playwright.async_api import async_playwright


async def search_angeloni_products(search_term):
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
            print("Navigating to Angeloni...")
            await page.goto("https://www.angeloni.com.br/super/?utm_source=site+eletro&utm_medium=clicks&utm_campaign=Super_Eletro&utm_id=super", timeout=30000)
            await asyncio.sleep(3)
            
            # Try multiple approaches to find the search input
            print("Looking for search input...")
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
                        print(f"Found search input with selector: {selector}")
                        break
                except:
                    continue
            
            if not search_input:
                print("Could not find search input!")
                # List all inputs for debugging
                all_inputs = await page.query_selector_all('input')
                print(f"Found {len(all_inputs)} input elements:")
                for i, inp in enumerate(all_inputs[:5]):
                    placeholder = await inp.get_attribute('placeholder')
                    input_type = await inp.get_attribute('type')
                    print(f"Input {i}: type='{input_type}', placeholder='{placeholder}'")
                return
            
            # Perform search
            print(f"Searching for '{search_term}'...")
            await search_input.click()
            await search_input.fill(search_term)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            
            # Wait for search results with longer timeout
            print("Waiting for search results...")
            await asyncio.sleep(5)  # Give more time for results to load
            
            # Check current URL to see if we're on a search results page
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Load all products by handling pagination
            print("Loading all products...")
            previous_count = 0
            max_iterations = 10  # Safety limit to prevent infinite loops
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
                print(f"Currently loaded: {current_count} products (iteration {iteration_count})")
                
                # If no new products were loaded, break
                if current_count == previous_count:
                    print("No new products loaded, stopping pagination")
                    break
                
                previous_count = current_count
                
                # Look for the specific "Mostrar mais" button from the HTML you provided
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
                            print(f"Found 'Mostrar mais' button with selector: {selector}")
                            break
                    except:
                        continue
                
                if mostrar_mais_button:
                    # Scroll to the button and click it
                    await mostrar_mais_button.scroll_into_view_if_needed()
                    await mostrar_mais_button.click()
                    print("Clicked 'Mostrar mais' button")
                    await asyncio.sleep(2)  # Reduced wait time
                else:
                    print("No 'Mostrar mais' button found, all products loaded")
                    break
            
            if iteration_count >= max_iterations:
                print(f"Reached maximum iterations ({max_iterations}), stopping to prevent infinite loop")
            
            # Get final product count
            for selector in product_selectors:
                products = await page.query_selector_all(selector)
                if products:
                    working_selector = selector
                    print(f"Final count: {len(products)} products using selector: {selector}")
                    break
            
            if not products:
                print("No products found with any selector. Debugging...")
                
                # Check if there's a "no results" message
                no_results_selectors = [
                    ':text("Não encontramos")',
                    ':text("nenhum resultado")',
                    ':text("Nenhum produto")',
                    '[class*="no-results"]',
                    '[class*="empty"]'
                ]
                
                for selector in no_results_selectors:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        print(f"Found no-results message: {text}")
                        return
                
                # Show page title to understand where we are
                title = await page.title()
                print(f"Page title: {title}")
                
                return
            
            # Extract product information
            print(f"\nFound {len(products)} products for '{search_term}':")
            
            for i, product in enumerate(products):  # Show all products, not just first 20
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
                                # For currencyInteger, we might need to get the full price container
                                if 'currencyInteger' in selector:
                                    # Try to get the parent container that might have the full price
                                    price_container = await price_element.query_selector('xpath=..')
                                    if price_container:
                                        full_price = await price_container.text_content()
                                        if full_price and 'R$' in full_price:
                                            price = full_price.strip()
                                            break
                                    # If no container, try to build price from multiple elements
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
                    
                    product_info = f"- {name}: {price}"
                    if unit_price and unit_price.strip() and unit_price != price:
                        product_info += f" ({unit_price.strip()})"
                    
                    print(product_info)
                    
                except Exception as e:
                    print(f"Error processing product {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()


def main():
    search_term = "arroz 5kg"  # Change this to search for any product
    asyncio.run(search_angeloni_products(search_term))


if __name__ == "__main__":
    main()
