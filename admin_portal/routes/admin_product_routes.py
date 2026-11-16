"""
Admin Product Routes
Complete CRUD operations for e-commerce catalog management with image upload validation.
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app import mysql
from models.product import Product
from models.category import Category
from admin_portal.routes.admin_auth_routes import admin_login_required

admin_product_bp = Blueprint('admin_product', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_product_bp.route('/products')
@admin_login_required
def product_list():
    """List all products with search and category filters."""
    category_id = request.args.get('category', type=int)
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'all')

    cur = mysql.connection.cursor()
    query = """
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    """
    params = []
    if category_id:
        query += " AND p.category_id = %s"; params.append(category_id)
    if search:
        query += " AND (p.name LIKE %s OR p.sku LIKE %s OR p.brand LIKE %s)"
        st = f"%{search}%"; params.extend([st, st, st])
    if status_filter == 'active':
        query += " AND p.is_active = 1"
    elif status_filter == 'inactive':
        query += " AND p.is_active = 0"

    query += " ORDER BY p.id DESC"
    cur.execute(query, params)
    products = cur.fetchall()
    cur.close()

    categories = Category.get_all(active_only=False)
    return render_template(
        'admin/products/index.html',
        products=products,
        categories=categories,
        current_category=category_id,
        search=search,
        status_filter=status_filter
    )


@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
@admin_login_required
def add_product():
    """Add a new product to catalog."""
    categories = Category.get_all(active_only=True)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        brand = request.form.get('brand', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        discount_price = request.form.get('discount_price', type=float) or None
        stock = request.form.get('stock', 0, type=int)
        sku = request.form.get('sku', '').strip()
        short_desc = request.form.get('short_description', '').strip()
        desc = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()

        # Handle File Upload
        file = request.files.get('product_image_file')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'products')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            image_url = f"/static/images/products/{filename}"

        if not name or not price or not category_id:
            flash('Product Name, Category, and Valid Price are required.', 'danger')
            return render_template('admin/products/form.html', categories=categories, product=None)

        import re
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
        # Check uniqueness of slug
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM products WHERE slug = %s", (slug,))
        if cur.fetchone():
            import uuid
            slug = f"{slug}-{uuid.uuid4().hex[:4]}"

        # Insert product
        cur.execute("""
            INSERT INTO products 
            (name, slug, brand, category_id, price, discount_price, stock, sku, short_description, description, image_url, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (name, slug, brand, category_id, price, discount_price, stock, sku, short_desc, desc, image_url))
        new_prod_id = cur.lastrowid

        # Insert inventory record
        cur.execute("""
            INSERT INTO inventory (product_id, quantity, low_stock_threshold, reorder_point, lead_time_days)
            VALUES (%s, %s, 10, 15, 5)
        """, (new_prod_id, stock))

        # Insert product_images record
        if image_url:
            cur.execute("""
                INSERT INTO product_images (product_id, image_url, is_primary)
                VALUES (%s, %s, 1)
            """, (new_prod_id, image_url))

        mysql.connection.commit()
        cur.close()

        flash(f"Product '{name}' added successfully and is now live in Customer Portal!", 'success')
        return redirect(url_for('admin_product.product_list'))

    return render_template('admin/products/form.html', categories=categories, product=None)


@admin_product_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_product(product_id):
    """Edit an existing product."""
    product = Product.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_product.product_list'))

    categories = Category.get_all(active_only=False)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        brand = request.form.get('brand', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        discount_price = request.form.get('discount_price', type=float) or None
        stock = request.form.get('stock', 0, type=int)
        sku = request.form.get('sku', '').strip()
        short_desc = request.form.get('short_description', '').strip()
        desc = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip() or product['image_url']
        is_active = 1 if request.form.get('is_active') == 'on' else 0

        # Handle file upload if provided
        file = request.files.get('product_image_file')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'products')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            image_url = f"/static/images/products/{filename}"

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE products 
            SET name = %s, brand = %s, category_id = %s, price = %s, 
                discount_price = %s, stock = %s, sku = %s, 
                short_description = %s, description = %s, image_url = %s, is_active = %s
            WHERE id = %s
        """, (name, brand, category_id, price, discount_price, stock, sku, short_desc, desc, image_url, is_active, product_id))

        # Update inventory table quantity to sync
        cur.execute("UPDATE inventory SET quantity = %s WHERE product_id = %s", (stock, product_id))

        mysql.connection.commit()
        cur.close()

        flash(f"Product '{name}' updated successfully! Changes reflected across the system.", 'success')
        return redirect(url_for('admin_product.product_list'))

    return render_template('admin/products/form.html', categories=categories, product=product)


@admin_product_bp.route('/products/toggle-status/<int:product_id>', methods=['POST'])
@admin_login_required
def toggle_status(product_id):
    """Toggle product active/inactive state."""
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET is_active = NOT is_active WHERE id = %s", (product_id,))
    mysql.connection.commit()
    cur.close()
    flash('Product visibility status toggled.', 'info')
    return redirect(url_for('admin_product.product_list'))
