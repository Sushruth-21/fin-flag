from app import app


# Test Cases for dashboard redirects unauthenticated users to login
def test_dashboard_redirects_unauthenticated_user():
    client = app.test_client()
    response = client.get('/dashboard')

    assert response.status_code == 302
    assert response.location == "/login"


# Test Cases for login route
def test_login_route():
    client = app.test_client()
    response = client.get('/login')

    assert response.status_code == 200
    assert b"Login" in response.data


# Test Cases for login route with missing credentials
def test_login_rejects_missing_credentials():
    client = app.test_client()
    response = client.post('/login', data={'username': 'testuser'})

    assert response.status_code == 400
    assert b"All fields required" in response.data


# Test Cases for login route with invalid credentials are rejected
def test_login_rejects_invalid_credentials():
    client = app.test_client()
    response = client.post('/login', data={'username': 'invaliduser', 'password': 'invalidpass'})

    assert response.status_code == 400
    assert b"Invalid username and/or password" in response.data


# Test Cases for session contains admin_id for the dashboard route to allow access
def test_dashboard_allows_authenticated_user():
    client = app.test_client()

    # Simulate an authenticated session
    with client.session_transaction() as session:
        session['admin_id'] = 1  # check session["admin_id"] is present

    response = client.get('/dashboard')

    assert response.status_code == 200
    assert b"SOC Dashboard" in response.data


# Test Cases for API endpoint without session returns 401 Unauthorized
def test_api_alerts_rejects_unauthenticated_user():
    client = app.test_client()
    response = client.get('/api/alerts')

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"} # JSON response into Python dictionary and check for the error message