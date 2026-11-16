"""
Admin Business Insights Routes
Presents rule-based MIS Decision Support recommendations synthesized from real database trends.
"""

from flask import Blueprint, render_template
from admin_portal.routes.admin_auth_routes import admin_login_required
from admin_portal.services.decision_support_service import DecisionSupportService

admin_insights_bp = Blueprint('admin_insights', __name__)


@admin_insights_bp.route('/insights')
@admin_login_required
def insights_view():
    """Business Insights & Recommendations."""
    recommendations = DecisionSupportService.generate_all_recommendations()
    return render_template('admin/insights/index.html', recommendations=recommendations)
