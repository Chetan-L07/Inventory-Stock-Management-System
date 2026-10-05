import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io
import os

# ---------------------------------------------------------
# PAGE CONFIGURATION & THEME STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Inventory Stock Pro",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for dark glassmorphism aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
    color: #ffffff;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #080c14 !important;
    border-right: 1px solid #1e293b;
}

/* Glassmorphism Metric Cards */
.metric-box {
    background: rgba(30, 41, 59, 0.55);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 22px 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, border-color 0.2s ease;
    margin-bottom: 12px;
}

.metric-box:hover {
    transform: translateY(-3px);
    border-color: #ffffff;
}

.metric-icon {
    font-size: 1.8rem;
    margin-bottom: 8px;
}

.metric-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
}

.metric-subtitle {
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 6px;
}

.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
.text-rose { color: #f87171; }
.text-indigo { color: #818cf8; }

/* Status Badges */
.badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
}
.badge-success { background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-warning { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-danger { background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-info { background: rgba(99, 102, 241, 0.18); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
.badge-neutral { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }

/* Custom Section Card */
.content-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

/* Client Avatar & Card Styling */
.client-avatar {
    width: 46px;
    height: 46px;
    min-width: 46px;
    border-radius: 14px;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.15rem;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.client-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(10px);
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: all 0.2s ease-in-out;
}

.client-card:hover {
    border-color: rgba(99, 102, 241, 0.45);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

/* User Card Sidebar */
.user-profile-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 20px;
}

/* Alert Banners */
.alert-banner {
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.alert-warning {
    background: rgba(245, 158, 11, 0.1);
    border-left: 4px solid #f59e0b;
    color: #fef3c7;
}

/* Hide default streamlit headers / footers padding adjustments */
header[data-testid="stHeader"] {
    background: transparent !important;
}

div.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GLOBAL STATE & CONSTANTS
# ---------------------------------------------------------
BASE_URL = os.getenv("FLASK_API_URL", "http://127.0.0.1:5001/api/v1")

if "user" not in st.session_state:
    st.session_state["user"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ---------------------------------------------------------
# API CLIENT UTILITIES
# ---------------------------------------------------------
def api_health_check():
    """Verify backend API reachability"""
    try:
        res = requests.get(f"{BASE_URL.replace('/api/v1', '')}/", timeout=3)
        return res.status_code == 200
    except Exception:
        return False

def api_get(endpoint):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if res.status_code == 200:
            return res.json()
        return {"status": "Error", "message": f"Server error ({res.status_code})"}
    except requests.exceptions.ConnectionError:
        return {"status": "Error", "message": "Cannot connect to Flask Backend API. Make sure backend app.py is running on port 5001!"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

def api_post(endpoint, json_payload):
    try:
        res = requests.post(f"{BASE_URL}{endpoint}", json=json_payload, timeout=5)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"status": "Error", "message": "Backend server disconnected"}, 503
    except Exception as e:
        return {"status": "Error", "message": str(e)}, 500

def api_put(endpoint, json_payload):
    try:
        res = requests.put(f"{BASE_URL}{endpoint}", json=json_payload, timeout=5)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"status": "Error", "message": "Backend server disconnected"}, 503
    except Exception as e:
        return {"status": "Error", "message": str(e)}, 500

def api_delete(endpoint):
    try:
        res = requests.delete(f"{BASE_URL}{endpoint}", timeout=5)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"status": "Error", "message": "Backend server disconnected"}, 503
    except Exception as e:
        return {"status": "Error", "message": str(e)}, 500


# ---------------------------------------------------------
# SIDEBAR NAVIGATION & PROFILE
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <div style="background: #6366f1; padding: 10px; border-radius: 12px; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; font-size: 22px;">
                📦
            </div>
            <div>
                <h3 style="margin:0; font-size: 1.15rem; font-weight: 800; color: #ffffff;">Nagu Stock</h3>
                <span style="font-size: 0.75rem; color: #ffffff; font-weight: 600;">Inventory Pro v1.0</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Backend Status Indicator
    is_online = api_health_check()
    if is_online:
        st.markdown('<span class="badge badge-success">● API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-danger">● API Connecting / Offline</span>', unsafe_allow_html=True)
        st.caption(f"Target: `{BASE_URL}`")
        st.caption("*(If on free hosting like Render, the backend may take 30-50s to wake up from idle)*")
        if st.button("🔄 Retry Connection", key="btn_retry_conn"):
            st.rerun()

    st.markdown("<hr style='border-color: #1e293b; margin: 16px 0;'>", unsafe_allow_html=True)

    # User Auth state in sidebar
    if st.session_state["logged_in"] and st.session_state["user"]:
        user = st.session_state["user"]
        st.markdown(f"""
            <div class="user-profile-card">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #ffffff; font-weight: 700;">Active Account</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-top: 2px;">{user.get('name', 'User')}</div>
                <div style="font-size: 0.8rem; color:#ffffff;">{user.get('email', '')}</div>
                <div style="margin-top: 8px;">
                    <span class="badge badge-info">{user.get('role', 'user').upper()}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["logged_in"] = False
            st.toast("Logged out successfully", icon="👋")
            st.rerun()
    else:
        st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.4); border-radius: 10px; padding: 12px; margin-bottom: 15px; border: 1px solid #1e293b;">
                <div style="font-size: 0.85rem; color: #cbd5e1;">Sign in to access restricted admin actions and management tools.</div>
            </div>
        """, unsafe_allow_html=True)

    # Navigation Menu
    st.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;'>Navigation</div>", unsafe_allow_html=True)
    
    menu_choice = st.radio(
        "Menu",
        options=[
            "📊 Dashboard",
            "📦 Product Inventory",
            "📁 Categories",
            "👥 Client Management",
            "⚠️ Stock Alerts",
            "📈 Financial Analytics",
            "🔐 Authentication",
            "⚙️ System Settings"
        ],
        label_visibility="collapsed"
    )

# ---------------------------------------------------------
# AUTHENTICATION SCREEN
# ---------------------------------------------------------
if menu_choice == "🔐 Authentication":
    st.title("🔐 Account Access")
    st.caption("Sign in to your account or register a new user for the inventory system.")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Register New User"])
        
        with tab_login:
            st.markdown("### Welcome Back")
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Sign In to Dashboard", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please fill in both email and password fields.")
                else:
                    with st.spinner("Authenticating..."):
                        resp, status = api_post("/auth/login", {"email": login_email, "password": login_password})
                        if status == 200 and resp.get("status") == "Success":
                            st.session_state["user"] = resp.get("data")
                            st.session_state["logged_in"] = True
                            st.success(f"Welcome back, {st.session_state['user']['name']}!")
                            st.toast("Login successful", icon="🎉")
                            st.rerun()
                        else:
                            st.error(resp.get("message", "Invalid login credentials"))

        with tab_register:
            st.markdown("### Create an Account")
            reg_name = st.text_input("Full Name / Username", key="reg_name")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_role = st.selectbox("Assign Role", ["user", "manager", "admin", "nagu_bhai"])
            
            if st.button("Register Account", use_container_width=True):
                if not reg_name or not reg_email or not reg_pass:
                    st.error("All fields are required for registration.")
                else:
                    with st.spinner("Creating account..."):
                        payload = {
                            "user_name": reg_name,
                            "email": reg_email,
                            "password": reg_pass,
                            "role": reg_role
                        }
                        resp, status = api_post("/auth/register", payload)
                        if status in [200, 201] and resp.get("status") == "Success":
                            st.success("Account created successfully! You can now log in.")
                            st.toast("Registration complete!", icon="✅")
                        else:
                            st.error(resp.get("message", "Registration failed."))

    with col2:
        st.markdown("""
            <div class="content-card" style="height: 100%;">
                <h3>🚀 Streamlined Stock Management</h3>
                <p style="color: #94a3b8;">Manage your inventory seamlessly with real-time tracking, profit metrics, low stock alerts, and automated reporting.</p>
                <br>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: rgba(16,185,129,0.2); color: #34d399; padding: 6px; border-radius: 8px;">✓</span>
                        <span>Track Stock Levels & Barcodes</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: rgba(99,102,241,0.2); color: #818cf8; padding: 6px; border-radius: 8px;">✓</span>
                        <span>Real-Time Profit Margin Calculation</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: rgba(245,158,11,0.2); color: #fbbf24; padding: 6px; border-radius: 8px;">✓</span>
                        <span>Automated Low-Stock Threshold Alerts</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: rgba(168,85,247,0.2); color: #c084fc; padding: 6px; border-radius: 8px;">✓</span>
                        <span>Manage Clients, Corporate Billing & GST</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# DASHBOARD OVERVIEW
# ---------------------------------------------------------
elif menu_choice == "📊 Dashboard":
    st.title("📊 Executive Dashboard")
    st.caption("Live overview of stock metrics, category distribution, clients, and inventory warnings.")

    # Fetch data
    products_res = api_get("/products")
    categories_res = api_get("/categories")
    clients_res = api_get("/client/read_client")

    products = products_res.get("data", []) if isinstance(products_res, dict) and products_res.get("status") == "Success" else []
    categories = categories_res.get("data", []) if isinstance(categories_res, dict) and categories_res.get("status") == "Success" else []
    clients = clients_res.get("data", []) if isinstance(clients_res, dict) and clients_res.get("status") == "Success" else []

    if not is_online:
        st.warning("⚠️ Backend API server is offline. Showing empty/cached dashboard state.")

    # Calculate metrics
    total_products = len(products)
    total_categories = len(categories)
    total_clients = len(clients)
    active_clients = len([c for c in clients if (c.get("status") or "").lower() == "active"])
    
    total_cost_val = sum([p.get("cost_price", 0) * p.get("stock_quantity", 0) for p in products])
    total_retail_val = sum([p.get("selling_price", 0) * p.get("stock_quantity", 0) for p in products])
    
    low_stock_items = [p for p in products if p.get("stock_quantity", 0) <= p.get("min_stock_level", 5)]
    out_of_stock_items = [p for p in products if p.get("stock_quantity", 0) == 0]

    # Metric Cards Row
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">📦</div>
                <div class="metric-title">Total Products</div>
                <div class="metric-value">{total_products}</div>
                <div class="metric-subtitle text-indigo">{total_categories} Categories • {total_clients} Clients</div>
            </div>
        """, unsafe_allow_html=True)

    with mcol2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">💵</div>
                <div class="metric-title">Inventory Valuation</div>
                <div class="metric-value">₹{total_cost_val:,.2f}</div>
                <div class="metric-subtitle text-emerald">Retail Value: ₹{total_retail_val:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with mcol3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">⚠️</div>
                <div class="metric-title">Low Stock Alerts</div>
                <div class="metric-value">{len(low_stock_items)}</div>
                <div class="metric-subtitle text-amber">{len(out_of_stock_items)} Out of Stock</div>
            </div>
        """, unsafe_allow_html=True)

    with mcol4:
        potential_profit = total_retail_val - total_cost_val
        margin_pct = ((potential_profit / total_retail_val) * 100) if total_retail_val > 0 else 0
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">📈</div>
                <div class="metric-title">Potential Profit</div>
                <div class="metric-value">₹{potential_profit:,.2f}</div>
                <div class="metric-subtitle text-emerald">Avg Margin: {margin_pct:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts and Low Stock Section
    c1, c2 = st.columns([1.6, 1])

    with c1:
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700;'>📊 Stock Level by Product</h3>", unsafe_allow_html=True)
        if products:
            df_prod = pd.DataFrame(products)
            chart_data = df_prod[["name", "stock_quantity", "min_stock_level"]].set_index("name")
            st.bar_chart(chart_data, color=["#6366f1", "#f59e0b"])
        else:
            st.info("No product data available yet. Add products to see stock visualizations.")

    with c2:
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700;'>⚠️ Critical Stock Warnings</h3>", unsafe_allow_html=True)
        if low_stock_items:
            for item in low_stock_items[:6]:
                status_class = "badge-danger" if item["stock_quantity"] == 0 else "badge-warning"
                status_text = "OUT OF STOCK" if item["stock_quantity"] == 0 else "LOW STOCK"
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid {'#ef4444' if item['stock_quantity'] == 0 else '#f59e0b'}; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 700; font-size: 0.9rem;">{item['name']}</div>
                            <div style="font-size: 0.78rem; color: #94a3b8;">Category: {item.get('category_name') or 'Unassigned'}</div>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge {status_class}">{status_text}</span>
                            <div style="font-size: 0.8rem; margin-top: 4px; color: #cbd5e1;"><b>{item['stock_quantity']}</b> / {item['min_stock_level']} {item['unit']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ All product stock levels are healthy!")

    st.markdown("<hr style='border-color: #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)

    # Categories and Clients Summary Section (2-Columns)
    row_cat_col, row_client_col = st.columns([1.2, 1.2])

    with row_cat_col:
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700;'>📁 Category Distribution</h3>", unsafe_allow_html=True)
        if categories:
            df_cat = pd.DataFrame(categories)
            st.dataframe(
                df_cat[["id", "name", "total_products", "created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No categories registered in the database.")

    with row_client_col:
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700;'>👥 Recent Client Overview</h3>", unsafe_allow_html=True)
        if clients:
            for cl in clients[:4]:
                cl_status = (cl.get("status") or "active").lower()
                status_b = '<span class="badge badge-success">ACTIVE</span>' if cl_status == "active" else '<span class="badge badge-danger">INACTIVE</span>'
                comp_tag = f" • <b>{cl['company_name']}</b>" if cl.get("company_name") else ""
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid #1e293b; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">{cl['name']}{comp_tag}</div>
                            <div style="font-size: 0.78rem; color: #94a3b8;">📞 {cl.get('phone', 'N/A')} &nbsp;|&nbsp; 📍 {cl.get('city') or 'Unknown City'}</div>
                        </div>
                        <div>
                            {status_b}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            if len(clients) > 4:
                st.caption(f"*Showing 4 of {len(clients)} registered clients. Go to '👥 Client Management' for full details.*")
        else:
            st.info("No clients registered yet. Add clients in '👥 Client Management'.")


# ---------------------------------------------------------
# PRODUCT INVENTORY MANAGEMENT
# ---------------------------------------------------------
elif menu_choice == "📦 Product Inventory":
    st.title("📦 Product Inventory Management")
    st.caption("Add, search, edit, update stock levels, and remove items from inventory.")

    products_res = api_get("/products")
    categories_res = api_get("/categories")
    
    products = products_res.get("data", []) if isinstance(products_res, dict) and products_res.get("status") == "Success" else []
    categories = categories_res.get("data", []) if isinstance(categories_res, dict) and categories_res.get("status") == "Success" else []
    
    cat_mapping = {c["name"]: c["id"] for c in categories}
    cat_names = ["All Categories"] + list(cat_mapping.keys())

    # Add Product Expander / Modal
    with st.expander("➕ **Add New Product to Stock**", expanded=False):
        st.markdown("<div style='font-weight: 600; margin-bottom: 10px;'>Enter Product Specification Details</div>", unsafe_allow_html=True)
        with st.form("add_product_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                prod_name = st.text_input("Product Title *", placeholder="e.g. Wireless Mouse")
                prod_barcode = st.text_input("Barcode / UPC", placeholder="e.g. 890123456789")
            with col_b:
                selected_cat = st.selectbox("Category", list(cat_mapping.keys()) if cat_mapping else ["Unassigned"])
                prod_unit = st.text_input("Unit", value="pcs")
            with col_c:
                cost_p = st.number_input("Cost Price (₹) *", min_value=0.0, step=0.5, value=10.0)
                sell_p = st.number_input("Selling Price (₹) *", min_value=0.0, step=0.5, value=15.0)

            col_d, col_e = st.columns(2)
            with col_d:
                stock_qty = st.number_input("Initial Stock Quantity", min_value=0, value=20, step=1)
            with col_e:
                min_stock = st.number_input("Minimum Stock Warning Threshold", min_value=1, value=5, step=1)

            submit_add = st.form_submit_button("🚀 Save Product", type="primary", use_container_width=True)

            if submit_add:
                if not prod_name:
                    st.error("Product title is required!")
                elif sell_p < cost_p:
                    st.warning("Warning: Selling price is less than cost price (Negative Margin).")
                else:
                    cat_id = cat_mapping.get(selected_cat) if cat_mapping else None
                    payload = {
                        "name": prod_name.strip(),
                        "barcode": prod_barcode.strip() if prod_barcode else None,
                        "category_id": cat_id,
                        "cost_price": cost_p,
                        "selling_price": sell_p,
                        "stock_quantity": stock_qty,
                        "min_stock_level": min_stock,
                        "unit": prod_unit.strip()
                    }
                    resp, status = api_post("/products", payload)
                    if status in [200, 201] and resp.get("status") == "Success":
                        st.success(f"Product '{prod_name}' added successfully!")
                        st.toast("Product created", icon="📦")
                        st.rerun()
                    else:
                        st.error(resp.get("message", "Failed to add product."))

    st.markdown("<hr style='border-color: #1e293b; margin: 16px 0;'>", unsafe_allow_html=True)

    # Search & Filter Controls
    fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
    with fcol1:
        search_query = st.text_input("🔍 Search Products", placeholder="Search by name or barcode...", label_visibility="collapsed")
    with fcol2:
        filter_cat = st.selectbox("Category Filter", cat_names, label_visibility="collapsed")
    with fcol3:
        filter_stock = st.selectbox("Stock Status", ["All Items", "In Stock", "Low Stock (<= Min)", "Out of Stock"], label_visibility="collapsed")

    # Filter Logic
    filtered_products = products
    if search_query:
        sq = search_query.lower()
        filtered_products = [p for p in filtered_products if sq in p["name"].lower() or (p.get("barcode") and sq in p["barcode"].lower())]
    if filter_cat != "All Categories":
        filtered_products = [p for p in filtered_products if p.get("category_name") == filter_cat]
    if filter_stock == "In Stock":
        filtered_products = [p for p in filtered_products if p.get("stock_quantity", 0) > p.get("min_stock_level", 5)]
    elif filter_stock == "Low Stock (<= Min)":
        filtered_products = [p for p in filtered_products if 0 < p.get("stock_quantity", 0) <= p.get("min_stock_level", 5)]
    elif filter_stock == "Out of Stock":
        filtered_products = [p for p in filtered_products if p.get("stock_quantity", 0) == 0]

    st.markdown(f"**Showing {len(filtered_products)} of {len(products)} products**")

    # Display Interactive Product Cards / List
    if filtered_products:
        for prod in filtered_products:
            stock = prod.get("stock_quantity", 0)
            min_lvl = prod.get("min_stock_level", 5)
            
            if stock == 0:
                badge_html = '<span class="badge badge-danger">OUT OF STOCK</span>'
            elif stock <= min_lvl:
                badge_html = '<span class="badge badge-warning">LOW STOCK</span>'
            else:
                badge_html = '<span class="badge badge-success">IN STOCK</span>'

            margin_val = prod["selling_price"] - prod["cost_price"]
            margin_pct = (margin_val / prod["selling_price"] * 100) if prod["selling_price"] > 0 else 0

            with st.container():
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <h4 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #ffffff;">{prod['name']}</h4>
                                    {badge_html}
                                </div>
                                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
                                    Category: <b>{prod.get('category_name') or 'Unassigned'}</b> &nbsp;|&nbsp; Barcode: <code>{prod.get('barcode') or 'N/A'}</code>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.15rem; font-weight: 800; color: #34d399;">₹{prod['selling_price']:.2f} <span style="font-size: 0.75rem; color: #94a3b8;">/{prod['unit']}</span></div>
                                <div style="font-size: 0.78rem; color: #94a3b8;">Cost: ₹{prod['cost_price']:.2f} (Profit: +₹{margin_val:.2f} | {margin_pct:.0f}%)</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Edit & Delete Action row in nested columns
                ec1, ec2, ec3, ec4 = st.columns([2, 1, 1, 1])
                with ec1:
                    st.caption(f"Current Stock: **{stock} {prod['unit']}** (Min threshold: {min_lvl})")
                with ec2:
                    # Quick Restock button
                    if st.button(f"➕ Quick +5 Stock", key=f"restock_{prod['id']}"):
                        new_qty = stock + 5
                        api_put(f"/products/{prod['id']}", {"stock_quantity": new_qty})
                        st.toast(f"Updated {prod['name']} stock to {new_qty}", icon="📈")
                        st.rerun()
                with ec3:
                    # Edit expander toggle
                    with st.popover("✏️ Edit Details"):
                        st.markdown(f"**Edit {prod['name']}**")
                        edit_name = st.text_input("Name", value=prod['name'], key=f"ename_{prod['id']}")
                        edit_cost = st.number_input("Cost (₹)", value=float(prod['cost_price']), key=f"ecost_{prod['id']}")
                        edit_sell = st.number_input("Selling (₹)", value=float(prod['selling_price']), key=f"esell_{prod['id']}")
                        edit_qty = st.number_input("Stock Qty", value=int(prod['stock_quantity']), key=f"eqty_{prod['id']}")
                        edit_min = st.number_input("Min Level", value=int(prod['min_stock_level']), key=f"emin_{prod['id']}")
                        
                        if st.button("Save Changes", key=f"save_{prod['id']}", type="primary"):
                            up_payload = {
                                "name": edit_name,
                                "cost_price": edit_cost,
                                "selling_price": edit_sell,
                                "stock_quantity": edit_qty,
                                "min_stock_level": edit_min
                            }
                            resp, st_code = api_put(f"/products/{prod['id']}", up_payload)
                            if st_code == 200:
                                st.success("Updated successfully!")
                                st.rerun()
                            else:
                                st.error(resp.get("message", "Error updating"))
                with ec4:
                    if st.button("🗑️ Delete", key=f"del_{prod['id']}", type="secondary"):
                        resp, st_code = api_delete(f"/products/{prod['id']}")
                        if st_code == 200:
                            st.toast(f"Deleted product {prod['name']}", icon="🗑️")
                            st.rerun()
                        else:
                            st.error(resp.get("message", "Error deleting"))

                st.markdown("<hr style='border-color: #1e293b; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
    else:
        st.info("No matching products found in inventory.")


# ---------------------------------------------------------
# CATEGORY MANAGEMENT
# ---------------------------------------------------------
elif menu_choice == "📁 Categories":
    st.title("📁 Category Management")
    st.caption("Organize your products into custom inventory categories.")

    categories_res = api_get("/categories")
    categories = categories_res.get("data", []) if isinstance(categories_res, dict) and categories_res.get("status") == "Success" else []

    col_cat_list, col_cat_add = st.columns([1.5, 1])

    with col_cat_add:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("### ➕ Create Category")
        cat_name_input = st.text_input("Category Title *", placeholder="e.g. Electronics, Snacks, Dairy")
        if st.button("Create Category", type="primary", use_container_width=True):
            if not cat_name_input.strip():
                st.error("Category title cannot be empty.")
            else:
                resp, status = api_post("/categories", {"name": cat_name_input.strip()})
                if status in [200, 201] and resp.get("status") == "Success":
                    st.success(f"Category '{cat_name_input}' created!")
                    st.toast("Category added", icon="📁")
                    st.rerun()
                else:
                    st.error(resp.get("message", "Failed to create category."))
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cat_list:
        st.markdown("### Existing Categories")
        if categories:
            for cat in categories:
                with st.container():
                    st.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid #1e293b; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 700; font-size: 1rem; color: #ffffff;">{cat['name']}</div>
                                <div style="font-size: 0.8rem; color: #94a3b8;">Total Products: <b style="color:#818cf8;">{cat.get('total_products', 0)}</b></div>
                            </div>
                            <div style="font-size: 0.75rem; color: #64748b;">
                                Created: {cat.get('created_at', '')[:10]}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    c_edit, c_del = st.columns([3, 1])
                    with c_edit:
                        with st.popover(f"✏️ Rename '{cat['name']}'"):
                            new_c_name = st.text_input("New Name", value=cat['name'], key=f"c_ren_{cat['id']}")
                            if st.button("Save", key=f"c_save_{cat['id']}", type="primary"):
                                api_put(f"/categories/{cat['id']}", {"name": new_c_name})
                                st.rerun()
                    with c_del:
                        if st.button("🗑️ Delete", key=f"c_del_{cat['id']}"):
                            resp, code = api_delete(f"/categories/{cat['id']}")
                            if code == 200:
                                st.toast("Category deleted", icon="🗑️")
                                st.rerun()
                            else:
                                st.error(resp.get("message", "Cannot delete category."))
        else:
            st.info("No categories registered yet. Use the form on the right to add one.")


# ---------------------------------------------------------
# STOCK ALERTS & REORDER PLANNER
# ---------------------------------------------------------
elif menu_choice == "⚠️ Stock Alerts":
    st.title("⚠️ Low Stock & Reorder Planner")
    st.caption("Monitor items running below safety thresholds and plan stock replenishment.")

    products_res = api_get("/products")
    products = products_res.get("data", []) if isinstance(products_res, dict) and products_res.get("status") == "Success" else []

    low_stock = [p for p in products if p.get("stock_quantity", 0) <= p.get("min_stock_level", 5)]

    if low_stock:
        st.markdown(f"""
            <div class="alert-banner alert-warning">
                <span style="font-size: 1.5rem;">⚠️</span>
                <div>
                    <b>{len(low_stock)} Items Require Immediate Reordering</b>
                    <div style="font-size: 0.85rem;">The items listed below are at or below their designated minimum threshold level.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        reorder_data = []
        for p in low_stock:
            defic = max(0, (p["min_stock_level"] * 2) - p["stock_quantity"]) # recommended reorder qty
            reorder_cost = defic * p["cost_price"]
            reorder_data.append({
                "Product Name": p["name"],
                "Category": p.get("category_name") or "Unassigned",
                "Current Stock": f"{p['stock_quantity']} {p['unit']}",
                "Min Threshold": f"{p['min_stock_level']} {p['unit']}",
                "Suggested Restock Qty": f"{defic} {p['unit']}",
                "Est Restock Cost": f"${reorder_cost:.2f}"
            })

        df_reorder = pd.DataFrame(reorder_data)
        st.table(df_reorder)
    else:
        st.success("🎉 Great job! No products are currently below their minimum stock thresholds.")


# ---------------------------------------------------------
# FINANCIAL ANALYTICS & REPORTS
# ---------------------------------------------------------
elif menu_choice == "📈 Financial Analytics":
    st.title("📈 Financial Analytics & Reports")
    st.caption("Export inventory summaries and review financial valuation analysis.")

    products_res = api_get("/products")
    products = products_res.get("data", []) if isinstance(products_res, dict) and products_res.get("status") == "Success" else []

    if products:
        df = pd.DataFrame(products)
        df["total_cost_value"] = df["cost_price"] * df["stock_quantity"]
        df["total_retail_value"] = df["selling_price"] * df["stock_quantity"]
        df["potential_profit"] = df["total_retail_value"] - df["total_cost_value"]

        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Total Asset Cost Value", f"₹{df['total_cost_value'].sum():,.2f}")
        with r2:
            st.metric("Total Projected Revenue", f"₹{df['total_retail_value'].sum():,.2f}")
        with r3:
            st.metric("Total Potential Net Profit", f"₹{df['potential_profit'].sum():,.2f}")

        st.markdown("<hr style='border-color: #1e293b; margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown("### 📄 Export Reports")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            # CSV Export
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Complete Inventory Report (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"inventory_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_exp2:
            # PDF summary text generator
            pdf_summary = f"""INVENTORY STOCK MANAGEMENT REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
--------------------------------------------------
Total Unique Products: {len(df)}
Total Stock Valuation (Cost): ₹{df['total_cost_value'].sum():,.2f}
Total Potential Revenue: ₹{df['total_retail_value'].sum():,.2f}
Estimated Net Profit: ₹{df['potential_profit'].sum():,.2f}

PRODUCT LIST:
"""
            for _, r in df.iterrows():
                pdf_summary += f"- {r['name']} | Qty: {r['stock_quantity']} {r['unit']} | Cost: ₹{r['cost_price']} | Sell: ${r['selling_price']}\n"

            st.download_button(
                label="📄 Download Summary Report (.txt/.pdf)",
                data=pdf_summary,
                file_name=f"inventory_summary_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Detailed Inventory Valuation Data")
        st.dataframe(
            df[["name", "category_name", "stock_quantity", "unit", "cost_price", "selling_price", "total_cost_value", "total_retail_value", "potential_profit"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No product data available for financial analysis.")


# ---------------------------------------------------------
# CLIENT MANAGEMENT
# ---------------------------------------------------------
elif menu_choice == "👥 Client Management":
    st.title("👥 Client & Customer Management")
    st.caption("Manage corporate partners, retail buyers, contact directories, and billing profiles.")

    # Fetch clients data
    clients_res = api_get("/client/read_client")
    clients = clients_res.get("data", []) if isinstance(clients_res, dict) and clients_res.get("status") == "Success" else []

    if not is_online:
        st.warning("⚠️ Backend API server is offline. Showing empty/cached client directory.")

    # Client KPI Metrics
    total_clients = len(clients)
    active_clients = len([c for c in clients if (c.get("status") or "").lower() == "active"])
    inactive_clients = total_clients - active_clients
    gst_clients = len([c for c in clients if c.get("gst_number") or c.get("company_name")])
    unique_cities = len(set([c.get("city").strip().title() for c in clients if c.get("city") and c.get("city").strip()]))

    # Top KPI Metrics Row
    ckpi1, ckpi2, ckpi3, ckpi4 = st.columns(4)
    with ckpi1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">👥</div>
                <div class="metric-title">Total Clients</div>
                <div class="metric-value">{total_clients}</div>
                <div class="metric-subtitle text-indigo">{active_clients} Active Accounts</div>
            </div>
        """, unsafe_allow_html=True)

    with ckpi2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">🟢</div>
                <div class="metric-title">Active Customers</div>
                <div class="metric-value">{active_clients}</div>
                <div class="metric-subtitle text-emerald">{inactive_clients} Inactive</div>
            </div>
        """, unsafe_allow_html=True)

    with ckpi3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">🏢</div>
                <div class="metric-title">Corporate Accounts</div>
                <div class="metric-value">{gst_clients}</div>
                <div class="metric-subtitle text-amber">GST Registered / Business</div>
            </div>
        """, unsafe_allow_html=True)

    with ckpi4:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">📍</div>
                <div class="metric-title">Territory Reach</div>
                <div class="metric-value">{unique_cities}</div>
                <div class="metric-subtitle text-indigo">Cities & Regions</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Add Client Form in Expander
    with st.expander("➕ **Register New Client / Customer**", expanded=False):
        st.markdown("<div style='font-weight: 600; margin-bottom: 12px; color: #cbd5e1;'>Fill in Contact and Business Profile Details</div>", unsafe_allow_html=True)
        with st.form("add_client_form", clear_on_submit=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                c_name = st.text_input("Full Name *", placeholder="e.g. Rahul Sharma")
                c_phone = st.text_input("Phone Number *", placeholder="e.g. +91 9876543210")
            with col_c2:
                c_email = st.text_input("Email Address", placeholder="e.g. rahul@example.com")
                c_company = st.text_input("Company / Business Name", placeholder="e.g. Sharma Enterprises")
            with col_c3:
                c_gst = st.text_input("GST Number", placeholder="e.g. 27ABCDE1234F1Z5")
                c_status = st.selectbox("Customer Status", ["active", "inactive"])

            col_c4, col_c5, col_c6, col_c7 = st.columns([2, 1, 1, 1])
            with col_c4:
                c_address = st.text_input("Street / Area Address", placeholder="e.g. Shop 12, Main Market Road")
            with col_c5:
                c_city = st.text_input("City", placeholder="e.g. Pune")
            with col_c6:
                c_state = st.text_input("State", placeholder="e.g. Maharashtra")
            with col_c7:
                c_pincode = st.text_input("Pincode", placeholder="e.g. 411001")

            submit_client = st.form_submit_button("🚀 Register Client", type="primary", use_container_width=True)

            if submit_client:
                if not c_name.strip():
                    st.error("Client name is required!")
                elif not c_phone.strip():
                    st.error("Client phone number is required!")
                else:
                    payload = {
                        "name": c_name.strip(),
                        "phone": c_phone.strip(),
                        "email": c_email.strip() if c_email.strip() else None,
                        "company_name": c_company.strip() if c_company.strip() else None,
                        "gst_number": c_gst.strip() if c_gst.strip() else None,
                        "address": c_address.strip() if c_address.strip() else None,
                        "city": c_city.strip() if c_city.strip() else None,
                        "state": c_state.strip() if c_state.strip() else None,
                        "pincode": c_pincode.strip() if c_pincode.strip() else None,
                        "status": c_status
                    }
                    resp, status_code = api_post("/client/create_client", payload)
                    if status_code in [200, 201] and resp.get("status") == "Success":
                        st.success(f"Client '{c_name}' registered successfully!")
                        st.toast("Client registered", icon="👥")
                        st.rerun()
                    else:
                        st.error(resp.get("message", "Failed to add client."))

    st.markdown("<hr style='border-color: #1e293b; margin: 16px 0;'>", unsafe_allow_html=True)

    # Search & Filter Controls
    sf1, sf2, sf3, sf4 = st.columns([2, 1, 1, 1])
    with sf1:
        client_search_query = st.text_input("🔍 Search Clients", placeholder="Search by name, phone, email, company, or city...", label_visibility="collapsed")
    with sf2:
        status_filter = st.selectbox("Status Filter", ["All Status", "Active Only", "Inactive Only"], label_visibility="collapsed")
    with sf3:
        all_cities = sorted(list(set([c.get("city").strip().title() for c in clients if c.get("city") and c.get("city").strip()])))
        city_filter = st.selectbox("City Filter", ["All Cities"] + all_cities, label_visibility="collapsed")
    with sf4:
        view_mode = st.selectbox("Display View", ["🗂️ Client Cards", "📋 Table & CSV Export"], label_visibility="collapsed")

    # Filter Logic
    filtered_clients = clients
    if client_search_query:
        sq = client_search_query.lower()
        filtered_clients = [
            c for c in filtered_clients
            if (sq in (c.get("name") or "").lower() or
                sq in (c.get("phone") or "").lower() or
                sq in (c.get("email") or "").lower() or
                sq in (c.get("company_name") or "").lower() or
                sq in (c.get("city") or "").lower() or
                sq in (c.get("gst_number") or "").lower())
        ]

    if status_filter == "Active Only":
        filtered_clients = [c for c in filtered_clients if (c.get("status") or "").lower() == "active"]
    elif status_filter == "Inactive Only":
        filtered_clients = [c for c in filtered_clients if (c.get("status") or "").lower() != "active"]

    if city_filter != "All Cities":
        filtered_clients = [c for c in filtered_clients if (c.get("city") or "").strip().title() == city_filter]

    st.markdown(f"**Showing {len(filtered_clients)} of {len(clients)} clients**")

    # -------------------------------------------------------------
    # View 1: Interactive Client Cards
    # -------------------------------------------------------------
    if view_mode == "🗂️ Client Cards":
        if filtered_clients:
            for client in filtered_clients:
                cid = client["id"]
                c_name_val = client.get("name", "Unnamed Client")
                c_status_val = (client.get("status") or "active").lower()
                c_company_val = client.get("company_name")
                c_email_val = client.get("email")
                c_phone_val = client.get("phone", "N/A")
                c_gst_val = client.get("gst_number")
                c_city_val = client.get("city")
                c_state_val = client.get("state")
                c_pincode_val = client.get("pincode")
                c_address_val = client.get("address")

                # Initials for avatar
                initials = "".join([part[0].upper() for part in c_name_val.split()[:2]]) if c_name_val else "CL"
                status_badge = '<span class="badge badge-success">ACTIVE</span>' if c_status_val == "active" else '<span class="badge badge-danger">INACTIVE</span>'
                company_badge = f'<span class="badge badge-info">🏢 {c_company_val}</span>' if c_company_val else '<span class="badge badge-neutral">👤 Individual</span>'

                location_str = ", ".join([p for p in [c_city_val, c_state_val] if p])
                if c_pincode_val:
                    location_str += f" - {c_pincode_val}" if location_str else c_pincode_val
                if not location_str:
                    location_str = "No location specified"

                with st.container():
                    st.markdown(f"""
                        <div class="client-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                                <div style="display: flex; align-items: center; gap: 14px;">
                                    <div class="client-avatar">
                                        {initials}
                                    </div>
                                    <div>
                                        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                                            <h4 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #ffffff;">{c_name_val}</h4>
                                            {status_badge}
                                            {company_badge}
                                        </div>
                                        <div style="font-size: 0.83rem; color: #94a3b8; margin-top: 4px; display: flex; gap: 16px; flex-wrap: wrap;">
                                            <span>📞 <b>{c_phone_val}</b></span>
                                            <span>✉️ {c_email_val if c_email_val else '<span style="color:#64748b;">No Email</span>'}</span>
                                            <span>📍 {location_str}</span>
                                        </div>
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 0.78rem; color: #94a3b8;">GST / Tax ID:</div>
                                    <code style="font-size: 0.82rem; color: #818cf8;">{c_gst_val if c_gst_val else 'Unregistered'}</code>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Action buttons in columns
                    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1.5, 1, 1, 1])

                    with btn_c1:
                        st.caption(f"ID #{cid} • Joined: {client.get('created_at', '')[:10] if client.get('created_at') else 'N/A'}")

                    with btn_c2:
                        # Full profile view popover
                        with st.popover(f"👁️ View Profile"):
                            st.markdown(f"### 👤 {c_name_val}")
                            st.markdown(f"**Status:** `{c_status_val.upper()}`")
                            st.markdown(f"**Company / Business:** {c_company_val or 'N/A'}")
                            st.markdown(f"**GST / Tax ID:** `{c_gst_val or 'N/A'}`")
                            st.markdown("---")
                            st.markdown(f"**Phone Number:** `{c_phone_val}`")
                            st.markdown(f"**Email Address:** `{c_email_val or 'N/A'}`")
                            st.markdown(f"**Full Address:** {c_address_val or 'N/A'}")
                            st.markdown(f"**City:** {c_city_val or 'N/A'} | **State:** {c_state_val or 'N/A'} | **Pincode:** {c_pincode_val or 'N/A'}")
                            st.markdown("---")
                            st.caption(f"Created: {client.get('created_at', 'N/A')} | Last Updated: {client.get('updated_at', 'N/A')}")

                    with btn_c3:
                        # Edit Client Info popover calling the new update route!
                        with st.popover(f"✏️ Edit Info"):
                            st.markdown(f"**Edit Information for {c_name_val}**")
                            e_name = st.text_input("Full Name *", value=c_name_val, key=f"e_name_{cid}")
                            e_phone = st.text_input("Phone Number *", value=c_phone_val, key=f"e_phone_{cid}")
                            e_email = st.text_input("Email Address", value=c_email_val or "", key=f"e_email_{cid}")
                            e_company = st.text_input("Company Name", value=c_company_val or "", key=f"e_comp_{cid}")
                            e_gst = st.text_input("GST Number", value=c_gst_val or "", key=f"e_gst_{cid}")
                            
                            e_addr = st.text_input("Street Address", value=c_address_val or "", key=f"e_addr_{cid}")
                            ec1, ec2, ec3 = st.columns(3)
                            with ec1:
                                e_city = st.text_input("City", value=c_city_val or "", key=f"e_city_{cid}")
                            with ec2:
                                e_state = st.text_input("State", value=c_state_val or "", key=f"e_state_{cid}")
                            with ec3:
                                e_pin = st.text_input("Pincode", value=c_pincode_val or "", key=f"e_pin_{cid}")
                                
                            status_idx = 0 if c_status_val == "active" else 1
                            e_status = st.selectbox("Status", ["active", "inactive"], index=status_idx, key=f"e_stat_{cid}")

                            if st.button("💾 Update Client", key=f"save_client_{cid}", type="primary", use_container_width=True):
                                if not e_name.strip():
                                    st.error("Name cannot be empty!")
                                elif not e_phone.strip():
                                    st.error("Phone cannot be empty!")
                                else:
                                    update_payload = {
                                        "name": e_name.strip(),
                                        "phone": e_phone.strip(),
                                        "email": e_email.strip() if e_email.strip() else None,
                                        "company_name": e_company.strip() if e_company.strip() else None,
                                        "gst_number": e_gst.strip() if e_gst.strip() else None,
                                        "address": e_addr.strip() if e_addr.strip() else None,
                                        "city": e_city.strip() if e_city.strip() else None,
                                        "state": e_state.strip() if e_state.strip() else None,
                                        "pincode": e_pin.strip() if e_pin.strip() else None,
                                        "status": e_status
                                    }
                                    up_resp, up_code = api_put(f"/client/update_client/{cid}", update_payload)
                                    if up_code == 200 and up_resp.get("status") == "Success":
                                        st.success("Client updated successfully!")
                                        st.toast(f"Updated {e_name}", icon="✅")
                                        st.rerun()
                                    else:
                                        st.error(up_resp.get("message", "Error updating client"))

                    with btn_c4:
                        # Delete confirmation popover
                        with st.popover("🗑️ Delete"):
                            st.markdown(f"**Delete {c_name_val}?**")
                            st.caption("This action cannot be undone.")
                            if st.button("Confirm Delete", key=f"del_client_{cid}", type="primary"):
                                del_resp, del_code = api_delete(f"/client/delete_client/{cid}")
                                if del_code == 200 and del_resp.get("status") == "Success":
                                    st.toast(f"Deleted client {c_name_val}", icon="🗑️")
                                    st.rerun()
                                else:
                                    st.error(del_resp.get("message", "Error deleting client"))

                    st.markdown("<hr style='border-color: #1e293b; margin: 12px 0 18px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No matching clients found in the directory.")

    # -------------------------------------------------------------
    # View 2: Tabular Directory & CSV Export
    # -------------------------------------------------------------
    elif view_mode == "📋 Table & CSV Export":
        if filtered_clients:
            df_clients = pd.DataFrame(filtered_clients)
            
            # Format columns
            cols_to_show = ["id", "name", "phone", "email", "company_name", "gst_number", "city", "state", "pincode", "status", "created_at"]
            available_cols = [c for c in cols_to_show if c in df_clients.columns]
            
            st.dataframe(
                df_clients[available_cols],
                use_container_width=True,
                hide_index=True
            )

            # Export Button
            csv_buf = io.StringIO()
            df_clients.to_csv(csv_buf, index=False)
            st.download_button(
                label="📥 Download Clients Directory (CSV)",
                data=csv_buf.getvalue(),
                file_name=f"clients_directory_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No clients available to display in table.")


# ---------------------------------------------------------
# SYSTEM SETTINGS & DIAGNOSTICS
# ---------------------------------------------------------
elif menu_choice == "⚙️ System Settings":
    st.title("⚙️ System Configuration & Diagnostics")
    st.caption("Manage API endpoints and verify connection health.")

    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### 🔌 Flask Backend API Connection")
    current_url = st.text_input("Backend REST API Base URL", value=BASE_URL)
    
    if st.button("Test Connection"):
        with st.spinner("Testing API ping..."):
            if api_health_check():
                st.success("✅ Successfully connected to Flask backend API!")
            else:
                st.error("❌ Failed to reach Flask server at specified URL.")
    
    st.markdown("<br><b>Quick API Reference:</b>", unsafe_allow_html=True)
    st.code(f"Swagger Documentation: http://127.0.0.1:5001/swagger", language="text")
    st.code(f"Auth Endpoints: {BASE_URL}/auth/login | {BASE_URL}/auth/register", language="text")
    st.code(f"Product Endpoints: {BASE_URL}/products", language="text")
    st.code(f"Category Endpoints: {BASE_URL}/categories", language="text")
    st.code(f"Client Endpoints: {BASE_URL}/client/create_client | {BASE_URL}/client/read_client | {BASE_URL}/client/update_client/<id> | {BASE_URL}/client/delete_client/<id> | {BASE_URL}/client/search_client", language="text")
    st.markdown("</div>", unsafe_allow_html=True)



