import streamlit as st
import pandas as pd
import json
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#  CONFIGURATION & CONSTANTS

DATA_FILE = "expense_data.json"          # Local storage file
SETTINGS_FILE = "settings.json"          # Budget & limit settings

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

# Color palette for charts
CHART_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE"
]


#  PAGE CONFIG — must be first Streamlit call


st.set_page_config(
    page_title="Student Expense Tracker 🇮🇳",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

#  CUSTOM CSS — Professional Dark Theme


def inject_css():
    """Inject custom CSS for a polished, professional look."""
    st.markdown("""
    <style>
    /* ── Google Font Import ── */
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif;
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── App Background ── */
    .stApp {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #0D1117 100%);
        color: #E6EDF3;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161B22 0%, #21262D 100%);
        border-right: 1px solid #30363D;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-family: 'Sora', sans-serif;
        font-size: 0.9rem;
        color: #8B949E;
        padding: 6px 0;
        transition: color 0.2s;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        color: #58A6FF;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: linear-gradient(145deg, #1C2128, #21262D);
        border: 1px solid #30363D;
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }

    .card-income::before  { background: linear-gradient(90deg, #3FB950, #56D364); }
    .card-expense::before { background: linear-gradient(90deg, #F85149, #FF6B6B); }
    .card-balance::before { background: linear-gradient(90deg, #58A6FF, #79C0FF); }
    .card-budget::before  { background: linear-gradient(90deg, #D2A8FF, #BC8CFF); }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8B949E;
        margin-bottom: 8px;
    }

    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }

    .metric-value.income  { color: #3FB950; }
    .metric-value.expense { color: #F85149; }
    .metric-value.balance { color: #58A6FF; }
    .metric-value.budget  { color: #D2A8FF; }

    .metric-sub {
        font-size: 0.78rem;
        color: #6E7681;
        margin-top: 6px;
    }

    /* ── Section Headers ── */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #E6EDF3;
        border-left: 4px solid #58A6FF;
        padding-left: 14px;
        margin: 28px 0 18px 0;
        letter-spacing: -0.3px;
    }

    /* ── Warning / Success Banners ── */
    .banner {
        border-radius: 10px;
        padding: 14px 20px;
        margin: 12px 0;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .banner-danger {
        background: rgba(248, 81, 73, 0.15);
        border: 1px solid rgba(248, 81, 73, 0.4);
        color: #FF6B6B;
    }

    .banner-warn {
        background: rgba(210, 153, 34, 0.15);
        border: 1px solid rgba(210, 153, 34, 0.4);
        color: #F0B429;
    }

    .banner-success {
        background: rgba(63, 185, 80, 0.15);
        border: 1px solid rgba(63, 185, 80, 0.4);
        color: #3FB950;
    }

    /* ── Form Styling ── */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        background: #21262D !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        color: #E6EDF3 !important;
        font-family: 'Sora', sans-serif !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #238636, #2EA043) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2EA043, #3FB950) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(63,185,80,0.3) !important;
    }

    /* ── Dataframe Table ── */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #30363D;
    }

    /* ── Sidebar Logo ── */
    .sidebar-logo {
        text-align: center;
        padding: 20px 0 10px;
    }

    .sidebar-logo .logo-icon {
        font-size: 2.8rem;
        display: block;
        margin-bottom: 6px;
    }

    .sidebar-logo .logo-title {
        font-size: 1rem;
        font-weight: 700;
        color: #E6EDF3;
        letter-spacing: -0.3px;
    }

    .sidebar-logo .logo-sub {
        font-size: 0.72rem;
        color: #6E7681;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .sidebar-divider {
        border: none;
        border-top: 1px solid #30363D;
        margin: 16px 0;
    }

    /* ── Tag pills ── */
    .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .pill-income  { background: rgba(63,185,80,0.2);  color: #3FB950; }
    .pill-expense { background: rgba(248,81,73,0.2);  color: #F85149; }

    /* ── Chart container ── */
    .chart-container {
        background: #1C2128;
        border: 1px solid #30363D;
        border-radius: 14px;
        padding: 20px;
    }

    /* ── Page title ── */
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #E6EDF3;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .page-subtitle {
        font-size: 0.9rem;
        color: #6E7681;
        margin-bottom: 28px;
    }

    /* ── Divider ── */
    hr { border-color: #30363D !important; }

    /* ── Radio buttons ── */
    .stRadio > div { gap: 8px; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #1C2128;
        border-radius: 10px;
        gap: 4px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8B949E;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
    }

    .stTabs [aria-selected="true"] {
        background: #58A6FF !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)



#  DATA LAYER — Load / Save / CRUD


def load_data() -> pd.DataFrame:
    """Load transactions from JSON file. Returns empty DataFrame if file missing."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r",encoding="utf-8") as f:
            records = json.load(f)
        if records:
            df = pd.DataFrame(records)
            df["date"] = pd.to_datetime(df["date"],errors ="coerce")
            df = df.dropna(subset=["date"])

            df["amount"] = df["amount"].astype(float)
            return df
        
    # Return empty DataFrame with correct columns

    return pd.DataFrame(columns=["id", "type", "amount", "category", "date", "notes"])


def save_data(df: pd.DataFrame):
    """Persist DataFrame to JSON file."""
    records = df.copy()
    records["date"] = records["date"].astype(str)   # Serialize datetime
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records.to_dict(orient="records"), f, indent=2,ensure_ascii=False)


