"""
Product Analysis Service
Identifies Top 10 Best Sellers and 30-Day Slow-Moving Inventory with suggested business actions.
"""

from datetime import datetime, timedelta
from app import mysql


class ProductAnalysisService:
    @staticmethod
    def get_top_selling_products(limit=10, days=None):
        """Retrieve top selling products based on actual order items sales quantity and revenue."""
        cur = mysql.connection.cursor()
        query = """
            SELECT 
                p.id, p.name, p.brand, p.price, p.discount_price, p.stock, p.image_url,
                c.name as category_name,
                COALESCE(SUM(oi.quantity), 0) as total_units_sold,
                COALESCE(SUM(oi.subtotal), 0) as total_revenue_generated
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status != 'Cancelled'
        """
        params = []
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            query += " AND o.created_at >= %s"
            params.append(cutoff)

        query += """
            GROUP BY p.id, c.name
            ORDER BY total_units_sold DESC, total_revenue_generated DESC
            LIMIT %s
        """
        params.append(limit)

        cur.execute(query, params)
        top_products = cur.fetchall()
        cur.close()

        # Add ranking index and aliases
        for rank, item in enumerate(top_products, start=1):
            item['sales_rank'] = rank
            item['total_units_sold'] = int(item['total_units_sold'])
            item['units_sold'] = item['total_units_sold']
            item['total_revenue_generated'] = float(item['total_revenue_generated'])
            item['total_revenue'] = item['total_revenue_generated']

        return top_products

    @staticmethod
    def get_slow_moving_products(days=30, max_sales=1):
        """
        Identify products with low or zero sales over the last N days.
        Criteria:
        - Product was created at least 14 days ago (to avoid falsely penalizing brand new arrivals)
        - Sold fewer than max_sales units in the designated period
        - Currently has available stock sitting idle
        """
        cur = mysql.connection.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)

        cur.execute("""
            SELECT 
                p.id, p.name, p.brand, p.price, p.discount_price, p.stock, p.created_at,
                c.name as category_name,
                COALESCE(SUM(CASE WHEN o.created_at >= %s AND o.status != 'Cancelled' THEN oi.quantity ELSE 0 END), 0) as recent_units_sold,
                MAX(o.created_at) as last_sold_date,
                DATEDIFF(NOW(), p.created_at) as days_in_catalog
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE p.is_active = 1 AND p.stock > 0
            GROUP BY p.id, c.name
            HAVING recent_units_sold <= %s AND days_in_catalog >= 14
            ORDER BY p.stock DESC, recent_units_sold ASC
        """, (cutoff_date, max_sales))

        slow_products = cur.fetchall()
        cur.close()

        for item in slow_products:
            stock = int(item['stock'])
            units = int(item['recent_units_sold'])
            item['recent_units_sold'] = units
            item['recent_sales'] = units
            item['locked_capital'] = round(float(item['price'] or 0) * stock, 2)

            # Formulate tailored business recommendations
            if stock >= 40:
                item['recommendation'] = "Launch a Flash Discount (15-25% off) to liquidate surplus inventory and free working capital."
                item['urgency'] = "High"
            elif stock >= 20:
                item['recommendation'] = "Feature in 'Home Refresh' or 'Weekly Deals' carousel to boost organic visibility."
                item['urgency'] = "Medium"
            else:
                item['recommendation'] = "Monitor demand; hold off on placing restocking purchase orders until velocity improves."
                item['urgency'] = "Low"

        return slow_products
