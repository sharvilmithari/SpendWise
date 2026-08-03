from itertools import count

import streamlit as st
from landing import show_landing_page  # ← landing page module
import pandas as pd
import json
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from supabase import create_client, Client

# ─────────────────────────────────────────────
#  SUPABASE CLIENT
# ─────────────────────────────────────────────

from pathlib import Path
from dotenv import load_dotenv

# Load key.env dynamically using the script's directory absolute path
env_path = Path(__file__).parent / "key.env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Fallback to Streamlit secrets (for cloud deployments)
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        if not GEMINI_API_KEY:
            GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass


@st.cache_resource
def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase environment variables not set. Please check your key.env file.")
        st.stop()
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.sidebar.warning(f"⚠️ Supabase init offline: {e}")
        return None

supabase = get_supabase()

from pathlib import Path
favicon_path = Path(__file__).parent / "favicon.png"

st.set_page_config(
    page_title="SpendWise India",
    page_icon=str(favicon_path) if favicon_path.exists() else "💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.components.v1.html(
    """
    <script>
        function fixTabTitle() {
            try {
                if (window.parent && window.parent.document) {
                    window.parent.document.title = "SpendWise India";
                }
                document.title = "SpendWise India";
            } catch (e) {}
        }
        fixTabTitle();
        setInterval(fixTabTitle, 300);
    </script>
    """,
    height=0,
)

# ─────────────────────────────────────────────
#  CONFIGURATION & CONSTANTS
# ─────────────────────────────────────────────

EXPENSE_CATEGORIES = [
    "🍱 Food",
    "🚌 Travel",
    "📱 Recharge",
    "🏠 Rent",
    "🛍️ Shopping",
    "📚 Education",
    "💊 Healthcare",
    "🎮 Entertainment",
    "🔧 Other",
]

INCOME_CATEGORIES = [
    "💰 Stipend",
    "🏦 Allowance",
    "💼 Part-time Job",
    "🎁 Gift",
    "📈 Other Income",
]

CHART_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE"
]

# ─────────────────────────────────────────────
#  AUTH — Supabase Auth + profiles table
#
#  profiles table schema:
#    id          uuid primary key references auth.users(id)
#    username    text
#    created_at  timestamptz default now()
#
#  transactions table:
#    user_id     uuid (not username)
#
#  settings table:
#    user_id     uuid (not username)
# ─────────────────────────────────────────────

def signup(email: str, username: str, password: str) -> tuple:
    """
    Create a Supabase Auth user and insert profile row.
    Returns (True, "") on success or (False, error_message) on failure.
    """
    if supabase is None:
        return False, "Cannot sign up: Supabase is offline due to invalid API key."
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user is None:
            return False, "Signup failed. Please try again."
        supabase.table("profiles").insert({
            "id": res.user.id,
            "username": username,
        }).execute()
        return True, ""
    except Exception as e:
        err = str(e)
        err_lower = err.lower()
        if "already registered" in err_lower or "already been registered" in err_lower:
            return False, "An account with this email already exists."
        if "name or service not known" in err_lower or "getaddrinfo failed" in err_lower or "connect" in err_lower or "temporary failure" in err_lower:
            return False, "Failed to connect to the Supabase database. Please check if your SUPABASE_URL in key.env is correct/active, and that your internet connection is active."
        return False, err


def login(email: str, password: str) -> tuple:
    """
    Sign in via Supabase Auth.
    Stores user_uuid, user_email, and username in session_state.
    Returns (True, "") on success, or (False, error_message) on failure.
    """
    if supabase is None:
        return False, "Cannot log in: Supabase is offline due to invalid API key."
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user is None:
            return False, "Login failed. Please try again."
        st.session_state["user_uuid"] = res.user.id
        st.session_state["user_email"] = res.user.email

        # Fetch display username from profiles table
        profile = (
            supabase.table("profiles")
            .select("username")
            .eq("id", res.user.id)
            .single()
            .execute()
        )
        username = profile.data["username"] if profile.data else res.user.email
        st.session_state["user"] = username
        return True, ""
    except Exception as e:
        err = str(e)
        err_lower = err.lower()
        if "name or service not known" in err_lower or "getaddrinfo failed" in err_lower or "connect" in err_lower or "temporary failure" in err_lower:
            return False, "Failed to connect to the Supabase database. Please check if your SUPABASE_URL in key.env is correct/active, and that your internet connection is active."
        return False, "Invalid email or password."


def request_password_reset(email: str) -> tuple:
    """Send a password reset email via Supabase Auth."""
    if supabase is None:
        return False, "Cannot reset password: Supabase is offline due to invalid API key."
    try:
        supabase.auth.reset_password_email(email)
        return True, ""
    except Exception as e:
        err = str(e)
        err_lower = err.lower()
        if "name or service not known" in err_lower or "getaddrinfo failed" in err_lower or "connect" in err_lower or "temporary failure" in err_lower:
            return False, "Failed to connect to the Supabase database. Please check if your SUPABASE_URL in key.env is correct/active, and that your internet connection is active."
        return False, err


# ─────────────────────────────────────────────
#  DATA LAYER — Supabase transactions table
# ─────────────────────────────────────────────

