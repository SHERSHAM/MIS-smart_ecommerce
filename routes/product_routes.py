"""Product routes - shop, product details, search, categories."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.product import Product
from models.category import Category
from config import Config

product_bp = Blueprint('product', __name__)


@product_bp.route('/shop')
def shop():
    """Product catalogue page."""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand')
    search = request.args.get('q')
    in_stock = request.args.get('in_stock')
    
    products, total = Product.get_all(
        page=page,
        per_page=Config.PRODUCTS_PER_PAGE,
        category_id=category_id,
        sort_by=sort_by,
        min_price=min_price,
        max_price=max_price,
        search=search,
        brand=brand,
        in_stock=in_stock
    )
    
    categories = Category.get_all()
    brands = Product.get_brands()
    
    total_pages = (total + Config.PRODUCTS_PER_PAGE - 1) // Config.PRODUCTS_PER_PAGE
    
    # Get current category info
    current_category = None
    if category_id:
        current_category = Category.get_by_id(category_id)
    
    return render_template('customer/shop.html',
                           products=products,
                           categories=categories,
                           brands=brands,
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           sort_by=sort_by,
                           current_category=current_category,
                           search=search,
                           min_price=min_price,
                           max_price=max_price,
                           current_brand=brand)


@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page."""
    product = Product.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('product.shop'))
    
    images = Product.get_images(product_id)
    related = Product.get_related(product_id, product['category_id'])
    
    # Check if in wishlist
    in_wishlist = False
    if 'customer_id' in session:
        from models.wishlist import Wishlist
        in_wishlist = Wishlist.is_in_wishlist(session['customer_id'], product_id)
    
    return render_template('customer/product_details.html',
                           product=product,
                           images=images,
                           related_products=related,
                           in_wishlist=in_wishlist)


@product_bp.route('/category/<int:category_id>')
def category(category_id):
    """Products by category."""
    return redirect(url_for('product.shop', category=category_id))


@product_bp.route('/search')
def search():
    """Search products."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('product.shop'))
    return redirect(url_for('product.shop', q=query))


@product_bp.route('/deals')
def deals():
    """Products with discounts."""
    page = request.args.get('page', 1, type=int)
    from app import mysql
    cur = mysql.connection.cursor()
    
    offset = (page - 1) * Config.PRODUCTS_PER_PAGE
    cur.execute("""
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.is_active = 1 AND p.discount_price IS NOT NULL AND p.discount_price < p.price
        ORDER BY ((p.price - p.discount_price) / p.price * 100) DESC
        LIMIT %s OFFSET %s
    """, (Config.PRODUCTS_PER_PAGE, offset))
    products = cur.fetchall()
    
    cur.execute("""
        SELECT COUNT(*) as total FROM products 
        WHERE is_active = 1 AND discount_price IS NOT NULL AND discount_price < price
    """)
    total = cur.fetchone()['total']
    cur.close()
    
    total_pages = (total + Config.PRODUCTS_PER_PAGE - 1) // Config.PRODUCTS_PER_PAGE
    categories = Category.get_all()
    
    return render_template('customer/shop.html',
                           products=products,
                           categories=categories,
                           brands=Product.get_brands(),
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           sort_by='newest',
                           current_category=None,
                           search=None,
                           page_title='Deals & Discounts')


@product_bp.route('/new-arrivals')
def new_arrivals():
    """New arrival products."""
    return redirect(url_for('product.shop', sort='newest'))
