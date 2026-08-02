import os
import sqlite3
import datetime
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# Load Supabase keys
from pathlib import Path
env_path = Path(__file__).parent / "key.env"
load_dotenv(dotenv_path=env_path)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase_client = get_supabase_client()

# SQLite setup
SQLITE_DB = "spendwise_local.db"

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    # 0. Local Transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        notes TEXT
    )
    """)
    
    # 0.1 Local Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id TEXT PRIMARY KEY,
        monthly_budget REAL DEFAULT 0.0,
        daily_limit REAL DEFAULT 0.0
    )
    """)
    
    # 1. Goals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0.0,
        target_date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Split Groups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS split_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Split Group Members
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS split_group_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        friend_name TEXT NOT NULL,
        user_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(group_id) REFERENCES split_groups(id) ON DELETE CASCADE,
        UNIQUE(group_id, friend_name)
    )
    """)
    
    # 4. Split Bills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS split_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        paid_by_name TEXT NOT NULL,
        paid_by_uid TEXT,
        date TEXT NOT NULL,
        split_type TEXT DEFAULT 'equal',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(group_id) REFERENCES split_groups(id) ON DELETE CASCADE
    )
    """)
    
    # 5. Split Bill Shares
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS split_bill_shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        member_name TEXT NOT NULL,
        share_amount REAL NOT NULL,
        has_settled INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(bill_id) REFERENCES split_bills(id) ON DELETE CASCADE,
        UNIQUE(bill_id, member_name)
    )
    """)
    
    # 6. Split Settlements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS split_settlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        from_member TEXT NOT NULL,
        to_member TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(group_id) REFERENCES split_groups(id) ON DELETE CASCADE
    )
    """)

    # 7. Local Configuration Settings (API Keys, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS local_settings (
        user_id TEXT PRIMARY KEY,
        gemini_api_key TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def get_gemini_key(user_uuid: str) -> str:
    """Fetch Gemini API Key from local SQLite or key.env."""
    # First check env variables
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
        
    # Check SQLite
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT gemini_api_key FROM local_settings WHERE user_id = ?", (user_uuid,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["gemini_api_key"] or ""
    return ""

def save_gemini_key(user_uuid: str, key: str):
    """Save Gemini API Key to local SQLite."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO local_settings (user_id, gemini_api_key) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET gemini_api_key = ?",
        (user_uuid, key, key)
    )
    conn.commit()
    conn.close()


# Initialize local SQLite schema on module import
init_sqlite_db()

# Check Supabase status
def check_supabase_table_exists(table_name: str) -> bool:
    if not supabase_client:
        return False
    if f"supa_has_{table_name}" in st.session_state:
        return st.session_state[f"supa_has_{table_name}"]
    
    try:
        supabase_client.table(table_name).select("*").limit(1).execute()
        st.session_state[f"supa_has_{table_name}"] = True
        return True
    except Exception:
        st.session_state[f"supa_has_{table_name}"] = False
        return False

# ─────────────────────────────────────────────
#  SMART GOALS API
# ─────────────────────────────────────────────

def get_goals(user_uuid: str) -> list:
    """Load all goals for the user, checking Supabase first, falling back to SQLite."""
    if check_supabase_table_exists("goals"):
        try:
            res = supabase_client.table("goals").select("*").eq("user_id", user_uuid).order("created_at").execute()
            # Standardize records
            goals = []
            for r in res.data:
                goals.append({
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "name": r["name"],
                    "target_amount": float(r["target_amount"]),
                    "current_amount": float(r["current_amount"]),
                    "target_date": r["target_date"],
                    "created_at": r["created_at"]
                })
            return goals
        except Exception:
            pass # Fall back to SQLite
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals WHERE user_id = ? ORDER BY created_at", (user_uuid,))
    rows = cursor.fetchall()
    goals = []
    for r in rows:
        goals.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "name": r["name"],
            "target_amount": float(r["target_amount"]),
            "current_amount": float(r["current_amount"]),
            "target_date": r["target_date"],
            "created_at": r["created_at"]
        })
    conn.close()
    return goals

def add_goal(user_uuid: str, name: str, target: float, current: float, date_str: str) -> bool:
    """Save a goal to Supabase or SQLite."""
    if check_supabase_table_exists("goals"):
        try:
            supabase_client.table("goals").insert({
                "user_id": user_uuid,
                "name": name,
                "target_amount": target,
                "current_amount": current,
                "target_date": date_str
            }).execute()
            return True
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO goals (user_id, name, target_amount, current_amount, target_date) VALUES (?, ?, ?, ?, ?)",
        (user_uuid, name, target, current, date_str)
    )
    conn.commit()
    conn.close()
    return True

def delete_goal_db(user_uuid: str, goal_id: int) -> bool:
    """Delete a goal."""
    if check_supabase_table_exists("goals"):
        try:
            supabase_client.table("goals").delete().eq("id", goal_id).eq("user_id", user_uuid).execute()
            return True
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_uuid))
    conn.commit()
    conn.close()
    return True

def update_goal_progress_db(user_uuid: str, goal_id: int, current: float) -> bool:
    """Update progress amount of a goal."""
    if check_supabase_table_exists("goals"):
        try:
            supabase_client.table("goals").update({"current_amount": current}).eq("id", goal_id).eq("user_id", user_uuid).execute()
            return True
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE goals SET current_amount = ? WHERE id = ? AND user_id = ?", (current, goal_id, user_uuid))
    conn.commit()
    conn.close()
    return True


# ─────────────────────────────────────────────
#  SPLIT BILLS API
# ─────────────────────────────────────────────

def get_groups(user_uuid: str, username: str) -> list:
    """Load groups that user created or is part of."""
    if check_supabase_table_exists("split_groups") and check_supabase_table_exists("split_group_members"):
        try:
            # 1. Fetch group IDs where user is member or creator
            member_res = supabase_client.table("split_group_members").select("group_id").eq("user_id", user_uuid).execute()
            gp_ids = [m["group_id"] for m in member_res.data]
            
            created_res = supabase_client.table("split_groups").select("id").eq("created_by", user_uuid).execute()
            gp_ids.extend([g["id"] for g in created_res.data])
            gp_ids = list(set(gp_ids))
            
            if not gp_ids:
                return []
                
            res = supabase_client.table("split_groups").select("*").in_("id", gp_ids).order("created_at").execute()
            groups = []
            for r in res.data:
                groups.append({
                    "id": r["id"],
                    "name": r["name"],
                    "created_by": r["created_by"],
                    "created_at": r["created_at"]
                })
            return groups
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT g.id, g.name, g.created_by, g.created_at 
        FROM split_groups g
        LEFT JOIN split_group_members m ON g.id = m.group_id
        WHERE g.created_by = ? OR m.user_id = ? OR m.friend_name = ?
        ORDER BY g.created_at
    """, (user_uuid, user_uuid, username))
    rows = cursor.fetchall()
    groups = [{"id": r["id"], "name": r["name"], "created_by": r["created_by"], "created_at": r["created_at"]} for r in rows]
    conn.close()
    return groups

