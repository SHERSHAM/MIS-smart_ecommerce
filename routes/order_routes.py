"""Order routes - order history, order details, tracking."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.order import Order
from routes.auth_routes import login_required

order_bp = Blueprint('order', __name__)


@order_bp.route('/my-orders')
@login_required
def my_orders():
    """View order history."""
    orders = Order.get_by_customer(session['customer_id'])
    return render_template('customer/my_orders.html', orders=orders)


@order_bp.route('/order-details/<int:order_id>')
@login_required
def order_details(order_id):
    """View order details."""
    order = Order.get_by_id(order_id, session['customer_id'])
    if not order:
        flash('Order not found.', 'warning')
        return redirect(url_for('order.my_orders'))
    
    items = Order.get_items(order_id)
    return render_template('customer/order_details.html', order=order, items=items)


@order_bp.route('/track-order', methods=['GET', 'POST'])
def track_order():
    """Track order by order number."""
    order = None
    items = None
    
    if request.method == 'POST' or request.args.get('order_number'):
        order_number = request.form.get('order_number') or request.args.get('order_number', '')
        order_number = order_number.strip()
        
        if not order_number:
            flash('Please enter an order number.', 'warning')
        else:
            customer_id = session.get('customer_id')
            order = Order.get_by_order_number(order_number, customer_id)
            if order:
                items = Order.get_items(order['id'])
            else:
                flash('Order not found. Please check your order number.', 'warning')
    
    return render_template('customer/track_order.html', order=order, items=items)
