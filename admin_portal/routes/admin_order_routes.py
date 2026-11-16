"""
Admin Order Routes
Tracks customer orders, updates delivery statuses, and manages cancellation inventory rollbacks.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from models.order import Order
from admin_portal.routes.admin_auth_routes import admin_login_required

admin_order_bp = Blueprint('admin_order', __name__)


@admin_order_bp.route('/orders')
@admin_login_required
def order_list():
    """List customer orders with status, date, and payment filters."""
    status_filter = request.args.get('status')
    payment_filter = request.args.get('payment')
    search = request.args.get('q', '').strip()

    cur = mysql.connection.cursor()
    query = """
        SELECT o.*, p.payment_method, p.status as payment_status
        FROM orders o
        LEFT JOIN payments p ON o.id = p.order_id
        WHERE 1=1
    """
    params = []
    if status_filter and status_filter != 'all':
        query += " AND o.status = %s"; params.append(status_filter)
    if payment_filter and payment_filter != 'all':
        query += " AND p.payment_method = %s"; params.append(payment_filter)
    if search:
        query += " AND (o.order_number LIKE %s OR o.delivery_name LIKE %s OR o.delivery_email LIKE %s)"
        st = f"%{search}%"; params.extend([st, st, st])

    query += " ORDER BY o.created_at DESC"
    cur.execute(query, params)
    orders = cur.fetchall()
    cur.close()

    return render_template(
        'admin/orders/index.html',
        orders=orders,
        status_filter=status_filter,
        payment_filter=payment_filter,
        search=search
    )


@admin_order_bp.route('/orders/<int:order_id>')
@admin_login_required
def order_detail(order_id):
    """View comprehensive order details, items, delivery address, and payment."""
    order = Order.get_by_id(order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_order.order_list'))

    items = Order.get_items(order_id)
    return render_template('admin/orders/details.html', order=order, items=items)


@admin_order_bp.route('/orders/update-status/<int:order_id>', methods=['POST'])
@admin_login_required
def update_status(order_id):
    """Update order status and handle inventory reversal if cancelled."""
    new_status = request.form.get('status')
    valid_statuses = ['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

    if new_status not in valid_statuses:
        flash('Invalid status transition.', 'danger')
        return redirect(url_for('admin_order.order_detail', order_id=order_id))

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT status, order_number FROM orders WHERE id = %s", (order_id,))
        order = cur.fetchone()
        if not order:
            flash('Order not found.', 'danger')
            cur.close()
            return redirect(url_for('admin_order.order_list'))

        prev_status = order['status']

        # If order is being cancelled now and was not cancelled before, safely restore inventory
        if new_status == 'Cancelled' and prev_status != 'Cancelled':
            items = Order.get_items(order_id)
            admin_id = session.get('admin_id')
            for item in items:
                qty = int(item['quantity'])
                pid = item['product_id']
                if pid:
                    cur.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (qty, pid))
                    cur.execute("UPDATE inventory SET quantity = quantity + %s WHERE product_id = %s", (qty, pid))

                    # Log restoration in inventory_transactions
                    cur.execute("SELECT id FROM inventory WHERE product_id = %s", (pid,))
                    inv = cur.fetchone()
                    if inv:
                        cur.execute("""
                            INSERT INTO inventory_transactions 
                            (inventory_id, product_id, transaction_type, quantity, reference_type, reference_id, admin_id, notes)
                            VALUES (%s, %s, 'IN', %s, 'order_cancellation', %s, %s, %s)
                        """, (inv['id'], pid, qty, order_id, admin_id, f"Order {order['order_number']} cancelled - inventory restored"))

        # Update order status
        cur.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))

        # If status is Delivered, update payment status to Completed if COD
        if new_status == 'Delivered':
            cur.execute("UPDATE payments SET status = 'Completed' WHERE order_id = %s AND payment_method = 'COD'", (order_id,))

        mysql.connection.commit()
        cur.close()

        flash(f"Order #{order['order_number']} status updated from '{prev_status}' to '{new_status}'. Customer tracking is updated.", 'success')
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        flash(f"Failed to update status: {str(e)}", 'danger')

    return redirect(url_for('admin_order.order_detail', order_id=order_id))