def load_settings() -> dict:
    """Load budget & daily limit settings."""
    defaults = {"monthly_budget": 0.0, "daily_limit": 0.0}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r" , encoding="utf=8") as f:
            return {**defaults, **json.load(f)}
    return defaults


def save_settings(settings: dict):
    """Persist settings to JSON."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def add_transaction(df: pd.DataFrame, t_type: str, amount: float,
                    category: str, date, notes: str) -> pd.DataFrame:
    """Append a new transaction row and return updated DataFrame."""
    new_id = int(df["id"].max() + 1) if not df.empty else 1
    new_row = {
        "id": new_id,
        "type": t_type,
        "amount": amount,
        "category": category,
        "date": pd.to_datetime(date),
        "notes": notes,
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)


def delete_transaction(df: pd.DataFrame, row_id: int) -> pd.DataFrame:
    """Remove a transaction by ID."""
    return df[df["id"] != row_id].reset_index(drop=True)



#  CALCULATIONS


def get_summary(df: pd.DataFrame) -> dict:
    """Calculate total income, expenses, and balance."""
    total_income  = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    balance       = total_income - total_expense
    return {
        "income":  total_income,
        "expense": total_expense,
        "balance": balance,
    }


def get_today_expense(df):
    df = df.copy()

    # ✅ Fix date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    today = pd.Timestamp.now().normalize()

    mask = (df["type"] == "Expense") & \
           (df["date"].dt.normalize() == today)

    return df[mask]["amount"].sum()


def get_this_month_expense(df: pd.DataFrame) -> float:
    df = df.copy()  # ✅ important

    # ✅ fix date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    now = pd.Timestamp.now()

    mask = (df["type"] == "Expense") & \
           (df["date"].dt.year == now.year) & \
           (df["date"].dt.month == now.month)

    return df[mask]["amount"].sum()


def fmt(amount: float) -> str:
    """Format number as Indian Rupee string with commas."""
    return f"₹{amount:,.2f}"


#  UI COMPONENTS


def render_metric_card(label: str, value: str, card_class: str,
                       value_class: str, sub: str = ""):
    """Render a styled metric card via HTML."""
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card {card_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {value_class}">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_banner(message: str, level: str = "warn"):
    """Render a colored alert banner (danger / warn / success)."""
    st.markdown(f'<div class="banner banner-{level}">{message}</div>',
                unsafe_allow_html=True)


def render_section_header(title: str):
    """Render a styled section heading."""
    st.markdown(f'<div class="section-header">{title}</div>',
                unsafe_allow_html=True)



#  PAGE: DASHBOARD


def page_dashboard(df: pd.DataFrame, settings: dict):
      # ✅ FIX DATE ISSUE (ADD THIS BLOCK)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    """Main dashboard: summary cards + alerts + recent transactions."""
    st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your financial snapshot for this month</div>',
                unsafe_allow_html=True)

    summary = get_summary(df)
    month_expense = get_this_month_expense(df)
    today_expense = get_today_expense(df)

    # ── Summary Cards ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Income", fmt(summary["income"]),
                           "card-income", "income", "All time")
    with c2:
        render_metric_card("Total Expenses", fmt(summary["expense"]),
                           "card-expense", "expense", "All time")
    with c3:
        render_metric_card("Net Balance", fmt(summary["balance"]),
                           "card-balance", "balance",
                           "✅ Surplus" if summary["balance"] >= 0 else "⚠️ Deficit")
    with c4:
        budget = settings["monthly_budget"]
        remaining = budget - month_expense if budget > 0 else 0
        sub = fmt(remaining) + " left" if budget > 0 else "No budget set"
        render_metric_card("Monthly Budget", fmt(budget),
                           "card-budget", "budget", sub)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Budget Alerts ──
    budget = settings["monthly_budget"]
    if budget > 0:
        pct = (month_expense / budget) * 100
        if month_expense > budget:
            render_banner(
                f"🚨 Budget exceeded! You've spent {fmt(month_expense)} of your "
                f"{fmt(budget)} budget this month ({pct:.0f}%).", "danger"
            )
        elif pct >= 80:
            render_banner(
                f"⚠️ Heads up! You've used {pct:.0f}% of your monthly budget. "
                f"Only {fmt(budget - month_expense)} remaining.", "warn"
            )
        else:
            render_banner(
                f"✅ Budget on track! {fmt(budget - month_expense)} remaining "
                f"({100 - pct:.0f}% left).", "success"
            )

    # ── Daily Limit Alert ──
    daily_limit = settings.get("daily_limit", 0)
    if daily_limit > 0 and today_expense > daily_limit:
        render_banner(
            f"🔴 Daily limit breached! Today's spending: {fmt(today_expense)} "
            f"(limit: {fmt(daily_limit)}).", "danger"
        )

    # ── This Month's Mini Stats ──
    render_section_header("📅 This Month at a Glance")
    m1, m2, m3 = st.columns(3)
    tx_count = len(df[
        (df["date"].dt.year == pd.Timestamp.now().year) &
        (df["date"].dt.month == pd.Timestamp.now().month)
    ])
    with m1:
        st.metric("Month Expenses", fmt(month_expense))
    with m2:
        st.metric("Today's Spending", fmt(today_expense))
    with m3:
        st.metric("Transactions This Month", tx_count)

    # ── Recent Transactions ──
    render_section_header("🕐 Recent Transactions")
    if df.empty:
        st.info("No transactions yet. Add your first transaction from the sidebar!")
    else:
        recent = df.sort_values("date", ascending=False).head(10).copy()
        recent["date"] = recent["date"].dt.strftime("%d %b %Y")
        recent["amount"] = recent["amount"].apply(fmt)
        recent = recent[["date", "type", "category", "amount", "notes"]].rename(
            columns={"date": "Date", "type": "Type", "category": "Category",
                     "amount": "Amount", "notes": "Notes"}
        )
        st.dataframe(recent, use_container_width=True, hide_index=True)



#  PAGE: ADD TRANSACTION


def page_add_transaction(df: pd.DataFrame, settings: dict):
    """Form to add a new income or expense entry."""
    st.markdown('<div class="page-title">➕ Add Transaction</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Record your income or expenses</div>',
                unsafe_allow_html=True)

    with st.form("add_txn_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            t_type = st.selectbox("Transaction Type", ["Expense", "Income"])
            amount = st.number_input("Amount (₹)", min_value=0.01,
                                     value=100.0, step=10.0, format="%.2f")
            date   = st.date_input("Date", value=datetime.date.today())

        with col2:
            # Switch category list based on type
            cats = EXPENSE_CATEGORIES if t_type == "Expense" else INCOME_CATEGORIES
            category = st.selectbox("Category", cats)
            notes    = st.text_area("Notes (optional)", placeholder="e.g. Lunch at canteen…",
                                    height=120)

        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)

        if submitted:
            # Validate amount
            if amount <= 0:
                st.error("Please enter a valid amount greater than ₹0.")
            else:
                # Check daily limit
                daily_limit = settings.get("daily_limit", 0)
                if t_type == "Expense" and daily_limit > 0:
                    today_total = get_today_expense(df) + amount
                    if today_total > daily_limit:
                        st.warning(
                            f"⚠️ Adding this will exceed your daily limit! "
                            f"(Today total: {fmt(today_total)}, Limit: {fmt(daily_limit)})"
                        )

                # Add & save
                updated = add_transaction(df, t_type, amount, category, date, notes)
                save_data(updated)
                st.session_state["df"] = updated
                st.success(f"✅ {t_type} of {fmt(amount)} added successfully!")
                st.balloons()

    # ── Quick budget status reminder ──
    if settings["monthly_budget"] > 0:
        month_expense = get_this_month_expense(df)
        remaining     = settings["monthly_budget"] - month_expense
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("💡 Budget Reminder")
        pct = (month_expense / settings["monthly_budget"]) * 100
        st.progress(min(pct / 100, 1.0))
        st.caption(
            f"Spent {fmt(month_expense)} of {fmt(settings['monthly_budget'])} "
            f"({pct:.1f}%) — {fmt(max(remaining, 0))} remaining this month"
        )



#  PAGE: TRANSACTION HISTORY


def page_history(df: pd.DataFrame):
    """Display filterable transaction history with delete & CSV export."""
    st.markdown('<div class="page-title">📋 Transaction History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse, filter, and manage all your records</div>',
                unsafe_allow_html=True)

    if df.empty:
        st.info("No transactions recorded yet. Start by adding one!")
        return

    # ── Filters ──
    render_section_header("🔍 Filters")
    f1, f2, f3 = st.columns(3)

    with f1:
        type_filter = st.selectbox("Type", ["All", "Income", "Expense"])
    with f2:
        all_cats = ["All"] + sorted(df["category"].unique().tolist())
        cat_filter = st.selectbox("Category", all_cats)
    with f3:
        months = ["All"] + sorted(
            df["date"].dt.strftime("%b %Y").unique().tolist(), reverse=True
        )
        month_filter = st.selectbox("Month", months)

    # Apply filters
    filtered = df.copy()
    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if month_filter != "All":
        filtered = filtered[filtered["date"].dt.strftime("%b %Y") == month_filter]

    # ── Export ──
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

    # ── Display table ──
    display = filtered.sort_values("date", ascending=False).copy()
    display["date"]   = display["date"].dt.strftime("%d %b %Y")
    display["amount"] = display["amount"].apply(fmt)
    display = display[["id", "date", "type", "category", "amount", "notes"]].rename(
        columns={"id": "ID", "date": "Date", "type": "Type",
                 "category": "Category", "amount": "Amount", "notes": "Notes"}
    )
    st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Delete transaction ──
    render_section_header("🗑️ Delete Transaction")
    del_id = st.number_input("Enter Transaction ID to delete", min_value=1, step=1)
    if st.button("Delete"):
        if del_id in df["id"].values:
            updated = delete_transaction(df, int(del_id))
            save_data(updated)
            st.session_state["df"] = updated
            st.success(f"Transaction #{int(del_id)} deleted.")
            st.rerun()
        else:
            st.error(f"No transaction found with ID {int(del_id)}.")



#  PAGE: ANALYTICS


def page_analytics(df: pd.DataFrame):
    """Charts: pie by category + bar by month."""
    st.markdown('<div class="page-title">📈 Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visual breakdown of your spending patterns</div>',
                unsafe_allow_html=True)

    if df.empty or df[df["type"] == "Expense"].empty:
        st.info("Add some expense transactions to see analytics.")
        return

    expenses = df[df["type"] == "Expense"].copy()

    # ── Tabs ──
    tab1, tab2, tab3 = st.tabs(["🥧 Category Breakdown", "📊 Monthly Trend", "📋 Summary Table"])

    # ── Pie Chart ──────────────────────────────
    with tab1:
        cat_totals = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor("#1C2128")
        ax.set_facecolor("#1C2128")

        wedges, texts, autotexts = ax.pie(
            cat_totals,
            labels=None,
            autopct="%1.1f%%",
            colors=CHART_COLORS[:len(cat_totals)],
            startangle=140,
            pctdistance=0.82,
            wedgeprops=dict(width=0.6, edgecolor="#1C2128", linewidth=2),
        )

        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(10)
            at.set_fontweight("bold")

        # Legend
        legend_patches = [
            mpatches.Patch(color=CHART_COLORS[i], label=f"{cat}  {fmt(val)}")
            for i, (cat, val) in enumerate(cat_totals.items())
        ]
        ax.legend(handles=legend_patches, loc="center left", bbox_to_anchor=(1, 0.5),
                  fontsize=9, frameon=False, labelcolor="white")

        ax.set_title("Expense by Category", color="#E6EDF3", fontsize=14,
                     fontweight="bold", pad=18)

        st.pyplot(fig, use_container_width=True)
        plt.close()

    # ── Bar Chart ──────────────────────────────
    with tab2:
        expenses["month"] = expenses["date"].dt.to_period("M")
        monthly = expenses.groupby("month")["amount"].sum().reset_index()
        monthly["month_str"] = monthly["month"].astype(str)
        monthly = monthly.sort_values("month")

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#1C2128")
        ax.set_facecolor("#1C2128")

        bars = ax.bar(
            monthly["month_str"],
            monthly["amount"],
            color=CHART_COLORS[0],
            edgecolor="#1C2128",
            linewidth=0.5,
            width=0.5,
        )

        # Color highest bar differently
        if len(bars) > 0:
            max_idx = monthly["amount"].idxmax()
            bars[monthly.index.get_loc(max_idx)].set_color(CHART_COLORS[2])

        # Value labels on bars
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + (monthly["amount"].max() * 0.01),
                    fmt(h), ha="center", va="bottom", color="#E6EDF3", fontsize=8)

        ax.set_facecolor("#1C2128")
        ax.tick_params(colors="#8B949E", labelsize=9)
        ax.spines["bottom"].set_color("#30363D")
        ax.spines["left"].set_color("#30363D")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlabel("Month", color="#8B949E", fontsize=10)
        ax.set_ylabel("Total Expense (₹)", color="#8B949E", fontsize=10)
        ax.set_title("Monthly Spending Trend", color="#E6EDF3", fontsize=14,
                     fontweight="bold", pad=14)
        ax.yaxis.label.set_color("#8B949E")

        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # ── Summary Table ──────────────────────────
    with tab3:
        render_section_header("💰 Category-wise Summary")
        summary = expenses.groupby("category")["amount"].agg(["sum", "count", "mean"])
        summary.columns = ["Total Spent", "Transactions", "Avg per Transaction"]
        summary["Total Spent"] = summary["Total Spent"].apply(fmt)
        summary["Avg per Transaction"] = summary["Avg per Transaction"].apply(fmt)
        summary = summary.sort_values("Transactions", ascending=False)
        st.dataframe(summary, use_container_width=True)


# ─────────────────────────────────────────────
#  PAGE: SETTINGS
# ─────────────────────────────────────────────

def page_settings(settings: dict) -> dict:
    """Budget & daily limit configuration page."""
    st.markdown('<div class="page-title">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Configure your budget and spending limits</div>',
                unsafe_allow_html=True)

    render_section_header("💼 Monthly Budget")
    budget = st.number_input(
        "Set your monthly budget (₹)",
        min_value=0.0,
        value=float(settings.get("monthly_budget", 0)),
        step=500.0,
        format="%.2f",
        help="Set ₹0 to disable budget tracking",
    )

    render_section_header("🔔 Daily Expense Limit")
    daily = st.number_input(
        "Set daily expense limit (₹)",
        min_value=0.0,
        value=float(settings.get("daily_limit", 0)),
        step=50.0,
        format="%.2f",
        help="You'll be warned when you exceed this each day. Set ₹0 to disable.",
    )

    if st.button("💾 Save Settings"):
        new_settings = {"monthly_budget": budget, "daily_limit": daily}
        save_settings(new_settings)
        st.success("✅ Settings saved!")
        return new_settings

    return settings


#  SIDEBAR

def render_sidebar() -> str:
    with st.sidebar:

        st.image("logo.png", width=230)  # ✅ correct place

        st.markdown("""
