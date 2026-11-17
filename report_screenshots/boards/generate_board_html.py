import os

os.makedirs('d:/file/mis/smart_ecommerce/report_screenshots/boards', exist_ok=True)

SHARED_CSS = """
:root {
    --bg-main: #0B1118;
    --bg-card: #131E29;
    --bg-col: #0E1620;
    --border-color: #202F3E;
    --neon-green: #00F59B;
    --text-primary: #F0F4F8;
    --text-muted: #8E9FAA;
    --must-have: #FF4757;
    --should-have: #FFA502;
    --done-badge: #00F59B;
}
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
body { background: var(--bg-main); color: var(--text-primary); padding: 24px; min-height: 100vh; }
.header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); margin-bottom: 24px; }
.project-title { display: flex; align-items: center; gap: 14px; }
.project-icon { width: 42px; height: 42px; background: linear-gradient(135deg, #00F59B, #00A86B); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #000; font-size: 20px; box-shadow: 0 0 15px rgba(0,245,155,0.3); }
.project-name { font-size: 22px; font-weight: 700; color: #FFF; letter-spacing: -0.5px; }
.project-subtitle { font-size: 13px; color: var(--text-muted); margin-top: 2px; }
.meta-badges { display: flex; gap: 10px; align-items: center; }
.meta-badge { background: #182533; border: 1px solid var(--border-color); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.meta-badge.active { border-color: var(--neon-green); color: var(--neon-green); background: rgba(0,245,155,0.08); }

.sprint-summary-bar { background: var(--bg-col); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
.sprint-info-left { display: flex; align-items: center; gap: 18px; }
.sprint-name { font-size: 17px; font-weight: 700; color: #FFF; }
.sprint-dates { font-size: 13px; color: var(--text-muted); }
.sprint-stats { display: flex; gap: 20px; }
.stat-item { text-align: right; }
.stat-val { font-size: 16px; font-weight: 700; color: var(--neon-green); }
.stat-lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

.kanban-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.kanban-grid-full { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.column { background: var(--bg-col); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; min-height: 600px; }
.col-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 14px; border-bottom: 1px solid var(--border-color); margin-bottom: 14px; }
.col-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); display: flex; align-items: center; gap: 8px; }
.col-count { background: #1E2D3D; color: var(--text-primary); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.card-stack { display: flex; flex-direction: column; gap: 14px; flex-grow: 1; }

.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; position: relative; transition: all 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.card:hover { border-color: var(--neon-green); transform: translateY(-2px); }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.card-id { font-size: 12px; font-weight: 800; color: var(--neon-green); background: rgba(0,245,155,0.1); padding: 2px 8px; border-radius: 6px; letter-spacing: 0.5px; }
.priority-tag { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px; }
.priority-must { background: rgba(255, 71, 87, 0.15); color: #FF4757; border: 1px solid rgba(255, 71, 87, 0.3); }
.priority-should { background: rgba(255, 165, 2, 0.15); color: #FFA502; border: 1px solid rgba(255, 165, 2, 0.3); }

.epic-tag { font-size: 11px; font-weight: 600; color: #64B5F6; background: rgba(33, 150, 243, 0.12); padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
.epic-logistics { color: #81C784; background: rgba(76, 175, 80, 0.12); }
.epic-analytics { color: #BA68C8; background: rgba(156, 39, 176, 0.12); }
.epic-security { color: #FFB74D; background: rgba(255, 152, 0, 0.12); }

.card-title { font-size: 13.5px; font-weight: 600; line-height: 1.45; color: #FFFFFF; margin-bottom: 12px; }
.card-desc { font-size: 12px; color: var(--text-muted); line-height: 1.4; margin-bottom: 14px; background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border-left: 3px solid var(--border-color); }
.card-footer { display: flex; justify-content: space-between; align-items: center; font-size: 12px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: 4px; }
.card-points { background: #1C2B39; color: #A4B8C7; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.card-status { font-weight: 700; font-size: 11px; display: flex; align-items: center; gap: 5px; color: var(--neon-green); }
.card-status::before { content: ""; width: 7px; height: 7px; background: var(--neon-green); border-radius: 50%; box-shadow: 0 0 6px var(--neon-green); }

.avatar { width: 22px; height: 22px; border-radius: 50%; background: #2A3F54; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: #FFF; }
"""

