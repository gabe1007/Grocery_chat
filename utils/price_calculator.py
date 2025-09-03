import json
import logging

logger = logging.getLogger(__name__)

def sum_prices_by_store(file_path: str = 'product_list.json') -> str:
    """
    Sum the total price of products from the product list grouped by supermarket
    
    Args:
        file_path: Path to the product list JSON file
        
    Returns:
        Total prices separated by supermarket
    """
    try:
        with open(file_path, 'r') as file:
            products = json.load(file)
        
        store_totals = {}
        
        for product in products:
            store = product.get('store', 'Unknown')
            price_str = product.get('price', 'R$ 0,00')
            unidades_str = product.get('unidades', '1')
            
            # Extract numeric value from price string (e.g., "R$ 16,07" -> 16.07)
            price_clean = price_str.replace('R$', '').strip().replace(',', '.')
            price_value = float(price_clean)
            
            # Extract unidades value
            unidades = float(unidades_str)
            
            # Calculate total for this product (price * unidades)
            total_product_value = price_value * unidades
            
            if store in store_totals:
                store_totals[store] += total_product_value
            else:
                store_totals[store] = total_product_value
        
        # Format the results
        result = "💰 Price Summary by Supermarket:\n\n"
        grand_total = 0
        
        for store, total in store_totals.items():
            formatted_total = f"R$ {total:.2f}".replace('.', ',')
            result += f"🏪 {store}: {formatted_total}\n"
            grand_total += total
        
        formatted_grand_total = f"R$ {grand_total:.2f}".replace('.', ',')
        result += f"\n📊 Grand Total: {formatted_grand_total}"
        
        return result
        
    except FileNotFoundError:
        return "❌ Product list file not found. Please add some products first."
    except json.JSONDecodeError:
        return "❌ Error reading product list file. File may be corrupted."
    except Exception as e:
        logger.error(f"Error summing prices: {e}")
        return f"❌ Error calculating price totals: {str(e)}"