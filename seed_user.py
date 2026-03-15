"""
CLI script to add a user to the database.

Usage:
    python seed_user.py <username> <password>

Example:
    python seed_user.py alice mysecretpassword
"""

import sys
from database import engine, SessionLocal
from models import Base, User
from auth import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def add_user(username: str, password: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"Error: User '{username}' already exists.")
            sys.exit(1)

        user = User(username=username, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        print(f"User '{username}' created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python seed_user.py <username> <password>")
        sys.exit(1)

    add_user(sys.argv[1], sys.argv[2])
