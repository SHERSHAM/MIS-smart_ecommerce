"""Category model - database operations for categories."""

from app import mysql


class Category:
    @staticmethod
    def get_all(active_only=True):
        """Get all categories."""
        cur = mysql.connection.cursor()
        query = "SELECT * FROM categories"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY display_order ASC, name ASC"
        cur.execute(query)
        categories = cur.fetchall()
        cur.close()
        return categories

    @staticmethod
    def get_by_id(category_id):
        """Get category by ID."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        category = cur.fetchone()
        cur.close()
        return category

    @staticmethod
    def get_by_slug(slug):
        """Get category by slug."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM categories WHERE slug = %s", (slug,))
        category = cur.fetchone()
        cur.close()
        return category

    @staticmethod
    def get_product_count(category_id):
        """Get number of active products in category."""
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT COUNT(*) as count FROM products WHERE category_id = %s AND is_active = 1",
            (category_id,)
        )
        result = cur.fetchone()
        cur.close()
        return result['count'] if result else 0
