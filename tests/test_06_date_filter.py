import pytest
from app import app as flask_app
from database.db import init_db, create_user
from database.db import get_db

@pytest.fixture
def app(tmp_path):
    # Use a temporary file for the database to allow persistence across connections
    db_path = str(tmp_path / "test_spendly.db")
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in with a specific test user."""
    # Create user directly in DB to ensure we have a known ID and password
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Test User", "test@example.com", "pbkdf2:sha256:260000$somehash$somesalt")
    )
    # Note: We use a simple password check in the app, but for tests we can just
    # use the registration route to keep it simple and consistent with how app works.
    conn.close()

    # Use the app's registration and login flow
    client.post('/register', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seeded_expenses(auth_client):
    """Inserts a set of expenses across different dates for the logged-in user."""
    # Get the logged-in user's ID from the session via the client (indirectly)
    # Since we just logged in, we can query the DB for the user we just created.
    conn = get_db()
    user = conn.execute("SELECT id FROM users WHERE email = ?", ("test@example.com",)).fetchone()
    user_id = user["id"]

    expenses = [
        (user_id, 100.0, "Food", "2026-01-01", "Jan Food"),
        (user_id, 200.0, "Rent", "2026-01-15", "Jan Rent"),
        (user_id, 50.0, "Food", "2026-02-01", "Feb Food"),
        (user_id, 300.0, "Tech", "2026-02-15", "Feb Tech"),
        (user_id, 20.0, "Other", "2026-03-01", "Mar Other"),
    ]

    with conn:
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
    conn.close()

class TestDateFilter:
    def test_profile_auth_guard(self, client):
        """Ensure the /profile route still requires authentication."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_profile_no_filters_shows_all(self, auth_client, seeded_expenses):
        """Page should load all-time data when no filters are provided."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
        # Total = 100+200+50+300+20 = 670
        assert '₹670.00' in response.data.decode('utf-8')
        assert '5' in response.data.decode('utf-8')  # Transaction count
        assert 'Tech' in response.data.decode('utf-8') # Top category

    def test_profile_full_range_filter(self, auth_client, seeded_expenses):
        """Filter by a valid date range (Feb 2026)."""
        # Feb expenses: 50.0 (Food), 300.0 (Tech) -> Total 350, Count 2, Top Tech
        response = auth_client.get('/profile?start_date=2026-02-01&end_date=2026-02-28')
        assert response.status_code == 200
        assert '₹350.00' in response.data.decode('utf-8')
        assert '2' in response.data.decode('utf-8')
        assert 'Tech' in response.data.decode('utf-8')
        assert 'Feb Tech' in response.data.decode('utf-8')
        assert 'Feb Food' in response.data.decode('utf-8')
        # Ensure Jan/Mar data is NOT present
        assert b'Jan Food' not in response.data
        assert b'Mar Other' not in response.data

    def test_profile_start_date_only(self, auth_client, seeded_expenses):
        """Only start_date provided: all expenses from Feb 1st onwards."""
        # Feb + Mar: 50 + 300 + 20 = 370
        response = auth_client.get('/profile?start_date=2026-02-01')
        assert response.status_code == 200
        assert '₹370.00' in response.data.decode('utf-8')
        assert '3' in response.data.decode('utf-8')
        assert b'Jan Rent' not in response.data

    def test_profile_end_date_only(self, auth_client, seeded_expenses):
        """Only end_date provided: all expenses up to Jan 31st."""
        # Jan: 100 + 200 = 300
        response = auth_client.get('/profile?end_date=2026-01-31')
        assert response.status_code == 200
        assert '₹300.00' in response.data.decode('utf-8')
        assert '2' in response.data.decode('utf-8')
        assert b'Feb Tech' not in response.data

    def test_profile_reset_filters(self, auth_client, seeded_expenses):
        """Clearing filters (submitting empty params) should restore all-time data."""
        # First apply filter
        auth_client.get('/profile?start_date=2026-02-01&end_date=2026-02-28')
        # Then reset by removing parameters
        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert '₹670.00' in response.data.decode('utf-8')

    def test_profile_no_data_in_range(self, auth_client, seeded_expenses):
        """Dates with no data should show zeroed stats."""
        response = auth_client.get('/profile?start_date=2025-01-01&end_date=2025-01-31')
        assert response.status_code == 200
        assert '₹0.00' in response.data.decode('utf-8')
        assert '0' in response.data.decode('utf-8')
        assert '—' in response.data.decode('utf-8') # Default for no top category

    def test_profile_single_day_range(self, auth_client, seeded_expenses):
        """Start and end date are the same day."""
        # Jan 1st: 100.0
        response = auth_client.get('/profile?start_date=2026-01-01&end_date=2026-01-01')
        assert response.status_code == 200
        assert '₹100.00' in response.data.decode('utf-8')
        assert '1' in response.data.decode('utf-8')

    @pytest.mark.parametrize("invalid_date", [
        "not-a-date",
        "2026-13-01",
        "abc-def-ghi",
        "2026/01/01"
    ])
    def test_profile_invalid_date_formats(self, auth_client, seeded_expenses, invalid_date):
        """Invalid date formats should not crash the server (no 500)."""
        response = auth_client.get(f'/profile?start_date={invalid_date}')
        assert response.status_code == 200, f"Server crashed with invalid start_date: {invalid_date}"

        response = auth_client.get(f'/profile?end_date={invalid_date}')
        assert response.status_code == 200, f"Server crashed with invalid end_date: {invalid_date}"
