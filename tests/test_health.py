from fastapi.testclient import TestClient
# to send fake http requests to the fastapi app

from app.main import app

client = TestClient(app)
# to create a test client connected to the app

def test_health_check():
    response = client.get("/") # send GET request to home/health route
    assert response.status_code == 200 #checks if backend returns successful response
    data = response.json() # to convert response JSON into python dict
    assert data["status"] == "healthy"
    assert data["app"] == "ECHELON"