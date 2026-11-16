"""
VIVA - LIVE BETTER | Smart E-Commerce Decision Support System
Main Application Entry Point
"""

import os
import pymysql
import pymysql.cursors
from flask import Flask, g, session, render_template_string, current_app
from config import config as config_dict


class MySQLHelper:
    """Robust MySQL connection manager for Flask."""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.teardown_appcontext(self.teardown)

    @property
    def connection(self):
        if 'mysql_db' not in g:
            cfg = current_app.config if current_app else (self.app.config if self.app else {})
            g.mysql_db = pymysql.connect(
                host=cfg.get('MYSQL_HOST', 'localhost'),
                user=cfg.get('MYSQL_USER', 'root'),
                password=cfg.get('MYSQL_PASSWORD', 'Shersha123'),
                database=cfg.get('MYSQL_DB', 'smart_ecommerce_db'),
                port=int(cfg.get('MYSQL_PORT', 3306)),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset='utf8mb4'
            )
        return g.mysql_db

    def teardown(self, exception):
        db = g.pop('mysql_db', None)
        if db is not None:
            try:
                db.close()
            except Exception:
                pass


# Initialize MySQL extension
mysql = MySQLHelper()


def create_app(config_name='default'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_dict.get(config_name, config_dict['default']))

    # Configure Jinja template search paths for customer and admin portals
    import jinja2
    admin_template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_portal', 'templates')
    customer_template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app.jinja_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(customer_template_dir),
        jinja2.FileSystemLoader(admin_template_dir),
    ])

    # Initialize extensions
    mysql.init_app(app)

    # Static routes for Admin Portal assets
    from flask import send_from_directory
    admin_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_portal', 'static')

    @app.route('/static/admin_portal/<path:filename>')
    def serve_admin_portal_static(filename):
        return send_from_directory(admin_static_dir, filename)

    @app.route('/admin/static/<path:filename>')
    def serve_admin_static(filename):
        return send_from_directory(admin_static_dir, filename)

    # Register Customer Blueprints (Phase 1)
    from routes.auth_routes import auth_bp
    from routes.customer_routes import customer_bp
    from routes.product_routes import product_bp
    from routes.cart_routes import cart_bp
    from routes.wishlist_routes import wishlist_bp
    from routes.order_routes import order_bp
    from routes.checkout_routes import checkout_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(checkout_bp)

    # Register Admin & MIS Decision Support Blueprints (Phase 2)
    from admin_portal.routes.admin_auth_routes import admin_auth_bp
    from admin_portal.routes.admin_dashboard_routes import admin_dashboard_bp
    from admin_portal.routes.admin_product_routes import admin_product_bp
    from admin_portal.routes.admin_category_routes import admin_category_bp
    from admin_portal.routes.admin_order_routes import admin_order_bp
    from admin_portal.routes.admin_customer_routes import admin_customer_bp
    from admin_portal.routes.admin_inventory_routes import admin_inventory_bp
    from admin_portal.routes.admin_analytics_routes import admin_analytics_bp
    from admin_portal.routes.admin_insights_routes import admin_insights_bp
    from admin_portal.routes.admin_report_routes import admin_report_bp

    app.register_blueprint(admin_auth_bp, url_prefix='/admin')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_product_bp, url_prefix='/admin')
    app.register_blueprint(admin_category_bp, url_prefix='/admin')
    app.register_blueprint(admin_order_bp, url_prefix='/admin')
    app.register_blueprint(admin_customer_bp, url_prefix='/admin')
    app.register_blueprint(admin_inventory_bp, url_prefix='/admin')
    app.register_blueprint(admin_analytics_bp, url_prefix='/admin')
    app.register_blueprint(admin_insights_bp, url_prefix='/admin')
    app.register_blueprint(admin_report_bp, url_prefix='/admin')

    # Context processors - inject cart count and wishlist count into all templates
    @app.context_processor
    def inject_counts():
        cart_count = 0
        wishlist_count = 0
        if 'customer_id' in session:
            try:
                cur = mysql.connection.cursor()
                # Cart count
                cur.execute("""
                    SELECT COALESCE(SUM(ci.quantity), 0) as count
                    FROM cart c
                    JOIN cart_items ci ON c.id = ci.cart_id
                    WHERE c.customer_id = %s
                """, (session['customer_id'],))
                result = cur.fetchone()
                cart_count = int(result['count']) if result and result['count'] else 0

                # Wishlist count
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM wishlist w
                    JOIN wishlist_items wi ON w.id = wi.wishlist_id
                    WHERE w.customer_id = %s
                """, (session['customer_id'],))
                result = cur.fetchone()
                wishlist_count = int(result['count']) if result and result['count'] else 0
                cur.close()
            except Exception:
                pass
        return dict(cart_count=cart_count, wishlist_count=wishlist_count)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Page Not Found | VIVA{% endblock %}
        {% block content %}
        <div class="container py-5 text-center">
            <h1 class="display-4 text-muted fw-bold">404</h1>
            <p class="lead text-muted">The page you're looking for doesn't exist.</p>
            <a href="/" class="btn btn-viva-primary mt-3">Back to Homepage</a>
        </div>
        {% endblock %}
        """), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Server Error | VIVA{% endblock %}
        {% block content %}
        <div class="container py-5 text-center">
            <h1 class="display-4 text-muted fw-bold">500</h1>
            <p class="lead text-muted">Something went wrong on our end. Please try again shortly.</p>
            <a href="/" class="btn btn-viva-primary mt-3">Back to Homepage</a>
        </div>
        {% endblock %}
        """), 500

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, port=5000)
