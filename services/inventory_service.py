"""Inventory service - business logic for inventory management."""

from app import mysql


class InventoryService:
    @staticmethod
    def check_stock(product_id, quantity):
        """Check if sufficient stock is available."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT stock FROM products WHERE id = %s AND is_active = 1", (product_id,))
        product = cur.fetchone()
        cur.close()
        
        if not product:
            return False, "Product not found"
        if product['stock'] < quantity:
            return False, f"Only {product['stock']} items available"
        return True, "Stock available"

    @staticmethod
    def get_low_stock_products(threshold=10):
        """Get products with stock below threshold."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.id, p.name, p.stock, p.sku, i.low_stock_threshold
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.is_active = 1 AND p.stock <= COALESCE(i.low_stock_threshold, %s)
            ORDER BY p.stock ASC
        """, (threshold,))
        products = cur.fetchall()
        cur.close()
        return products
