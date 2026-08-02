import os
import datetime
import requests
import json
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────
#  FINANCIAL HEALTH SCORE CALCULATOR
# ─────────────────────────────────────────────

def calculate_health_score(df: pd.DataFrame, settings: dict) -> dict:
    """
    Calculate Financial Health Score (0-100) based on:
    - Savings Rate (40%)
    - Expense Ratio (20%)
    - Budget Usage (20%)
    - Income Stability / Consistency (20%)
    """
    if df.empty:
        return {
            "score": 50,
            "status": "Neutral Financial Health",
            "suggestions": [
                "Start tracking your income and expenses to get an accurate financial health score.",
                "Set a monthly budget in the Settings tab."
            ]
        }

    # Calculations for current month
    now = datetime.datetime.now()
    month_mask = (df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)
    df_month = df[month_mask]
    
    total_income = df_month[df_month["type"] == "Income"]["amount"].sum()
    total_expense = df_month[df_month["type"] == "Expense"]["amount"].sum()
    
    # Fallback to all-time averages if current month has no data
    if total_income == 0 and total_expense == 0:
        total_income = df[df["type"] == "Income"]["amount"].sum() / max(1, len(df["date"].dt.to_period("M").unique()))
        total_expense = df[df["type"] == "Expense"]["amount"].sum() / max(1, len(df["date"].dt.to_period("M").unique()))

    # 1. Savings Rate Sub-score (40 points)
    # Savings Rate = (Income - Expense) / Income
    savings_rate_score = 0.0
    savings_rate = 0.0
    if total_income > 0:
        savings = total_income - total_expense
        savings_rate = savings / total_income
        if savings_rate >= 0.30:  # 30% or more savings is excellent
            savings_rate_score = 40.0
        elif savings_rate > 0:
            savings_rate_score = (savings_rate / 0.30) * 40.0
        else:
            savings_rate_score = 0.0
    else:
        # If no income, check if they spent money
        savings_rate_score = 0.0 if total_expense > 0 else 20.0

    # 2. Expense Ratio Sub-score (20 points)
    # Ideal: <= 50%
    expense_ratio_score = 0.0
    if total_income > 0:
        ratio = total_expense / total_income
        if ratio <= 0.50:
            expense_ratio_score = 20.0
        elif ratio <= 1.0:
            expense_ratio_score = 20.0 - ((ratio - 0.50) * 40.0) # Down to 0 at 100% expense
        else:
            expense_ratio_score = 0.0
    else:
        expense_ratio_score = 0.0 if total_expense > 0 else 10.0

    # 3. Budget Usage Sub-score (20 points)
    budget = settings.get("monthly_budget", 0.0)
    budget_score = 0.0
    if budget > 0:
        usage = total_expense / budget
        if usage <= 0.80:
            budget_score = 20.0
        elif usage <= 1.00:
            budget_score = 20.0 - ((usage - 0.80) * 100.0) # Drops to 0 at 100% budget usage
        else:
            budget_score = 0.0
    else:
        budget_score = 12.0 # Neutral fallback for not setting budget

    # 4. Income Stability / Consistency (20 points)
    # Check if there is income in recent months
    all_income = df[df["type"] == "Income"]
    if not all_income.empty:
        income_months = len(all_income["date"].dt.to_period("M").unique())
        total_tracked_months = max(1, len(df["date"].dt.to_period("M").unique()))
        consistency = income_months / total_tracked_months
        income_score = consistency * 20.0
    else:
        income_score = 0.0

    # Total Score
    score = int(savings_rate_score + expense_ratio_score + budget_score + income_score)
    score = max(0, min(100, score))

    # Evaluate Status & Suggestions
    suggestions = []
    if score >= 85:
        status = "Excellent Financial Health"
        suggestions.append("🌟 Maintain your excellent savings rate. Consider allocating funds to long-term investments.")
        suggestions.append("💼 Maintain your emergency fund representing 6 months of expenses.")
    elif score >= 70:
        status = "Good Financial Health"
        suggestions.append("📈 Good job! Try to increase your savings rate to 30% by cutting small daily expenses.")
        suggestions.append("🛒 Keep shopping and discretionary categories under strict check.")
    elif score >= 50:
        status = "Average Financial Health"
        suggestions.append("⚠️ Budget warning: Your expenses are consuming a large share of your income.")
        suggestions.append("🍱 Look to optimize food and dining expenses, which are often the easiest to reduce.")
        if budget == 0:
            suggestions.append("🎯 Set a Monthly Budget in Settings to better track your allocations.")
    else:
        status = "Critical Financial Health"
        suggestions.append("🚨 Action required: You are spending more than you earn, or have very little savings.")
        suggestions.append("🛑 Stop all non-essential discretionary spending immediately.")
        suggestions.append("📉 Create a strict monthly budget and build a ₹10,000 emergency fund immediately.")

    # Specific suggestion based on expense categories
    expenses_df = df[df["type"] == "Expense"]
    if not expenses_df.empty:
        cat_totals = expenses_df.groupby("category")["amount"].sum()
        top_cat = cat_totals.idxmax()
        top_cat_pct = (cat_totals.max() / cat_totals.sum()) * 100
        if top_cat_pct > 35:
            suggestions.append(f"🔍 Your highest expense is {top_cat} ({top_cat_pct:.0f}% of expenses). Focus on lowering this category.")

    return {
        "score": score,
        "status": status,
        "savings_rate": savings_rate,
        "suggestions": suggestions
    }