<hr class="sidebar-divider">
""", unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["📊 Dashboard", "➕ Add Transaction", "📋 History",
             "📈 Analytics", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.72rem; color: #6E7681; text-align: center; padding: 8px 0;">
            Built by Sharvil Mithari using Python & Streamlit<br>
            <span style="color: #3FB950;">Open Source · LinkedIn Ready</span>
        </div>
        """, unsafe_allow_html=True)

    return page



#  MAIN ENTRY POINT


def main():
    inject_css()

    # ── Load data into session state (persist across reruns) ──
    if "df" not in st.session_state:
        st.session_state["df"] = load_data()
    if "settings" not in st.session_state:
        st.session_state["settings"] = load_settings()

    df       = st.session_state["df"]
    settings = st.session_state["settings"]

    # ── Sidebar navigation ──
    page = render_sidebar()

    # ── Route to correct page ──
    if page == "📊 Dashboard":
        page_dashboard(df, settings)

    elif page == "➕ Add Transaction":
        page_add_transaction(df, settings)
        # Reload df after potential add
        st.session_state["df"] = load_data()

    elif page == "📋 History":
        page_history(df)

    elif page == "📈 Analytics":
        page_analytics(df)

    elif page == "⚙️ Settings":
        new_settings = page_settings(settings)
        st.session_state["settings"] = new_settings


if __name__ == "__main__":
    main()


if "data" not in st.session_state:
    st.session_state.data = load_data()