class Config:
    """
    Configuration class for Angeloni scraper.
    """
    def __init__(self):
        self.base_url = "https://www.angeloni.com.br/super/?utm_source=site+eletro&utm_medium=clicks&utm_campaign=Super_Eletro&utm_id=super"
        
        self.browser_args = ['--disable-dev-shm-usage', '--no-sandbox']
        self.viewport = {'width': 1920, 'height': 1080}
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        self.timeouts = {
            "page_load": 30000,
            "element_wait": 3000,
            "load_more": 2000
        }
        
        self.selectors = {
            "search_input": [
                'input[placeholder="Buscar por categorias, produtos ou marcas"]',
                'input[placeholder*="Buscar"]',
                'input[type="text"]',
                '.vtex-styleguide-9-x-input'
            ],
            "product_items": [
                '.vtex-search-result-3-x-galleryItem',
                '.vtex-product-summary-2-x-container',
                '.vtex-product-summary-2-x-element',
                '[data-testid*="product"]',
                '[class*="product-summary"]',
                '[class*="galleryItem"]',
                '[class*="product-item"]',
                '.shelf-item'
            ],
            "load_more": [
                'a.vtex-button[rel="next"]:has-text("Mostrar mais")',
                'a[rel="next"]:has-text("Mostrar mais")',
                'a.vtex-button:has-text("Mostrar mais")',
                'a[href*="page="]:has-text("Mostrar mais")'
            ],
            "name": [
                '.vtex-product-summary-2-x-productBrand',
                '.vtex-product-summary-2-x-productName',
                '[class*="productBrand"]',
                '[class*="productName"]',
                'h1', 'h2', 'h3', 'h4',
                'a[title]'
            ],
            "price": [
                '.vtex-product-price-1-x-currencyInteger',
                '.vtex-product-price-1-x-currencyInteger--summary',
                '.vtex-product-summary-2-x-price_sellingPrice',
                '.vtex-product-price-1-x-sellingPriceValue',
                '.vtex-product-price-1-x-sellingPrice',
                '[class*="sellingPrice"]',
                '[class*="currencyInteger"]',
                '[class*="price"]',
                '[class*="Price"]'
            ],
            "unit_price": [
                '[class*="unitPrice"]', 
                '[class*="unit-price"]'
            ]
        }