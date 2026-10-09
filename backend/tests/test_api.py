import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["api_version"] == "1.0.0"

def test_model_info(client):
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "RandomForestRegressor"
    assert data["target"] == "Demand"
    assert "hour" in data["expected_features"]

def test_valid_prediction(client):
    payload = {
        "hour": 18,
        "day_of_week": 6,
        "month": 8,
        "is_weekend": 1,
        "ChargerType": 0,
        "ChargerCompany": 1,
        "Location": "apartment"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_kwh" in data
    assert isinstance(data["predicted_kwh"], float)
    assert data["model_name"] == "RandomForestRegressor"

def test_invalid_prediction_missing_field(client):
    payload = {
        "hour": 18,
        "day_of_week": 6
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422

def test_invalid_prediction_out_of_bounds(client):
    payload = {
        "hour": 25,
        "day_of_week": 6,
        "month": 8,
        "is_weekend": 1,
        "ChargerType": 0,
        "ChargerCompany": 1,
        "Location": "apartment"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422

def test_analytics_summary(client):
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data

def test_analytics_hourly(client):
    response = client.get("/api/analytics/hourly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 24

def test_model_performance(client):
    response = client.get("/api/model-performance")
    assert response.status_code == 200
    data = response.json()
    assert "validation" in data
    assert "test" in data
    assert "MAE" in data["test"]

def test_cors_headers(client):
    response = client.options(
        "/api/predict",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    # FastAPI CORS middleware echoes the origin back when allow_origins=["*"] is used with allow_credentials=True
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