def load_user_data() -> pd.DataFrame:
    """Load all transactions for the logged-in user."""

    empty = pd.DataFrame(
        columns=["id", "type", "amount", "category", "date", "notes"]
    )

    user_uuid = st.session_state.get("user_uuid")

    if not user_uuid:
        return empty

    if supabase is None:
        from database import get_local_transactions
        txs = get_local_transactions(user_uuid)
        if not txs:
            return empty
        df = pd.DataFrame(txs)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["amount"] = df["amount"].astype(float)
        return df

    try:
        res = (
            supabase.table("transactions")
            .select("*")
            .eq("user_id", user_uuid)
            .execute()
        )

        if not res.data:
            return empty

        df = pd.DataFrame(res.data)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["amount"] = df["amount"].astype(float)
        return df
    except Exception:
        from database import get_local_transactions
        txs = get_local_transactions(user_uuid)
        if not txs:
            return empty
        df = pd.DataFrame(txs)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["amount"] = df["amount"].astype(float)
        return df


def save_transaction(
    t_type: str,
    amount: float,
    category: str,
    date,
    notes: str,
):
    """Insert a single new transaction into Supabase or SQLite."""

    user_uuid = st.session_state.get("user_uuid")

    if not user_uuid:
        st.error("User not logged in.")
        return

    if supabase is None:
        from database import add_local_transaction
        add_local_transaction(user_uuid, t_type, float(amount), category, str(date), notes)
        return

    try:
        (
            supabase.table("transactions")
            .insert(
                {
                    "user_id": user_uuid,
                    "type": t_type,
                    "amount": float(amount),
                    "category": category,
                    "date": str(date),
                    "notes": notes,
                }
            )
            .execute()
        )
    except Exception:
        from database import add_local_transaction
        add_local_transaction(user_uuid, t_type, float(amount), category, str(date), notes)


def delete_transaction_db(row_id: int):
    """Delete a transaction by its row id."""

    user_uuid = st.session_state.get("user_uuid")

    if supabase is None:
        from database import delete_local_transaction
        delete_local_transaction(user_uuid, int(row_id))
        return

    try:
        (
            supabase.table("transactions")
            .delete()
            .eq("id", row_id)
            .eq("user_id", user_uuid)
            .execute()
        )
    except Exception:
        from database import delete_local_transaction
        delete_local_transaction(user_uuid, int(row_id))


# ─────────────────────────────────────────────
#  SETTINGS — Supabase settings table
# ─────────────────────────────────────────────

def load_settings(username: str) -> dict:
    defaults = {"monthly_budget": 0.0, "daily_limit": 0.0}
    user_uuid = st.session_state.get("user_uuid")
    if not user_uuid:
        return defaults

    if supabase is None:
        from database import get_local_settings
        return get_local_settings(user_uuid, defaults)

    try:
        res = supabase.table("settings").select("*").eq("user_id", user_uuid).execute()
        if res.data:
            row = res.data[0]
            return {"monthly_budget": row.get("monthly_budget", 0.0),
                    "daily_limit": row.get("daily_limit", 0.0)}
        return defaults
    except Exception:
        from database import get_local_settings
        return get_local_settings(user_uuid, defaults)


def save_settings(username: str, settings: dict):
    """Upsert settings for the user."""
    user_uuid = st.session_state.get("user_uuid")
    if not user_uuid:
        return

    if supabase is None:
        from database import save_local_settings
        save_local_settings(user_uuid, settings["monthly_budget"], settings["daily_limit"])
        return

    try:
        supabase.table("settings").upsert({
            "user_id": user_uuid,
            "monthly_budget": settings["monthly_budget"],
            "daily_limit": settings["daily_limit"],
        }).execute()
    except Exception:
        from database import save_local_settings
        save_local_settings(user_uuid, settings["monthly_budget"], settings["daily_limit"])


# ─────────────────────────────────────────────
#  CUSTOM CSS — Professional Dark Theme
# ─────────────────────────────────────────────

def inject_css():
    try:
        from pathlib import Path
        css_path = Path(__file__).parent / "styles" / "app.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS: {e}")


# ─────────────────────────────────────────────
#  CALCULATIONS
# ─────────────────────────────────────────────

def get_summary(df: pd.DataFrame) -> dict:
    total_income  = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    return {"income": total_income, "expense": total_expense, "balance": total_income - total_expense}


def get_today_expense(df: pd.DataFrame) -> float:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    today = pd.Timestamp.now().normalize()
    mask = (df["type"] == "Expense") & (df["date"].dt.normalize() == today)
    return df[mask]["amount"].sum()


def get_this_month_expense(df: pd.DataFrame) -> float:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    now = pd.Timestamp.now()
    mask = (df["type"] == "Expense") & (df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)
    return df[mask]["amount"].sum()


def fmt(amount: float) -> str:
    return f"₹{amount:,.2f}"


# ─────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────

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
#  PAGE: DASHBOARD
# ─────────────────────────────────────────────

