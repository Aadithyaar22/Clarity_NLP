from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pipeline_endpoint():
    response = client.post(
        "/api/v1/pipeline",
        json={"documents": ["I loved this product", "Worst service ever"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["documents"]) == 2
    assert payload["documents"][0]["sentiment"]["label"] == "positive"
