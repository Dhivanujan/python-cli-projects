import random
import string

def generate_password(length=12, use_digits=True, use_symbols=True):
    """Generate a random password with given options."""
    characters = string.ascii_letters  # a-zA-Z

    if use_digits:
        characters += string.digits  # 0-9
    if use_symbols:
        characters += string.punctuation  # !@#$%^&*()

    if length < 4:
        print("Password length should be at least 4 characters.")
        return None

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def main():
    print("=== Python CLI Password Generator ===")
    
    # Get user input
    try:
        length = int(input("Enter password length (default 12): ") or 12)
    except ValueError:
        length = 12

    use_digits = input("Include digits? (y/n, default y): ").lower() != 'n'
    use_symbols = input("Include symbols? (y/n, default y): ").lower() != 'n'

    # Generate password
    password = generate_password(length, use_digits, use_symbols)
    if password:
        print(f"\nGenerated Password: {password}")

if __name__ == "__main__":
    main()
