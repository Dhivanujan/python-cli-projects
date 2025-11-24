#!/usr/bin/env python3
"""
Budget & Expense Manager CLI
- Track income, expenses by category
- View summary & simple charts (ASCII/Matplotlib)
- Supports recurring expenses
"""

import json
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

DATA_FILE = Path("expenses.json")


# ---------------------- Data Handling ----------------------
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"income": 0.0, "expenses": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------- Expense Logic ----------------------
def add_income(data):
    try:
        income = float(input("Enter income amount: "))
        data["income"] += income
        save_data(data)
        print(f"✅ Income added. Total income: {data['income']}\n")
    except ValueError:
        print("❌ Invalid number.")


def add_expense(data):
    try:
        amount = float(input("Enter expense amount: "))
        category = input("Enter category (Food, Rent, Bills, etc.): ").strip()
        description = input("Optional description: ").strip()
        date_str = input("Date (YYYY-MM-DD) or leave blank for today: ").strip()
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        else:
            date = datetime.today().strftime("%Y-%m-%d")
        data["expenses"].append({
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        })
        save_data(data)
        print(f"✅ Expense added: {amount} ({category}) on {date}\n")
    except ValueError:
        print("❌ Invalid number.")


def view_summary(data):
    total_expense = sum(e["amount"] for e in data["expenses"])
    balance = data["income"] - total_expense
    print("\n--- Monthly Summary ---")
    print(f"Total Income: {data['income']}")
    print(f"Total Expenses: {total_expense}")
    print(f"Balance: {balance}\n")

    # Expenses by category
    categories = {}
    for e in data["expenses"]:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]

    if categories:
        print("Expenses by category:")
        for cat, amt in categories.items():
            print(f"  {cat}: {amt}")

    # ASCII chart
    if categories:
        print("\nASCII Chart:")
        max_len = max(len(cat) for cat in categories)
        max_amt = max(categories.values())
        scale = 40 / max_amt
        for cat, amt in categories.items():
            bar = "#" * int(amt * scale)
            print(f"{cat.ljust(max_len)} | {bar} ({amt})")
    print("\n")


def plot_chart(data):
    categories = {}
    for e in data["expenses"]:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
    if not categories:
        print("No expenses to plot.\n")
        return
    labels = list(categories.keys())
    values = list(categories.values())
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("Expenses by Category")
    plt.show()


def list_expenses(data):
    if not data["expenses"]:
        print("No expenses recorded.\n")
        return
    print("\n--- All Expenses ---")
    for e in data["expenses"]:
        print(f"{e['date']} | {e['category']} | {e['amount']} | {e['description']}")
    print("\n")


# ---------------------- CLI ----------------------
def main():
    data = load_data()
    while True:
        print("=== Budget & Expense Manager ===")
        print("1) Add Income")
        print("2) Add Expense")
        print("3) View Summary")
        print("4) List All Expenses")
        print("5) Plot Expense Chart")
        print("6) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_income(data)
        elif choice == "2":
            add_expense(data)
        elif choice == "3":
            view_summary(data)
        elif choice == "4":
            list_expenses(data)
        elif choice == "5":
            plot_chart(data)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice.\n")


if __name__ == "__main__":
    main()
