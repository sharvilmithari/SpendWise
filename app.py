from itertools import count

import streamlit as st
import pandas as pd
import json
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import hashlib
from supabase import create_client, Client

# SupaBase
SUPABASE_URL = "https://qqdiqibbwukxkkyenylp.supabase.co"
SUPABASE_KEY = "sb_publishable__O01VDfxjTVKbxJIQli9nQ_cJA22CUX"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

st.set_page_config(
    page_title="SpendWise India",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CONFIGURATION & CONSTANTS
# ─────────────────────────────────────────────

EXPENSE_CATEGORIES = [
    "🍱 Food", "🚌 Travel", "📱 Recharge", "🏠 Rent", "🛍️ Shopping",
    "📚 Education", "💊 Healthcare", "🎮 Entertainment", "🔧 Other",
]

INCOME_CATEGORIES = [
    "💰 Stipend", "🏦 Allowance", "💼 Part-time Job", "🎁 Gift", "📈 Other Income",
]

CHART_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE"
]

# ─────────────────────────────────────────────
#  AUTH — UPDATED TO HANDLE UUID
# ─────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username: str, password: str) -> bool:
    """Create a new user. Returns False if username taken."""
    existing = supabase.table("users").select("id").eq("username", username).execute()
    if existing.data:
        return False
    supabase.table("users").insert({"username": username, "password": _hash(password)}).execute()
    return True

def login(username: str, password: str):
    """Verify credentials. Returns user UUID on success, or False."""
    # Username is used only to find the record
    res = supabase.table("users").select("id, password").eq("username", username).execute()
    if not res.data:
        return False
    row = res.data[0]
    if row["password"] != _hash(password):
        return False
    return row["id"]  # Returns UUID

def reset_password(username: str, new_password: str) -> bool:
    """Reset password. Returns False if user not found."""
    res = supabase.table("users").select("id").eq("username", username).execute()
    if not res.data:
        return False
    supabase.table("users").update({"password": _hash(new_password)}).eq("username", username).execute()
    return True

# ─────────────────────────────────────────────
#  DATA LAYER — UPDATED TO USE user_id (UUID)
# ─────────────────────────────────────────────

