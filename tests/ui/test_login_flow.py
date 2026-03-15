"""UI tests using Playwright"""


class TestLoginFlow:
    """Test user login flow"""

    def test_hello_world_login(self, browser):
        """
        Single test: Navigate to home, click login,
        fill credentials, and verify successful login
        """
        # Navigate to home page
        browser.goto("http://localhost:8000/")

        # Verify we're on home page
        page_content = browser.content().lower()
        assert "home" in page_content or browser.url.endswith("/")

        # Click login link
        try:
            browser.click("a:has-text('Login')")
        except Exception:
            # Try alternative selector if text selector fails
            browser.click("a[href='/login']")

        # Wait for navigation and verify on login page
        browser.wait_for_url("**/login")

        # Verify login form exists
        login_form = browser.query_selector("form")
        assert login_form is not None

        # Fill in login credentials
        username_input = browser.query_selector("input[name='username']")
        password_input = browser.query_selector("input[name='password']")

        assert username_input is not None, "Username input not found"
        assert password_input is not None, "Password input not found"

        # Enter test credentials
        username_input.fill("test_user")
        password_input.fill("TestPassword123!@#")

        # Submit form by clicking submit button
        submit_button = browser.query_selector("button[type='submit']")
        if submit_button is None:
            # Try alternative selectors
            submit_button = browser.query_selector("button:has-text('Login')")

        assert submit_button is not None, "Submit button not found"
        submit_button.click()

        # Wait for redirect and page load
        browser.wait_for_load_state("networkidle")

        # Verify we're redirected to home page
        assert browser.url.endswith("/") or "login" not in browser.url


class TestHomePageElements:
    """Test home page structure and elements"""

    def test_home_page_has_navigation(self, browser):
        """Test home page has navigation elements"""
        browser.goto("http://localhost:8000/")

        # Check for navigation or menu
        page_content = browser.content()
        assert "login" in page_content.lower() or "navbar" in page_content.lower()

    def test_home_page_title_exists(self, browser):
        """Test home page has a title"""
        browser.goto("http://localhost:8000/")

        title = browser.title()
        assert title is not None and len(title) > 0


class TestLoginPageElements:
    """Test login page structure"""

    def test_login_form_has_input_fields(self, browser):
        """Test login form has required input fields"""
        browser.goto("http://localhost:8000/login")

        username_input = browser.query_selector("input[name='username']")
        password_input = browser.query_selector("input[name='password']")

        assert username_input is not None
        assert password_input is not None

    def test_login_form_has_submit_button(self, browser):
        """Test login form has submit button"""
        browser.goto("http://localhost:8000/login")

        submit_button = browser.query_selector("button[type='submit']")
        if submit_button is None:
            submit_button = browser.query_selector("button:has-text('Login')")

        assert submit_button is not None
