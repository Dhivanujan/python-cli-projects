#!/usr/bin/env python3
"""
Expense Tracker CLI
"""

import sqlite3
from datetime import datetime
import csv
import os

DB = "expenses.db"


# ---------------------------------------
# DATABASE SETUP
# ---------------------------------------
def get_conn():
    return sqlite3.connect(DB)


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
        """)
        conn.commit()


# ---------------------------------------
# CORE FUNCTIONS
# ---------------------------------------
def add_expense():
    try:
        amount = float(input("Enter amount: ").strip())
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

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (amount, category, note, created_at) VALUES (?, ?, ?, ?)",
                    (amount, category, note, created_at))
        conn.commit()

    print("✔ Expense added successfully.")


def view_expenses():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, amount, category, note, created_at FROM expenses ORDER BY created_at DESC")
        rows = cur.fetchall()

    if not rows:
        print("No expenses recorded yet.")
        return

    print("\n--- All Expenses ---")
    for row in rows:
        print(f"ID: {row[0]} | ₹{row[1]:.2f} | {row[2]} | {row[3]} | {row[4]}")


def delete_expense():
    try:
        exp_id = int(input("Enter expense ID to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
        conn.commit()

    print("✔ Expense deleted (if existed).")


def monthly_report():
    month = input("Enter month (01-12): ").strip()
    year = input("Enter year (YYYY): ").strip()

    try:
        int(month)
        int(year)
    except ValueError:
        print("Invalid month/year.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE strftime('%m', created_at) = ? AND strftime('%Y', created_at) = ?
            GROUP BY category
        """, (month, year))
        rows = cur.fetchall()

    if not rows:
        print("No expenses found for this month.")
        return

    print(f"\n--- Expense Summary for {month}/{year} ---")
    total = 0
    for cat, amt in rows:
        print(f"{cat}: ₹{amt:.2f}")
        total += amt
    print(f"Total: ₹{total:.2f}")


def export_csv():
    filename = "expenses_export.csv"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM expenses ORDER BY created_at DESC")
        rows = cur.fetchall()

    if not rows:
        print("No data to export.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Amount", "Category", "Note", "Created At"])
        writer.writerows(rows)

    print(f"✔ Exported to {filename} in {os.getcwd()}")


# ---------------------------------------
# MENU
# ---------------------------------------
def main_menu():
    init_db()

    while True:
        print("\n=== Expense Tracker CLI ===")
        print("1) Add Expense")
        print("2) View All Expenses")
        print("3) Delete Expense")
        print("4) Monthly Summary")
        print("5) Export as CSV")
        print("0) Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            delete_expense()
        elif choice == "4":
            monthly_report()
        elif choice == "5":
            export_csv()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
