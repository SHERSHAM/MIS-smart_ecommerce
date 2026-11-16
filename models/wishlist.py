"""Wishlist model - database operations for wishlists."""

from app import mysql


class Wishlist:
    @staticmethod
    def get_or_create(customer_id):
        """Get existing wishlist or create new one."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM wishlist WHERE customer_id = %s", (customer_id,))
        wishlist = cur.fetchone()
        if not wishlist:
            cur.execute("INSERT INTO wishlist (customer_id) VALUES (%s)", (customer_id,))
            mysql.connection.commit()
            wishlist_id = cur.lastrowid
        else:
            wishlist_id = wishlist['id']
        cur.close()
        return wishlist_id

    @staticmethod
    def get_items(customer_id):
        """Get all wishlist items with product details."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT wi.*, p.name, p.price, p.discount_price, p.stock, p.image_url,
                   p.rating, p.review_count, p.brand, c.name as category_name
            FROM wishlist w
            JOIN wishlist_items wi ON w.id = wi.wishlist_id
            JOIN products p ON wi.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE w.customer_id = %s AND p.is_active = 1
            ORDER BY wi.created_at DESC
        """, (customer_id,))
        items = cur.fetchall()
        cur.close()
        return items

    @staticmethod
    def add_item(customer_id, product_id):
        """Add item to wishlist."""
        wishlist_id = Wishlist.get_or_create(customer_id)
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO wishlist_items (wishlist_id, product_id) VALUES (%s, %s)",
                (wishlist_id, product_id)
            )
            mysql.connection.commit()
            cur.close()
            return True
        except Exception:
            # Duplicate entry - already in wishlist
            cur.close()
            return False

    @staticmethod
    def remove_item(customer_id, product_id):
        """Remove item from wishlist."""
        cur = mysql.connection.cursor()
        cur.execute("""
            DELETE wi FROM wishlist_items wi
            JOIN wishlist w ON wi.wishlist_id = w.id
            WHERE w.customer_id = %s AND wi.product_id = %s
        """, (customer_id, product_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def is_in_wishlist(customer_id, product_id):
        """Check if product is in customer's wishlist."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT wi.id FROM wishlist_items wi
            JOIN wishlist w ON wi.wishlist_id = w.id
            WHERE w.customer_id = %s AND wi.product_id = %s
        """, (customer_id, product_id))
        result = cur.fetchone()
        cur.close()
        return result is not None

    @staticmethod
    def get_count(customer_id):
        """Get number of items in wishlist."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as count
            FROM wishlist w
            JOIN wishlist_items wi ON w.id = wi.wishlist_id
            WHERE w.customer_id = %s
        """, (customer_id,))
        result = cur.fetchone()
        cur.close()
        return result['count'] if result else 0