def create_group_db(user_uuid: str, creator_name: str, group_name: str, member_names: list) -> int:
    """Create a split group and add members."""
    # Ensure creator is in the member names
    all_members = list(set([creator_name] + member_names))
    
    if check_supabase_table_exists("split_groups") and check_supabase_table_exists("split_group_members"):
        try:
            res = supabase_client.table("split_groups").insert({
                "name": group_name,
                "created_by": user_uuid
            }).execute()
            
            if res.data:
                group_id = res.data[0]["id"]
                
                # Insert members
                for member in all_members:
                    uid = user_uuid if member == creator_name else None
                    supabase_client.table("split_group_members").insert({
                        "group_id": group_id,
                        "friend_name": member,
                        "user_id": uid
                    }).execute()
                return group_id
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO split_groups (name, created_by) VALUES (?, ?)", (group_name, user_uuid))
    group_id = cursor.lastrowid
    
    for member in all_members:
        uid = user_uuid if member == creator_name else None
        cursor.execute(
            "INSERT INTO split_group_members (group_id, friend_name, user_id) VALUES (?, ?, ?)",
            (group_id, member, uid)
        )
    conn.commit()
    conn.close()
    return group_id

def get_group_members(group_id: int) -> list:
    """Fetch all members of a group."""
    if check_supabase_table_exists("split_group_members"):
        try:
            res = supabase_client.table("split_group_members").select("*").eq("group_id", group_id).execute()
            return [m["friend_name"] for m in res.data]
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT friend_name FROM split_group_members WHERE group_id = ?", (group_id,))
    rows = cursor.fetchall()
    members = [r["friend_name"] for r in rows]
    conn.close()
    return members

def add_split_bill_db(group_id: int, description: str, amount: float, paid_by_name: str, paid_by_uid: str, date_str: str, shares: dict) -> bool:
    """Add a bill and insert splits."""
    if check_supabase_table_exists("split_bills") and check_supabase_table_exists("split_bill_shares"):
        try:
            res = supabase_client.table("split_bills").insert({
                "group_id": group_id,
                "description": description,
                "amount": amount,
                "paid_by_name": paid_by_name,
                "paid_by_uid": paid_by_uid,
                "date": date_str
            }).execute()
            
            if res.data:
                bill_id = res.data[0]["id"]
                for m_name, m_share in shares.items():
                    supabase_client.table("split_bill_shares").insert({
                        "bill_id": bill_id,
                        "member_name": m_name,
                        "share_amount": m_share
                    }).execute()
                return True
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO split_bills (group_id, description, amount, paid_by_name, paid_by_uid, date) VALUES (?, ?, ?, ?, ?, ?)",
        (group_id, description, amount, paid_by_name, paid_by_uid, date_str)
    )
    bill_id = cursor.lastrowid
    
    for m_name, m_share in shares.items():
        cursor.execute(
            "INSERT INTO split_bill_shares (bill_id, member_name, share_amount) VALUES (?, ?, ?)",
            (bill_id, m_name, m_share)
        )
    conn.commit()
    conn.close()
    return True

