from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def get_auth_headers():

    login_response = client.post(
        "/auth/login",
        data={
            "username": "testuser_auth",
            "password": "test123"
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_incident():
    headers = get_auth_headers()
    response = client.post(
        "/incidents/",
    
        json = {
            "title": "Test fire incident",
            "description": "Smoke reported near infrastructure",
            "category": "fire",
            "severity": 4,
            "latitude": 37.7749,
            "longitude": -122.4194
        },

        headers = headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test fire incident"
    assert data["category"] == "fire"
    assert data["severity"] == 4


def test_get_my_incidents():
    headers = get_auth_headers()

    response = client.get(
        "/incidents/",
        headers = headers
    )

    assert response.status_code == 200
    
    data = response.json()

    assert isinstance(data, list)
    # to confirm that backend returns a list of incidents


def test_update_incident():
    headers = get_auth_headers()

    create_response = client.post(
        "/incidents/",
        json = {
            "title": "Incident to update",
            "description": "Initial incident description",
            "category": "fire",
            "severity": 3,
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        headers = headers
    )

    incident_id = create_response.json()["id"]

    update_response = client.patch(
        f"/incidents/{incident_id}",
        json = {
            "status": "resolved",
            "severity": 2
        },
        headers = headers
    )
    assert update_response.status_code == 200

    data = update_response.json()

    assert data["status"] == "resolved"
    assert data["severity"] == 2


def test_delete_incident():
    headers = get_auth_headers()
    create_response = client.post(
        "/incidents/",
        json = {
            "title": "Incident to delete",
            "description": "Delete test incident",
            "category": "fire",
            "severity": 3,
            "latitude": 37.7749,
            "longitude": -122.4194
        },

        headers = headers
    )

    incident_id = create_response.json()["id"]
    
    delete_response = client.delete(
        f"/incidents/{incident_id}",

        headers = headers
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["message"] == "Incident deleted successfully"


def test_viewer_cannot_create_incident():
    # tests that viewer role cannot create incidents

    client.post(
        "/auth/register",
        json={
            "username": "viewer_test",
            "email": "viewer_test@test.com",
            "password": "test123",
            "role": "viewer"
        }
    )
    # creates viewer user if not already created

    login_response = client.post(
        "/auth/login",
        data={
            "username": "viewer_test",
            "password": "test123"
        }
    )
    # logs in as viewer

    token = login_response.json()["access_token"]
    # extracts JWT token

    response = client.post(
        "/incidents/",
        json={
            "title": "Viewer blocked incident",
            "description": "Viewer should not create this",
            "category": "fire",
            "severity": 3,
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    # viewer tries to create incident

    assert response.status_code == 403
    # backend should block viewer

def test_operator_cannot_delete_incident():
    # tests that operator can create but cannot delete

    client.post(
        "/auth/register",
        json={
            "username": "operator_test",
            "email": "operator_test@test.com",
            "password": "test123",
            "role": "operator"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "operator_test",
            "password": "test123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = client.post(
        "/incidents/",
        json={
            "title": "Operator incident",
            "description": "Operator can create this incident",
            "category": "fire",
            "severity": 3,
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        headers=headers
    )

    incident_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/incidents/{incident_id}",
        headers=headers
    )

    assert delete_response.status_code == 403