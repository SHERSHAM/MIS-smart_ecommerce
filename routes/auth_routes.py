"""Authentication routes - login, register, logout."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.customer import Customer

auth_bp = Blueprint('auth', __name__)


def clean_next_url(target):
    """Sanitize redirect destination to prevent landing on POST action routes."""
    if not target:
        return None
    # Block action URLs that don't make sense to GET
    action_endpoints = ['/add-to-cart', '/update-cart', '/remove-from-cart',
                        '/clear-cart', '/add-to-wishlist', '/remove-from-wishlist',
                        '/move-to-cart', '/place-order']
    for endpoint in action_endpoints:
        if endpoint in target:
            return url_for('cart.view_cart') if 'cart' in endpoint else url_for('customer.home')
    return target


def login_required(f):
    """Decorator to require login with safe redirect URL."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in or create an account to continue.', 'warning')
            # If arriving via POST action, return to referrer page (e.g. product page)
            fallback = request.referrer if (request.referrer and request.method == 'POST') else request.url
            safe_next = clean_next_url(fallback) or url_for('customer.home')
            return redirect(url_for('auth.login', next=safe_next))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'customer_id' in session:
        return redirect(url_for('customer.home'))

    next_page = clean_next_url(request.args.get('next') or request.form.get('next'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not email or '@' not in email:
            errors.append('A valid email address is required.')
        if not password:
            errors.append('Password is required.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if email and Customer.email_exists(email):
            errors.append('An account with this email already exists. Please log in.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html',
                                   full_name=full_name, email=email, phone=phone, next=next_page)

        try:
            customer_id = Customer.create(full_name, email, phone, password)
            # Auto-login after registration
            session['customer_id'] = customer_id
            session['customer_name'] = full_name
            session['customer_email'] = email
            session.permanent = True

            flash(f'Welcome to VIVA, {full_name}! Your account was created successfully. 🎉', 'success')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('customer.home'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
            return render_template('auth/register.html',
                                   full_name=full_name, email=email, phone=phone, next=next_page)

    return render_template('auth/register.html', next=next_page)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'customer_id' in session:
        return redirect(url_for('customer.home'))

    next_page = clean_next_url(request.args.get('next') or request.form.get('next'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html', email=email, next=next_page)

        customer = Customer.find_by_email(email)
        if customer and Customer.verify_password(customer['password_hash'], password):
            if not customer['is_active']:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html', email=email, next=next_page)

            session['customer_id'] = customer['id']
            session['customer_name'] = customer['full_name']
            session['customer_email'] = customer['email']
            session.permanent = True

            flash(f'Welcome back, {customer["full_name"]}!', 'success')

            if next_page:
                return redirect(next_page)
            return redirect(url_for('customer.home'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', email=email, next=next_page)

    return render_template('auth/login.html', next=next_page)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('customer.home'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if email:
            flash('If an account exists with that email, password reset instructions have been sent.', 'info')
            return redirect(url_for('auth.login'))
        flash('Please enter your email address.', 'danger')
    return render_template('auth/forgot_password.html')
