import json
import os

DATA_FILE = "library_data.json"

# ------------------ Helper Functions ------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"books": [], "borrowed": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_book():
    data = load_data()
    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()
    genre = input("Enter genre: ").strip()

    for book in data["books"]:
        if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
            print("This book already exists in the library!")
            return

    data["books"].append({"title": title, "author": author, "genre": genre})
    save_data(data)
    print(f"✅ '{title}' by {author} added to the library.")

def remove_book():
    data = load_data()
    title = input("Enter book title to remove: ").strip()
    author = input("Enter author name: ").strip()

    for book in data["books"]:
        if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
            data["books"].remove(book)
            save_data(data)
            print(f"✅ '{title}' by {author} removed from the library.")
            return
    print("Book not found!")

def search_books():
    data = load_data()
    query = input("Enter title or author to search: ").strip().lower()
    results = [book for book in data["books"] if query in book["title"].lower() or query in book["author"].lower()]
    
    if results:
        print("\nBooks found:")
        for i, book in enumerate(results, start=1):
            print(f"{i}. {book['title']} by {book['author']} ({book['genre']})")
    else:
        print("No books found.")

def borrow_book():
    data = load_data()
    title = input("Enter title of the book to borrow: ").strip()
    author = input("Enter author of the book: ").strip()
    borrower = input("Enter your name: ").strip()

    for book in data["books"]:
        if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
            # Check if already borrowed
            for b in data["borrowed"]:
                if b["title"].lower() == title.lower() and b["author"].lower() == author.lower():
                    print("Sorry, this book is already borrowed.")
                    return
            data["borrowed"].append({"title": title, "author": author, "borrower": borrower})
            save_data(data)
            print(f"✅ {borrower} borrowed '{title}' by {author}.")
            return
    print("Book not found!")

def return_book():
    data = load_data()
    title = input("Enter title of the book to return: ").strip()
    author = input("Enter author of the book: ").strip()
    borrower = input("Enter your name: ").strip()

    for b in data["borrowed"]:
        if b["title"].lower() == title.lower() and b["author"].lower() == author.lower() and b["borrower"].lower() == borrower.lower():
            data["borrowed"].remove(b)
            save_data(data)
            print(f"✅ {borrower} returned '{title}' by {author}.")
            return
    print("No record found for this borrowed book.")

def view_books():
    data = load_data()
    if not data["books"]:
        print("Library is empty!")
        return
    print("\nAll Books in Library:")
    for i, book in enumerate(data["books"], start=1):
        borrowed = any(b["title"].lower() == book["title"].lower() and b["author"].lower() == book["author"].lower() for b in data["borrowed"])
        status = "Borrowed" if borrowed else "Available"
        print(f"{i}. {book['title']} by {book['author']} ({book['genre']}) - {status}")

def view_borrowed():
    data = load_data()
    if not data["borrowed"]:
        print("No books are currently borrowed.")
        return
    print("\nBorrowed Books:")
    for i, b in enumerate(data["borrowed"], start=1):
        print(f"{i}. '{b['title']}' by {b['author']} borrowed by {b['borrower']}")

# ------------------ Main Menu ------------------
def main():
    while True:
        print("\n=== Library Management System ===")
        print("1. View all books")
        print("2. Add a book")
        print("3. Remove a book")
        print("4. Search books")
        print("5. Borrow a book")
        print("6. Return a book")
        print("7. View borrowed books")
        print("8. Exit")

        choice = input("Enter choice (1-8): ").strip()

        if choice == '1':
            view_books()
        elif choice == '2':
            add_book()
        elif choice == '3':
            remove_book()
        elif choice == '4':
            search_books()
        elif choice == '5':
            borrow_book()
        elif choice == '6':
            return_book()
        elif choice == '7':
            view_borrowed()
        elif choice == '8':
            print("Goodbye! 📚")
            break
        else:
            print("Invalid input! Please choose a number between 1-8.")

if __name__ == '__main__':
    main()
