"""
Admin Inventory Routes
Inventory tracking, threshold management, manual adjustments, and audit trail.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from admin_portal.routes.admin_auth_routes import admin_login_required
from admin_portal.services.inventory_analysis_service import InventoryAnalysisService

admin_inventory_bp = Blueprint('admin_inventory', __name__)


@admin_inventory_bp.route('/inventory')
@admin_login_required
def inventory_list():
    """List inventory items with stock status and Reorder Recommendations."""
    status_filter = request.args.get('status')
    search = request.args.get('q', '').strip()

    items = InventoryAnalysisService.get_inventory_status_list(status_filter=status_filter, search=search)
    restock_recs = InventoryAnalysisService.get_restock_recommendations()

    return render_template(
        'admin/inventory/index.html',
        items=items,
        products=items,
        restock_recs=restock_recs,
        restock_recommendations=restock_recs,
        status_filter=status_filter,
        current_status=status_filter,
        search=search
    )


@admin_inventory_bp.route('/inventory/adjust', methods=['POST'])
@admin_login_required
def adjust_stock():
    """Execute manual stock adjustment with transactional audit logging."""
    product_id = request.form.get('product_id', type=int)
    raw_qty = request.form.get('quantity', type=int)
    if raw_qty is None:
        raw_qty = request.form.get('quantity_change', type=int)
    
    adjustment_type = request.form.get('adjustment_type') or request.form.get('transaction_type', 'RESTOCK')
    reason = request.form.get('notes', '').strip() or request.form.get('reason', '').strip()

    if not product_id or raw_qty is None:
        flash('Invalid product or quantity change.', 'danger')
        return redirect(url_for('admin_inventory.inventory_list'))

    # If adjustment is negative (e.g. Damage/Scrap), ensure sign is negative
    if adjustment_type in ['DAMAGE', 'SCRAP', 'REDUCTION'] and raw_qty > 0:
        change_qty = -raw_qty
    else:
        change_qty = raw_qty

    if not reason:
        reason = f"Stock update ({adjustment_type}) via Admin Portal"

    admin_id = session.get('admin_id')
    success, msg = InventoryAnalysisService.adjust_stock(
        product_id=product_id,
        quantity_change=change_qty,
        transaction_type=adjustment_type,
        reason=reason,
        admin_id=admin_id
    )

    if success:
        flash(f"Success: {msg}", 'success')
    else:
        flash(f"Adjustment failed: {msg}", 'danger')

    return redirect(url_for('admin_inventory.inventory_list'))


@admin_inventory_bp.route('/inventory/transactions')
@admin_login_required
def transactions():
    """View inventory transaction history and full audit log."""
    logs = InventoryAnalysisService.get_transaction_history(limit=100)
    return render_template('admin/inventory/transactions.html', logs=logs, transactions=logs)