def get_group_bills(group_id: int) -> list:
    """Get all bills for a group."""
    if check_supabase_table_exists("split_bills"):
        try:
            res = supabase_client.table("split_bills").select("*").eq("group_id", group_id).order("date", desc=True).execute()
            bills = []
            for r in res.data:
                bills.append({
                    "id": r["id"],
                    "description": r["description"],
                    "amount": float(r["amount"]),
                    "paid_by_name": r["paid_by_name"],
                    "paid_by_uid": r["paid_by_uid"],
                    "date": r["date"]
                })
            return bills
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM split_bills WHERE group_id = ? ORDER BY date DESC", (group_id,))
    rows = cursor.fetchall()
    bills = []
    for r in rows:
        bills.append({
            "id": r["id"],
            "description": r["description"],
            "amount": float(r["amount"]),
            "paid_by_name": r["paid_by_name"],
            "paid_by_uid": r["paid_by_uid"],
            "date": r["date"]
        })
    conn.close()
    return bills

def get_bill_shares(bill_id: int) -> list:
    """Fetch details of how a bill was split."""
    if check_supabase_table_exists("split_bill_shares"):
        try:
            res = supabase_client.table("split_bill_shares").select("*").eq("bill_id", bill_id).execute()
            return [{"member_name": s["member_name"], "share_amount": float(s["share_amount"])} for s in res.data]
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT member_name, share_amount FROM split_bill_shares WHERE bill_id = ?", (bill_id,))
    rows = cursor.fetchall()
    shares = [{"member_name": r["member_name"], "share_amount": float(r["share_amount"])} for r in rows]
    conn.close()
    return shares

def add_settlement_db(group_id: int, from_member: str, to_member: str, amount: float, date_str: str) -> bool:
    """Add a settlement record."""
    if check_supabase_table_exists("split_settlements"):
        try:
            supabase_client.table("split_settlements").insert({
                "group_id": group_id,
                "from_member": from_member,
                "to_member": to_member,
                "amount": amount,
                "date": date_str
            }).execute()
            return True
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO split_settlements (group_id, from_member, to_member, amount, date) VALUES (?, ?, ?, ?, ?)",
        (group_id, from_member, to_member, amount, date_str)
    )
    conn.commit()
    conn.close()
    return True

def get_group_settlements(group_id: int) -> list:
    """Get settlement history for a group."""
    if check_supabase_table_exists("split_settlements"):
        try:
            res = supabase_client.table("split_settlements").select("*").eq("group_id", group_id).order("date", desc=True).execute()
            settlements = []
            for r in res.data:
                settlements.append({
                    "id": r["id"],
                    "from_member": r["from_member"],
                    "to_member": r["to_member"],
                    "amount": float(r["amount"]),
                    "date": r["date"]
                })
            return settlements
        except Exception:
            pass
            
    # SQLite Fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM split_settlements WHERE group_id = ? ORDER BY date DESC", (group_id,))
    rows = cursor.fetchall()
    settlements = []
    for r in rows:
        settlements.append({
            "id": r["id"],
            "from_member": r["from_member"],
            "to_member": r["to_member"],
            "amount": float(r["amount"]),
            "date": r["date"]
        })
    conn.close()
    return settlements

# ─────────────────────────────────────────────
#  LOCAL TRANSACTIONS & LOCAL SETTINGS HELPERS
# ─────────────────────────────────────────────

def get_local_transactions(user_uuid: str) -> list:
    """Fetch user transactions from local SQLite."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_uuid,))
    rows = cursor.fetchall()
    txns = []
    for r in rows:
        txns.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "type": r["type"],
            "amount": float(r["amount"]),
            "category": r["category"],
            "date": r["date"],
            "notes": r["notes"] or ""
        })
    conn.close()
    return txns

def add_local_transaction(user_uuid: str, t_type: str, amount: float, category: str, date_str: str, notes: str) -> bool:
    """Insert transaction into local SQLite."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, type, amount, category, date, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (user_uuid, t_type, amount, category, date_str, notes)
    )
    conn.commit()
    conn.close()
    return True

def delete_local_transaction(user_uuid: str, row_id: int) -> bool:
    """Delete transaction from local SQLite."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (row_id, user_uuid))
    conn.commit()
    conn.close()
    return True

def get_local_settings(user_uuid: str, defaults: dict) -> dict:
    """Load settings from local SQLite."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT monthly_budget, daily_limit FROM settings WHERE user_id = ?", (user_uuid,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "monthly_budget": float(row["monthly_budget"] or 0.0),
            "daily_limit": float(row["daily_limit"] or 0.0)
        }
    return defaults

def save_local_settings(user_uuid: str, monthly_budget: float, daily_limit: float) -> bool:
    """Upsert settings in local SQLite."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO settings (user_id, monthly_budget, daily_limit) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET monthly_budget = ?, daily_limit = ?",
        (user_uuid, monthly_budget, daily_limit, monthly_budget, daily_limit)
    )
    conn.commit()
    conn.close()
    return True