# ─────────────────────────────────────────────
#  AUTOMATED INSIGHTS ENGINE
# ─────────────────────────────────────────────

def generate_automated_insights(df: pd.DataFrame, settings: dict, goals: list = None) -> list:
    """Generate dynamic insights based on transactions and goal status."""
    insights = []
    if df.empty:
        return ["💡 Welcome to SpendWise Copilot! Start logging transactions to view live AI insights here."]

    now = datetime.datetime.now()
    
    # 1. Monthly growth / savings rate
    this_month_mask = (df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)
    last_month_date = now.replace(day=1) - datetime.timedelta(days=1)
    last_month_mask = (df["date"].dt.year == last_month_date.year) & (df["date"].dt.month == last_month_date.month)
    
    df_this = df[this_month_mask]
    df_last = df[last_month_mask]
    
    # Compare Food spending
    food_this = df_this[(df_this["type"] == "Expense") & (df_this["category"].str.contains("Food|🍱", case=False))]["amount"].sum()
    food_last = df_last[(df_last["type"] == "Expense") & (df_last["category"].str.contains("Food|🍱", case=False))]["amount"].sum()
    if food_last > 0:
        increase = ((food_this - food_last) / food_last) * 100
        if increase >= 15:
            insights.append(f"📈 Food spending increased by {increase:.0f}% compared to last month.")
        elif increase <= -15:
            insights.append(f"📉 Good work! Food & dining expenses dropped by {abs(increase):.0f}%.")

    # Discretionary / Entertainment check
    ent_this = df_this[(df_this["type"] == "Expense") & (df_this["category"].str.contains("Entertainment|🎮|Shopping|🛍️", case=False))]["amount"].sum()
    total_exp_this = df_this[df_this["type"] == "Expense"]["amount"].sum()
    if total_exp_this > 0:
        pct = (ent_this / total_exp_this) * 100
        if pct > 25:
            insights.append(f"⚠️ Entertainment & Shopping make up {pct:.0f}% of this month's spending. Consider lowering it.")

    # Shopping expense comparison
    shop_this = df_this[(df_this["type"] == "Expense") & (df_this["category"].str.contains("Shopping|🛍️", case=False))]["amount"].sum()
    shop_last = df_last[(df_last["type"] == "Expense") & (df_last["category"].str.contains("Shopping|🛍️", case=False))]["amount"].sum()
    if shop_last > 0 and shop_this < shop_last:
        insights.append("📉 Shopping expenses dropped this month. Excellent self-control!")

    # Savings comparison
    inc_this = df_this[df_this["type"] == "Income"]["amount"].sum()
    inc_last = df_last[df_last["type"] == "Income"]["amount"].sum()
    exp_this = df_this[df_this["type"] == "Expense"]["amount"].sum()
    exp_last = df_last[df_last["type"] == "Expense"]["amount"].sum()
    
    sav_this = max(0, inc_this - exp_this)
    sav_last = max(0, inc_last - exp_last)
    
    if sav_last > 0 and sav_this > sav_last:
        inc_pct = ((sav_this - sav_last) / sav_last) * 100
        insights.append(f"💰 You saved {inc_pct:.0f}% more than last month! Keep it up.")

    # Goal proximity check
    if goals:
        for goal in goals:
            target = goal["target_amount"]
            current = goal["current_amount"]
            if target > 0:
                pct = (current / target) * 100
                if 80 <= pct < 100:
                    insights.append(f"🎯 You are close to achieving your savings goal '{goal['name']}' ({pct:.0f}% completed)!")

    # Budget pace warning
    budget = settings.get("monthly_budget", 0)
    if budget > 0:
        day_of_month = now.day
        days_in_month = (datetime.date(now.year, now.month + 1, 1) - datetime.date(now.year, now.month, 1)).days if now.month < 12 else 31
        pace = day_of_month / days_in_month
        exp_pace = total_exp_this / budget
        if exp_pace > pace + 0.10:
            insights.append("⚡ Your current spending trend may exceed this month's budget.")

    # Add defaults if list is too small
    if not insights:
        insights.append("💡 Tip: Try saving at least 20% of your stipend/allowance every month to build a safety net.")
        insights.append("🎯 Define specific financial goals in settings to trigger dynamic AI projections.")
        insights.append("👥 Using Split Bills? Keep your settlements updated to maintain accurate debt tracking.")
        
    return insights[:4]