def load_user_data(username: str) -> pd.DataFrame:
    """Load all transactions for the logged-in user using UUID."""
    empty = pd.DataFrame(columns=["id", "type", "amount", "category", "date", "notes"])
    # CHANGE: Use session_state UUID instead of username
    user_uuid = st.session_state.get("user_uuid")
    if not user_uuid:
        return empty
    
    # CHANGE: Query filtered by user_id
    res = supabase.table("transactions").select("*").eq("user_id", user_uuid).execute()
    if not res.data:
        return empty
    df = pd.DataFrame(res.data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["amount"] = df["amount"].astype(float)
    return df

def save_transaction(username: str, t_type: str, amount: float,
                     category: str, date, notes: str):
    """Insert a single new transaction into Supabase using UUID."""
    # CHANGE: Use session_state UUID
    user_uuid = st.session_state.get("user_uuid")
    if not user_uuid: return
    
    # CHANGE: Insert user_id instead of username
    supabase.table("transactions").insert({
        "user_id": user_uuid,
        "type": t_type,
        "amount": float(amount),
        "category": category,
        "date": str(date),
        "notes": notes,
    }).execute()

def delete_transaction_db(username: str, row_id: int):
    """Delete a transaction by its Supabase row id (scoped to user UUID)."""
    # CHANGE: Use session_state UUID
    user_uuid = st.session_state.get("user_uuid")
    # CHANGE: Ensure delete is scoped to both id and user_id for security
    supabase.table("transactions").delete().eq("id", row_id).eq("user_id", user_uuid).execute()

# ─────────────────────────────────────────────
#  SETTINGS — UPDATED TO USE user_id (UUID)
# ─────────────────────────────────────────────

def load_settings(username: str) -> dict:
    """Load settings for the user using UUID."""
    defaults = {"monthly_budget": 0.0, "daily_limit": 0.0}
    # CHANGE: Use session_state UUID
    user_uuid = st.session_state.get("user_uuid")
    if not user_uuid: return defaults

    # CHANGE: Query filtered by user_id
    res = supabase.table("settings").select("*").eq("user_id", user_uuid).execute()
    if res.data:
        row = res.data[0]
        return {"monthly_budget": row.get("monthly_budget", 0.0),
                "daily_limit": row.get("daily_limit", 0.0)}
    return defaults

def save_settings(username: str, settings: dict):
    """Upsert settings for the user using UUID."""
    # CHANGE: Use session_state UUID
    user_uuid = st.session_state.get("user_uuid")
    if not user_uuid: return

    # CHANGE: Upsert uses user_id as the key
    supabase.table("settings").upsert({
        "user_id": user_uuid,
        "monthly_budget": settings["monthly_budget"],
        "daily_limit": settings["daily_limit"],
    }).execute()

# ─────────────────────────────────────────────
#  CSS & UI (UNCHANGED AS PER REQUIREMENTS)
# ─────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #080b11; color: #e2e8f0; }
    .block-container { padding: 2.5rem 2.5rem 4rem !important; max-width: 1200px !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d111a 0%, #090d15 100%) !important; border-right: 1px solid rgba(99,102,241,0.12) !important; box-shadow: 4px 0 40px rgba(0,0,0,0.5) !important; }
    [data-testid="stSidebar"] > div { padding-top: 0 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { display: block !important; width: 100% !important; margin: 6px 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div { background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(139,92,246,0.12)) !important; color: #a5b4fc !important; font-weight: 600 !important; border: 1px solid rgba(99,102,241,0.25) !important; box-shadow: 0 0 20px rgba(99,102,241,0.08); }
    .sidebar-divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 14px 0; }
    [data-testid="stSidebar"] .stButton:last-child > button { background: rgba(239,68,68,0.08) !important; border: 1px solid rgba(239,68,68,0.2) !important; color: #f87171 !important; font-weight: 600 !important; border-radius: 10px !important; font-size: 0.875rem !important; }
    .metric-card { background: linear-gradient(145deg, #0f1420, #111827); border: 1px solid rgba(255,255,255,0.07); border-radius: 20px; padding: 26px 24px 22px; position: relative; overflow: hidden; transition: transform 0.2s; }
    .metric-card-icon { font-size: 1.6rem; margin-bottom: 14px; display: block; }
    .metric-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; color: #64748b; margin-bottom: 6px; font-weight: 600; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.75rem; font-weight: 600; }
    .metric-value.income { color: #34d399; }
    .metric-value.expense { color: #f87171; }
    .metric-value.balance { color: #818cf8; }
    .metric-value.budget { color: #c084fc; }
    .card-income { border-left: 3px solid #34d399 !important; }
    .card-expense { border-left: 3px solid #f87171 !important; }
    .card-balance { border-left: 3px solid #818cf8 !important; }
    .card-budget { border-left: 3px solid #c084fc !important; }
    .section-header { font-size: 1rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; margin: 32px 0 16px 0; display: flex; align-items: center; gap: 10px; }
    .section-header::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(99,102,241,0.3), transparent); }
    .page-title { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #e2e8f0 30%, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .page-subtitle { font-size: 0.85rem; color: #475569; margin-bottom: 32px; }
    .banner { border-radius: 12px; padding: 14px 18px; margin: 10px 0; font-size: 0.875rem; font-weight: 500; display: flex; align-items: center; gap: 10px; }
    .banner-danger { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25); color: #fca5a5; }
    .banner-warn { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #fcd34d; }
    .banner-success { background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.25); color: #6ee7b7; }
    .stButton > button { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: #fff !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CALCULATIONS & UI COMPONENTS (UNCHANGED)
# ─────────────────────────────────────────────

def get_summary(df: pd.DataFrame) -> dict:
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    return {"income": total_income, "expense": total_expense, "balance": total_income - total_expense}

def get_today_expense(df: pd.DataFrame) -> float:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    today = pd.Timestamp.now().normalize()
    mask = (df["type"] == "Expense") & (df["date"].dt.normalize() == today)
    return df[mask]["amount"].sum()

def get_this_month_expense(df: pd.DataFrame) -> float:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    now = pd.Timestamp.now()
    mask = (df["type"] == "Expense") & (df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)
    return df[mask]["amount"].sum()

def fmt(amount: float) -> str:
    return f"₹{amount:,.2f}"

CARD_ICONS = {"card-income": "💵", "card-expense": "💸", "card-balance": "⚖️", "card-budget": "🎯"}

def render_metric_card(label, value, card_class, value_class, sub=""):
    icon = CARD_ICONS.get(card_class, "📊")
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card {card_class}">
        <span class="metric-card-icon">{icon}</span>
        <div class="metric-label">{label}</div>
        <div class="metric-value {value_class}">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def render_banner(message, level="warn"):
    st.markdown(f'<div class="banner banner-{level}">{message}</div>', unsafe_allow_html=True)

def render_section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGES (LOGIC PRESERVED, ONLY DB HOOKS FIXED)
# ─────────────────────────────────────────────

def page_dashboard(df: pd.DataFrame, settings: dict):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your complete financial overview</div>', unsafe_allow_html=True)
    summary = get_summary(df)
    month_expense = get_this_month_expense(df)
    today_expense = get_today_expense(df)
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Total Income", fmt(summary["income"]), "card-income", "income", "All time")
    with c2: render_metric_card("Total Expenses", fmt(summary["expense"]), "card-expense", "expense", "All time")
    with c3: render_metric_card("Net Balance", fmt(summary["balance"]), "card-balance", "balance", "✅ Surplus" if summary["balance"] >= 0 else "⚠️ Deficit")
    with c4:
        budget = settings["monthly_budget"]
        remaining = budget - month_expense if budget > 0 else 0
        sub = fmt(remaining) + " left" if budget > 0 else "No budget set"
        render_metric_card("Monthly Budget", fmt(budget), "card-budget", "budget", sub)

    st.markdown("<br>", unsafe_allow_html=True)
    budget = settings["monthly_budget"]
    if budget > 0:
        pct = (month_expense / budget) * 100
        if month_expense > budget: render_banner(f"🚨 Budget exceeded! Spent {fmt(month_expense)} of {fmt(budget)}.", "danger")
        elif pct >= 80: render_banner(f"⚠️ Used {pct:.0f}% of budget. {fmt(budget - month_expense)} left.", "warn")

    render_section_header("🕐 Recent Transactions")
    if df.empty: st.info("No transactions yet.")
    else:
        recent = df.sort_values("date", ascending=False).head(10).copy()
        recent["date"] = recent["date"].dt.strftime("%d %b %Y")
        recent["amount"] = recent["amount"].apply(fmt)
        st.dataframe(recent[["date", "type", "category", "amount", "notes"]], use_container_width=True, hide_index=True)

def page_add_transaction(df: pd.DataFrame, settings: dict):
    st.markdown('<div class="page-title">Add Transaction</div>', unsafe_allow_html=True)
    if "txn_type_radio" not in st.session_state: st.session_state["txn_type_radio"] = "Expense"
    t_type = st.session_state["txn_type_radio"]
    
    _c1, _c2 = st.columns(2)
    with _c1:
        if st.button("💸 Expense", use_container_width=True): st.session_state["txn_type_radio"] = "Expense"; st.rerun()
    with _c2:
        if st.button("💰 Income", use_container_width=True): st.session_state["txn_type_radio"] = "Income"; st.rerun()

    with st.form("add_txn_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Category", EXPENSE_CATEGORIES if t_type == "Expense" else INCOME_CATEGORIES)
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        with col2:
            date = st.date_input("Date", value=datetime.date.today())
            notes = st.text_area("Notes", height=120)
        if st.form_submit_button("💾 Save Transaction"):
            if amount > 0:
                # CHANGE: user parameter passed but function now uses session_state UUID internally
                save_transaction(st.session_state["user"], t_type, amount, category, date, notes)
                st.success("Transaction saved!")
                st.rerun()

def page_history(df: pd.DataFrame):
    st.markdown('<div class="page-title">Transaction History</div>', unsafe_allow_html=True)
    if df.empty:
        st.info("No records.")
        return
    render_section_header("🔍 Filters")
    f1, f2, f3 = st.columns(3)
    with f1: type_filter = st.selectbox("Type", ["All", "Income", "Expense"])
    with f2: cat_filter = st.selectbox("Category", ["All"] + sorted(df["category"].unique().tolist()))
    
    filtered = df.copy()
    if type_filter != "All": filtered = filtered[filtered["type"] == type_filter]
    if cat_filter != "All": filtered = filtered[filtered["category"] == cat_filter]

    display = filtered.sort_values("date", ascending=False).copy()
    display["date"] = display["date"].dt.strftime("%d %b %Y")
    display["amount"] = display["amount"].apply(fmt)
    st.dataframe(display[["id", "date", "type", "category", "amount", "notes"]], use_container_width=True, hide_index=True)
    
    render_section_header("🗑️ Delete Transaction")
    del_id = st.number_input("Enter Transaction ID", min_value=1, step=1)
    if st.button("Delete"):
        match = df[df["id"] == int(del_id)]
        if not match.empty:
            delete_transaction_db(st.session_state["user"], int(del_id))
            st.success("Deleted.")
            st.rerun()

def page_analytics(df: pd.DataFrame):
    st.markdown('<div class="page-title">Analytics</div>', unsafe_allow_html=True)
    if df.empty or df[df["type"] == "Expense"].empty:
        st.info("Add expenses to see analytics.")
        return
    expenses = df[df["type"] == "Expense"].copy()
    tab1, tab2 = st.tabs(["🥧 Category", "📊 Monthly"])
    with tab1:
        cat_totals = expenses.groupby("category")["amount"].sum()
        fig, ax = plt.subplots()
        fig.patch.set_facecolor("#0f1520")
        ax.pie(cat_totals, labels=cat_totals.index, autopct='%1.1f%%', textprops={'color':"w"})
        st.pyplot(fig)
    with tab2:
        expenses["month"] = expenses["date"].dt.to_period("M").astype(str)
        monthly = expenses.groupby("month")["amount"].sum()
        st.bar_chart(monthly)

def page_settings(settings: dict) -> dict:
    st.markdown('<div class="page-title">Settings</div>', unsafe_allow_html=True)
    budget = st.number_input("Monthly budget (₹)", min_value=0.0, value=float(settings.get("monthly_budget", 0)))
    daily = st.number_input("Daily limit (₹)", min_value=0.0, value=float(settings.get("daily_limit", 0)))
    if st.button("💾 Save Settings"):
        new_s = {"monthly_budget": budget, "daily_limit": daily}
        save_settings(st.session_state["user"], new_s)
        st.success("Settings updated!")
        return new_s
    return settings

# ─────────────────────────────────────────────
#  SIDEBAR & LOGIN (UNCHANGED STYLING)
# ─────────────────────────────────────────────

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        user = st.session_state.get("user", "")
        st.markdown(f"**User:** {user}")
        page = st.radio("Navigate", ["🏠 Dashboard", "➕ Add Transaction", "📋 History", "📈 Analytics", "⚙️ Settings"])
        if st.button("🚪 Sign Out"):
            st.session_state["user"] = None
            st.session_state["user_uuid"] = None
            st.rerun()
    return page

def show_login():
    if "login_tab" not in st.session_state: st.session_state["login_tab"] = "login"
    tab = st.session_state["login_tab"]
    
    st.markdown("<h2 style='text-align:center'>SpendWise India</h2>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 1])
    with c1: 
        if st.button("Login"): st.session_state["login_tab"] = "login"; st.rerun()
    with c2: 
        if st.button("Sign Up"): st.session_state["login_tab"] = "signup"; st.rerun()

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if tab == "login":
        if st.button("Login →"):
            user_uuid = login(username, password)
            if user_uuid:
                # CHANGE: Store both username for UI and UUID for DB
                st.session_state["user"] = username
                st.session_state["user_uuid"] = user_uuid
                st.rerun()
            else: st.error("Invalid credentials.")
    else:
        if st.button("Register →"):
            if signup(username, password):
                st.success("Created! Log in now.")
                st.session_state["login_tab"] = "login"; st.rerun()

# ─────────────────────────────────────────────
#  MAIN ENTRY
# ─────────────────────────────────────────────

def main():
    inject_css()
    if "user" not in st.session_state: st.session_state["user"] = None
    if st.session_state["user"] is None:
        show_login()
        return

    user = st.session_state["user"]
    df = load_user_data(user)
    settings = load_settings(user)
    page_choice = render_sidebar()

    if "Dashboard" in page_choice: page_dashboard(df, settings)
    elif "Add" in page_choice: page_add_transaction(df, settings)
    elif "History" in page_choice: page_history(df)
    elif "Analytics" in page_choice: page_analytics(df)
    elif "Settings" in page_choice: page_settings(settings)

if __name__ == "__main__":
    main()
