"""
Inventory Analysis Service
Calculates Reorder Points, Stockout Risks, and executes transactional inventory changes.
"""

from datetime import datetime, timedelta
from app import mysql


class InventoryAnalysisService:
    @staticmethod
    def get_inventory_status_list(status_filter=None, search=None):
        """Retrieve all products with inventory status, thresholds, and last update."""
        cur = mysql.connection.cursor()
        query = """
            SELECT 
                p.id, p.name, p.sku, p.brand, p.price, p.stock, p.image_url,
                c.name as category_name,
                i.low_stock_threshold,
                COALESCE(i.reorder_point, 15) as reorder_point,
                COALESCE(i.lead_time_days, 5) as lead_time_days,
                i.updated_at as last_inventory_update
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.is_active = 1
        """
        params = []
        if search:
            query += " AND (p.name LIKE %s OR p.sku LIKE %s OR p.brand LIKE %s)"
            st = f"%{search}%"
            params.extend([st, st, st])

        query += " ORDER BY p.stock ASC"
        cur.execute(query, params)
        items = cur.fetchall()
        cur.close()

        filtered_items = []
        for item in items:
            stock = int(item['stock'])
            low_thresh = int(item['low_stock_threshold'] or item.get('reorder_point') or 15)
            item['inventory_value'] = round(float(item['price'] or 0) * stock, 2)
            if stock == 0:
                item['stock_status'] = 'Out of Stock'
                item['status_badge'] = 'danger'
            elif stock <= low_thresh:
                item['stock_status'] = 'Low Stock'
                item['status_badge'] = 'warning'
            else:
                item['stock_status'] = 'In Stock'
                item['status_badge'] = 'success'

            if not status_filter or status_filter == 'all':
                filtered_items.append(item)
            elif status_filter == 'low' and item['stock_status'] == 'Low Stock':
                filtered_items.append(item)
            elif status_filter == 'out' and item['stock_status'] == 'Out of Stock':
                filtered_items.append(item)
            elif status_filter == 'in' and item['stock_status'] == 'In Stock':
                filtered_items.append(item)

        return filtered_items

    @staticmethod
    def get_restock_recommendations():
        """
        Calculates mathematical Reorder Recommendations:
        Average Daily Sales (ADS) = Units Sold in Past 30 Days / 30
        Reorder Point (ROP) = (ADS * Lead Time) + Safety Stock (default: 10 units)
        Target Buffer = Max(ROP * 1.5, 30 units)
        Recommended Order Qty = Max(0, Target Buffer - Current Stock)
        """
        cur = mysql.connection.cursor()
        thirty_days_ago = datetime.now() - timedelta(days=30)

        cur.execute("""
            SELECT 
                p.id, p.name, p.sku, p.stock, p.price,
                c.name as category_name,
                COALESCE(i.low_stock_threshold, 10) as low_stock_threshold,
                COALESCE(i.reorder_point, 15) as configured_reorder_point,
                COALESCE(i.lead_time_days, 5) as lead_time_days,
                COALESCE(SUM(CASE WHEN o.created_at >= %s AND o.status != 'Cancelled' THEN oi.quantity ELSE 0 END), 0) as sales_last_30_days
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE p.is_active = 1
            GROUP BY p.id, c.name, i.low_stock_threshold, i.reorder_point, i.lead_time_days
            ORDER BY p.stock ASC
        """, (thirty_days_ago,))
        records = cur.fetchall()
        cur.close()

        recommendations = []
        for r in records:
            stock = int(r['stock'])
            sales_30d = int(r['sales_last_30_days'])
            lead_time = int(r['lead_time_days'] or 5)
            ads = round(sales_30d / 30.0, 2)

            # Mathematical Reorder Point calculation
            safety_stock = int(r['low_stock_threshold'] or 10)
            calculated_rop = int(round((ads * lead_time) + safety_stock))
            rop = max(calculated_rop, int(r['configured_reorder_point'] or 15))

            target_stock = max(int(rop * 1.5), 30)
            recommended_qty = max(0, target_stock - stock)

            # Include if stock has dropped below or near reorder point
            if stock <= rop or stock <= safety_stock:
                if stock == 0:
                    urgency = "Critical (Stockout)"
                    reason = f"Item is completely depleted! Zero available inventory while daily demand is ~{ads} units/day."
                elif stock <= safety_stock:
                    urgency = "High (Below Safety Buffer)"
                    reason = f"Current stock ({stock}) has breached safety threshold ({safety_stock}). Supplier lead time is {lead_time} days."
                else:
                    urgency = "Medium (Approaching ROP)"
                    reason = f"Stock ({stock}) is below calculated Reorder Point ({rop}). Order now to avoid stockouts."

                recommendations.append({
                    'product_id': r['id'],
                    'name': r['name'],
                    'sku': r['sku'],
                    'category_name': r['category_name'],
                    'current_stock': stock,
                    'avg_daily_sales': ads,
                    'lead_time_days': lead_time,
                    'reorder_point': rop,
                    'recommended_reorder_qty': recommended_qty,
                    'urgency': urgency,
                    'reason': reason
                })

        return recommendations

    @staticmethod
    def adjust_stock(product_id, quantity_change, transaction_type, reason, admin_id=None):
        """
        Safely adjust stock in products, inventory, and record in inventory_transactions.
        transaction_type: 'IN', 'OUT', or 'ADJUSTMENT'
        quantity_change: positive or negative number
        """
        # Map friendly types to ENUM('IN','OUT','ADJUSTMENT')
        normalized_type = str(transaction_type).upper() if transaction_type else 'ADJUSTMENT'
        if normalized_type in ['RESTOCK', 'RETURN', 'IN']:
            db_txn_type = 'IN'
        elif normalized_type in ['DAMAGE', 'SCRAP', 'SALE', 'OUT']:
            db_txn_type = 'OUT'
        else:
            db_txn_type = 'ADJUSTMENT'

        cur = mysql.connection.cursor()
        try:
            # 1. Fetch current stock
            cur.execute("SELECT stock, name FROM products WHERE id = %s", (product_id,))
            prod = cur.fetchone()
            if not prod:
                raise Exception("Product not found.")

            current_stock = int(prod['stock'])
            new_stock = current_stock + int(quantity_change)
            if new_stock < 0:
                raise Exception(f"Stock cannot be negative. Current stock is {current_stock}.")

            # 2. Update products table
            cur.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, product_id))

            # 3. Update or Insert inventory table
            cur.execute("SELECT id FROM inventory WHERE product_id = %s", (product_id,))
            inv = cur.fetchone()
            if inv:
                cur.execute("""
                    UPDATE inventory 
                    SET quantity = %s, last_restocked = CASE WHEN %s > 0 THEN CURRENT_TIMESTAMP ELSE last_restocked END
                    WHERE product_id = %s
                """, (new_stock, quantity_change, product_id))
                inv_id = inv['id']
            else:
                cur.execute("INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)", (product_id, new_stock))
                inv_id = cur.lastrowid

            # 4. Log in inventory_transactions with audit notes
            audit_note = f"{reason} | Prev: {current_stock} -> New: {new_stock}"
            cur.execute("""
                INSERT INTO inventory_transactions 
                (inventory_id, product_id, transaction_type, quantity, reference_type, admin_id, notes)
                VALUES (%s, %s, %s, %s, 'manual_adjustment', %s, %s)
            """, (inv_id, product_id, db_txn_type, abs(quantity_change), admin_id, audit_note))

            mysql.connection.commit()
            cur.close()
            return True, f"Stock updated from {current_stock} to {new_stock}."
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            return False, str(e)

    @staticmethod
    def get_transaction_history(limit=50):
        """Retrieve historical inventory transactions audit log."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT it.*, p.name as product_name, p.sku, a.username as admin_username
            FROM inventory_transactions it
            JOIN products p ON it.product_id = p.id
            LEFT JOIN admins a ON it.admin_id = a.id
            ORDER BY it.created_at DESC
            LIMIT %s
        """, (limit,))
        logs = cur.fetchall()
        cur.close()
        return logs
