-- SQL schema to upgrade SpendWise database with Split Bills and Smart Goals tables.
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor > New query > Run).

-- 1. SMART GOALS TABLE
CREATE TABLE IF NOT EXISTS goals (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    target_amount NUMERIC(15, 2) NOT NULL,
    current_amount NUMERIC(15, 2) DEFAULT 0.00,
    target_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. SPLIT BILLS GROUPS
CREATE TABLE IF NOT EXISTS split_groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_by UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. SPLIT BILLS GROUP MEMBERS
CREATE TABLE IF NOT EXISTS split_group_members (
    id SERIAL PRIMARY KEY,
    group_id INT REFERENCES split_groups(id) ON DELETE CASCADE,
    friend_name TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_group_friend UNIQUE (group_id, friend_name)
);

-- 4. SPLIT BILLS
CREATE TABLE IF NOT EXISTS split_bills (
    id SERIAL PRIMARY KEY,
    group_id INT REFERENCES split_groups(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    paid_by_name TEXT NOT NULL, -- Friend name or username of the person who paid
    paid_by_uid UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    split_type TEXT DEFAULT 'equal',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. SPLIT BILL SHARES (who owes how much for a bill)
CREATE TABLE IF NOT EXISTS split_bill_shares (
    id SERIAL PRIMARY KEY,
    bill_id INT REFERENCES split_bills(id) ON DELETE CASCADE,
    member_name TEXT NOT NULL,
    share_amount NUMERIC(15, 2) NOT NULL,
    has_settled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_bill_member UNIQUE (bill_id, member_name)
);

-- 6. SPLIT SETTLEMENTS (payment logs between friends)
CREATE TABLE IF NOT EXISTS split_settlements (
    id SERIAL PRIMARY KEY,
    group_id INT REFERENCES split_groups(id) ON DELETE CASCADE,
    from_member TEXT NOT NULL,
    to_member TEXT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
