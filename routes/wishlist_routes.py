"""Wishlist routes - add, remove, view wishlist."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.wishlist import Wishlist
from models.cart import Cart
from models.product import Product
from routes.auth_routes import login_required

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('/wishlist')
@login_required
def view_wishlist():
    """View wishlist."""
    items = Wishlist.get_items(session['customer_id'])
    return render_template('customer/wishlist.html', items=items)


@wishlist_bp.route('/add-to-wishlist', methods=['GET', 'POST'])
@login_required
def add_to_wishlist():
    """Add product to wishlist."""
    if request.method == 'GET':
        return redirect(url_for('wishlist.view_wishlist'))

    product_id = request.form.get('product_id', type=int)

    if not product_id:
        flash('Invalid product.', 'danger')
        return redirect(request.referrer or url_for('product.shop'))

    product = Product.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('product.shop'))

    added = Wishlist.add_item(session['customer_id'], product_id)
    if added:
        flash(f'{product["name"]} added to wishlist!', 'success')
    else:
        flash(f'{product["name"]} is already in your wishlist.', 'info')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success' if added else 'exists',
            'message': f'{product["name"]} {"added to" if added else "already in"} wishlist!',
            'wishlist_count': Wishlist.get_count(session['customer_id'])
        })

    return redirect(request.referrer or url_for('wishlist.view_wishlist'))


@wishlist_bp.route('/remove-from-wishlist', methods=['GET', 'POST'])
@login_required
def remove_from_wishlist():
    """Remove product from wishlist."""
    if request.method == 'GET':
        return redirect(url_for('wishlist.view_wishlist'))

    product_id = request.form.get('product_id', type=int)

    if product_id:
        Wishlist.remove_item(session['customer_id'], product_id)
        flash('Item removed from wishlist.', 'info')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'wishlist_count': Wishlist.get_count(session['customer_id'])
        })

    return redirect(url_for('wishlist.view_wishlist'))


@wishlist_bp.route('/move-to-cart', methods=['GET', 'POST'])
@login_required
def move_to_cart():
    """Move wishlist item to cart."""
    if request.method == 'GET':
        return redirect(url_for('wishlist.view_wishlist'))

    product_id = request.form.get('product_id', type=int)

    if product_id:
        product = Product.get_by_id(product_id)
        if product and product['stock'] > 0:
            Cart.add_item(session['customer_id'], product_id, 1)
            Wishlist.remove_item(session['customer_id'], product_id)
            flash(f'{product["name"]} moved to cart!', 'success')
        elif product:
            flash(f'{product["name"]} is out of stock.', 'warning')
        else:
            flash('Product not found.', 'danger')

    return redirect(url_for('wishlist.view_wishlist'))
