"""
Admin Report Routes
Generates 8 standard business reports with date range filtering and CSV export using Pandas.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, Response
from admin_portal.routes.admin_auth_routes import admin_login_required
from admin_portal.services.report_service import ReportService

admin_report_bp = Blueprint('admin_report', __name__)

REPORT_NAMES = {
    'daily_sales': 'Daily Sales Report',
    'monthly_sales': 'Monthly Sales Report',
    'product_performance': 'Product Performance Report',
    'customer_purchase': 'Customer Purchase Report',
    'inventory_status': 'Inventory Status Report',
    'low_stock': 'Low Stock Alert Report',
    'best_sellers': 'Best-Selling Products Report',
    'order_status': 'Order Status Report'
}


@admin_report_bp.route('/reports')
@admin_login_required
def report_view():
    """Interactive Report Viewer."""
    report_type = request.args.get('type', 'daily_sales')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    data, columns = ReportService.get_report_data(report_type, start_date, end_date)
    report_title = REPORT_NAMES.get(report_type, 'Business Report')

    return render_template(
        'admin/reports/index.html',
        report_type=report_type,
        report_title=report_title,
        data=data,
        columns=columns,
        start_date=start_date,
        end_date=end_date,
        report_names=REPORT_NAMES
    )


@admin_report_bp.route('/reports/export-csv')
@admin_login_required
def export_csv():
    """Export selected report as a downloadable CSV file."""
    report_type = request.args.get('type', 'daily_sales')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    csv_data = ReportService.export_csv(report_type, start_date, end_date)
    filename = f"VIVA_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
