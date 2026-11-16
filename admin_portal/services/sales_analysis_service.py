"""
Sales Analysis Service
Aggregates actual database transactions to compute executive KPIs, monthly trends, and category distribution.
"""

from datetime import datetime, timedelta
from app import mysql


class SalesAnalysisService:
    @staticmethod
    def get_dashboard_kpis():
        """Compute high-level executive KPIs from actual MySQL records."""
        cur = mysql.connection.cursor()

        # 1. Total Revenue (sum of all non-cancelled orders)
        cur.execute("SELECT COALESCE(SUM(total), 0) as total_revenue FROM orders WHERE status != 'Cancelled'")
        total_revenue = float(cur.fetchone()['total_revenue'])

        # 2. Total Orders
        cur.execute("SELECT COUNT(*) as total_orders FROM orders")
        total_orders = int(cur.fetchone()['total_orders'])

        # 3. Total Customers
        cur.execute("SELECT COUNT(*) as total_customers FROM customers WHERE is_active = 1")
        total_customers = int(cur.fetchone()['total_customers'])

        # 4. Total Products
        cur.execute("SELECT COUNT(*) as total_products FROM products WHERE is_active = 1")
        total_products = int(cur.fetchone()['total_products'])

        # 5. Pending Orders
        cur.execute("SELECT COUNT(*) as pending_orders FROM orders WHERE status IN ('Pending', 'Processing')")
        pending_orders = int(cur.fetchone()['pending_orders'])

        # 6. Low Stock Products (stock <= low_stock_threshold or stock <= 10)
        cur.execute("""
            SELECT COUNT(*) as low_stock_count
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.is_active = 1 AND p.stock <= COALESCE(i.low_stock_threshold, 10)
        """)
        low_stock_products = int(cur.fetchone()['low_stock_count'])

        # 7. Current Month vs Previous Month Revenue
        now = datetime.now()
        first_day_curr_month = datetime(now.year, now.month, 1)
        # Prev month first day
        if now.month == 1:
            first_day_prev_month = datetime(now.year - 1, 12, 1)
        else:
            first_day_prev_month = datetime(now.year, now.month - 1, 1)

        cur.execute("""
            SELECT COALESCE(SUM(total), 0) as current_month_rev
            FROM orders
            WHERE status != 'Cancelled' AND created_at >= %s
        """, (first_day_curr_month,))
        curr_month_revenue = float(cur.fetchone()['current_month_rev'])

        cur.execute("""
            SELECT COALESCE(SUM(total), 0) as prev_month_rev
            FROM orders
            WHERE status != 'Cancelled' AND created_at >= %s AND created_at < %s
        """, (first_day_prev_month, first_day_curr_month))
        prev_month_revenue = float(cur.fetchone()['prev_month_rev'])

        # Growth calculation
        if prev_month_revenue > 0:
            growth_pct = ((curr_month_revenue - prev_month_revenue) / prev_month_revenue) * 100.0
        else:
            growth_pct = 100.0 if curr_month_revenue > 0 else 0.0

        cur.close()

        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_customers': total_customers,
            'total_products': total_products,
            'pending_orders': pending_orders,
            'low_stock_products': low_stock_products,
            'curr_month_revenue': curr_month_revenue,
            'prev_month_revenue': prev_month_revenue,
            'revenue_growth_pct': round(growth_pct, 1)
        }

    @staticmethod
    def get_monthly_revenue_trend(months=6):
        """Retrieve monthly revenue for past N months for Chart.js line chart."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                DATE_FORMAT(created_at, '%%b %%Y') as month_label,
                DATE_FORMAT(created_at, '%%Y-%%m') as sort_key,
                COALESCE(SUM(total), 0) as revenue,
                COUNT(*) as order_count
            FROM orders
            WHERE status != 'Cancelled'
            GROUP BY sort_key, month_label
            ORDER BY sort_key ASC
            LIMIT %s
        """, (months,))
        records = cur.fetchall()
        cur.close()

        labels = [r['month_label'] for r in records]
        revenues = [float(r['revenue']) for r in records]
        orders = [int(r['order_count']) for r in records]

        return {
            'labels': labels,
            'revenues': revenues,
            'orders': orders
        }

    @staticmethod
    def get_category_sales_distribution():
        """Retrieve category revenue distribution for Chart.js donut chart."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                COALESCE(c.name, 'Uncategorized') as category_name,
                COALESCE(SUM(oi.subtotal), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_units
            FROM categories c
            JOIN products p ON c.id = p.category_id
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status != 'Cancelled'
            GROUP BY c.id, c.name
            ORDER BY total_sales DESC
        """)
        records = cur.fetchall()
        cur.close()

        labels = [r['category_name'] for r in records]
        sales = [float(r['total_sales']) for r in records]
        units = [int(r['total_units']) for r in records]

        return {
            'labels': labels,
            'sales': sales,
            'units': units
        }

    @staticmethod
    def get_order_status_distribution():
        """Retrieve counts per order status for status breakdown charts."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT status, COUNT(*) as count
            FROM orders
            GROUP BY status
            ORDER BY count DESC
        """)
        records = cur.fetchall()
        cur.close()

        status_dict = {
            'Pending': 0, 'Confirmed': 0, 'Processing': 0,
            'Shipped': 0, 'Delivered': 0, 'Cancelled': 0
        }
        for r in records:
            status_dict[r['status']] = int(r['count'])

        return status_dict

    @staticmethod
    def get_recent_orders(limit=6):
        """Retrieve recent customer orders for the dashboard table."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT o.id, o.order_number, o.delivery_name, o.delivery_email,
                   o.total, o.status, COALESCE(p.payment_method, 'COD') as payment_method, o.created_at,
                   COUNT(oi.id) as item_count
            FROM orders o
            LEFT JOIN payments p ON o.id = p.order_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id, p.payment_method
            ORDER BY o.created_at DESC
            LIMIT %s
        """, (limit,))
        orders = cur.fetchall()
        cur.close()
        return orders
