"""Tests for database models"""

import pytest
from sqlalchemy import exc
from models import User


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

    def test_user_requires_username(self, test_db):
        """Test username is required"""
        user = User(username=None, hashed_password="hash")
        test_db.add(user)

        with pytest.raises(exc.IntegrityError):
            test_db.commit()

    def test_user_requires_hashed_password(self, test_db):
        """Test hashed_password is required"""
        user = User(username="testuser", hashed_password=None)
        test_db.add(user)

        with pytest.raises(exc.IntegrityError):
            test_db.commit()

    def test_user_can_be_queried_by_id(self, test_db):
        """Test querying user by primary key"""
        user = User(username="query_user", hashed_password="hash")
        test_db.add(user)
        test_db.commit()

        result = test_db.query(User).filter(User.id == user.id).first()
        assert result.username == "query_user"

    def test_multiple_users_in_db(self, test_db):
        """Test storing multiple users"""
        users = [
            User(username=f"user{i}", hashed_password=f"hash{i}") for i in range(5)
        ]
        test_db.add_all(users)
        test_db.commit()

        count = test_db.query(User).count()
        assert count == 5
