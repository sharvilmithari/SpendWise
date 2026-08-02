import streamlit as st
import datetime
import pandas as pd
from database import (
    get_groups, 
    create_group_db, 
    get_group_members, 
    add_split_bill_db, 
    get_group_bills, 
    get_bill_shares, 
    add_settlement_db, 
    get_group_settlements
)

# ─────────────────────────────────────────────
#  DEBT SIMPLIFICATION ALGORITHM (SPLITWISE-STYLE)
# ─────────────────────────────────────────────

def calculate_group_balances(group_id: int) -> tuple:
    """
    Calculate the net balances of each member and simplify the debts.
    Returns (balances_dict, simplified_debts_list)
    - net balance > 0: member is owed money (creditor)
    - net balance < 0: member owes money (debtor)
    """
    members = get_group_members(group_id)
    if not members:
        return {}, []
        
    balances = {m: 0.0 for m in members}
    
    # 1. Process all bills
    bills = get_group_bills(group_id)
    for bill in bills:
        amount = bill["amount"]
        payer = bill["paid_by_name"]
        
        # Load shares
        shares = get_bill_shares(bill["id"])
        if not shares:
            # Fallback to equal split if share records are missing
            share_amt = amount / len(members)
            shares = [{"member_name": m, "share_amount": share_amt} for m in members]
            
        for s in shares:
            m_name = s["member_name"]
            m_share = s["share_amount"]
            if m_name in balances:
                balances[m_name] -= m_share
                
        if payer in balances:
            balances[payer] += amount
            
    # 2. Process all settlements
    settlements = get_group_settlements(group_id)
    for setl in settlements:
        from_m = setl["from_member"]
        to_m = setl["to_member"]
        amt = setl["amount"]
        
        if from_m in balances:
            balances[from_m] += amt
        if to_m in balances:
            balances[to_m] -= amt

    # 3. Simplify debts (greedy min-max matching)
    # debtors owe money (balance < 0)
    debtors = []
    # creditors are owed money (balance > 0)
    creditors = []
    
    for name, bal in balances.items():
        # Round to avoid floating point precision issues
        rounded_bal = round(bal, 2)
        if rounded_bal < -0.01:
            debtors.append([name, abs(rounded_bal)])
        elif rounded_bal > 0.01:
            creditors.append([name, rounded_bal])
            
    simplified_debts = []
    
    # Run matching
    while debtors and creditors:
        # Sort so we match the largest debtor with the largest creditor
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)
        
        debtor_name, debt_amt = debtors[0]
        creditor_name, credit_amt = creditors[0]
        
        settle_amt = min(debt_amt, credit_amt)
        simplified_debts.append({
            "from": debtor_name,
            "to": creditor_name,
            "amount": settle_amt
        })
        
        # Update remaining balances
        debtors[0][1] -= settle_amt
        creditors[0][1] -= settle_amt
        
        # Remove completed balances
        if debtors[0][1] <= 0.01:
            debtors.pop(0)
        if creditors[0][1] <= 0.01:
            creditors.pop(0)
            
    return balances, simplified_debts


# ─────────────────────────────────────────────
#  UI PAGE: SPLIT BILLS
# ─────────────────────────────────────────────

