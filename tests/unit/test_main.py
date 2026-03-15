"""Tests for FastAPI routes and main application"""

from fastapi.testclient import TestClient


class TestHomeRoute:
    """Test home page endpoint"""

    def test_home_page_loads(self, test_client):
        """Test home page returns 200 status"""
        response = test_client.get("/")
        assert response.status_code == 200

    def test_home_page_html_response(self, test_client):
        """Test home page returns HTML"""
        response = test_client.get("/")
        assert "text/html" in response.headers.get("content-type", "")

    def test_home_page_contains_title(self, test_client):
        """Test home page has title"""
        response = test_client.get("/")
        content = response.text.lower()
        assert "<title>" in content or "home" in content

    def test_home_page_unauthenticated_user(self, test_client):
        """Test home page accessible without authentication"""
        response = test_client.get("/")
        assert response.status_code == 200

    def test_home_page_authenticated_user(
        self, test_client, test_user, test_user_creds
    ):
        """Test home page accessible with authentication"""
        # Login first
        response = test_client.post(
            "/login", data=test_user_creds, follow_redirects=True
        )

        # Navigate to home
        response = test_client.get("/")
        assert response.status_code == 200


class TestLoginPageRoute:
    """Test GET /login endpoint"""

    def test_login_page_loads(self, test_client):
        """Test login page returns 200 status"""
        response = test_client.get("/login")
        assert response.status_code == 200
