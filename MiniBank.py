#!/usr/bin/env python3
"""
Mini Banking System - CLI
Save as: mini_bank.py
Run: python mini_bank.py
"""

import sqlite3
import hashlib
import secrets
import getpass
import sys
from datetime import datetime
from typing import Optional

DB = "mini_bank.db"


# --------- Database helpers ----------
def get_conn():
    return sqlite3.connect(DB)


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,              -- deposit, withdraw, transfer_out, transfer_in
            amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        conn.commit()


# --------- Security helpers ----------
def hash_pin(pin: str, salt: str) -> str:
    # returns hex digest of sha256(salt + pin)
    h = hashlib.sha256()
    h.update((salt + pin).encode("utf-8"))
    return h.hexdigest()


def create_salt() -> str:
    return secrets.token_hex(16)


# --------- Core operations ----------
def create_account():
    name = input("Full name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    while True:
        pin = getpass.getpass("Choose a 4-6 digit numeric PIN: ").strip()
        if not (pin.isdigit() and 4 <= len(pin) <= 6):
            print("PIN must be 4-6 digits. Try again.")
            continue
        pin_confirm = getpass.getpass("Confirm PIN: ").strip()
        if pin != pin_confirm:
            print("PINs do not match. Try again.")
            continue
        break

    salt = create_salt()
    pin_hash = hash_pin(pin, salt)
    created_at = datetime.utcnow().isoformat()

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, pin_hash, salt, balance, created_at) VALUES (?, ?, ?, ?, ?)",
                    (name, pin_hash, salt, 0.0, created_at))
        conn.commit()
        user_id = cur.lastrowid
    print(f"Account created. Your account ID is: {user_id}")
    print("Keep your account ID and PIN safe.")


def find_user_by_id(uid: int) -> Optional[dict]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, pin_hash, salt, balance, created_at FROM users WHERE id = ?", (uid,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "pin_hash": row[2],
            "salt": row[3],
            "balance": float(row[4]),
            "created_at": row[5],
        }


def authenticate(uid: int) -> Optional[dict]:
    user = find_user_by_id(uid)
    if not user:
        print("Account not found.")
        return None
    tries = 3
    while tries > 0:
        pin = getpass.getpass("Enter PIN: ").strip()
        if hash_pin(pin, user["salt"]) == user["pin_hash"]:
            print(f"Welcome, {user['name']}!")
            return user
        tries -= 1
        print(f"Incorrect PIN. {tries} attempt(s) left.")
    print("Authentication failed.")
    return None


def update_balance(user_id: int, new_balance: float):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        conn.commit()


def record_transaction(user_id: int, ttype: str, amount: float, details: str = ""):
    ts = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (user_id, type, amount, timestamp, details) VALUES (?, ?, ?, ?, ?)",
                    (user_id, ttype, amount, ts, details))
        conn.commit()


def deposit(user: dict):
    try:
        amt = float(input("Enter amount to deposit: ").strip())
    except ValueError:
        print("Invalid amount.")
        return
    if amt <= 0:
        print("Amount must be positive.")
        return
    new_bal = user["balance"] + amt
    update_balance(user["id"], new_bal)
    record_transaction(user["id"], "deposit", amt, "Deposit via CLI")
    user["balance"] = new_bal
    print(f"Deposited {amt:.2f}. New balance: {new_bal:.2f}")


def withdraw(user: dict):
    try:
        amt = float(input("Enter amount to withdraw: ").strip())
    except ValueError:
        print("Invalid amount.")
        return
    if amt <= 0:
        print("Amount must be positive.")
        return
    if amt > user["balance"]:
        print("Insufficient funds.")
        return
    new_bal = user["balance"] - amt
    update_balance(user["id"], new_bal)
    record_transaction(user["id"], "withdraw", amt, "Withdrawal via CLI")
    user["balance"] = new_bal
    print(f"Withdrew {amt:.2f}. New balance: {new_bal:.2f}")


def show_balance(user: dict):
    # refresh from DB
    u = find_user_by_id(user["id"])
    if u:
        user["balance"] = u["balance"]
    print(f"Account ID: {user['id']} | Name: {user['name']} | Balance: {user['balance']:.2f}")


def transfer(user: dict):
    try:
        target_id = int(input("Recipient account ID: ").strip())
    except ValueError:
        print("Invalid account ID.")
        return
    if target_id == user["id"]:
        print("Cannot transfer to the same account.")
        return
    target = find_user_by_id(target_id)
    if not target:
        print("Recipient account not found.")
        return
    try:
        amt = float(input("Amount to transfer: ").strip())
    except ValueError:
        print("Invalid amount.")
        return
    if amt <= 0:
        print("Amount must be positive.")
        return
    if amt > user["balance"]:
        print("Insufficient funds.")
        return
    # perform transfer
    new_bal_from = user["balance"] - amt
    new_bal_to = target["balance"] + amt
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_bal_from, user["id"]))
        cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_bal_to, target_id))
        # record both sides
        ts = datetime.utcnow().isoformat()
        cur.execute("INSERT INTO transactions (user_id, type, amount, timestamp, details) VALUES (?, ?, ?, ?, ?)",
                    (user["id"], "transfer_out", amt, ts, f"To account {target_id}"))
        cur.execute("INSERT INTO transactions (user_id, type, amount, timestamp, details) VALUES (?, ?, ?, ?, ?)",
                    (target_id, "transfer_in", amt, ts, f"From account {user['id']}"))
        conn.commit()
    user["balance"] = new_bal_from
    print(f"Transferred {amt:.2f} to account {target_id}. New balance: {user['balance']:.2f}")


def show_transactions(user: dict, limit: int = 20):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT type, amount, timestamp, details FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                    (user["id"], limit))
        rows = cur.fetchall()
    if not rows:
        print("No transactions found.")
        return
    print(f"Last {len(rows)} transactions (most recent first):")
    for ttype, amt, ts, details in rows:
        print(f"{ts} | {ttype:12} | {amt:10.2f} | {details}")


def close_account(user: dict):
    confirm = input("Are you sure you want to close your account? This is irreversible (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE user_id = ?", (user["id"],))
        cur.execute("DELETE FROM users WHERE id = ?", (user["id"],))
        conn.commit()
    print("Account closed and all data removed. Goodbye.")
    sys.exit(0)


# --------- CLI flow ----------
def user_menu(user: dict):
    while True:
        print("\n--- Account Menu ---")
        print("1) Show balance")
        print("2) Deposit")
        print("3) Withdraw")
        print("4) Transfer")
        print("5) Transaction history")
        print("6) Close account")
        print("0) Logout")
        choice = input("Select an option: ").strip()
        if choice == "1":
            show_balance(user)
        elif choice == "2":
            deposit(user)
        elif choice == "3":
            withdraw(user)
        elif choice == "4":
            transfer(user)
        elif choice == "5":
            show_transactions(user)
        elif choice == "6":
            close_account(user)
        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")


def main_menu():
    init_db()
    print("=== Welcome to MiniBank CLI ===")
    while True:
        print("\nMain Menu:")
        print("1) Create account")
        print("2) Login")
        print("0) Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            create_account()
        elif choice == "2":
            try:
                uid = int(input("Enter your account ID: ").strip())
            except ValueError:
                print("Invalid account ID.")
                continue
            user = authenticate(uid)
            if user:
                # refresh balance from DB
                user = find_user_by_id(user["id"])
                user_menu(user)
        elif choice == "0":
            print("Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()
