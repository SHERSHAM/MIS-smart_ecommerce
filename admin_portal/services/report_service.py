"""
Report Generation Service
Generates 8 distinct MIS operational and strategic reports with date range filtering and CSV export using Pandas.
"""

import csv
import io
from datetime import datetime
from app import mysql


class ReportService:
    @staticmethod
    def get_report_data(report_type, start_date=None, end_date=None):
        """Fetch report dataset from MySQL based on report_type and optional date range."""
        cur = mysql.connection.cursor()
        data = []
        columns = []

        # 1. Daily Sales Report
        if report_type == 'daily_sales':
            query = """
                SELECT 
                    DATE(created_at) as sale_date,
                    COUNT(*) as total_orders,
                    COALESCE(SUM(subtotal), 0) as gross_sales,
                    COALESCE(SUM(shipping_fee), 0) as shipping_collected,
                    COALESCE(SUM(total), 0) as net_revenue
                FROM orders
                WHERE status != 'Cancelled'
            """
            params = []
            if start_date:
                query += " AND created_at >= %s"; params.append(start_date)
            if end_date:
                query += " AND created_at <= %s"; params.append(f"{end_date} 23:59:59")
            query += " GROUP BY DATE(created_at) ORDER BY sale_date DESC"
            cur.execute(query, params)
            data = cur.fetchall()
            columns = [
                {'key': 'sale_date', 'label': 'Sale Date'},
                {'key': 'total_orders', 'label': 'Total Orders'},
                {'key': 'gross_sales', 'label': 'Gross Sales (Rs)'},
                {'key': 'shipping_collected', 'label': 'Shipping Fee (Rs)'},
                {'key': 'net_revenue', 'label': 'Net Revenue (Rs)'}
            ]

        # 2. Monthly Sales Report
        elif report_type == 'monthly_sales':
            cur.execute("""
                SELECT 
                    DATE_FORMAT(created_at, '%%Y-%%m') as month_period,
                    COUNT(*) as order_volume,
                    COALESCE(SUM(total), 0) as total_revenue,
                    ROUND(AVG(total), 2) as average_order_value
                FROM orders
                WHERE status != 'Cancelled'
                GROUP BY month_period
                ORDER BY month_period DESC
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'month_period', 'label': 'Month Period'},
                {'key': 'order_volume', 'label': 'Order Volume'},
                {'key': 'total_revenue', 'label': 'Total Revenue (Rs)'},
                {'key': 'average_order_value', 'label': 'Average Order Value (Rs)'}
            ]

        # 3. Product Performance Report
        elif report_type == 'product_performance':
            cur.execute("""
                SELECT 
                    p.id as product_id, p.name as product_name, p.sku,
                    c.name as category_name, p.price, p.stock as available_stock,
                    COALESCE(SUM(oi.quantity), 0) as units_sold,
                    COALESCE(SUM(oi.subtotal), 0) as revenue_generated
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN order_items oi ON p.id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'Cancelled'
                WHERE p.is_active = 1
                GROUP BY p.id, c.name
                ORDER BY revenue_generated DESC
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'product_id', 'label': 'Product ID'},
                {'key': 'product_name', 'label': 'Product Name'},
                {'key': 'sku', 'label': 'SKU'},
                {'key': 'category_name', 'label': 'Category'},
                {'key': 'price', 'label': 'Unit Price (Rs)'},
                {'key': 'available_stock', 'label': 'Stock'},
                {'key': 'units_sold', 'label': 'Units Sold'},
                {'key': 'revenue_generated', 'label': 'Revenue (Rs)'}
            ]

        # 4. Customer Purchase Report
        elif report_type == 'customer_purchase':
            cur.execute("""
                SELECT 
                    c.id as customer_id, c.full_name, c.email, c.phone,
                    COUNT(DISTINCT o.id) as order_count,
                    COALESCE(SUM(CASE WHEN o.status != 'Cancelled' THEN o.total ELSE 0 END), 0) as total_spent,
                    MAX(o.created_at) as last_order_date
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY total_spent DESC
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'customer_id', 'label': 'Customer ID'},
                {'key': 'full_name', 'label': 'Full Name'},
                {'key': 'email', 'label': 'Email'},
                {'key': 'phone', 'label': 'Phone'},
                {'key': 'order_count', 'label': 'Orders Count'},
                {'key': 'total_spent', 'label': 'Total Spent (Rs)'},
                {'key': 'last_order_date', 'label': 'Last Order Date'}
            ]

        # 5. Inventory Report
        elif report_type == 'inventory_status':
            cur.execute("""
                SELECT 
                    p.id, p.name as product_name, p.sku, p.brand,
                    c.name as category_name, p.price, p.stock,
                    (p.price * p.stock) as total_inventory_value,
                    COALESCE(i.low_stock_threshold, 10) as threshold,
                    COALESCE(i.reorder_point, 15) as reorder_point
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE p.is_active = 1
                ORDER BY p.stock ASC
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'id', 'label': 'Product ID'},
                {'key': 'product_name', 'label': 'Product Name'},
                {'key': 'sku', 'label': 'SKU'},
                {'key': 'brand', 'label': 'Brand'},
                {'key': 'category_name', 'label': 'Category'},
                {'key': 'price', 'label': 'Unit Price'},
                {'key': 'stock', 'label': 'Current Stock'},
                {'key': 'total_inventory_value', 'label': 'Stock Value (Rs)'},
                {'key': 'threshold', 'label': 'Threshold'},
                {'key': 'reorder_point', 'label': 'Reorder Point'}
            ]

        # 6. Low Stock Report
        elif report_type == 'low_stock':
            cur.execute("""
                SELECT 
                    p.id, p.name as product_name, p.sku, c.name as category_name,
                    p.stock, COALESCE(i.low_stock_threshold, 10) as threshold,
                    COALESCE(i.reorder_point, 15) as reorder_point,
                    CASE WHEN p.stock = 0 THEN 'OUT OF STOCK' ELSE 'LOW STOCK' END as alert_level
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE p.is_active = 1 AND p.stock <= COALESCE(i.low_stock_threshold, 10)
                ORDER BY p.stock ASC
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'id', 'label': 'Product ID'},
                {'key': 'product_name', 'label': 'Product Name'},
                {'key': 'sku', 'label': 'SKU'},
                {'key': 'category_name', 'label': 'Category'},
                {'key': 'stock', 'label': 'Current Stock'},
                {'key': 'threshold', 'label': 'Threshold'},
                {'key': 'reorder_point', 'label': 'Reorder Point'},
                {'key': 'alert_level', 'label': 'Alert Level'}
            ]

        # 7. Best-Selling Products Report
        elif report_type == 'best_sellers':
            cur.execute("""
                SELECT 
                    p.id, p.name as product_name, p.sku, c.name as category_name,
                    p.price, p.stock as current_stock,
                    COALESCE(SUM(oi.quantity), 0) as units_sold,
                    COALESCE(SUM(oi.subtotal), 0) as gross_revenue
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                JOIN order_items oi ON p.id = oi.product_id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.status != 'Cancelled'
                GROUP BY p.id, c.name
                ORDER BY units_sold DESC
                LIMIT 15
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'id', 'label': 'Product ID'},
                {'key': 'product_name', 'label': 'Product Name'},
                {'key': 'sku', 'label': 'SKU'},
                {'key': 'category_name', 'label': 'Category'},
                {'key': 'price', 'label': 'Price (Rs)'},
                {'key': 'current_stock', 'label': 'Current Stock'},
                {'key': 'units_sold', 'label': 'Units Sold'},
                {'key': 'gross_revenue', 'label': 'Gross Revenue (Rs)'}
            ]

        # 8. Order Status Report
        elif report_type == 'order_status':
            cur.execute("""
                SELECT 
                    o.id as order_id, o.order_number, o.delivery_name,
                    o.status, COALESCE(p.payment_method, 'COD') as payment_method, o.total, o.created_at
                FROM orders o
                LEFT JOIN payments p ON o.id = p.order_id
                ORDER BY o.created_at DESC
            """)
            data = cur.fetchall()
            columns = [
                {'key': 'order_id', 'label': 'Order ID'},
                {'key': 'order_number', 'label': 'Order Number'},
                {'key': 'delivery_name', 'label': 'Customer'},
                {'key': 'status', 'label': 'Status'},
                {'key': 'payment_method', 'label': 'Payment Method'},
                {'key': 'total', 'label': 'Total (Rs)'},
                {'key': 'created_at', 'label': 'Created At'}
            ]

        cur.close()
        return data, columns

    @staticmethod
    def export_csv(report_type, start_date=None, end_date=None):
        """Generate an RFC 4180 compliant CSV string from report query."""
        data, columns = ReportService.get_report_data(report_type, start_date, end_date)
        output = io.StringIO()
        fieldnames = [c['key'] for c in columns]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # Write human header row
        writer.writerow({c['key']: c['label'] for c in columns})
        for row in data:
            clean_row = {}
            for col in columns:
                k = col['key']
                v = row.get(k)
                if isinstance(v, datetime) or hasattr(v, 'strftime'):
                    clean_row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    clean_row[k] = v
            writer.writerow(clean_row)
        return output.getvalue()
