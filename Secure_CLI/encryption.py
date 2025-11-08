from cryptography.fernet import Fernet
import os

def encrypt_message(message, key):
    """Encrypt a message using the provided key."""
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return encrypted

def decrypt_message(encrypted_message, key):
    """Decrypt an encrypted message using the key."""
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_message)
    return decrypted.decode()

def save_message(encrypted_message):
    """Save encrypted message to file."""
    with open("messages.txt", "ab") as f:
        f.write(encrypted_message + b"\n")
    print("💾 Encrypted message saved to messages.txt")

def load_messages():
    """Load all encrypted messages from file."""
    if not os.path.exists("messages.txt"):
        print("⚠️ No saved messages found.")
        return []
    with open("messages.txt", "rb") as f:
        return f.readlines()
