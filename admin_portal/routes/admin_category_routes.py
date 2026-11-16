"""
Admin Category Routes
Manages product taxonomy, hierarchy, and icon configurations.
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mysql
from models.category import Category
from admin_portal.routes.admin_auth_routes import admin_login_required

admin_category_bp = Blueprint('admin_category', __name__)


@admin_category_bp.route('/categories')
@admin_login_required
def category_list():
    """List all categories with live product counts."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.is_active = 1
        GROUP BY c.id
        ORDER BY c.display_order ASC, c.name ASC
    """)
    categories = cur.fetchall()
    cur.close()

    return render_template('admin/categories/index.html', categories=categories)


@admin_category_bp.route('/categories/add', methods=['POST'])
@admin_login_required
def add_category():
    """Add a new category."""
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', 'bi-tag').strip()
    image = request.form.get('image', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Category Name is required.', 'danger')
        return redirect(url_for('admin_category.category_list'))

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO categories (name, slug, description, image, icon, is_active)
        VALUES (%s, %s, %s, %s, %s, 1)
    """, (name, slug, description, image, icon))
    mysql.connection.commit()
    cur.close()

    flash(f"Category '{name}' created successfully!", 'success')
    return redirect(url_for('admin_category.category_list'))


@admin_category_bp.route('/categories/edit/<int:category_id>', methods=['POST'])
@admin_login_required
def edit_category(category_id):
    """Edit an existing category."""
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', '').strip()
    image = request.form.get('image', '').strip()
    description = request.form.get('description', '').strip()
    is_active = 1 if request.form.get('is_active') == 'on' else 0

    if not name:
        flash('Category Name cannot be empty.', 'danger')
        return redirect(url_for('admin_category.category_list'))

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE categories 
        SET name = %s, description = %s, image = %s, icon = %s, is_active = %s
        WHERE id = %s
    """, (name, description, image, icon, is_active, category_id))
    mysql.connection.commit()
    cur.close()

    flash(f"Category '{name}' updated successfully!", 'success')
    return redirect(url_for('admin_category.category_list'))


@admin_category_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@admin_login_required
def delete_category(category_id):
    """Safe deletion of category only if it has no associated products."""
    count = Category.get_product_count(category_id)
    if count > 0:
        flash(f"Cannot delete category: {count} active products are linked to it. Reassign or delete products first.", 'warning')
        return redirect(url_for('admin_category.category_list'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM categories WHERE id = %s", (category_id,))
    mysql.connection.commit()
    cur.close()

    flash('Category deleted successfully.', 'info')
    return redirect(url_for('admin_category.category_list'))