def page_split_bills(user_uuid: str, username: str):
    st.markdown('<div class="page-title">Split Bills</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Split expenses with friends, trip groups, or flatmates</div>', unsafe_allow_html=True)
    
    # Load all groups user belongs to
    groups = get_groups(user_uuid, username)
    
    # Sidebar or Header Group Selector
    col_sel, col_new = st.columns([3, 1])
    
    with col_sel:
        if groups:
            group_options = {g["name"]: g["id"] for g in groups}
            selected_group_name = st.selectbox("Select Group", list(group_options.keys()))
            active_group_id = group_options[selected_group_name]
        else:
            st.info("💡 You are not in any split bill groups yet. Create one below to get started!")
            active_group_id = None
            
    with col_new:
        create_new = st.button("➕ Create Group", use_container_width=True)
        
    if create_new or not active_group_id:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Create a New Split Group")
        with st.form("create_group_form", clear_on_submit=True):
            g_name = st.text_input("Group Name", placeholder="e.g. Goa Trip 2026, Room 402 Expenses")
            friends_input = st.text_area("Friend Names (Comma-separated)", placeholder="Rahul, Priya, Amit")
            submit_g = st.form_submit_button("📁 Initialize Group")
            
            if submit_g:
                if not g_name:
                    st.error("Please enter a group name.")
                else:
                    friends = [f.strip() for f in friends_input.split(",") if f.strip()]
                    # Create group, inserting creator too
                    group_id = create_group_db(user_uuid, username, g_name, friends)
                    st.success(f"✅ Group '{g_name}' created successfully!")
                    st.rerun()
        return

    # Load active group details
    members = get_group_members(active_group_id)
    balances, simplified_debts = calculate_group_balances(active_group_id)
    
    # BALANCES & INSIGHT CARDS
    st.markdown(f"### 👥 {selected_group_name} Dashboard")
    
    # Show grid of member balances
    st.markdown("##### Member Net Standings")
    cols = st.columns(min(len(members), 4))
    for i, member in enumerate(members):
        col_idx = i % len(cols)
        bal = balances.get(member, 0.0)
        bal_formatted = f"₹{bal:+,.2f}" if bal != 0 else "Settled"
        
        card_class = "card-income" if bal > 0.01 else ("card-expense" if bal < -0.01 else "card-balance")
        value_class = "income" if bal > 0.01 else ("expense" if bal < -0.01 else "balance")
        
        with cols[col_idx]:
            st.markdown(f"""
            <div class="member-card {card_class}">
                <div class="member-card-name">{member}</div>
                <div class="member-card-balance {value_class}">{bal_formatted}</div>
            </div>
            """, unsafe_allow_html=True)
            
    # TAB CONTROL
    tab_debts, tab_add_bill, tab_settle, tab_history = st.tabs([
        "🤝 Who Owes Whom", 
        "➕ Add Expense", 
        "💳 Record Settlement", 
        "📜 Transaction History"
    ])
    
    # ── TAB 1: WHO OWES WHOM ──
    with tab_debts:
        st.markdown("##### Simplified Debt Instructions")
        if not simplified_debts:
            st.success("🎉 All settled up! Nobody owes anything in this group.")
        else:
            for debt in simplified_debts:
                st.markdown(f"""
                <div class="debt-row">
                    <div><strong>{debt['from']}</strong> owes <strong>{debt['to']}</strong></div>
                    <div class="debt-amount">₹{debt['amount']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: ADD EXPENSE ──
    with tab_add_bill:
        st.markdown("##### Log a New Bill")
        with st.form("add_bill_form", clear_on_submit=True):
            desc = st.text_input("Description", placeholder="e.g. Dinner, Fuel, Airbnb booking")
            amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            paid_by = st.selectbox("Paid By", members)
            bill_date = st.date_input("Date", value=datetime.date.today())
            
            submit_bill = st.form_submit_button("💸 Save & Split Equally")
            
            if submit_bill:
                if not desc:
                    st.error("Please enter a description.")
                elif amt <= 0:
                    st.error("Please enter a valid amount greater than ₹0.")
                else:
                    # Calculate equal shares
                    share = amt / len(members)
                    shares = {m: share for m in members}
                    
                    paid_uid = user_uuid if paid_by == username else None
                    
                    ok = add_split_bill_db(active_group_id, desc, amt, paid_by, paid_uid, str(bill_date), shares)
                    if ok:
                        st.success(f"✅ Expense of ₹{amt:,.2f} split equally among {len(members)} members!")
                        st.rerun()
                        
    # ── TAB 3: RECORD SETTLEMENT ──
    with tab_settle:
        st.markdown("##### Log a Direct Payment")
        with st.form("record_settlement_form", clear_on_submit=True):
            # Show dropdown values from the simplified debts if available
            debtor_defaults = [d["from"] for d in simplified_debts]
            creditor_defaults = [d["to"] for d in simplified_debts]
            
            from_m = st.selectbox("Who Paid?", members, index=members.index(debtor_defaults[0]) if debtor_defaults else 0)
            to_m = st.selectbox("Who Received?", members, index=members.index(creditor_defaults[0]) if creditor_defaults else 0)
            
            # Suggest settlement amount from the matched debt if relevant
            suggested_amt = 0.0
            if debtor_defaults and creditor_defaults:
                for d in simplified_debts:
                    if d["from"] == from_m and d["to"] == to_m:
                        suggested_amt = float(d["amount"])
                        break
            
            settle_amt = st.number_input("Settlement Amount (₹)", min_value=0.0, value=suggested_amt, step=10.0)
            settle_date = st.date_input("Settlement Date", value=datetime.date.today())
            submit_settle = st.form_submit_button("💳 Log Settlement")
            
            if submit_settle:
                if from_m == to_m:
                    st.error("Sender and receiver cannot be the same person.")
                elif settle_amt <= 0:
                    st.error("Please enter a valid amount greater than ₹0.")
                else:
                    ok = add_settlement_db(active_group_id, from_m, to_m, settle_amt, str(settle_date))
                    if ok:
                        st.success(f"✅ Recorded: {from_m} paid {to_m} ₹{settle_amt:,.2f}!")
                        st.rerun()

    # ── TAB 4: TRANSACTION HISTORY ──
    with tab_history:
        st.markdown("##### Expense Ledger")
        bills = get_group_bills(active_group_id)
        settlements = get_group_settlements(active_group_id)
        
        ledger_data = []
        for b in bills:
            ledger_data.append({
                "Date": b["date"],
                "Type": "💸 Bill Expense",
                "Description": b["description"],
                "Amount": f"₹{b['amount']:,.2f}",
                "Paid By": b["paid_by_name"],
                "Details": "Split Equally"
            })
            
        for s in settlements:
            ledger_data.append({
                "Date": s["date"],
                "Type": "🤝 Settlement Payment",
                "Description": f"Payment: {s['from_member']} ➔ {s['to_member']}",
                "Amount": f"₹{s['amount']:,.2f}",
                "Paid By": s["from_member"],
                "Details": f"Received by {s['to_member']}"
            })
            
        if not ledger_data:
            st.info("No logs registered in this group yet.")
        else:
            df_ledger = pd.DataFrame(ledger_data)
            df_ledger["Date"] = pd.to_datetime(df_ledger["Date"])
            df_ledger = df_ledger.sort_values("Date", ascending=False)
            df_ledger["Date"] = df_ledger["Date"].dt.strftime("%d %b %Y")
            
            st.dataframe(df_ledger, use_container_width=True, hide_index=True)
            
            # Simple summary stat
            total_spent = sum([b["amount"] for b in bills])
            st.caption(f"Total spent across group history: ₹{total_spent:,.2f}")
