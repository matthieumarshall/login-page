"""
CLI script to add a user to the database.

Usage:
    python -m website.seed_user <username> <password>

Example:
    python -m website.seed_user alice mysecretpassword
"""

import sys
from website.database import engine, SessionLocal
from website.models import Base, User
from website.auth import hash_password

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
        print("Usage: python -m website.seed_user <username> <password>")
        sys.exit(1)

    add_user(sys.argv[1], sys.argv[2])