def page_dashboard(df: pd.DataFrame, settings: dict):
    from ai_copilot import calculate_health_score, generate_automated_insights, get_predictions
    from database import get_goals, get_groups
    from split_bills import calculate_group_balances
    
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    user_uuid = st.session_state.get("user_uuid")
    username = st.session_state.get("user")

    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Welcome to your upgraded AI Financial Copilot platform</div>', unsafe_allow_html=True)

    summary = get_summary(df)
    month_expense = get_this_month_expense(df)
    today_expense = get_today_expense(df)
    
    # Load AI insights and values
    goals = get_goals(user_uuid)
    health_info = calculate_health_score(df, settings)
    insights = generate_automated_insights(df, settings, goals)
    predictions = get_predictions(df, settings)

    # 1. Row 1: KPI Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Income", fmt(summary["income"]), "card-income", "income", "All time")
    with c2:
        render_metric_card("Total Expenses", fmt(summary["expense"]), "card-expense", "expense", "All time")
    with c3:
        render_metric_card("Net Savings Balance", fmt(summary["balance"]), "card-balance", "balance",
                           "✅ Surplus" if summary["balance"] >= 0 else "⚠️ Deficit")
    with c4:
        budget = settings["monthly_budget"]
        remaining = budget - month_expense if budget > 0 else 0
        sub = fmt(remaining) + " left" if budget > 0 else "No budget set"
        render_metric_card("Monthly Budget", fmt(budget), "card-budget", "budget", sub)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Alerts, warnings, and predicted spending banner
    if predictions["warning"]:
        render_banner(predictions["warning"], "warn")

    budget = settings["monthly_budget"]
    if budget > 0:
        pct = (month_expense / budget) * 100
        if month_expense > budget:
            render_banner(f"🚨 Budget exceeded! You've spent {fmt(month_expense)} of your {fmt(budget)} budget this month ({pct:.0f}%).", "danger")
        elif pct >= 80:
            render_banner(f"⚠️ Heads up! You've used {pct:.0f}% of your monthly budget. Only {fmt(budget - month_expense)} remaining.", "warn")

    daily_limit = settings.get("daily_limit", 0)
    if daily_limit > 0 and today_expense > daily_limit:
        render_banner(f"🔴 Daily limit breached! Today's spending: {fmt(today_expense)} (limit: {fmt(daily_limit)}).", "danger")

    # 3. Row 2: Financial Health & AI Insights (Glassmorphism layout)
    col_health, col_insights = st.columns([1, 2])
    
    with col_health:
        render_section_header("🏥 Health Score")
        st.markdown(f"""
        <div class="metric-card card-balance health-score-card">
            <div class="health-score-number">
                {health_info['score']}<span>/100</span>
            </div>
            <div class="health-score-status">{health_info['status']}</div>
            <div class="health-score-desc">
                Calculated on savings rate, consistency, and budget usage.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_insights:
        render_section_header("🤖 Copilot Insights")
        insight_html = ""
        for ins in insights:
            cls = ""
            if "📈" in ins or "⚠️" in ins or "⚡" in ins or "🚨" in ins:
                cls = "warn"
            elif "📉" in ins or "💰" in ins or "✅" in ins:
                cls = "good"
                
            insight_html += f"""
            <div class="copilot-insight {cls}">
                {ins}
            </div>
            """
        st.markdown(insight_html, unsafe_allow_html=True)

    # 4. Row 3: Month at Glance, Goals Progress, and Split Bills summaries
    col_goals, col_splits = st.columns([1, 1])
    
    with col_goals:
        render_section_header("🎯 Goal Progress")
        if not goals:
            st.info("No active goals. Set goals in the Smart Goals page to see progress here.")
        else:
            for goal in goals[:3]:
                target = goal["target_amount"]
                current = goal["current_amount"]
                pct = min(100.0, (current / target) * 100 if target > 0 else 100.0)
                st.markdown(f"**{goal['name']}** - {fmt(current)} of {fmt(target)} ({pct:.0f}%)")
                st.progress(pct / 100.0)
                
    with col_splits:
        render_section_header("👥 Split Bills Standings")
        groups = get_groups(user_uuid, username)
        if not groups:
            st.info("No split bill groups. Create one in the Split Bills page to track debts.")
        else:
            summary_found = False
            for group in groups[:3]:
                balances, simplified = calculate_group_balances(group["id"])
                user_bal = balances.get(username, 0.0)
                if user_bal != 0:
                    summary_found = True
                    color_bal = "color:#34d399;" if user_bal > 0 else "color:#f87171;"
                    sign = "+" if user_bal > 0 else ""
                    st.markdown(f"**{group['name']}**: <span style='font-family:monospace; {color_bal} font-weight:700;'>{sign}₹{user_bal:,.2f}</span>", unsafe_allow_html=True)
            if not summary_found and groups:
                st.success("🎉 You are completely settled up in all your groups!")

    # 5. Row 4: Recent Transactions
    render_section_header("🕐 Recent Transactions")
    if df.empty:
        st.info("No transactions yet. Add your first transaction from the Expense Tracker tab!")
    else:
        recent = df.sort_values("date", ascending=False).head(5).copy()
        recent["date"] = recent["date"].dt.strftime("%d %b %Y")
        recent["amount"] = recent["amount"].apply(fmt)
        recent = recent[["date", "type", "category", "amount", "notes"]].rename(
            columns={"date": "Date", "type": "Type", "category": "Category", "amount": "Amount", "notes": "Notes"}
        )
        st.dataframe(recent, use_container_width=True, hide_index=True)



# ─────────────────────────────────────────────
#  PAGE: ADD TRANSACTION
# ─────────────────────────────────────────────

def page_add_transaction(df: pd.DataFrame, settings: dict):
    st.markdown('<div class="page-title">Add Transaction</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Record a new income or expense entry</div>', unsafe_allow_html=True)

    if "txn_type_radio" not in st.session_state:
        st.session_state["txn_type_radio"] = "Expense"
    t_type = st.session_state["txn_type_radio"]

    st.markdown(f"""
    <style>
    [data-testid="stButton-_exp_btn"] > button {{
        background: {"linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(239,68,68,0.05) 100%)" if t_type == "Expense" else "rgba(255,255,255,0.02)"} !important;
        border: 2px solid {"#f87171" if t_type == "Expense" else "rgba(255,255,255,0.05)"} !important;
        color: {"#fca5a5" if t_type == "Expense" else "var(--text-muted)"} !important;
        box-shadow: {"0 0 0 4px rgba(239,68,68,0.08), 0 12px 35px rgba(239,68,68,0.18)" if t_type == "Expense" else "none"} !important;
    }}
    [data-testid="stButton-_inc_btn"] > button {{
        background: {"linear-gradient(135deg, rgba(52,211,153,0.15) 0%, rgba(52,211,153,0.05) 100%)" if t_type == "Income" else "rgba(255,255,255,0.02)"} !important;
        border: 2px solid {"#34d399" if t_type == "Income" else "rgba(255,255,255,0.05)"} !important;
        color: {"#6ee7b7" if t_type == "Income" else "var(--text-muted)"} !important;
        box-shadow: {"0 0 0 4px rgba(52,211,153,0.08), 0 12px 35px rgba(52,211,153,0.18)" if t_type == "Income" else "none"} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    _c1, _c2 = st.columns(2)
    with _c1:
        if st.button("💸   Expense\n Money going out", key="_exp_btn", use_container_width=True):
            st.session_state["txn_type_radio"] = "Expense"
            st.rerun()
    with _c2:
        if st.button("💰   Income\n Money coming in", key="_inc_btn", use_container_width=True):
            st.session_state["txn_type_radio"] = "Income"
            st.rerun()

    t_type = st.session_state["txn_type_radio"]

    if "prev_type" not in st.session_state:
        st.session_state.prev_type = t_type
    if st.session_state.prev_type != t_type:
        st.session_state.pop("exp_cat", None)
        st.session_state.pop("inc_cat", None)
        st.session_state.prev_type = t_type

    with st.form("add_txn_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            if t_type == "Expense":
                category = st.selectbox("Category", EXPENSE_CATEGORIES, key="exp_cat")
            else:
                category = st.selectbox("Category", INCOME_CATEGORIES, key="inc_cat")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
        with col2:
            date = st.date_input("Date", value=datetime.date.today())
            notes = st.text_area("Notes (optional)", placeholder="e.g. Lunch at canteen...", height=120)

        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.error("Please enter a valid amount greater than ₹0.")
            else:
                daily_limit = settings.get("daily_limit", 0)
                if t_type == "Expense" and daily_limit > 0:
                    today_total = get_today_expense(df) + amount
                    if today_total > daily_limit:
                        st.warning(f"⚠️ Adding this will exceed your daily limit! (Today total: {fmt(today_total)}, Limit: {fmt(daily_limit)})")

                user = st.session_state["user"]
                save_transaction(t_type, amount, category, date, notes)
                st.success(f"✅ {t_type} of {fmt(amount)} added successfully!")
                st.balloons()
                st.rerun()

    if settings["monthly_budget"] > 0:
        month_expense = get_this_month_expense(df)
        remaining = settings["monthly_budget"] - month_expense
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("💡 Budget Reminder")
        pct = (month_expense / settings["monthly_budget"]) * 100
        st.progress(min(pct / 100, 1.0))
        st.caption(f"Spent {fmt(month_expense)} of {fmt(settings['monthly_budget'])} ({pct:.1f}%) — {fmt(max(remaining, 0))} remaining this month")


# ─────────────────────────────────────────────
#  PAGE: TRANSACTION HISTORY
# ─────────────────────────────────────────────

def page_history(df: pd.DataFrame):
    st.markdown('<div class="page-title">Transaction History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse, filter, and export all your records</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("No transactions recorded yet. Start by adding one!")
        return

    render_section_header("🔍 Filters")
    f1, f2, f3 = st.columns(3)
    with f1:
        type_filter = st.selectbox("Type", ["All", "Income", "Expense"])
    with f2:
        all_cats = ["All"] + sorted(df["category"].unique().tolist())
        cat_filter = st.selectbox("Category", all_cats)
    with f3:
        months = ["All"] + sorted(df["date"].dt.strftime("%b %Y").unique().tolist(), reverse=True)
        month_filter = st.selectbox("Month", months)

    filtered = df.copy()
    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if month_filter != "All":
        filtered = filtered[filtered["date"].dt.strftime("%b %Y") == month_filter]

    col_exp, col_del = st.columns([3, 1])
    with col_exp:
        csv = filtered.copy()
        csv["date"] = csv["date"].dt.strftime("%Y-%m-%d")
        st.download_button(
            label="⬇️ Export CSV",
            data=csv.to_csv(index=False).encode("utf-8"),
            file_name="expense_export.csv",
            mime="text/csv",
        )
    with col_del:
        st.caption(f"{len(filtered)} record(s) found")

    display = filtered.sort_values("date", ascending=False).copy()
    display["date"] = display["date"].dt.strftime("%d %b %Y")
    display["amount"] = display["amount"].apply(fmt)
    display = display[["id", "date", "type", "category", "amount", "notes"]].rename(
        columns={"id": "ID", "date": "Date", "type": "Type", "category": "Category", "amount": "Amount", "notes": "Notes"}
    )
    st.dataframe(display, use_container_width=True, hide_index=True)

    render_section_header("🗑️ Delete Transaction")
    del_id = st.number_input("Enter Transaction ID to delete", min_value=1, step=1)
    if st.button("Delete"):
        user = st.session_state["user"]
        match = df[df["id"] == int(del_id)]
        if not match.empty:
            delete_transaction_db(int(del_id)) 
            st.success(f"Transaction #{int(del_id)} deleted.")
            st.rerun()
        else:
            st.error(f"No transaction found with ID {int(del_id)}.")


# ─────────────────────────────────────────────
#  PAGE: ANALYTICS
# ─────────────────────────────────────────────

def page_analytics(df: pd.DataFrame):
    st.markdown('<div class="page-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visual breakdown of your spending patterns</div>', unsafe_allow_html=True)

    if df.empty or df[df["type"] == "Expense"].empty:
        st.info("Add some expense transactions to see analytics.")
        return

    expenses = df[df["type"] == "Expense"].copy()

    tab1, tab2, tab3 = st.tabs(["🥧 Category Breakdown", "📊 Monthly Trend", "📋 Summary Table"])

    with tab1:
        cat_totals = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor("#0f1520")
        ax.set_facecolor("#0f1520")
        try:
            pie_results = ax.pie(
                cat_totals, labels=None, autopct="%1.1f%%",
                colors=CHART_COLORS[:len(cat_totals)], startangle=140,
                pctdistance=0.75, wedgeprops=dict(width=0.45, edgecolor="#1C2128", linewidth=2),
            )
            # ax.pie with autopct always returns (wedges, texts, autotexts)
            wedges, texts, autotexts = pie_results
            for at in autotexts:
                at.set_color("white"); at.set_fontsize(10); at.set_fontweight("bold")
        except Exception:
            pass
        import matplotlib.patches as mpatches
        legend_patches = [mpatches.Patch(color=CHART_COLORS[i % len(CHART_COLORS)], label=f"{cat}  {fmt(val)}") for i, (cat, val) in enumerate(cat_totals.items())]
        ax.legend(handles=legend_patches, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9, frameon=False, labelcolor="white")
        ax.set_title("Expense by Category", color="#E6EDF3", fontsize=14, fontweight="bold", pad=18)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with tab2:
        expenses["month"] = expenses["date"].dt.to_period("M")
        monthly = expenses.groupby("month")["amount"].sum().reset_index()
        monthly["month_str"] = monthly["month"].astype(str)
        monthly = monthly.sort_values("month").reset_index(drop=True)
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#0f1520"); ax.set_facecolor("#0f1520")
        bars = ax.bar(monthly["month_str"], monthly["amount"], color="#4f46e5", edgecolor="#0f1520", linewidth=0.5, width=0.5)
        if len(bars) > 0:
            # Use positional index after reset_index to avoid index mismatch
            max_pos = int(monthly["amount"].idxmax())
            bars[max_pos].set_color("#7c3aed")
        max_val = monthly["amount"].max() if not monthly.empty else 1
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + (max_val * 0.01), fmt(h), ha="center", va="bottom", color="#94a3b8", fontsize=8)
        ax.tick_params(colors="#475569", labelsize=9)
        for spine in ["bottom", "left"]:
            ax.spines[spine].set_color("#1e293b")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.set_xlabel("Month", color="#475569", fontsize=10)
        ax.set_ylabel("Total Expense (₹)", color="#475569", fontsize=10)
        ax.set_title("Monthly Spending Trend", color="#e2e8f0", fontsize=14, fontweight="bold", pad=14)
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with tab3:
        render_section_header("💰 Category-wise Summary")
        summary = expenses.groupby("category")["amount"].agg(["sum", "count", "mean"])
        summary.columns = ["Total Spent", "Transactions", "Avg per Transaction"]
        summary["Total Spent"] = summary["Total Spent"].apply(fmt)
        summary["Avg per Transaction"] = summary["Avg per Transaction"].apply(fmt)
        summary = summary.sort_values("Transactions", ascending=False)
        st.dataframe(summary, use_container_width=True)

    st.markdown("### 💡 Insights")
    raw_summary = df.groupby("category")["amount"].sum()
    if not raw_summary.empty:
        top_category = raw_summary.idxmax()
        max_amount = raw_summary.max()
        total_expense = raw_summary.sum()
        percentage = (max_amount / total_expense) * 100
        st.success(f"🧠 You spent most on **{top_category}** (₹{max_amount:.2f}, {percentage:.1f}% of total expenses)")


# ─────────────────────────────────────────────
def update_user_name(user_uuid: str, new_username: str):
    st.session_state["user"] = new_username
    if supabase is not None and user_uuid:
        try:
            supabase.table("profiles").upsert({
                "id": user_uuid,
                "username": new_username
            }).execute()
        except Exception:
            pass


# ─────────────────────────────────────────────
#  PAGE: SETTINGS
# ─────────────────────────────────────────────

def page_settings(settings: dict) -> dict:
    st.markdown('<div class="page-title">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Configure your profile, budget, alerts, and database options</div>', unsafe_allow_html=True)

    user_uuid = st.session_state.get("user_uuid")
    current_username = st.session_state.get("user", "")

    render_section_header("👤 Profile Settings")
    new_username = st.text_input("Display Name", value=current_username, placeholder="Enter your display name", help="Change your display name shown in the app")

    render_section_header("💼 Monthly Budget")
    budget = st.number_input("Set your monthly budget (₹)", min_value=0.0,
                             value=float(settings.get("monthly_budget", 0)), step=500.0, format="%.2f",
                             help="Set ₹0 to disable budget tracking")

    render_section_header("🔔 Daily Expense Limit")
    daily = st.number_input("Set daily expense limit (₹)", min_value=0.0,
                            value=float(settings.get("daily_limit", 0)), step=50.0, format="%.2f",
                            help="You'll be warned when you exceed this each day. Set ₹0 to disable.")

    import os
    global_api_key_set = bool(os.getenv("GEMINI_API_KEY"))
    gemini_key = ""
    
    if not global_api_key_set:
        render_section_header("🤖 AI Copilot Configuration")
        from database import get_gemini_key
        existing_key = get_gemini_key(user_uuid)
        gemini_key = st.text_input("Gemini API Key", value=existing_key, type="password", 
                                   placeholder="starts with AIza...",
                                   help="Get an API key from Google AI Studio")

    if st.button("💾 Save Settings"):
        if new_username and new_username.strip() and new_username != current_username:
            update_user_name(user_uuid, new_username.strip())
        new_settings = {"monthly_budget": budget, "daily_limit": daily}
        user = st.session_state["user"]
        save_settings(user, new_settings)
        if not global_api_key_set and gemini_key:
            from database import save_gemini_key
            save_gemini_key(user_uuid, gemini_key)
        st.success("✅ Settings saved successfully!")
        st.rerun()
        return new_settings

    return settings



# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar() -> str:
    with st.sidebar:
        from pathlib import Path
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=200)
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        user = st.session_state.get("user", "")
        initial = user[0].upper() if user else "?"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 4px 16px;">
            <div style="width:38px;height:38px;border-radius:var(--radius-md);
                        background:var(--accent-gradient);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.95rem;font-weight:700;color:#fff;
                        box-shadow:0 4px 15px rgba(79,70,229,0.4);flex-shrink:0;">
                {initial}
            </div>
            <div>
                <div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);letter-spacing:-0.2px;">{user}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["🏠  Dashboard", "🤖  AI Copilot", "👥  Split Bills", "🎯  Smart Goals", "💰  Expense Tracker", "📈  Analytics", "📋  History", "⚙️  Settings"],
            label_visibility="collapsed",
        )

        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        if st.button("🚪  Sign Out", use_container_width=True, key="logout_btn"):
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            for key in ["user", "user_uuid", "user_email"]:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("""
        <div style="font-size:0.65rem;color:#334155;text-align:center;padding:14px 0 4px;letter-spacing:0.3px;">
            Developed by Sharvil Mithari<br>
            <span style="color:#4f46e5;font-weight:600;">SpendWise · India 2026</span>
        </div>
        """, unsafe_allow_html=True)

    page_map = {
        "🏠  Dashboard": "🏠 Dashboard",
        "🤖  AI Copilot": "🤖 AI Copilot",
        "👥  Split Bills": "👥 Split Bills",
        "🎯  Smart Goals": "🎯 Smart Goals",
        "💰  Expense Tracker": "💰 Expense Tracker",
        "📋  History": "📋 History",
        "📈  Analytics": "📈 Analytics",
        "⚙️  Settings": "⚙️ Settings",
    }
    return page_map.get(page, page)


# ─────────────────────────────────────────────
#  LOGIN UI
# ─────────────────────────────────────────────

def show_login():
    import base64

    if "login_tab" not in st.session_state:
        st.session_state["login_tab"] = "login"
    tab = st.session_state["login_tab"]

    from pathlib import Path
    logo_path = Path(__file__).parent / "logo.png"
    logo_b64 = ""
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()

    st.markdown("""
    <style>
    .block-container { padding-top: 6vh !important; padding-bottom: 0 !important; max-width: 440px !important; margin: 0 auto !important; }
    div[data-testid="stVerticalBlock"] > div:has(> div > .lcard) {
        background: #0d111a !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 24px !important;
        padding: 40px 36px 36px !important;
        box-shadow: 0 30px 90px rgba(0,0,0,0.7), 0 0 40px rgba(147, 51, 234, 0.12) !important;
        backdrop-filter: blur(20px) !important;
    }

    /* Modern text inputs */
    .stTextInput > div > div > input {
        background: #161c28 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        height: 48px !important;
        color: #f8fafc !important;
        font-size: 0.95rem !important;
        padding: 0 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #9333ea !important;
        box-shadow: 0 0 0 3px rgba(147, 51, 234, 0.25) !important;
    }

    /* Primary Sunset Gradient Action Buttons */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff6b57 0%, #9333ea 50%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        height: 48px !important;
        font-size: 0.98rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 8px 25px rgba(147, 51, 234, 0.4) !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 12px 35px rgba(255, 107, 87, 0.5) !important;
        filter: brightness(1.08) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="lcard" style="display:none"></div>', unsafe_allow_html=True)

        if logo_b64:
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-width:110px;max-height:110px;object-fit:contain;display:block;margin:0 auto 12px;mix-blend-mode:screen;">'
        else:
            logo_html = '<div style="font-size:2.4rem;text-align:center;margin-bottom:12px;">💰</div>'

        st.markdown(logo_html, unsafe_allow_html=True)

        # ── LOGIN TAB ──
        if tab == "login":
            st.markdown("""
            <h2 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.7rem;color:#f8fafc;text-align:center;margin:0 0 4px 0;">Welcome back</h2>
            <p style="color:#64748b;font-size:0.88rem;text-align:center;margin:0 0 24px 0;">Sign in to your account</p>
            """, unsafe_allow_html=True)

            email    = st.text_input("Email", placeholder="you@example.com", key="auth_email")
            password = st.text_input("Password", placeholder="Enter your password",
                                     type="password", key="auth_password")
            if st.button("Sign In", key="login_btn", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both fields.")
                else:
                    ok, err = login(email, password)
                    if ok:
                        st.rerun()
                    else:
                        st.error(f"❌ {err}")

            # Forgot password link
            st.markdown("""
            <div style='text-align:center;margin-top:10px;'>
                <span style='font-size:0.83rem;color:#64748b;'>Forgot your password? </span>
            </div>
            """, unsafe_allow_html=True)
            c_fp_l, c_fp_m, c_fp_r = st.columns([1.5, 2, 1.5])
            with c_fp_m:
                if st.button("Reset Password", key="switch_to_forgot", use_container_width=True):
                    st.session_state["login_tab"] = "forgot"
                    st.rerun()

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            c_left, c_mid, c_right = st.columns([1, 4, 1])
            with c_mid:
                st.markdown('<p style="font-size:0.85rem;color:#64748b;text-align:center;margin-bottom:4px;">Don\'t have an account?</p>', unsafe_allow_html=True)
                if st.button("Create an Account", key="switch_to_signup", use_container_width=True):
                    st.session_state["login_tab"] = "signup"
                    st.rerun()

        # ── SIGN UP TAB ──
        elif tab == "signup":
            st.markdown("""
            <h2 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.7rem;color:#f8fafc;text-align:center;margin:0 0 4px 0;">Create an account</h2>
            <p style="color:#64748b;font-size:0.88rem;text-align:center;margin:0 0 24px 0;">Sign up to get started</p>
            """, unsafe_allow_html=True)

            email    = st.text_input("Email", placeholder="you@example.com", key="auth_email")
            username = st.text_input("Username", placeholder="Choose a display name", key="auth_username")
            password = st.text_input("Password", placeholder="Min. 6 characters",
                                     type="password", key="auth_password")
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                if not email or not username or not password:
                    st.error("Please fill in all fields.")
                elif len(password) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    ok, err = signup(email, username, password)
                    if ok:
                        st.success("✅ Account created! Please log in.")
                        st.session_state["login_tab"] = "login"
                        st.rerun()
                    else:
                        st.error(f"⚠️ {err}")

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            c_left, c_mid, c_right = st.columns([1, 4, 1])
            with c_mid:
                st.markdown('<p style="font-size:0.85rem;color:#64748b;text-align:center;margin-bottom:4px;">Already have an account?</p>', unsafe_allow_html=True)
                if st.button("Sign In", key="switch_to_login", use_container_width=True):
                    st.session_state["login_tab"] = "login"
                    st.rerun()

        # ── FORGOT PASSWORD TAB ──
        elif tab == "forgot":
            st.markdown("""
            <h2 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.7rem;color:#f8fafc;text-align:center;margin:0 0 4px 0;">Reset Password</h2>
            <p style="color:#64748b;font-size:0.88rem;text-align:center;margin:0 0 24px 0;">Enter your email to receive a reset link</p>
            """, unsafe_allow_html=True)

            email = st.text_input("Email", placeholder="you@example.com", key="fp_email")
            if st.button("Send Reset Link", key="forgot_btn", use_container_width=True):
                if not email:
                    st.error("Please enter your email address.")
                else:
                    ok, err = request_password_reset(email)
                    if ok:
                        st.success("✅ Reset link sent! Check your inbox.")
                        st.session_state["login_tab"] = "login"
                        st.rerun()
                    else:
                        st.error(f"⚠️ {err}")

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            c_left, c_mid, c_right = st.columns([1, 4, 1])
            with c_mid:
                if st.button("← Back to Sign In", key="switch_back_login", use_container_width=True):
                    st.session_state["login_tab"] = "login"
                    st.rerun()

        if supabase is None:
            st.markdown("<hr style='margin:18px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
            st.warning("🔌 Supabase connection is offline or paused. Please check your database settings.")

        st.markdown(
            '<p style="font-size:0.65rem;color:#1e293b;text-align:center;margin-top:24px;margin-bottom:0;letter-spacing:0.5px;">'
            'Developed by Sharvil Mithari · <span style="color:#4f46e5;">SpendWise India 2026</span></p>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    # ── SESSION STATE BOOTSTRAP ──────────────────
    if "page" not in st.session_state:
        st.session_state["page"] = "home"
    if "user" not in st.session_state:
        st.session_state["user"] = None

    # ── ROUTE: LANDING PAGE ──────────────────────
    if st.session_state["page"] == "home" and st.session_state["user"] is None:
        show_landing_page()
        return

    # ── ROUTE: LOGIN / SIGNUP ────────────────────
    if st.session_state["user"] is None:
        inject_css()
        show_login()
        st.markdown("<div style='text-align:center;margin-top:24px;'>", unsafe_allow_html=True)
        if st.button("← Back to Home", key="back_to_home"):
            st.session_state["page"] = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── ROUTE: APP (authenticated) ───────────────
    st.session_state["page"] = "app"
    inject_css()

    user = st.session_state["user"]
    user_uuid = st.session_state["user_uuid"]
    df = load_user_data()
    settings = load_settings(user)
    page = render_sidebar()

    if page == "🏠 Dashboard":
        page_dashboard(df, settings)
    elif page == "🤖 AI Copilot":
        from ai_copilot import ask_ai_copilot, calculate_health_score, generate_automated_insights, get_predictions
        from database import get_goals, get_gemini_key
        
        # Check system key first, then fall back to user key in SQLite
        gemini_api_key = GEMINI_API_KEY if GEMINI_API_KEY else get_gemini_key(user_uuid)
        goals = get_goals(user_uuid)
        health_info = calculate_health_score(df, settings)
        predictions = get_predictions(df, settings)
        
        st.markdown('<div class="page-title">🤖 AI Copilot</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Your personal intelligent financial advisor</div>', unsafe_allow_html=True)
        
        col_main, col_side = st.columns([2, 1])
        
        with col_side:
            st.markdown(f"""
            <div class="metric-card card-balance" style="margin-bottom:15px;">
                <div class="metric-label">Financial Health</div>
                <div class="metric-value balance" style="font-size:1.6rem; margin-top:5px;">{health_info['score']}/100</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0; margin-top:8px;">{health_info['status']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### 💡 AI Suggestions")
            for sug in health_info["suggestions"][:3]:
                st.markdown(f"- {sug}")
                
            st.markdown("##### 📈 Expected Forecast")
            st.markdown(f"- **Expected Income**: ₹{predictions['expected_income']:,.2f}")
            st.markdown(f"- **Expected Expenses**: ₹{predictions['expected_expense']:,.2f}")
            st.markdown(f"- **Expected Net Savings**: ₹{predictions['expected_savings']:,.2f}")
            if predictions['warning']:
                st.warning(predictions['warning'])
                
        with col_main:
            st.markdown("##### ⚡ Ask AI Copilot")
            c_q1, c_q2 = st.columns(2)
            c_q3, c_q4 = st.columns(2)
            
            q_asked = ""
            with c_q1:
                if st.button("📱 Can I afford an iPhone?", use_container_width=True):
                    q_asked = "Can I afford an iPhone?"
            with c_q2:
                if st.button("⚖️ How is my financial health?", use_container_width=True):
                    q_asked = "How is my financial health?"
            with c_q3:
                if st.button("💸 Where am I wasting money?", use_container_width=True):
                    q_asked = "Where am I wasting money?"
            with c_q4:
                if st.button("📊 How can I save ₹5000 this month?", use_container_width=True):
                    q_asked = "How can I save ₹5000 this month?"
                    
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []
                
            user_input = st.text_input("Ask a question about your finances...", value=q_asked if q_asked else "", placeholder="e.g. Will I run out of money?")
            send_btn = st.button("💬 Send to Copilot")
            
            if (send_btn or q_asked) and user_input:
                with st.spinner("Analyzing your transactions and thinking..."):
                    answer = ask_ai_copilot(df, settings, goals, user_input, gemini_api_key)
                    st.session_state["chat_history"].append({"user": user_input, "ai": answer})
                    
            if st.session_state["chat_history"]:
                st.markdown("<br>##### 💬 Conversation History", unsafe_allow_html=True)
                for chat in st.session_state["chat_history"]:
                    st.markdown(f"""
                    <div class="chat-bubble-user">
                        <strong>👤 You:</strong> {chat['user']}
                    </div>
                    <div class="chat-bubble-ai">
                        <strong>🤖 Copilot:</strong><br>{chat['ai']}
                    </div>
                    """, unsafe_allow_html=True)
                    
    elif page == "👥 Split Bills":
        from split_bills import page_split_bills
        page_split_bills(user_uuid, user)
        
    elif page == "🎯 Smart Goals":
        from goals import page_smart_goals
        page_smart_goals(df, user_uuid)
        
    elif page == "💰 Expense Tracker":
        page_add_transaction(df, settings)
        
    elif page == "📋 History":
        page_history(df)
        
    elif page == "📈 Analytics":
        page_analytics(df)
        
    elif page == "⚙️ Settings":
        updated = page_settings(settings)
        if updated is not None:
            settings = updated


if __name__ == "__main__":
    main()