from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    """Generate and save a new key."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print("✅ New key generated and saved as secret.key")

def load_key():
    """Load the existing key."""
    if not os.path.exists(KEY_FILE):
        print("⚠️ No key found. Please generate one first using option 1.")
        return None
    with open(KEY_FILE, "rb") as f:
        return f.read()