# Story definitions
STORIES = {
    "US-01": {
        "id": "US-01", "epic": "Product Discovery", "epic_class": "epic-tag",
        "title": "Multi-Criteria Catalog Search & Dynamic Filtering",
        "statement": "As a customer, I want to filter products by category, price range, and brand with instant stock visibility so that I can quickly discover items.",
        "points": "5 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 1", "status": "Completed"
    },
    "US-02": {
        "id": "US-02", "epic": "Cart & Checkout", "epic_class": "epic-tag",
        "title": "Persistent Shopping Cart with Free Shipping Progress",
        "statement": "As a customer, I want to manage quantities in my cart and see real-time progress toward free delivery (₹999) so that I can optimize costs.",
        "points": "5 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 1", "status": "Completed"
    },
    "US-03": {
        "id": "US-03", "epic": "Order Placement", "epic_class": "epic-tag",
        "title": "Atomic Multi-Option Order Checkout Workflow",
        "statement": "As a customer, I want to complete checkout with Cash on Delivery or Simulated Online Payment with address verification.",
        "points": "8 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 1", "status": "Completed"
    },
    "US-04": {
        "id": "US-04", "epic": "Order Tracking", "epic_class": "epic-tag",
        "title": "Milestone Order Tracking with Visual Stepper",
        "statement": "As a customer, I want to track my order status through a 5-stage milestone timeline so that I know exact delivery ETA.",
        "points": "6 pts", "priority": "Should Have", "pri_class": "priority-should",
        "sprint": "Sprint 1", "status": "Completed"
    },
    "US-05": {
        "id": "US-05", "epic": "Admin Security", "epic_class": "epic-security",
        "title": "Executive Session Authentication & Role Authorization",
        "statement": "As a store owner, I want secure admin authentication with scrypt hashing and session guards so that unauthorized users cannot view data.",
        "points": "5 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 2", "status": "Completed"
    },
    "US-06": {
        "id": "US-06", "epic": "Executive Dashboard", "epic_class": "epic-analytics",
        "title": "Store-Wide Executive KPIs & Revenue Trend Line",
        "statement": "As an executive, I want real-time KPI tiles and monthly revenue trajectory charts to evaluate corporate business health at a glance.",
        "points": "8 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 3", "status": "Completed"
    },
    "US-07": {
        "id": "US-07", "epic": "Inventory Logistics", "epic_class": "epic-logistics",
        "title": "Automated Reorder Point (ROP) & Safety Stock DSS",
        "statement": "As an inventory manager, I want calculated Reorder Points (ROP = d*L + SS) and restock guidance so that I prevent stockouts.",
        "points": "8 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 2", "status": "Completed"
    },
    "US-08": {
        "id": "US-08", "epic": "Stock Adjustment Audit", "epic_class": "epic-logistics",
        "title": "Immutable Stock Adjustment Transaction Ledger",
        "statement": "As an inventory auditor, I want every manual stock adjustment logged with reason, operator, and timestamp to prevent warehouse shrinkage.",
        "points": "5 pts", "priority": "Should Have", "pri_class": "priority-should",
        "sprint": "Sprint 2", "status": "Completed"
    },
    "US-09": {
        "id": "US-09", "epic": "Order Fulfillment", "epic_class": "epic-logistics",
        "title": "Fulfillment Pipeline with Stock Reversal on Cancel",
        "statement": "As an administrator, I want to update order statuses and have stock automatically restored if an order is cancelled.",
        "points": "6 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 2", "status": "Completed"
    },
    "US-10": {
        "id": "US-10", "epic": "Merchandising DSS", "epic_class": "epic-analytics",
        "title": "Slow-Moving Inventory & Locked Capital Identification",
        "statement": "As a merchandising manager, I want the system to flag items idle for 30+ days and calculate tied-up capital to trigger clearance sales.",
        "points": "5 pts", "priority": "Should Have", "pri_class": "priority-should",
        "sprint": "Sprint 3", "status": "Completed"
    },
    "US-11": {
        "id": "US-11", "epic": "Decision Support Insights", "epic_class": "epic-analytics",
        "title": "Automated Strategic Decision Advisory Engine",
        "statement": "As an e-commerce executive, I want automated diagnostic signals for category concentration and pricing to make informed moves.",
        "points": "8 pts", "priority": "Should Have", "pri_class": "priority-should",
        "sprint": "Sprint 3", "status": "Completed"
    },
    "US-12": {
        "id": "US-12", "epic": "Business Reporting", "epic_class": "epic-analytics",
        "title": "Multi-Dimensional Sales Audit & CSV Data Export",
        "statement": "As an analyst, I want to filter daily/monthly sales reports and export tabular CSV datasets for financial compliance.",
        "points": "5 pts", "priority": "Must Have", "pri_class": "priority-must",
        "sprint": "Sprint 3", "status": "Completed"
    }
}

