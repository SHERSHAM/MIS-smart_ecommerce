"""Checkout routes - checkout page and order placement."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.cart import Cart
from models.order import Order
from models.address import Address
from models.product import Product
from routes.auth_routes import login_required
from config import Config

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page."""
    items = Cart.get_items(session['customer_id'])
    
    if not items:
        flash('Your cart is empty. Add items before checking out.', 'warning')
        return redirect(url_for('product.shop'))
    
    # Check stock for all items
    stock_issues = []
    for item in items:
        if item['quantity'] > item['stock']:
            stock_issues.append(f'{item["name"]}: only {item["stock"]} available (you have {item["quantity"]} in cart)')
    
    if stock_issues:
        for issue in stock_issues:
            flash(issue, 'warning')
    
    subtotal = sum(float(item['item_total']) for item in items)
    shipping = 0 if subtotal >= Config.FREE_SHIPPING_THRESHOLD else Config.SHIPPING_FEE
    total = subtotal + shipping
    
    addresses = Address.get_by_customer(session['customer_id'])
    from models.customer import Customer
    customer = Customer.find_by_id(session['customer_id'])
    
    return render_template('customer/checkout.html',
                           items=items,
                           subtotal=subtotal,
                           shipping=shipping,
                           total=total,
                           addresses=addresses,
                           customer=customer,
                           free_shipping_threshold=Config.FREE_SHIPPING_THRESHOLD)


@checkout_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """Place the order."""
    items = Cart.get_items(session['customer_id'])
    
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('product.shop'))
    
    # Validate stock again
    for item in items:
        product = Product.get_by_id(item['product_id'])
        if not product or product['stock'] < item['quantity']:
            flash(f'Sorry, {item["name"]} is no longer available in the requested quantity.', 'danger')
            return redirect(url_for('cart.view_cart'))
    
    # Get address data
    address_id = request.form.get('address_id', type=int)
    payment_method = request.form.get('payment_method', 'COD')
    
    address_data = {}
    if address_id:
        address = Address.get_by_id(address_id, session['customer_id'])
        if address:
            address_data = {
                'address_id': address_id,
                'full_name': address['full_name'],
                'phone': address['phone'],
                'email': session.get('customer_email', ''),
                'address_line1': address['address_line1'],
                'city': address['city'],
                'state': address['state'],
                'pincode': address['pincode']
            }
    
    if not address_data:
        # Use form data for new address
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address_line1 = request.form.get('address_line1', '').strip()
        address_line2 = request.form.get('address_line2', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        
        if not all([full_name, phone, address_line1, city, state, pincode]):
            flash('Please fill in all delivery address fields.', 'danger')
            return redirect(url_for('checkout.checkout'))
        
        # Save address if checkbox is checked
        save_address = request.form.get('save_address')
        new_address_id = None
        if save_address:
            new_address_id = Address.create(
                session['customer_id'], full_name, phone,
                address_line1, address_line2, city, state, pincode
            )
        
        address_data = {
            'address_id': new_address_id,
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'address_line1': address_line1,
            'city': city,
            'state': state,
            'pincode': pincode
        }
    
    # Calculate totals
    subtotal = sum(float(item['item_total']) for item in items)
    shipping = 0 if subtotal >= Config.FREE_SHIPPING_THRESHOLD else Config.SHIPPING_FEE
    discount = 0
    total = subtotal + shipping - discount
    
    try:
        order_id, order_number = Order.create(
            customer_id=session['customer_id'],
            address_data=address_data,
            cart_items=items,
            subtotal=subtotal,
            shipping_fee=shipping,
            discount=discount,
            total=total,
            payment_method=payment_method
        )
        
        # Clear cart
        Cart.clear(session['customer_id'])
        
        flash('Order placed successfully! 🎉', 'success')
        return redirect(url_for('checkout.order_confirmation', order_id=order_id))
        
    except Exception as e:
        flash(f'Failed to place order: {str(e)}', 'danger')
        return redirect(url_for('checkout.checkout'))


@checkout_bp.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Order confirmation page."""
    order = Order.get_by_id(order_id, session['customer_id'])
    if not order:
        flash('Order not found.', 'warning')
        return redirect(url_for('order.my_orders'))
    
    items = Order.get_items(order_id)
    return render_template('customer/order_confirmation.html', order=order, items=items)
