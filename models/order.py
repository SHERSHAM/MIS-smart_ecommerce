"""Order model - database operations for orders."""

import uuid
from datetime import datetime
from app import mysql


class Order:
    @staticmethod
    def generate_order_number():
        """Generate a unique order number."""
        timestamp = datetime.now().strftime('%Y%m%d')
        unique = uuid.uuid4().hex[:6].upper()
        return f"VIVA-{timestamp}-{unique}"

    @staticmethod
    def create(customer_id, address_data, cart_items, subtotal, shipping_fee, discount, total, payment_method):
        """Create a new order with items and payment. Uses transaction."""
        cur = mysql.connection.cursor()
        try:
            order_number = Order.generate_order_number()

            # Insert order
            cur.execute("""
                INSERT INTO orders (order_number, customer_id, address_id,
                    delivery_name, delivery_phone, delivery_email,
                    delivery_address, delivery_city, delivery_state, delivery_pincode,
                    subtotal, shipping_fee, discount, total, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (
                order_number, customer_id, address_data.get('address_id'),
                address_data['full_name'], address_data['phone'], address_data.get('email', ''),
                address_data['address_line1'], address_data['city'],
                address_data['state'], address_data['pincode'],
                subtotal, shipping_fee, discount, total
            ))
            order_id = cur.lastrowid

            # Insert order items and update stock
            for item in cart_items:
                effective_price = item.get('discount_price') or item['price']
                if item.get('discount_price') and float(item['discount_price']) > 0:
                    effective_price = item['discount_price']
                else:
                    effective_price = item['price']
                
                item_subtotal = float(effective_price) * int(item['quantity'])
                
                cur.execute("""
                    INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (order_id, item['product_id'], item['name'], effective_price, item['quantity'], item_subtotal))

                # Update product stock
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
                    (item['quantity'], item['product_id'], item['quantity'])
                )
                if cur.rowcount == 0:
                    raise Exception(f"Insufficient stock for {item['name']}")

                # Update inventory
                cur.execute(
                    "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s AND quantity >= %s",
                    (item['quantity'], item['product_id'], item['quantity'])
                )

                # Log inventory transaction
                cur.execute("SELECT id FROM inventory WHERE product_id = %s", (item['product_id'],))
                inv = cur.fetchone()
                if inv:
                    cur.execute("""
                        INSERT INTO inventory_transactions 
                        (inventory_id, product_id, transaction_type, quantity, reference_type, reference_id, notes)
                        VALUES (%s, %s, 'OUT', %s, 'order', %s, %s)
                    """, (inv['id'], item['product_id'], item['quantity'], order_id,
                          f"Order {order_number}"))

            # Insert payment
            payment_status = 'Completed' if payment_method == 'Online' else 'Pending'
            transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}" if payment_method == 'Online' else None
            
            cur.execute("""
                INSERT INTO payments (order_id, payment_method, amount, status, transaction_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, payment_method, total, payment_status, transaction_id))

            # Update order status to Confirmed
            cur.execute("UPDATE orders SET status = 'Confirmed' WHERE id = %s", (order_id,))

            mysql.connection.commit()
            cur.close()
            return order_id, order_number

        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            raise e

    @staticmethod
    def get_by_customer(customer_id):
        """Get all orders for a customer."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT o.*, p.payment_method, p.status as payment_status
            FROM orders o
            LEFT JOIN payments p ON o.id = p.order_id
            WHERE o.customer_id = %s
            ORDER BY o.created_at DESC
        """, (customer_id,))
        orders = cur.fetchall()
        cur.close()
        return orders

    @staticmethod
    def get_by_id(order_id, customer_id=None):
        """Get order by ID, optionally filtered by customer."""
        cur = mysql.connection.cursor()
        query = """
            SELECT o.*, p.payment_method, p.status as payment_status, p.transaction_id
            FROM orders o
            LEFT JOIN payments p ON o.id = p.order_id
            WHERE o.id = %s
        """
        params = [order_id]
        if customer_id:
            query += " AND o.customer_id = %s"
            params.append(customer_id)
        
        cur.execute(query, params)
        order = cur.fetchone()
        cur.close()
        return order

    @staticmethod
    def get_by_order_number(order_number, customer_id=None):
        """Get order by order number."""
        cur = mysql.connection.cursor()
        query = """
            SELECT o.*, p.payment_method, p.status as payment_status, p.transaction_id
            FROM orders o
            LEFT JOIN payments p ON o.id = p.order_id
            WHERE o.order_number = %s
        """
        params = [order_number]
        if customer_id:
            query += " AND o.customer_id = %s"
            params.append(customer_id)
        
        cur.execute(query, params)
        order = cur.fetchone()
        cur.close()
        return order

    @staticmethod
    def get_items(order_id):
        """Get items for an order."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT oi.*, p.image_url, p.slug
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cur.fetchall()
        cur.close()
        return items
