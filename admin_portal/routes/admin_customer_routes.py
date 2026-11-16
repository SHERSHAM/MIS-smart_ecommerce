"""
Admin Customer Routes
Customer intelligence, profiling, purchasing history, and value segmentation.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mysql
from models.customer import Customer
from models.order import Order
from admin_portal.routes.admin_auth_routes import admin_login_required
from admin_portal.services.customer_analysis_service import CustomerAnalysisService

admin_customer_bp = Blueprint('admin_customer', __name__)


@admin_customer_bp.route('/customers')
@admin_login_required
def customer_list():
    """List all customers with financial lifetime metrics and segmentation."""
    search = request.args.get('q', '').strip()
    customers = CustomerAnalysisService.get_customer_intelligence_list(search=search)
    summary_metrics = CustomerAnalysisService.get_customer_summary_metrics()

    return render_template(
        'admin/customers/index.html',
        customers=customers,
        summary_metrics=summary_metrics,
        search=search
    )


@admin_customer_bp.route('/customers/<int:customer_id>')
@admin_login_required
def customer_detail(customer_id):
    """View customer order history and profile details."""
    customer = Customer.find_by_id(customer_id)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('admin_customer.customer_list'))

    orders = Order.get_by_customer(customer_id)
    total_spent = sum(float(o['total']) for o in orders if o['status'] != 'Cancelled')

    return render_template(
        'admin/customers/details.html',
        customer=customer,
        orders=orders,
        total_spent=total_spent
    )