# ─────────────────────────────────────────────
#  PREDICTION ENGINE
# ─────────────────────────────────────────────

def get_predictions(df: pd.DataFrame, settings: dict) -> dict:
    """Predict expected expenses, savings, and warnings based on past data."""
    defaults = {
        "expected_income": 0.0,
        "expected_expense": 0.0,
        "expected_savings": 0.0,
        "warning": ""
    }
    if df.empty:
        return defaults
        
    # Calculate monthly averages
    monthly_data = df.copy()
    monthly_data["month"] = monthly_data["date"].dt.to_period("M")
    
    grouped = monthly_data.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    if grouped.empty:
        return defaults
        
    avg_income = float(grouped.get("Income", pd.Series([0.0])).mean())
    avg_expense = float(grouped.get("Expense", pd.Series([0.0])).mean())
    
    # Current month state
    now = datetime.datetime.now()
    this_month_mask = (df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)
    month_expense = df[this_month_mask & (df["type"] == "Expense")]["amount"].sum()
    month_income = df[this_month_mask & (df["type"] == "Income")]["amount"].sum()
    
    expected_inc = max(avg_income, month_income)
    expected_exp = max(avg_expense, month_expense)
    expected_sav = max(0, expected_inc - expected_exp)
    
    # Warnings
    warning = ""
    budget = settings.get("monthly_budget", 0.0)
    if budget > 0 and expected_exp > budget:
        warning = f"⚠️ Warning: Predicted monthly expense (₹{expected_exp:,.2f}) exceeds your budget limit (₹{budget:,.2f})."
    elif expected_exp > expected_inc and expected_inc > 0:
        warning = "🔴 Warning: Your predicted expenses exceed your income. You may run into a deficit this month."
        
    return {
        "expected_income": expected_inc,
        "expected_expense": expected_exp,
        "expected_savings": expected_sav,
        "warning": warning
    }


# ─────────────────────────────────────────────
#  GEMINI AI FINANCIAL ADVISOR API CLIENT
# ─────────────────────────────────────────────

