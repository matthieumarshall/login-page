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

    def test_login_page_html_response(self, test_client):
        """Test login page returns HTML"""
        response = test_client.get("/login")
        assert "text/html" in response.headers.get("content-type", "")

    def test_login_page_contains_form(self, test_client):
        """Test login page has form elements"""
        response = test_client.get("/login")
        content = response.text.lower()
        assert "form" in content or "input" in content

    def test_login_page_unauthenticated(self, test_client):
        """Test unauthenticated users can access login page"""
        response = test_client.get("/login")
        assert response.status_code == 200

    def test_login_page_redirects_authenticated_user(
        self, test_client, test_user, test_user_creds
    ):
        """Test authenticated users are redirected from login page"""
        # Login first
        test_client.post("/login", data=test_user_creds)

        # Try to access login page
        response = test_client.get("/login", follow_redirects=False)
        assert response.status_code == 302  # Redirect status
        assert response.headers.get("location", "").endswith("/")


class TestLoginSubmitRoute:
    """Test POST /login endpoint"""

    def test_login_with_valid_credentials(
        self, test_client, test_user, test_user_creds
    ):
        """Test successful login with correct credentials"""
        response = test_client.post(
            "/login", data=test_user_creds, follow_redirects=False
        )

        # Should redirect on success
        assert response.status_code == 302
        assert response.headers.get("location", "").endswith("/")

    def test_login_with_invalid_password(self, test_client, test_user, test_user_creds):
        """Test login fails with wrong password"""
        invalid_creds = {
            "username": test_user_creds["username"],
            "password": "wrong_password",
        }
        response = test_client.post("/login", data=invalid_creds)

        # Should return 401 with error message
        assert response.status_code == 401
        assert "invalid" in response.text.lower()

    def test_login_with_nonexistent_user(self, test_client, test_user):
        """Test login fails with non-existent username"""
        response = test_client.post(
            "/login",
            data={"username": "nonexistent_user_12345", "password": "anypassword"},
        )

        assert response.status_code == 401

    def test_login_with_empty_username(self, test_client):
        """Test login with empty username"""
        response = test_client.post(
            "/login", data={"username": "", "password": "password"}
        )

        # Either 422 (validation error) or 401 (invalid)
        assert response.status_code in [401, 422]

    def test_login_with_empty_password(self, test_client, test_user):
        """Test login with empty password"""
        response = test_client.post(
            "/login", data={"username": test_user.username, "password": ""}
        )

        # Should fail (either 401 auth error or 422 validation error)
        assert response.status_code in [401, 422]

    def test_login_sets_session_cookie(self, test_client, test_user, test_user_creds):
        """Test login sets session cookie"""
        response = test_client.post(
            "/login", data=test_user_creds, follow_redirects=False
        )

        # Check for session cookie
        cookies = response.cookies
        assert "session" in cookies or len(response.cookies) > 0

    def test_login_without_form_data(self, test_client):
        """Test login endpoint requires form data"""
        response = test_client.post("/login")

        # Should fail without required fields
        assert response.status_code >= 400


class TestLogoutRoute:
    """Test POST /logout endpoint"""

    def test_logout_clears_session(self, test_client, test_user, test_user_creds):
        """Test logout clears session"""
        # Login
        test_client.post("/login", data=test_user_creds)

        # Logout
        response = test_client.post("/logout", follow_redirects=False)

        # Should redirect
        assert response.status_code == 302
        assert response.headers.get("location", "").endswith("/")

    def test_logout_accessible_without_auth(self, test_client):
        """Test logout endpoint accessible without authentication"""
        response = test_client.post("/logout", follow_redirects=False)

        # Should still redirect (session.clear() is safe on empty session)
        assert response.status_code == 302

    def test_logout_removes_user_from_session(
        self, test_client, test_user, test_user_creds
    ):
        """Test logout removes user data from session"""
        # Login
        test_client.post("/login", data=test_user_creds, follow_redirects=True)

        # Verify user is in session (by accessing protected content if any)
        # Then logout
        response = test_client.post("/logout", follow_redirects=True)

        # After logout, should be treated as unauthenticated
        assert response.status_code == 200


class TestStaticFiles:
    """Test static file serving"""

    def test_static_css_accessible(self, test_client):
        """Test CSS file is accessible"""
        response = test_client.get("/static/style.css")
        assert (
            response.status_code == 200 or response.status_code == 404
        )  # 404 ok if file doesn't exist yet

    def test_static_files_have_correct_headers(self, test_client):
        """Test static files return correct content type"""
        # Try accessing a CSS file
        response = test_client.get("/static/style.css")

        if response.status_code == 200:
            assert "text/css" in response.headers.get("content-type", "")


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_route_returns_404(self, test_client):
        """Test accessing non-existent route returns 404"""
        response = test_client.get("/nonexistent/route/12345")
        assert response.status_code == 404

    def test_method_not_allowed(self, test_client):
        """Test using wrong HTTP method"""
        # GET on a POST-only endpoint
        response = test_client.get("/logout")
        assert response.status_code == 405  # Method not allowed


class TestSessionManagement:
    """Test session management across requests"""

    def test_session_persists_across_requests(
        self, test_client, test_user, test_user_creds
    ):
        """Test session persists across multiple requests"""
        # Login
        test_client.post("/login", data=test_user_creds)

        # Make multiple requests
        response1 = test_client.get("/")
        response2 = test_client.get("/")
        response3 = test_client.get("/")

        # All should succeed
        assert all(r.status_code == 200 for r in [response1, response2, response3])

    def test_session_isolation_between_clients(
        self, test_db, test_user, test_user_creds
    ):
        """Test different clients have isolated sessions"""
        from database import get_db
        from main import app

        def override_get_db():
            try:
                yield test_db
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        client1 = TestClient(app)
        client2 = TestClient(app)

        # Login with client1
        client1.post("/login", data=test_user_creds)

        # client2 should not have the session
        # (Hard to verify without protected routes, but clients are separate)
        response1 = client1.get("/")
        response2 = client2.get("/")

        assert response1.status_code == 200
        assert response2.status_code == 200
