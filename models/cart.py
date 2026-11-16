"""Cart model - database operations for shopping cart."""

from app import mysql


class Cart:
    @staticmethod
    def get_or_create(customer_id):
        """Get existing cart or create new one for customer."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM cart WHERE customer_id = %s", (customer_id,))
        cart = cur.fetchone()
        if not cart:
            cur.execute("INSERT INTO cart (customer_id) VALUES (%s)", (customer_id,))
            mysql.connection.commit()
            cart_id = cur.lastrowid
        else:
            cart_id = cart['id']
        cur.close()
        return cart_id

    @staticmethod
    def get_items(customer_id):
        """Get all cart items with product details."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ci.*, p.name, p.price, p.discount_price, p.stock, p.image_url,
                   COALESCE(p.discount_price, p.price) as effective_price,
                   (ci.quantity * COALESCE(p.discount_price, p.price)) as item_total
            FROM cart c
            JOIN cart_items ci ON c.id = ci.cart_id
            JOIN products p ON ci.product_id = p.id
            WHERE c.customer_id = %s AND p.is_active = 1
            ORDER BY ci.created_at DESC
        """, (customer_id,))
        items = cur.fetchall()
        cur.close()
        return items

    @staticmethod
    def add_item(customer_id, product_id, quantity=1):
        """Add item to cart or update quantity if exists."""
        cart_id = Cart.get_or_create(customer_id)
        cur = mysql.connection.cursor()
        
        # Check if item already in cart
        cur.execute(
            "SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s",
            (cart_id, product_id)
        )
        existing = cur.fetchone()
        
        if existing:
            new_qty = existing['quantity'] + quantity
            cur.execute(
                "UPDATE cart_items SET quantity = %s WHERE id = %s",
                (new_qty, existing['id'])
            )
        else:
            cur.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)",
                (cart_id, product_id, quantity)
            )
        
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def update_quantity(customer_id, product_id, quantity):
        """Update item quantity in cart."""
        cur = mysql.connection.cursor()
        if quantity <= 0:
            Cart.remove_item(customer_id, product_id)
            return
        cur.execute("""
            UPDATE cart_items ci
            JOIN cart c ON ci.cart_id = c.id
            SET ci.quantity = %s
            WHERE c.customer_id = %s AND ci.product_id = %s
        """, (quantity, customer_id, product_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def remove_item(customer_id, product_id):
        """Remove item from cart."""
        cur = mysql.connection.cursor()
        cur.execute("""
            DELETE ci FROM cart_items ci
            JOIN cart c ON ci.cart_id = c.id
            WHERE c.customer_id = %s AND ci.product_id = %s
        """, (customer_id, product_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def clear(customer_id):
        """Clear all items from cart."""
        cur = mysql.connection.cursor()
        cur.execute("""
            DELETE ci FROM cart_items ci
            JOIN cart c ON ci.cart_id = c.id
            WHERE c.customer_id = %s
        """, (customer_id,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_total(customer_id):
        """Calculate cart total."""
        items = Cart.get_items(customer_id)
        subtotal = sum(item['item_total'] for item in items)
        return subtotal

    @staticmethod
    def get_count(customer_id):
        """Get total number of items in cart."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(ci.quantity), 0) as count
            FROM cart c
            JOIN cart_items ci ON c.id = ci.cart_id
            WHERE c.customer_id = %s
        """, (customer_id,))
        result = cur.fetchone()
        cur.close()
        return result['count'] if result else 0
