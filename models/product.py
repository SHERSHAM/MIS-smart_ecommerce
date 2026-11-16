"""Product model - database operations for products."""

from app import mysql


class Product:
    @staticmethod
    def get_all(page=1, per_page=12, category_id=None, sort_by='newest',
                min_price=None, max_price=None, search=None, brand=None, in_stock=None):
        """Get products with filtering, sorting and pagination."""
        cur = mysql.connection.cursor()
        
        query = "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.is_active = 1"
        params = []

        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)

        if search:
            query += " AND (p.name LIKE %s OR p.brand LIKE %s OR p.description LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        if min_price:
            query += " AND COALESCE(p.discount_price, p.price) >= %s"
            params.append(min_price)

        if max_price:
            query += " AND COALESCE(p.discount_price, p.price) <= %s"
            params.append(max_price)

        if brand:
            query += " AND p.brand = %s"
            params.append(brand)

        if in_stock:
            query += " AND p.stock > 0"

        # Count total
        count_query = query.replace(
            "SELECT p.*, c.name as category_name",
            "SELECT COUNT(*) as total"
        )
        cur.execute(count_query, params)
        total = cur.fetchone()['total']

        # Sorting
        sort_map = {
            'price_low': 'COALESCE(p.discount_price, p.price) ASC',
            'price_high': 'COALESCE(p.discount_price, p.price) DESC',
            'newest': 'p.created_at DESC',
            'popularity': 'p.review_count DESC',
            'rating': 'p.rating DESC'
        }
        query += f" ORDER BY {sort_map.get(sort_by, 'p.created_at DESC')}"

        # Pagination
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cur.execute(query, params)
        products = cur.fetchall()
        cur.close()

        return products, total

    @staticmethod
    def get_by_id(product_id):
        """Get a single product by ID."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s AND p.is_active = 1
        """, (product_id,))
        product = cur.fetchone()
        cur.close()
        return product

    @staticmethod
    def get_by_slug(slug):
        """Get a single product by slug."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.slug = %s AND p.is_active = 1
        """, (slug,))
        product = cur.fetchone()
        cur.close()
        return product

    @staticmethod
    def get_featured(limit=10):
        """Get featured products."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND p.is_featured = 1
            ORDER BY p.rating DESC
            LIMIT %s
        """, (limit,))
        products = cur.fetchall()
        cur.close()
        return products

    @staticmethod
    def get_by_category(category_id, limit=12):
        """Get products by category."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s AND p.is_active = 1
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (category_id, limit))
        products = cur.fetchall()
        cur.close()
        return products

    @staticmethod
    def get_related(product_id, category_id, limit=4):
        """Get related products from same category."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s AND p.id != %s AND p.is_active = 1
            ORDER BY p.rating DESC
            LIMIT %s
        """, (category_id, product_id, limit))
        products = cur.fetchall()
        cur.close()
        return products

    @staticmethod
    def get_new_arrivals(limit=8):
        """Get newest products."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (limit,))
        products = cur.fetchall()
        cur.close()
        return products

    @staticmethod
    def get_brands():
        """Get all distinct brands."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT brand FROM products WHERE is_active = 1 AND brand IS NOT NULL ORDER BY brand")
        brands = cur.fetchall()
        cur.close()
        return [b['brand'] for b in brands]

    @staticmethod
    def get_images(product_id):
        """Get all images for a product."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM product_images 
            WHERE product_id = %s 
            ORDER BY is_primary DESC, display_order ASC
        """, (product_id,))
        images = cur.fetchall()
        cur.close()
        return images

    @staticmethod
    def search(query, limit=20):
        """Search products."""
        cur = mysql.connection.cursor()
        search_term = f"%{query}%"
        cur.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND (
                p.name LIKE %s OR p.brand LIKE %s OR 
                p.description LIKE %s OR c.name LIKE %s
            )
            ORDER BY p.rating DESC
            LIMIT %s
        """, (search_term, search_term, search_term, search_term, limit))
        products = cur.fetchall()
        cur.close()
        return products

    @staticmethod
    def update_stock(product_id, quantity_change):
        """Update product stock. Negative for decrease, positive for increase."""
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE products SET stock = stock + %s WHERE id = %s AND stock + %s >= 0",
            (quantity_change, product_id, quantity_change)
        )
        affected = cur.rowcount
        mysql.connection.commit()
        cur.close()
        return affected > 0
