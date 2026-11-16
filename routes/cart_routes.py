"""Cart routes - add, update, remove, view cart."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.cart import Cart
from models.product import Product
from routes.auth_routes import login_required
from config import Config

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart')
@login_required
def view_cart():
    """View shopping cart."""
    items = Cart.get_items(session['customer_id'])
    subtotal = sum(float(item['item_total']) for item in items)
    shipping = 0 if subtotal >= Config.FREE_SHIPPING_THRESHOLD else Config.SHIPPING_FEE if items else 0
    total = subtotal + shipping

    return render_template('customer/cart.html',
                           items=items,
                           subtotal=subtotal,
                           shipping=shipping,
                           total=total,
                           free_shipping_threshold=Config.FREE_SHIPPING_THRESHOLD)


@cart_bp.route('/add-to-cart', methods=['GET', 'POST'])
@login_required
def add_to_cart():
    """Add product to cart."""
    # Graceful handling if hit via GET (e.g. from an accidental browser redirect/refresh)
    if request.method == 'GET':
        return redirect(url_for('cart.view_cart'))

    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)

    if not product_id:
        flash('Invalid product selected.', 'danger')
        return redirect(request.referrer or url_for('product.shop'))

    product = Product.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('product.shop'))

    if product['stock'] < quantity:
        flash(f'Only {product["stock"]} items available in stock.', 'warning')
        return redirect(request.referrer or url_for('product.shop'))

    # Check existing quantity in cart
    cart_items = Cart.get_items(session['customer_id'])
    existing_qty = 0
    for item in cart_items:
        if item['product_id'] == product_id:
            existing_qty = item['quantity']
            break

    if existing_qty + quantity > product['stock']:
        flash(f'Cannot add more. Only {product["stock"]} items available (you have {existing_qty} in cart).', 'warning')
        return redirect(request.referrer or url_for('product.shop'))

    Cart.add_item(session['customer_id'], product_id, quantity)
    flash(f'{product["name"]} added to cart!', 'success')

    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': f'{product["name"]} added to cart!',
            'cart_count': Cart.get_count(session['customer_id'])
        })

    return redirect(request.referrer or url_for('cart.view_cart'))


@cart_bp.route('/update-cart', methods=['GET', 'POST'])
@login_required
def update_cart():
    """Update cart item quantity."""
    if request.method == 'GET':
        return redirect(url_for('cart.view_cart'))

    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)

    if not product_id or quantity is None:
        flash('Invalid request.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if quantity <= 0:
        Cart.remove_item(session['customer_id'], product_id)
        flash('Item removed from cart.', 'info')
    else:
        product = Product.get_by_id(product_id)
        if product and quantity > product['stock']:
            flash(f'Only {product["stock"]} items available.', 'warning')
            quantity = product['stock']
        Cart.update_quantity(session['customer_id'], product_id, quantity)
        flash('Cart updated.', 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        items = Cart.get_items(session['customer_id'])
        subtotal = sum(float(item['item_total']) for item in items)
        shipping = 0 if subtotal >= Config.FREE_SHIPPING_THRESHOLD else Config.SHIPPING_FEE if items else 0
        return jsonify({
            'status': 'success',
            'subtotal': float(subtotal),
            'shipping': float(shipping),
            'total': float(subtotal + shipping),
            'cart_count': Cart.get_count(session['customer_id'])
        })

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove-from-cart', methods=['GET', 'POST'])
@login_required
def remove_from_cart():
    """Remove item from cart."""
    if request.method == 'GET':
        return redirect(url_for('cart.view_cart'))

    product_id = request.form.get('product_id', type=int)

    if product_id:
        Cart.remove_item(session['customer_id'], product_id)
        flash('Item removed from cart.', 'info')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'cart_count': Cart.get_count(session['customer_id'])})

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/clear-cart', methods=['GET', 'POST'])
@login_required
def clear_cart():
    """Clear all items from cart."""
    if request.method == 'GET':
        return redirect(url_for('cart.view_cart'))

    Cart.clear(session['customer_id'])
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view_cart'))
