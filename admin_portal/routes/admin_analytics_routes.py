"""
Admin Analytics Routes
Deep-dive MIS decision analytics: Top 10 Best Sellers, 30-Day Slow Movers, and Category shares.
"""

from flask import Blueprint, render_template, request
from admin_portal.routes.admin_auth_routes import admin_login_required
from admin_portal.services.product_analysis_service import ProductAnalysisService
from admin_portal.services.sales_analysis_service import SalesAnalysisService

admin_analytics_bp = Blueprint('admin_analytics', __name__)


@admin_analytics_bp.route('/analytics')
@admin_login_required
def analytics_overview():
    """MIS Decision Analytics Overview."""
    days_filter = request.args.get('days', type=int)

    top_sellers = ProductAnalysisService.get_top_selling_products(limit=10, days=days_filter)
    slow_movers = ProductAnalysisService.get_slow_moving_products(days=30, max_sales=1)
    monthly_trend = SalesAnalysisService.get_monthly_revenue_trend(months=12)
    category_dist = SalesAnalysisService.get_category_sales_distribution()

    return render_template(
        'admin/analytics/index.html',
        top_sellers=top_sellers,
        slow_movers=slow_movers,
        monthly_trend=monthly_trend,
        category_dist=category_dist,
        days_filter=days_filter
    )
