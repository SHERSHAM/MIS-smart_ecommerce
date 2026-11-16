"""
Admin Dashboard Routes
Serves the executive MIS overview with Chart.js datasets and real-time business health indicators.
"""

from flask import Blueprint, render_template, redirect, url_for
from admin_portal.routes.admin_auth_routes import admin_login_required
from admin_portal.services.sales_analysis_service import SalesAnalysisService
from admin_portal.services.customer_analysis_service import CustomerAnalysisService
from admin_portal.services.product_analysis_service import ProductAnalysisService

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)


@admin_dashboard_bp.route('/')
def admin_root():
    """Redirect /admin to /admin/dashboard."""
    return redirect(url_for('admin_dashboard.dashboard'))


@admin_dashboard_bp.route('/dashboard')
@admin_login_required
def dashboard():
    """Main Executive MIS Dashboard matching reference design."""
    kpis = SalesAnalysisService.get_dashboard_kpis()
    monthly_trend = SalesAnalysisService.get_monthly_revenue_trend(months=6)
    category_dist = SalesAnalysisService.get_category_sales_distribution()
    status_dist = SalesAnalysisService.get_order_status_distribution()
    recent_orders = SalesAnalysisService.get_recent_orders(limit=6)
    top_products = ProductAnalysisService.get_top_selling_products(limit=5)
    customer_kpis = CustomerAnalysisService.get_customer_summary_metrics()

    return render_template(
        'admin/dashboard.html',
        kpis=kpis,
        monthly_trend=monthly_trend,
        category_dist=category_dist,
        status_dist=status_dist,
        recent_orders=recent_orders,
        top_products=top_products,
        customer_kpis=customer_kpis
    )
