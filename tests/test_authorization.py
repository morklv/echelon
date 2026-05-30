from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_root_route():
    response = client.get("/")
    assert response.status_code in [200,404]
    # 200 - means the root route exists
    # 404 - means app still started correctly


def test_login_invalid_credentials():
    #to verify that the backend rejects the invalid logins

    response = client.post(
        "/auth/login",
        data = {
            "username": "fakeuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def login(username, password):
    # logs in a test user and returns token

    response = client.post(
        "/auth/login",
        data = {
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200
    return response.json()["access_token"]

def test_operator_cannot_delete_incident():
    token = login("operator_test", "test123")

    response = client.delete(
        "/incidents/46",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403

def test_admin_can_delete_incident():
    token = login("admin", "test123")
    create_response = client.post(
        "/incidents/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Temporary Test Incident",
            "category": "test",
            "severity": 2,
            "description": "Temporary pytest incident",
            "latitude": 37.77,
            "longitude": -122.41
        }
    )
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]
    
    delete_response = client.delete(
        f"/incidents/{incident_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert delete_response.status_code == 200

def test_operator_cannot_update_infrastructure_asset():
    token = login("operator_test", "test123")
    response = client.patch(
        "/infrastructure/6",
        headers = {
            "Authorization": f"Bearer {token}"
        },
        json = {
            "name": "Zuckerberg San Francisco General Hospital",
            "asset_type": "hospital",
            "latitude": 37.7558,
            "longitude": -122.4058,
            "criticality": "HIGH",
            "description": "Major emergency medical facility.",
            "operational_status": "NORMAL",
            "geometry_type": "point",
            "geometry_coordinates": None
        }
    )

    assert response.status_code == 403


    def test_admin_can_update_infrastructure_asset():
        token = login("admin", "test123")
        response = client.patch(
            "/infrastructure/6",
            headers = {
                "Authorization": f"Bearer {token}" 
            },
            json = {
            "name": "Updated Hospital",
            "asset_type": "hospital",
            "latitude": 37.7558,
            "longitude": -122.4058,
            "criticality": "HIGH",
            "description": "Updated by pytest",
            "operational_status": "NORMAL",
            "geometry_type": "point",
            "geometry_coordinates": None
            }
        )

        assert response.status_code == 200
        updated_asset = response.json()
        assert updated_asset["name"] == "Updated Hospital"