from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/auth/register",
        json = {
            "username": "testuser_auth",
            "email": "testuser_auth@test.com",
            "password": "test123",
            "role": "admin"
        }
    )

    assert response.status_code in [200, 400] 
    # 200 - user created
    # 400 - user already exists from previous test

    data = response.json()

    if response.status_code == 200:
        assert data["username"] == "testuser_auth"
        assert data["email"] == "testuser_auth@test.com"
        assert data["role"] == "admin"


def test_login_user():
    response = client.post(
        "/auth/login",

        data={
            "username": "testuser_auth",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
 


def test_get_current_user():
    login_response = client.post(
        "/auth/login",
        data = {
            "username": "testuser_auth",
            "password": "test123"
        }
    )

    token = login_response.json()["access_token"]
    #to extract JWT token from response

    response = client.get(
        "/incidents/test-auth",

        headers = {
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser_auth"