def render_card(s):
    return f"""
    <div class="card">
        <div class="card-top">
            <span class="card-id">{s['id']}</span>
            <span class="priority-tag {s['pri_class']}">{s['priority']}</span>
        </div>
        <div class="epic-tag {s['epic_class']}">{s['epic']}</div>
        <div class="card-title">{s['title']}</div>
        <div class="card-desc">{s['statement']}</div>
        <div class="card-footer">
            <span class="card-points">{s['points']}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="card-status">Done</span>
                <div class="avatar" title="Academic Team">AT</div>
            </div>
        </div>
    </div>
    """

# 1. Fig 1.1 Full Backlog Board
html_fig_1_1 = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fig 1.1 - Full Backlog Board (All 12 User Stories)</title>
    <style>{SHARED_CSS}</style>
</head>
<body>
    <div class="header">
        <div class="project-title">
            <div class="project-icon">V</div>
            <div>
                <div class="project-name">VIVA SEDSS - Comprehensive Product Backlog</div>
                <div class="project-subtitle">Smart E-Commerce Decision Support System • Project Key: SEDSS</div>
            </div>
        </div>
        <div class="meta-badges">
            <div class="meta-badge"><span style="color: #64B5F6;">●</span> 12 Total Stories</div>
            <div class="meta-badge"><span style="color: #FFB74D;">●</span> 74 Story Points</div>
            <div class="meta-badge active"><span style="color: var(--neon-green);">✓</span> All Sprints Completed</div>
        </div>
    </div>

    <div class="sprint-summary-bar">
        <div class="sprint-info-left">
            <div>
                <div class="sprint-name">Complete Product Lifecycle Backlog (Sprint 1, 2, & 3)</div>
                <div class="sprint-dates">Agile Scope: Storefront Purchasing, Logistics Fulfillment, and MIS Decision Analytics</div>
            </div>
        </div>
        <div class="sprint-stats">
            <div class="stat-item">
                <div class="stat-val">100%</div>
                <div class="stat-lbl">Completion Rate</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">3 / 3</div>
                <div class="stat-lbl">Sprints Delivered</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">74 / 74</div>
                <div class="stat-lbl">Points Accepted</div>
            </div>
        </div>
    </div>

    <div class="kanban-grid-full">
        <!-- Sprint 1 Column -->
        <div class="column">
            <div class="col-header">
                <div class="col-title" style="color: #64B5F6;">
                    <span>●</span> Sprint 1: Customer Storefront
                </div>
                <span class="col-count">4 Stories (24 pts)</span>
            </div>
            <div class="card-stack">
                {render_card(STORIES['US-01'])}
                {render_card(STORIES['US-02'])}
                {render_card(STORIES['US-03'])}
                {render_card(STORIES['US-04'])}
            </div>
        </div>

        <!-- Sprint 2 Column -->
        <div class="column">
            <div class="col-header">
                <div class="col-title" style="color: #81C784;">
                    <span>●</span> Sprint 2: MIS Logistics & Admin
                </div>
                <span class="col-count">4 Stories (24 pts)</span>
            </div>
            <div class="card-stack">
                {render_card(STORIES['US-05'])}
                {render_card(STORIES['US-07'])}
                {render_card(STORIES['US-08'])}
                {render_card(STORIES['US-09'])}
            </div>
        </div>

        <!-- Sprint 3 Column -->
        <div class="column">
            <div class="col-header">
                <div class="col-title" style="color: #BA68C8;">
                    <span>●</span> Sprint 3: DSS Analytics & Reports
                </div>
                <span class="col-count">4 Stories (26 pts)</span>
            </div>
            <div class="card-stack">
                {render_card(STORIES['US-06'])}
                {render_card(STORIES['US-10'])}
                {render_card(STORIES['US-11'])}
                {render_card(STORIES['US-12'])}
            </div>
        </div>
    </div>
