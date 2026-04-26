#!/usr/bin/env python3
"""
Password Generator - A secure CLI tool for generating random passwords.

Uses Python's `secrets` module for cryptographically secure randomness.
"""

import argparse
import secrets
import string
import sys


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a random password with the specified criteria."""
    characters = ""
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character type must be selected.")

    # Ensure at least one character from each selected type is included
    password = []
    if use_lowercase:
        password.append(secrets.choice(string.ascii_lowercase))
    if use_uppercase:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice(string.punctuation))

    # Fill the rest of the password length with random choices
    for _ in range(length - len(password)):
        password.append(secrets.choice(characters))

    # Shuffle to avoid predictable positions for required characters
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


def check_strength(password: str) -> str:
    """Evaluate password strength and return a rating."""
    score = 0
    length = len(password)

    if length >= 12:
        score += 2
    elif length >= 8:
        score += 1

    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Moderate"
    else:
        return "Strong"


def main():
    parser = argparse.ArgumentParser(
        description="Generate secure random passwords.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python password_generator.py
  python password_generator.py -l 20 --no-symbols
  python password_generator.py -l 12 -c 5
        """,
    )
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=16,
        help="Length of the password (default: 16)",
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=1,
        help="Number of passwords to generate (default: 1)",
    )
    parser.add_argument(
        "--no-uppercase",
        action="store_true",
        help="Exclude uppercase letters",
    )
    parser.add_argument(
        "--no-lowercase",
        action="store_true",
        help="Exclude lowercase letters",
    )
    parser.add_argument(
        "--no-digits",
        action="store_true",
        help="Exclude digits",
    )
    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Exclude special symbols",
    )

    args = parser.parse_args()

    if args.length < 1:
        print("Error: Password length must be at least 1.", file=sys.stderr)
        sys.exit(1)

    if args.count < 1:
        print("Error: Count must be at least 1.", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 40)
    print("       Generated Passwords")
    print("=" * 40)

    for i in range(args.count):
        try:
            password = generate_password(
                length=args.length,
                use_uppercase=not args.no_uppercase,
                use_lowercase=not args.no_lowercase,
                use_digits=not args.no_digits,
                use_symbols=not args.no_symbols,
            )
            strength = check_strength(password)
            print(f"\n  [{i + 1}] {password}")
            print(f"      Strength: {strength}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    print("\n" + "=" * 40)
    print("Done! Keep your passwords safe.")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
