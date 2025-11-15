#!/usr/bin/env python3
"""
CLI Notes App
"""

import sqlite3
from datetime import datetime

DB = "notes.db"


# ---------------------------------------
# Database Setup
# ---------------------------------------
def get_conn():
    return sqlite3.connect(DB)


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            created_at TEXT NOT NULL
        )
        """)
        conn.commit()


# ---------------------------------------
# Add Note
# ---------------------------------------
def add_note():
    title = input("Title: ").strip()
    if not title:
        print("Title can't be empty.")
        return

    content = input("Content: ").strip()
    if not content:
        print("Content can't be empty.")
        return

    tags = input("Tags (comma-separated): ").strip()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (title, content, tags, created_at) VALUES (?, ?, ?, ?)",
                    (title, content, tags, created_at))
        conn.commit()

    print("✔ Note added successfully!")


# ---------------------------------------
# View All Notes
# ---------------------------------------
def view_notes():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, tags, created_at FROM notes ORDER BY created_at DESC")
        rows = cur.fetchall()

    if not rows:
        print("No notes available.")
        return

    print("\n--- All Notes ---")
    for note in rows:
        print(f"ID: {note[0]} | {note[1]} | Tags: {note[2]} | {note[3]}")


# ---------------------------------------
# View Note by ID
# ---------------------------------------
def view_note_by_id():
    try:
        nid = int(input("Enter note ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM notes WHERE id=?", (nid,))
        row = cur.fetchone()

    if not row:
        print("Note not found.")
        return

    print("\n--- Note Details ---")
    print(f"ID: {row[0]}")
    print(f"Title: {row[1]}")
    print(f"Content: {row[2]}")
    print(f"Tags: {row[3]}")
    print(f"Created: {row[4]}")


# ---------------------------------------
# Search Notes by Keywords
# ---------------------------------------
def search_notes():
    keyword = input("Enter keyword to search: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        return

    pattern = f"%{keyword}%"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, tags, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
        """, (pattern, pattern))
        rows = cur.fetchall()

    if not rows:
        print("No matching notes found.")
        return

    print("\n--- Search Results ---")
    for note in rows:
        print(f"ID: {note[0]} | {note[1]} | Tags: {note[2]} | {note[3]}")


# ---------------------------------------
# Filter Notes by Tags
# ---------------------------------------
def filter_by_tag():
    tag = input("Enter tag: ").strip().lower()
    if not tag:
        print("Tag cannot be empty.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, tags, created_at
            FROM notes
            WHERE lower(tags) LIKE ?
        """, (f"%{tag}%",))
        rows = cur.fetchall()

    if not rows:
        print("No notes found for this tag.")
        return

    print(f"\n--- Notes with Tag '{tag}' ---")
    for note in rows:
        print(f"ID: {note[0]} | {note[1]} | Tags: {note[2]} | {note[3]}")


# ---------------------------------------
# Delete Note
# ---------------------------------------
def delete_note():
    try:
        nid = int(input("Enter note ID to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id=?", (nid,))
        conn.commit()

    print("✔ Note deleted (if it existed).")


# ---------------------------------------
# Menu
# ---------------------------------------
def main_menu():
    init_db()

    while True:
        print("\n=== CLI Notes App ===")
        print("1) Add Note")
        print("2) View All Notes")
        print("3) View Note by ID")
        print("4) Search Notes (Keyword)")
        print("5) Filter Notes (Tag)")
        print("6) Delete Note")
        print("0) Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_note()
        elif choice == "2":
            view_notes()
        elif choice == "3":
            view_note_by_id()
        elif choice == "4":
            search_notes()
        elif choice == "5":
            filter_by_tag()
        elif choice == "6":
            delete_note()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
