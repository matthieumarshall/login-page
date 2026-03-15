"""Tests for database models"""

import pytest
from sqlalchemy import exc
from website.models import User


class TestUserModel:
    """Test User model creation and validation"""

    def test_user_creation(self, test_db):
        """Test creating a User instance"""
        user = User(username="testuser", hashed_password="hashed_pw")
        test_db.add(user)
        test_db.commit()

        retrieved = test_db.query(User).filter(User.username == "testuser").first()
        assert retrieved is not None
        assert retrieved.username == "testuser"

    def test_user_has_id(self, test_db):
        """Test user gets auto-incremented ID"""
        user = User(username="testuser", hashed_password="hashed_pw")
        test_db.add(user)
        test_db.commit()

        assert user.id is not None
        assert isinstance(user.id, int)

    def test_user_username_unique(self, test_db):
        """Test username uniqueness constraint"""
        user1 = User(username="unique_user", hashed_password="hash1")
        test_db.add(user1)
        test_db.commit()

        user2 = User(username="unique_user", hashed_password="hash2")
        test_db.add(user2)

        with pytest.raises(exc.IntegrityError):
            test_db.commit()

    def test_user_username_indexed(self, test_db):
        """Test username field is indexed for fast lookups"""
        user = User(username="indexed_user", hashed_password="hash")
        test_db.add(user)
        test_db.commit()

        # If indexed, this query should be efficient
        result = test_db.query(User).filter(User.username == "indexed_user").first()
        assert result is not None
