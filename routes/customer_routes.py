"""Customer routes - homepage, profile, addresses."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.product import Product
from models.category import Category
from models.customer import Customer
from models.address import Address
from routes.auth_routes import login_required

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/')
def home():
    """Homepage."""
    categories = Category.get_all()
    featured_products = Product.get_featured(limit=10)
    new_arrivals = Product.get_new_arrivals(limit=8)
    return render_template('customer/home.html',
                           categories=categories,
                           featured_products=featured_products,
                           new_arrivals=new_arrivals)


@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Customer profile page."""
    customer = Customer.find_by_id(session['customer_id'])
    addresses = Address.get_by_customer(session['customer_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            
            if not full_name:
                flash('Full name is required.', 'danger')
            else:
                Customer.update_profile(session['customer_id'], full_name, phone)
                session['customer_name'] = full_name
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('customer.profile'))
        
        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_new_password', '')
            
            if not Customer.verify_password(customer['password_hash'], current_password):
                flash('Current password is incorrect.', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                Customer.change_password(session['customer_id'], new_password)
                flash('Password changed successfully!', 'success')
                return redirect(url_for('customer.profile'))
    
    customer = Customer.find_by_id(session['customer_id'])
    return render_template('customer/profile.html', customer=customer, addresses=addresses)


@customer_bp.route('/addresses', methods=['GET', 'POST'])
@login_required
def addresses():
    """Manage delivery addresses."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            address_line1 = request.form.get('address_line1', '').strip()
            address_line2 = request.form.get('address_line2', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            is_default = request.form.get('is_default') == 'on'
            
            if not all([full_name, phone, address_line1, city, state, pincode]):
                flash('Please fill in all required fields.', 'danger')
            else:
                Address.create(session['customer_id'], full_name, phone,
                             address_line1, address_line2, city, state, pincode, is_default)
                flash('Address added successfully!', 'success')
        
        elif action == 'update':
            address_id = request.form.get('address_id')
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            address_line1 = request.form.get('address_line1', '').strip()
            address_line2 = request.form.get('address_line2', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            is_default = request.form.get('is_default') == 'on'
            
            if not all([full_name, phone, address_line1, city, state, pincode]):
                flash('Please fill in all required fields.', 'danger')
            else:
                Address.update(address_id, session['customer_id'], full_name, phone,
                             address_line1, address_line2, city, state, pincode, is_default)
                flash('Address updated successfully!', 'success')
        
        elif action == 'delete':
            address_id = request.form.get('address_id')
            Address.delete(address_id, session['customer_id'])
            flash('Address deleted successfully!', 'success')
        
        return redirect(url_for('customer.addresses'))
    
    customer_addresses = Address.get_by_customer(session['customer_id'])
    return render_template('customer/addresses.html', addresses=customer_addresses)


@customer_bp.route('/newsletter-subscribe', methods=['POST'])
def newsletter_subscribe():
    """Subscribe to newsletter."""
    from app import mysql
    email = request.form.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('customer.home'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO newsletter_subscribers (email) VALUES (%s)", (email,))
        mysql.connection.commit()
        cur.close()
        flash('Thank you for subscribing! 🎉', 'success')
    except Exception:
        flash('You are already subscribed!', 'info')
    
    return redirect(url_for('customer.home'))


# Static pages
@customer_bp.route('/about')
def about():
    return render_template('customer/static_page.html', 
                           title='About Us', 
                           content='VIVA - Live Better. Your one-stop shop for quality products across every category.')

@customer_bp.route('/contact')
def contact():
    return render_template('customer/static_page.html',
                           title='Contact Us',
                           content='Have questions? Reach out to us at support@viva.com or call us at 1800-VIVA-HELP.')

@customer_bp.route('/faq')
def faq():
    return render_template('customer/static_page.html',
                           title='Frequently Asked Questions',
                           content='Find answers to common questions about orders, shipping, returns, and more.')

@customer_bp.route('/shipping-info')
def shipping_info():
    return render_template('customer/static_page.html',
                           title='Shipping Information',
                           content='Free shipping on orders over ₹999. Standard delivery in 3-5 business days.')

@customer_bp.route('/returns')
def returns():
    return render_template('customer/static_page.html',
                           title='Returns & Refunds',
                           content='30-day easy return policy. Full refund or exchange on eligible products.')

@customer_bp.route('/privacy')
def privacy():
    return render_template('customer/static_page.html',
                           title='Privacy Policy',
                           content='Your privacy is important to us. We protect your personal information.')

@customer_bp.route('/terms')
def terms():
    return render_template('customer/static_page.html',
                           title='Terms of Service',
                           content='By using VIVA, you agree to our terms and conditions.')
