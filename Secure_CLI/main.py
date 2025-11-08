from key_manager import generate_key, load_key
from encryption import encrypt_message, decrypt_message, save_message, load_messages

def menu():
    print("\n🔐 SecureCLI – Text Encryption Tool")
    print("-----------------------------------")
    print("1. Generate new encryption key")
    print("2. Encrypt a message")
    print("3. Decrypt a message")
    print("4. View all encrypted messages")
    print("5. Exit")
    print("-----------------------------------")

def main():
    while True:
        menu()
        choice = input("Choose an option: ")

        if choice == "1":
            generate_key()

        elif choice == "2":
            key = load_key()
            if key:
                message = input("Enter the message to encrypt: ")
                encrypted = encrypt_message(message, key)
                print("🔒 Encrypted message:", encrypted.decode())
                save_message(encrypted)

        elif choice == "3":
            key = load_key()
            if key:
                encrypted_text = input("Enter the encrypted message: ").encode()
                try:
                    decrypted = decrypt_message(encrypted_text, key)
                    print("🔓 Decrypted message:", decrypted)
                except Exception:
                    print("❌ Decryption failed. Wrong key or message.")

        elif choice == "4":
            messages = load_messages()
            if messages:
                print("\n📜 Saved Encrypted Messages:")
                for i, msg in enumerate(messages, 1):
                    print(f"{i}. {msg.decode().strip()}")

        elif choice == "5":
            print("👋 Exiting SecureCLI...")
            break
        else:
            print("⚠️ Invalid option. Try again.")

if __name__ == "__main__":
    main()
