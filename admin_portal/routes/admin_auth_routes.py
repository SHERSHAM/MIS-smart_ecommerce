"""
Admin Authentication Routes
Handles admin login, logout, and role-based access protection.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.admin import Admin

admin_auth_bp = Blueprint('admin_auth', __name__)


def admin_login_required(f):
    """Decorator to protect admin routes from unauthorized or customer access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Administrator authentication required.', 'warning')
            return redirect(url_for('admin_auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin Login Page."""
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Please enter both administrator username/email and password.', 'danger')
            return render_template('admin/admin_login.html', identifier=identifier)

        admin = Admin.find_by_username_or_email(identifier)
        if admin and Admin.verify_password(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_name'] = admin['full_name']
            session['admin_role'] = admin['role']
            session.permanent = True

            Admin.update_last_login(admin['id'])
            flash(f'Welcome back, {admin["full_name"]}!', 'success')

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/admin'):
                return redirect(next_url)
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            flash('Invalid administrator credentials or unauthorized account.', 'danger')
            return render_template('admin/admin_login.html', identifier=identifier)

    return render_template('admin/admin_login.html')


@admin_auth_bp.route('/logout')
def logout():
    """Admin Logout."""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('admin_name', None)
    session.pop('admin_role', None)
    flash('Administrator session closed successfully.', 'info')
    return redirect(url_for('admin_auth.login'))