</body>
</html>
"""

# Helper function for sprint board with workflow columns
def make_sprint_board_html(fig_num, sprint_title, sprint_dates, story_keys, total_pts):
    s_cards = [STORIES[k] for k in story_keys]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fig {fig_num} - {sprint_title}</title>
    <style>{SHARED_CSS}</style>
</head>
<body>
    <div class="header">
        <div class="project-title">
            <div class="project-icon">V</div>
            <div>
                <div class="project-name">VIVA SEDSS - Active Sprint Execution Board</div>
                <div class="project-subtitle">Agile Board View • Sprint Key: {sprint_title.split(':')[0]} • Final Review</div>
            </div>
        </div>
        <div class="meta-badges">
            <div class="meta-badge"><span style="color: #64B5F6;">●</span> 4 Sprint Stories</div>
            <div class="meta-badge"><span style="color: #FFB74D;">●</span> {total_pts} Story Points</div>
            <div class="meta-badge active"><span style="color: var(--neon-green);">✓</span> Sprint Status: CLOSED</div>
        </div>
    </div>

    <div class="sprint-summary-bar">
        <div class="sprint-info-left">
            <div>
                <div class="sprint-name">{sprint_title}</div>
                <div class="sprint-dates">Iteration Window: {sprint_dates} • Velocity Target: {total_pts} pts</div>
            </div>
        </div>
        <div class="sprint-stats">
            <div class="stat-item">
                <div class="stat-val">100%</div>
                <div class="stat-lbl">Sprint Burn-Down</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">0</div>
                <div class="stat-lbl">Blockers</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">{total_pts} / {total_pts}</div>
                <div class="stat-lbl">Points Accepted</div>
            </div>
        </div>
    </div>

    <div class="kanban-grid">
        <!-- To Do -->
        <div class="column">
            <div class="col-header">
                <div class="col-title">To Do / Backlog</div>
                <span class="col-count">0</span>
            </div>
            <div class="card-stack" style="align-items: center; justify-content: center; border: 2px dashed #202F3E; border-radius: 8px;">
                <span style="font-size: 12px; color: #546E7A;">No pending tasks</span>
            </div>
        </div>

        <!-- In Progress -->
        <div class="column">
            <div class="col-header">
                <div class="col-title">In Development</div>
                <span class="col-count">0</span>
            </div>
            <div class="card-stack" style="align-items: center; justify-content: center; border: 2px dashed #202F3E; border-radius: 8px;">
                <span style="font-size: 12px; color: #546E7A;">All development complete</span>
            </div>
        </div>

        <!-- Code Review -->
        <div class="column">
            <div class="col-header">
                <div class="col-title">Testing & QA</div>
                <span class="col-count">0</span>
            </div>
            <div class="card-stack" style="align-items: center; justify-content: center; border: 2px dashed #202F3E; border-radius: 8px;">
                <span style="font-size: 12px; color: #546E7A;">All test suites passed</span>
            </div>
        </div>

        <!-- Done / Accepted -->
        <div class="column" style="border-color: rgba(0,245,155,0.3); background: rgba(0,245,155,0.02);">
            <div class="col-header">
                <div class="col-title" style="color: var(--neon-green);">
                    <span>✓</span> Done & Accepted
                </div>
                <span class="col-count" style="background: rgba(0,245,155,0.2); color: var(--neon-green);">{len(s_cards)}</span>
            </div>
            <div class="card-stack">
                {"".join(render_card(c) for c in s_cards)}
            </div>
        </div>
    </div>
</body>
</html>
"""

# Fig 2.1 Sprint 1
html_fig_2_1 = make_sprint_board_html("2.1", "Sprint 1: Storefront & Customer Purchasing Engine", "Oct 15 - Oct 29 (2 Weeks)", ["US-01", "US-02", "US-03", "US-04"], 24)

# Fig 2.6 Sprint 2
html_fig_2_6 = make_sprint_board_html("2.6", "Sprint 2: MIS Logistics & Admin Management Portal", "Oct 30 - Nov 13 (2 Weeks)", ["US-05", "US-07", "US-08", "US-09"], 24)

# Fig 2.11 Sprint 3
html_fig_2_11 = make_sprint_board_html("2.11", "Sprint 3: MIS Decision Support System (DSS) & Reports", "Nov 14 - Nov 16 (Sprint Final)", ["US-06", "US-10", "US-11", "US-12"], 26)

with open('d:/file/mis/smart_ecommerce/report_screenshots/boards/board_full_backlog.html', 'w', encoding='utf-8') as f:
    f.write(html_fig_1_1)

with open('d:/file/mis/smart_ecommerce/report_screenshots/boards/board_sprint_1.html', 'w', encoding='utf-8') as f:
    f.write(html_fig_2_1)

with open('d:/file/mis/smart_ecommerce/report_screenshots/boards/board_sprint_2.html', 'w', encoding='utf-8') as f:
    f.write(html_fig_2_6)

with open('d:/file/mis/smart_ecommerce/report_screenshots/boards/board_sprint_3.html', 'w', encoding='utf-8') as f:
    f.write(html_fig_2_11)

print("Generated 4 Agile Board HTML templates successfully!")