def ask_ai_copilot(df: pd.DataFrame, settings: dict, goals: list, query: str, api_key: str) -> str:
    """
    Call Gemini API to answer the user query based on financial data.
    Provides rule-based local answer fallback if api_key is missing.
    """
    # 1. Summary of financial facts
    if df.empty:
        total_income = 0.0
        total_expense = 0.0
        net_balance = 0.0
        month_income = 0.0
        month_expense = 0.0
        categories_breakdown = "No transactions tracked yet."
    else:
        total_income = df[df["type"] == "Income"]["amount"].sum()
        total_expense = df[df["type"] == "Expense"]["amount"].sum()
        net_balance = total_income - total_expense
        
        # Current month figures
        now = datetime.datetime.now()
        this_month_mask = (df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)
        df_month = df[this_month_mask]
        month_income = df_month[df_month["type"] == "Income"]["amount"].sum()
        month_expense = df_month[df_month["type"] == "Expense"]["amount"].sum()
        
        # Categories
        categories_breakdown = ""
        expenses_df = df[df["type"] == "Expense"]
        if not expenses_df.empty:
            cat_sums = expenses_df.groupby("category")["amount"].sum().sort_values(ascending=False)
            categories_breakdown = ", ".join([f"{c}: ₹{v:,.2f}" for c, v in cat_sums.items()])

    # Budget
    budget = settings.get("monthly_budget", 0)
    
    # Goals
    goals_desc = ""
    if goals:
        goals_desc = "; ".join([f"{g['name']} (Target ₹{g['target_amount']:.2f}, Saved: ₹{g['current_amount']:.2f}, Deadline: {g['target_date']})" for g in goals])
    else:
        goals_desc = "No active savings goals set."

    # Formulate a prompt context
    context = f"""
    You are SpendWise AI Copilot, a premium personal finance advisor. 
    Here is the user's financial profile:
    - All-time Tracked Income: ₹{total_income:,.2f}
    - All-time Tracked Expenses: ₹{total_expense:,.2f}
    - Net Savings Balance: ₹{net_balance:,.2f}
    - Current Month's Income: ₹{month_income:,.2f}
    - Current Month's Expense: ₹{month_expense:,.2f}
    - Monthly Budget: ₹{budget:,.2f} ({"No budget set" if budget == 0 else "Active"})
    - Spending Categories breakdown: {categories_breakdown}
    - Smart Financial Goals: {goals_desc}
    
    User Query: "{query}"
    
    Please provide a highly professional, empathetic, and quantitative answer to the user's query using the above numbers. Use bullet points and clean formatting. Always format money in INR (₹). Be realistic and direct. Keep response under 150 words.
    """

    # If no key, run rule-based fallback response
    if not api_key:
        return get_local_fallback_response(query, net_balance, month_expense, budget, goals, categories_breakdown, key_missing=True)

    # Try multiple Gemini models in order (newest → stable fallbacks)
    MODELS_TO_TRY = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b",
    ]
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{
                "text": context
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024
        }
    }

    last_error = ""
    for model in MODELS_TO_TRY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    response_text = candidates[0]["content"]["parts"][0]["text"]
                    return f"*[Powered by {model}]*\n\n" + response_text
            elif res.status_code == 404:
                # Model not found for this key — try next
                last_error = f"Model `{model}` not available on your API key."
                continue
            elif res.status_code == 429:
                last_error = "Rate limit hit. Please wait a moment and try again."
                break
            elif res.status_code == 400:
                last_error = f"Bad request: {res.text[:120]}"
                break
            else:
                last_error = f"API Error {res.status_code}: {res.text[:120]}"
                break
        except requests.exceptions.Timeout:
            last_error = "Request timed out (30s). Google's API may be slow or blocked on your network."
            continue
        except requests.exceptions.ConnectionError:
            last_error = "Cannot reach Google AI servers. Check your internet connection or firewall settings."
            break
        except Exception as e:
            last_error = str(e)
            continue

    # All models failed — show detailed error + offline fallback
    fallback = get_local_fallback_response(query, net_balance, month_expense, budget, goals, categories_breakdown, key_missing=False)
    return (
        f"⚠️ **AI Copilot could not connect**\n\n"
        f"**Reason:** {last_error}\n\n"
        f"**Troubleshoot:**\n"
        f"- Make sure your API Key in `key.env` is correct (starts with `AIza`)\n"
        f"- Check [Google AI Studio](https://aistudio.google.com) to confirm your key is active\n"
        f"- Verify that your internet connection can reach `generativelanguage.googleapis.com`\n\n"
        f"---\n*SpendWise offline analysis is running below:*\n\n" + fallback
    )


