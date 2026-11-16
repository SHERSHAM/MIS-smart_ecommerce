"""
Customer Analysis Service
Performs customer intelligence, lifetime spend calculation, and segmentation.
"""

from datetime import datetime, timedelta
from app import mysql


class CustomerAnalysisService:
    @staticmethod
    def get_customer_intelligence_list(search=None):
        """Retrieve customer list with purchase statistics, AOV, and segmentation tag."""
        cur = mysql.connection.cursor()
        query = """
            SELECT 
                c.id, c.full_name, c.email, c.phone, c.created_at as registered_at,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(CASE WHEN o.status != 'Cancelled' THEN o.total ELSE 0 END), 0) as total_spent,
                MAX(o.created_at) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            WHERE c.is_active = 1
        """
        params = []
        if search:
            query += " AND (c.full_name LIKE %s OR c.email LIKE %s OR c.phone LIKE %s)"
            st = f"%{search}%"
            params.extend([st, st, st])

        query += """
            GROUP BY c.id
            ORDER BY total_spent DESC, total_orders DESC
        """
        cur.execute(query, params)
        customers = cur.fetchall()
        cur.close()

        for cust in customers:
            spent = float(cust['total_spent'])
            orders = int(cust['total_orders'])
            cust['total_spent'] = spent
            cust['total_orders'] = orders
            cust['aov'] = round(spent / orders, 2) if orders > 0 else 0.0

            # Rule-based Customer Segmentation
            if spent >= 10000:
                cust['segment'] = 'VIP High-Value'
                cust['badge_class'] = 'bg-success'
            elif orders >= 2:
                cust['segment'] = 'Repeat Customer'
                cust['badge_class'] = 'bg-primary'
            elif orders == 1:
                cust['segment'] = 'First-Time Buyer'
                cust['badge_class'] = 'bg-info'
            else:
                cust['segment'] = 'Registered Lead'
                cust['badge_class'] = 'bg-secondary'

        return customers

    @staticmethod
    def get_customer_summary_metrics():
        """Compute aggregate customer health metrics."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                COUNT(*) as total_registered,
                COUNT(CASE WHEN o_cnt > 1 THEN 1 END) as repeat_customers,
                COUNT(CASE WHEN o_cnt = 1 THEN 1 END) as single_buyers,
                COUNT(CASE WHEN o_cnt = 0 THEN 1 END) as zero_buyers
            FROM (
                SELECT c.id, COUNT(o.id) as o_cnt
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id AND o.status != 'Cancelled'
                WHERE c.is_active = 1
                GROUP BY c.id
            ) as cust_stats
        """)
        stats = cur.fetchone()

        # Average Order Value across entire store
        cur.execute("""
            SELECT COALESCE(AVG(total), 0) as overall_aov
            FROM orders
            WHERE status != 'Cancelled'
        """)
        aov_res = cur.fetchone()
        cur.close()

        total = int(stats['total_registered']) if stats else 0
        repeat = int(stats['repeat_customers']) if stats else 0
        repeat_rate = round((repeat / total * 100.0), 1) if total > 0 else 0.0

        return {
            'total_customers': total,
            'repeat_customers': repeat,
            'repeat_rate_pct': repeat_rate,
            'overall_aov': round(float(aov_res['overall_aov']), 2) if aov_res else 0.0
        }
