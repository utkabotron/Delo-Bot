#!/usr/bin/env python3
"""
Helper script to generate bcrypt password hash for .env file.

Usage:
    python scripts/generate_password_hash.py

The script will prompt for a password and generate a bcrypt hash
that can be used in .env file as APP_PASSWORD value.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.password import hash_password
import getpass


def main():
    print("=== Delo-Bot Password Hash Generator ===\n")
    print("This script generates a bcrypt hash for your password.")
    print("Copy the generated hash to your .env file as APP_PASSWORD value.\n")

    # Prompt for password (hidden input)
    password = getpass.getpass("Enter password to hash: ")

    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    # Confirm password
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("Error: Passwords do not match")
        sys.exit(1)

    # Generate hash
    print("\nGenerating bcrypt hash...")
    hashed = hash_password(password)

    print("\n✅ Password hash generated successfully!\n")
    print("=" * 60)
    print(f"APP_PASSWORD={hashed}")
    print("=" * 60)
    print("\nCopy the line above to your .env file.")
    print("The application will automatically detect and use the hashed password.")


if __name__ == "__main__":
    main()
