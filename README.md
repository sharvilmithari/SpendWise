# 💰 Student Monthly Expense Tracker — India Edition 🇮🇳

> A professional, LinkedIn-ready personal finance web app built with **Python + Streamlit**.
> Designed for Indian students to track income, expenses, budgets, and spending patterns.

---

## 🚀 Quick Start (Run in 3 steps)

### Step 1 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the App
```bash
streamlit run app.py
```

### Step 3 — Open in Browser
Streamlit will automatically open `http://localhost:8501` in your browser.

> 💡 Sample data (`expense_data.json`) is included so you can explore all features right away!

---

## ✨ Features

| Feature | Details |
|---|---|
| 📊 **Dashboard** | Income / Expense / Balance cards, budget alerts, recent transactions |
| ➕ **Add Transaction** | Income or Expense with category, date, amount, notes |
| 📋 **History** | Filterable table by type, category, month + CSV export |
| 📈 **Analytics** | Pie chart (category-wise) + Bar chart (monthly trend) |
| ⚙️ **Settings** | Monthly budget + daily expense limit with live warnings |

---

## 📁 Project Structure

```
expense_tracker/
├── app.py               ← Main application (single file)
├── expense_data.json    ← Local data storage (auto-created)
├── settings.json        ← Budget & limit settings (auto-created)
├── requirements.txt     ← Python dependencies
└── README.md            ← This file
```

---

## 🏗️ Tech Stack

- **Python 3.9+** — Core language
- **Streamlit** — Web UI framework (no HTML/CSS knowledge needed)
- **Pandas** — Data manipulation and filtering
- **Matplotlib** — Charts and visualizations
- **JSON** — Lightweight local data storage

---

## 💡 Customization Tips

| What to change | Where |
|---|---|
| Add new categories | `EXPENSE_CATEGORIES` / `INCOME_CATEGORIES` lists at the top |
| Change chart colors | `CHART_COLORS` list |
| Change color theme | CSS variables in `inject_css()` function |
| Switch to SQLite | Replace `load_data()` / `save_data()` with SQLite queries |

---

## 📸 Pages Overview

### Dashboard
- 4 metric cards: Total Income, Total Expenses, Net Balance, Monthly Budget
- Budget health alerts (green / yellow / red)
- Daily limit warning
- Recent 10 transactions

### Add Transaction
- Type: Income or Expense
- Amount in ₹
- 9 expense categories + 5 income categories
- Date picker + Notes field
- Live budget progress bar

### Transaction History
- Filter by Type, Category, Month
- Export filtered data as CSV
- Delete transactions by ID

### Analytics
- Donut pie chart — spending by category
- Bar chart — monthly spending trend (highlights highest month)
- Summary table — totals, count, averages per category

### Settings
- Set/update monthly budget
- Set daily expense limit
- Both saved to `settings.json`

---

## 🎯 LinkedIn Showcase Tips

When posting this project on LinkedIn:
1. Record a short screen recording demo (Loom / OBS)
2. Highlight: "Built entirely in Python — no web dev experience needed"
3. Tag: `#Python` `#Streamlit` `#DataScience` `#StudentProject` `#PersonalFinance`
4. Share your GitHub repo link

---

## 📊 Sample Data

The included `expense_data.json` contains **30 realistic transactions** across Dec 2024 and Jan 2025 covering:
- PG rent, food, travel, recharge, shopping, education, entertainment, healthcare
- Multiple income sources: stipend, allowance, freelance, gift money

---

*Made with ❤️ for Indian students | Open Source*
