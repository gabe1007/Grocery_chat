import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ProductList:
    def __init__(self, file_path: str = "product_list.json"):
        self.file_path = file_path
    
    def load_products(self) -> List[Dict]:
        """
        Load product list from JSON file
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                logger.warning(f"Could not load {self.file_path}, starting with empty list")
        return []
    
    def save_products(self, products: List[Dict]) -> None:
        """
        Save product list to JSON file
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Could not save product list: {e}")
            raise

    def add_product(self, unidades: str, product_name: str, store: str, price: str) -> str:
        """
        Add a product to the list
        """
        products = self.load_products()
        
        # Check if product already exists
        for product in products:
            if product.get('name') == product_name and product.get('store') == store:
                return f"Product '{product_name}' from {store} is already in your list"
        
        # Add new product
        new_product = {
            'unidades': unidades,
            'name': product_name,
            'store': store,
            'price': price
        }
        products.append(new_product)
        self.save_products(products)
        
        return f"Added '{product_name}' from {store} (R$ {price}) to your list"
    
    def remove_product(self, product_name: str) -> str:
        """
        Remove a product from the list
        """
        products = self.load_products()
        
        # Find and remove product
        for i, product in enumerate(products):
            if product.get('name') == product_name:
                removed_product = products.pop(i)
                self.save_products(products)
                return f"Removed '{removed_product['name']}' from {removed_product['store']} from your list"
        
        return f"Product '{product_name}' not found in your list"
    
    def view_products(self) -> str:
        """
        View all products in the list
        """
        products = self.load_products()
        
        if not products:
            return "Your product list is empty"
        
        result = ["Your Product List:"]
        for i, product in enumerate(products, 1):
            unidades = product.get('unidades', 'N/A')
            result.append(f"{i}. {product['name']} - {product['store']} - R$ {product['price']} - Unidades: {unidades}")
        
        return "\n".join(result)
    
    def update_unidades(self, product_name: str, new_unidades: str) -> str:
        """
        Update the unidades value for a product
        """
        products = self.load_products()
        
        # Find and update product
        for product in products:
            if product.get('name') == product_name:
                old_unidades = product.get('unidades', 'N/A')
                product['unidades'] = new_unidades
                self.save_products(products)
                return f"Updated '{product_name}' unidades from {old_unidades} to {new_unidades}"
        
        return f"Product '{product_name}' not found in your list"