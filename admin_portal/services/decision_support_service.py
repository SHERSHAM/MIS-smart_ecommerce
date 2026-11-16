"""
Decision Support Service (MIS Rule-Based Engine)
Analyzes sales velocity, stock levels, revenue trends, and customer purchase patterns 
to synthesize transparent, actionable business recommendations.
"""

from app import mysql
from admin_portal.services.sales_analysis_service import SalesAnalysisService
from admin_portal.services.product_analysis_service import ProductAnalysisService
from admin_portal.services.inventory_analysis_service import InventoryAnalysisService
from admin_portal.services.customer_analysis_service import CustomerAnalysisService


class DecisionSupportService:
    @staticmethod
    def generate_all_recommendations():
        """
        Synthesize transparent business insights using deterministic decision rules:
        Rule 1: Imminent Stockout on Top Sellers
        Rule 2: Excess Capital Locked in Slow Movers
        Rule 3: Category Revenue Concentration / Imbalance
        Rule 4: Monthly Revenue Momentum & Trajectory
        Rule 5: Customer Retention & Repeat Buying Rate
        """
        insights = []

        # --- Rule 1: Imminent Stockout on Fast-Moving Products ---
        top_sellers = ProductAnalysisService.get_top_selling_products(limit=5)
        for prod in top_sellers:
            stock = int(prod['stock'])
            units_sold = int(prod['total_units_sold'])
            if stock <= 15:
                insights.append({
                    'category': 'Inventory Optimization',
                    'badge': 'danger',
                    'title': f"Stockout Risk on Top Performer: '{prod['name']}'",
                    'observation': f"'{prod['name']}' is currently sales rank #{prod['sales_rank']} with {units_sold} units sold, but only {stock} units remain in stock.",
                    'supporting_data': f"Available Inventory: {stock} units | Historical Sales: {units_sold} units | Revenue: Rs.{prod['total_revenue_generated']:,.0f}",
                    'business_implication': "Running out of stock on your top-performing SKU directly forfeits revenue and risks losing customer loyalty to competitors.",
                    'suggested_action': f"Issue an expedited purchase order for at least 35 units to ensure continuous product availability."
                })

        # --- Rule 2: Excess Capital Tied in Slow-Moving Inventory ---
        slow_movers = ProductAnalysisService.get_slow_moving_products(days=30, max_sales=1)
        if slow_movers:
            top_slow = slow_movers[0]
            insights.append({
                'category': 'Merchandising & Pricing',
                'badge': 'warning',
                'title': f"Capital Locked in Idle Inventory: '{top_slow['name']}'",
                'observation': f"'{top_slow['name']}' in category '{top_slow['category_name']}' has {top_slow['stock']} units on hand with only {top_slow['recent_units_sold']} units sold in the past 30 days.",
                'supporting_data': f"Idle Stock Value: Rs.{(float(top_slow['price']) * int(top_slow['stock'])):,.0f} | 30-Day Sales: {top_slow['recent_units_sold']} units",
                'business_implication': "Overstocked slow-moving goods increase warehouse holding costs and tie up liquidity that could be deployed to high-velocity lines.",
                'suggested_action': top_slow['recommendation']
            })

        # --- Rule 3: Category Revenue Contribution ---
        cat_dist = SalesAnalysisService.get_category_sales_distribution()
        if cat_dist['sales']:
            top_cat = cat_dist['labels'][0]
            top_cat_rev = cat_dist['sales'][0]
            total_cat_rev = sum(cat_dist['sales'])
            share = round((top_cat_rev / total_cat_rev * 100), 1) if total_cat_rev > 0 else 0
            
            insights.append({
                'category': 'Category Strategy',
                'badge': 'info',
                'title': f"Dominant Revenue Driver: '{top_cat}' ({share}% Store Share)",
                'observation': f"Category '{top_cat}' generates Rs.{top_cat_rev:,.0f}, accounting for {share}% of your total catalog sales.",
                'supporting_data': f"Top Category Share: {share}% | Category Revenue: Rs.{top_cat_rev:,.0f} across {cat_dist['units'][0]} items sold",
                'business_implication': f"While strong performance in '{top_cat}' drives top-line numbers, heavy revenue concentration in one vertical increases vulnerability.",
                'suggested_action': f"Cross-sell accessories from secondary categories (e.g. Home, Books, Beauty) on {top_cat} product pages to diversify your revenue mix."
            })

        # --- Rule 4: Revenue Growth Trajectory ---
        kpis = SalesAnalysisService.get_dashboard_kpis()
        growth = kpis['revenue_growth_pct']
        if growth >= 0:
            insights.append({
                'category': 'Sales Performance',
                'badge': 'success',
                'title': f"Positive Month-over-Month Revenue Growth (+{growth}%)",
                'observation': f"Current monthly revenue stands at Rs.{kpis['curr_month_revenue']:,.0f} compared to Rs.{kpis['prev_month_revenue']:,.0f} last month.",
                'supporting_data': f"Net Monthly Delta: +Rs.{(kpis['curr_month_revenue'] - kpis['prev_month_revenue']):,.0f} (+{growth}%)",
                'business_implication': "Sales momentum is strong. Customer acquisition channels and recent seasonal marketing are converting effectively.",
                'suggested_action': "Maintain promotional campaign pacing and ensure high inventory availability across core best-sellers to sustain the upward curve."
            })
        else:
            insights.append({
                'category': 'Sales Performance',
                'badge': 'warning',
                'title': f"Month-over-Month Revenue Contraction ({growth}%)",
                'observation': f"Current revenue of Rs.{kpis['curr_month_revenue']:,.0f} is lagging behind the prior month's Rs.{kpis['prev_month_revenue']:,.0f}.",
                'supporting_data': f"Net Monthly Decrease: Rs.{(kpis['curr_month_revenue'] - kpis['prev_month_revenue']):,.0f} ({growth}%)",
                'business_implication': "A decline in order volume or basket size suggests seasonal drop-off or marketing fatigue.",
                'suggested_action': "Trigger an email newsletter campaign to registered customers featuring an exclusive 15% discount code."
            })

        # --- Rule 5: Customer Repeat Purchase Behavior ---
        cust_summary = CustomerAnalysisService.get_customer_summary_metrics()
        repeat_rate = cust_summary['repeat_rate_pct']
        insights.append({
            'category': 'Customer Retention',
            'badge': 'primary',
            'title': f"Customer Retention Rate: {repeat_rate}% (AOV: Rs.{cust_summary['overall_aov']:,.0f})",
            'observation': f"Out of {cust_summary['total_customers']} registered customers, {cust_summary['repeat_customers']} have completed repeat purchases.",
            'supporting_data': f"Repeat Purchase Ratio: {repeat_rate}% | Overall Store AOV: Rs.{cust_summary['overall_aov']:,.0f}",
            'business_implication': "Repeat customers cost significantly less to convert than acquiring new customers and generate higher lifetime value.",
            'suggested_action': "Introduce a tiered loyalty or reward points mechanism to incentivize second and third purchases within 30 days of registration."
        })

        # Add compatibility aliases and icons
        for item in insights:
            item['finding'] = item.get('observation', '')
            item['impact'] = item.get('business_implication', '')
            item['recommendation'] = item.get('suggested_action', '')
            badge = item.get('badge', 'info')
            if badge == 'danger':
                item['severity'] = 'CRITICAL'
                item['icon'] = 'bi-exclamation-octagon-fill'
            elif badge == 'warning':
                item['severity'] = 'WARNING'
                item['icon'] = 'bi-exclamation-triangle-fill'
            elif badge == 'success':
                item['severity'] = 'GROWTH'
                item['icon'] = 'bi-graph-up-arrow'
            else:
                item['severity'] = 'STRATEGY'
                item['icon'] = 'bi-lightbulb-fill'

        return insights
