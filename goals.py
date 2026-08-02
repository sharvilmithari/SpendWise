import streamlit as st
import datetime
import pandas as pd
from database import get_goals, add_goal, delete_goal_db, update_goal_progress_db

# ─────────────────────────────────────────────
#  SMART GOALS CALCULATIONS & UI VIEWS
# ─────────────────────────────────────────────

def get_savings_trend(df: pd.DataFrame) -> float:
    """Calculate the average monthly net savings (Income - Expense) over tracked months."""
    if df.empty:
        return 0.0
        
    monthly_data = df.copy()
    monthly_data["month"] = monthly_data["date"].dt.to_period("M")
    
    # Sum income and expenses per month
    grouped = monthly_data.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    if grouped.empty:
        return 0.0
        
    if "Income" not in grouped.columns:
        grouped["Income"] = 0.0
    if "Expense" not in grouped.columns:
        grouped["Expense"] = 0.0
        
    incomes = grouped["Income"]
    expenses = grouped["Expense"]
    
    monthly_savings = incomes - expenses
    
    import math
    avg_savings = float(monthly_savings.mean())
    if math.isnan(avg_savings):
        return 0.0
    return avg_savings

def page_smart_goals(df: pd.DataFrame, user_uuid: str):
    st.markdown('<div class="page-title">Smart Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Set financial targets and let AI calculate timelines and success probabilities</div>', unsafe_allow_html=True)
    
    # Load goals
    goals = get_goals(user_uuid)
    avg_monthly_savings = get_savings_trend(df)
    
    # Layout: Create a Goal vs Active Goals list
    tab_active, tab_new = st.tabs(["🎯 Active Goals", "➕ Create Goal"])
    
    # ── TAB 1: ACTIVE GOALS ──
    with tab_active:
        if not goals:
            st.info("💡 You have no active goals. Click the 'Create Goal' tab to define your first financial milestone!")
        else:
            st.markdown(f"ℹ️ **Current Savings Trend**: Your average net savings is **₹{avg_monthly_savings:,.2f}/month** (based on transaction history).")
            st.markdown("<br>", unsafe_allow_html=True)
            
            for goal in goals:
                g_id = goal["id"]
                name = goal["name"]
                target = goal["target_amount"]
                current = goal["current_amount"]
                target_date = pd.to_datetime(goal["target_date"])
                
                # Math calculations
                today = datetime.datetime.now().date()
                delta_days = (target_date.date() - today).days
                months_remaining = max(0.1, delta_days / 30.4)
                
                remaining_amt = max(0.0, target - current)
                required_monthly = remaining_amt / months_remaining if remaining_amt > 0 else 0.0
                
                # Progress Percentage
                progress_pct = (current / target) * 100 if target > 0 else 100.0
                progress_pct = min(100.0, max(0.0, progress_pct))
                
                # Success Probability & Completion Date Projection
                if remaining_amt == 0:
                    prob = "🎉 COMPLETED"
                    prob_color = "#34d399"
                    est_finish = "Completed"
                elif avg_monthly_savings <= 0:
                    prob = "🔴 Low (0% - 5%) - Negative Savings Trend"
                    prob_color = "#f87171"
                    est_finish = "Never (Net savings is negative)"
                else:
                    ratio = avg_monthly_savings / required_monthly
                    if ratio >= 1.0:
                        prob = "🟢 High (90%+)"
                        prob_color = "#34d399"
                    elif ratio >= 0.7:
                        prob = "🟡 Medium (60% - 85%)"
                        prob_color = "#fcd34d"
                    else:
                        prob = "🔴 Low (10% - 40%) - Increase savings to match"
                        prob_color = "#f87171"
                        
                    import math
                    months_to_go = remaining_amt / avg_monthly_savings
                    # Guard: NaN / Inf check before timedelta
                    if math.isnan(months_to_go) or math.isinf(months_to_go) or months_to_go < 0:
                        est_finish = "Insufficient data to project"
                    else:
                        days_to_go = int(min(months_to_go * 30.4, 36500))  # cap at 100 years
                        finish_date = datetime.datetime.now() + datetime.timedelta(days=days_to_go)
                        est_finish = finish_date.strftime("%B %Y")
                    
                # Card Rendering
                st.markdown(f"""
                <div class="goal-card">
                    <div class="goal-card-header">
                        <span class="goal-card-name">🎯 {name}</span>
                        <span class="goal-card-amount">₹{current:,.0f} / ₹{target:,.0f}</span>
                    </div>
                    <div class="goal-card-deadline">
                        Target Deadline: {target_date.strftime('%d %b %Y')} ({months_remaining:.1f} months left)
                    </div>
                """, unsafe_allow_html=True)
                
                # Render progress bar
                st.progress(progress_pct / 100.0)
                
                st.markdown(f"""
                    <div class="goal-stats-grid">
                        <div>
                            <div class="goal-stat-label">Req. Savings / Mo</div>
                            <div class="goal-stat-value purple">₹{required_monthly:,.2f}</div>
                        </div>
                        <div>
                            <div class="goal-stat-label">Success Probability</div>
                            <div class="goal-stat-value" style="color:{prob_color}; font-weight:600; margin-top:4px;">{prob}</div>
                        </div>
                        <div>
                            <div class="goal-stat-label">AI Estimated Finish</div>
                            <div class="goal-stat-value white">{est_finish}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Inline controls: Update amount saved & Delete goal
                col_up, col_del = st.columns([3, 1])
                
                with col_up:
                    with st.expander(f"⚙️ Update Progress for {name}"):
                        new_saved = st.number_input("Current amount saved (₹)", min_value=0.0, max_value=float(target), value=float(current), key=f"amt_{g_id}")
                        if st.button("Update Amount", key=f"up_{g_id}"):
                            update_goal_progress_db(user_uuid, g_id, new_saved)
                            st.success(f"Goal progress updated to ₹{new_saved:,.2f}!")
                            st.rerun()
                            
                with col_del:
                    if st.button("🗑️ Delete Goal", key=f"del_{g_id}", use_container_width=True):
                        delete_goal_db(user_uuid, g_id)
                        st.success(f"Goal '{name}' removed.")
                        st.rerun()
                        
                st.markdown("<br>", unsafe_allow_html=True)

    # ── TAB 2: CREATE GOAL ──
    with tab_new:
        st.markdown("##### Setup a New Goal Target")
        with st.form("new_goal_form", clear_on_submit=True):
            g_name = st.text_input("Goal Name", placeholder="e.g. Macbook Air, Emergency Fund, Bali Vacation")
            target_amt = st.number_input("Target Amount (₹)", min_value=0.0, step=500.0)
            initial_saved = st.number_input("Already Saved (₹)", min_value=0.0, step=100.0)
            deadline = st.date_input("Target Date", value=datetime.date.today() + datetime.timedelta(days=365))
            
            submit_g = st.form_submit_button("💾 Save smart goal")
            
            if submit_g:
                if not g_name:
                    st.error("Please enter a goal name.")
                elif target_amt <= 0:
                    st.error("Please enter a valid target amount greater than ₹0.")
                elif initial_saved > target_amt:
                    st.error("Already saved amount cannot exceed target amount.")
                elif deadline <= datetime.date.today():
                    st.error("Deadline must be in the future.")
                else:
                    add_goal(user_uuid, g_name, target_amt, initial_saved, str(deadline))
                    st.success(f"✅ Goal '{g_name}' configured successfully!")
                    st.rerun()
