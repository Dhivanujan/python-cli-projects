#!/usr/bin/env python3
"""
Budget Planner CLI
"""

import sqlite3
from datetime import datetime
import os

DB = "budget_planner.db"


# ---------------------------------------
# DATABASE SETUP
# ---------------------------------------
def get_conn():
    return sqlite3.connect(DB)


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        # Income table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            year TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        # Expenses table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            month TEXT NOT NULL,
            year TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
        """)

        # Savings goal table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS savings_goal (
            id INTEGER PRIMARY KEY,
            goal REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        conn.commit()


# ---------------------------------------
# INCOME FUNCTIONS
# ---------------------------------------
def add_income():
    try:
        amount = float(input("Enter monthly income amount: ").strip())
        if amount <= 0:
            print("Income must be positive.")
            return
    except ValueError:
        print("Invalid number.")
        return

    now = datetime.now()
    month = now.strftime("%m")
    year = now.strftime("%Y")
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO income (amount, month, year, created_at) VALUES (?, ?, ?, ?)",
                    (amount, month, year, created_at))
        conn.commit()

    print("✔ Monthly income added.")


def get_income(month, year):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM income WHERE month=? AND year=?", (month, year))
        val = cur.fetchone()[0]
        return val if val else 0


# ---------------------------------------
# EXPENSE FUNCTIONS
# ---------------------------------------
def add_expense():
    try:
        amount = float(input("Enter expense amount: ").strip())
        if amount <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid number.")
        return

    category = input("Category (Food, Travel, Bills, Shopping, Other): ").strip()
    if not category:
        category = "Other"

    note = input("Note (optional): ").strip()
    now = datetime.now()

    month = now.strftime("%m")
    year = now.strftime("%Y")
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""INSERT INTO expenses (amount, category, month, year, note, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (amount, category, month, year, note, created_at))
        conn.commit()

    print("✔ Expense added.")


def get_expenses(month, year):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, SUM(amount) FROM expenses WHERE month=? AND year=? GROUP BY category",
                    (month, year))
        rows = cur.fetchall()
        return rows


def get_total_expenses(month, year):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM expenses WHERE month=? AND year=?", (month, year))
        val = cur.fetchone()[0]
        return val if val else 0


# ---------------------------------------
# SAVINGS GOAL
# ---------------------------------------
def set_savings_goal():
    try:
        goal = float(input("Set your savings goal: ").strip())
        if goal <= 0:
            print("Savings goal must be positive.")
            return
    except ValueError:
        print("Invalid number.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM savings_goal")
        cur.execute("INSERT INTO savings_goal (id, goal, created_at) VALUES (1, ?, ?)",
                    (goal, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    print(f"✔ Savings goal set: ₹{goal:.2f}")


def get_savings_goal():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT goal FROM savings_goal WHERE id=1")
        row = cur.fetchone()
        return row[0] if row else None


# ---------------------------------------
# SUMMARY
# ---------------------------------------
def monthly_summary():
    month = input("Enter month (01-12): ").strip()
    year = input("Enter year (YYYY): ").strip()

    income = get_income(month, year)
    expenses = get_total_expenses(month, year)
    categories = get_expenses(month, year)
    savings_goal = get_savings_goal()
    savings = income - expenses

    print(f"\n--- Budget Summary for {month}/{year} ---")
    print(f"Income: ₹{income:.2f}")
    print(f"Expenses: ₹{expenses:.2f}")
    print(f"Savings: ₹{savings:.2f}")

    print("\nCategory-wise spending:")
    if categories:
        for cat, amt in categories:
            print(f"{cat}: ₹{amt:.2f}")
    else:
        print("No expenses recorded.")

    if savings_goal:
        print(f"\nYour savings goal: ₹{savings_goal:.2f}")
        progress = (savings / savings_goal) * 100 if savings_goal > 0 else 0
        progress = max(0, progress)

        print(f"Progress: {progress:.2f}%")
        if savings >= savings_goal:
            print("🎉 Goal Achieved!")
        else:
            print(f"Remaining: ₹{savings_goal - savings:.2f}")
    else:
        print("\nNo savings goal set.")


# ---------------------------------------
# MENU
# ---------------------------------------
def main_menu():
    init_db()

    while True:
        print("\n=== Budget Planner CLI ===")
        print("1) Add Monthly Income")
        print("2) Add Expense")
        print("3) Monthly Summary")
        print("4) Set Savings Goal")
        print("0) Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_income()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            monthly_summary()
        elif choice == "4":
            set_savings_goal()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main_menu()
