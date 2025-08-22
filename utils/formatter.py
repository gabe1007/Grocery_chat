class Formatter:

    @staticmethod
    def format_results(results: dict) -> str:
        """
        Format the scraped product results into a readable string.
        
        Args:
            results: Dictionary containing the scraping results
            
        Returns:
            Formatted string with product information
        """
        if not results["success"]:
            return f"Search failed for '{results['search_term']}':\nError: {results.get('error', 'Unknown error')}"
            
        response_text = f"Search Results for '{results['search_term']}':\n"
        response_text += f"Total products found: {results['total_products']}\n\n"
        
        if results['total_products'] == 0:
            response_text += "No products found for this search term."
            return response_text
            
        for i, product in enumerate(results["products"], 1):
            response_text += f"{i}. {product['name']}\n"
            response_text += f" Price: {product['price']}\n"
            if product['unit_price']:
                response_text += f"Unit Price: {product['unit_price']}\n"
            response_text += "\n"
                
        return response_text
    