# ─────────────────────────────────────────────
#  LOCAL RULE-BASED FALLBACK GENERATOR
# ─────────────────────────────────────────────

def get_local_fallback_response(query: str, net_balance: float, month_expense: float, budget: float, goals: list, categories: str, key_missing: bool = False) -> str:
    """Generate a highly contextual rule-based response if the API Key is unavailable or call failed."""
    query_lower = query.lower()
    
    if key_missing:
        disclaimer = "\n\n*(Note: AI Copilot is running in offline rule-based mode. Add `GEMINI_API_KEY` to your `key.env` file to enable live AI answers.)*"
    else:
        disclaimer = "\n\n*(Offline analysis — Gemini API could not be reached on your network.)*"
    
    if "iphone" in query_lower or "phone" in query_lower or "afford" in query_lower or "buy" in query_lower:
        price = 70000.0 if "iphone" in query_lower else 40000.0
        if net_balance >= price:
            return f"⚖️ **Affordability Analysis**:\n\n- Yes, you can technically afford it, as your current net balance is **₹{net_balance:,.2f}** which is above the estimated cost of **₹{price:,.2f}**.\n- **Advisor Tip**: Buying this will reduce your net savings to **₹{net_balance - price:,.2f}**. Ensure you maintain a ₹15,000 emergency buffer before executing this purchase." + disclaimer
        else:
            deficit = price - net_balance
            return f"❌ **Affordability Analysis**:\n\n- No, you cannot comfortably afford this item right now. The estimated cost is **₹{price:,.2f}** and your net savings balance is **₹{net_balance:,.2f}** (Deficit of **₹{deficit:,.2f}**).\n- **Advisor Tip**: Set up a Smart Goal in Settings to save ₹5,000 monthly for this item, and we'll track your timeline to success!" + disclaimer
            
    if "save" in query_lower or "how to save" in query_lower or "investment" in query_lower or "invest" in query_lower:
        return f"💰 **Savings & Investment Advice**:\n\n- **Current Balance**: ₹{net_balance:,.2f}.\n- **Rule of Thumb (50/30/20)**: Aim to save at least 20% of your income. If you earn ₹50,000, that is ₹10,000.\n- **Discretionary Leakage**: Look at your categories: *{categories[:60]}*. Trimming 15% from dining and shopping will instantly increase your savings rate." + disclaimer
        
    if "health" in query_lower or "financial score" in query_lower:
        status_text = "Good" if net_balance > 15000 else "Needs Improvement"
        return f"🏥 **Financial Health Assessment**:\n\n- **Net balance**: ₹{net_balance:,.2f}.\n- **Overall Status**: **{status_text}**.\n- **Active Budget**: {f'₹{budget:,.2f}/month' if budget > 0 else 'None set (Please set one in Settings)'}.\n- **Recommendations**: Set up a monthly budget, hold an emergency fund in a separate savings account, and limit dining out." + disclaimer
        
    if "increase" in query_lower or "waste" in query_lower or "where did my money go" in query_lower:
        return f"🔍 **Spending Audit**:\n\n- **Month expenses**: ₹{month_expense:,.2f}.\n- **Top Categories**: {categories[:100]}...\n- **Advisor Tip**: Review your notes in the **History** tab. Small repeating transfers under ₹200 (recharges, snacks) often add up to over 20% of monthly leakage." + disclaimer
        
    return f"👋 **Hello! I am your AI Financial Copilot.**\n\n- **Net Balance**: ₹{net_balance:,.2f}\n- **Expenses this Month**: ₹{month_expense:,.2f}\n- **Budget**: ₹{budget:,.2f}\n\nI can analyze your transactions, evaluate purchase affordabilities, calculate budget timelines, and project goal completion dates. Enter your Gemini API Key in Settings to ask more detailed questions!" + disclaimer
