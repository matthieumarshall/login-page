"""Tests for authentication utilities"""

from auth import hash_password, verify_password, _prepare


class TestAuthFunctions:
    """Test password hashing and verification functions"""

    def test_hash_password_creates_hash(self):
        """Test password hashing creates non-plain output"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are long

    def test_hash_password_is_string(self):
        """Test hash_password returns string"""
        hashed = hash_password("test_password")
        assert isinstance(hashed, str)

    def test_verify_password_success(self):
        """Test correct password verification"""
        password = "correct_password"
        hashed = hash_password(password)

        result = verify_password(password, hashed)
        assert result is True

    def test_verify_password_failure(self):
        """Test incorrect password verification"""
        password = "correct_password"
        hashed = hash_password(password)

        result = verify_password("wrong_password", hashed)
        assert result is False

    def test_verify_password_empty_string(self):
        """Test verification with empty password"""
        hashed = hash_password("test")
        result = verify_password("", hashed)
        assert result is False

    def test_hash_same_password_different_hashes(self):
        """Test same password produces different hashes (due to salt)"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Different hashes due to random salt in bcrypt
        assert hash1 != hash2
        # But both verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_hash_long_password(self):
        """Test hashing very long password"""
        long_password = "a" * 500  # Longer than bcrypt's 72-byte limit
        hashed = hash_password(long_password)

        assert verify_password(long_password, hashed)

    def test_hash_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%&*()_+-=[]{}|;:',.<>?/~`"
        hashed = hash_password(password)

        assert verify_password(password, hashed)

    def test_prepare_creates_bytes(self):
        """Test _prepare function creates bytes"""
        result = _prepare("test_password")
        assert isinstance(result, bytes)

    def test_prepare_deterministic(self):
        """Test _prepare produces same output for same input"""
        password = "test_password"
        result1 = _prepare(password)
        result2 = _prepare(password)

        assert result1 == result2
