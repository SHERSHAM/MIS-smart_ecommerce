"""Cart service - business logic for cart operations."""

from models.cart import Cart
from models.product import Product
from config import Config


class CartService:
    @staticmethod
    def calculate_totals(customer_id):
        """Calculate cart totals including shipping."""
        items = Cart.get_items(customer_id)
        subtotal = sum(float(item['item_total']) for item in items)
        
        if not items:
            return {'items': [], 'subtotal': 0, 'shipping': 0, 'total': 0, 'item_count': 0}
        
        shipping = 0 if subtotal >= Config.FREE_SHIPPING_THRESHOLD else Config.SHIPPING_FEE
        total = subtotal + shipping
        item_count = sum(item['quantity'] for item in items)
        
        return {
            'items': items,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': total,
            'item_count': item_count
        }

    @staticmethod
    def validate_stock(customer_id):
        """Validate stock for all cart items. Returns list of issues."""
        items = Cart.get_items(customer_id)
        issues = []
        
        for item in items:
            product = Product.get_by_id(item['product_id'])
            if not product:
                issues.append({'product_id': item['product_id'], 'name': item['name'], 
                              'issue': 'Product no longer available'})
            elif product['stock'] < item['quantity']:
                issues.append({'product_id': item['product_id'], 'name': item['name'],
                              'issue': f'Only {product["stock"]} available',
                              'available': product['stock']})
        
        return issues
