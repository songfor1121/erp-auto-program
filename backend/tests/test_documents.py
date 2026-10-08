import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client(db_session, monkeypatch):
    def get_db_override():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[app.dependency_overrides.get("get_db", None)] = get_db_override

    # Mock OCR and AI Extractor to bypass actual logic for endpoint testing
    from app.services.ocr_service import OCRService
    monkeypatch.setattr(OCRService, "process", lambda x: "mock text")

    yield TestClient(app)

def test_invalid_file_type(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400

def test_upload_and_extract(client):
    # Test valid upload
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.jpg", b"fake image content", "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    doc_id = data["document_id"]

    # Test retrieve
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    doc_data = response.json()

    assert doc_data["header"]["vendor"]["raw_value"] == "ABC Semiconductor"
    assert len(doc_data["items"]) == 2

    # Since the mock field mapper returns empty for discount rate, AI assigns empty,
    # but the pipeline says CONFIRMED because confidence is artificially 0.99 in field mapper mock.
    # The actual behavior here verifies API and DB persistence work.
    assert doc_data["header"]["discount_rate"]["validation_status"] == "CONFIRMED"

def test_update_field(client):
    # Upload first
    response = client.post("/api/v1/documents/upload", files={"file": ("test.jpg", b"mock", "image/jpeg")})
    doc_id = response.json()["document_id"]

    # Update vendor field
    update_data = {
        "normalized_value": "XYZ Semiconductor",
        "validation_status": "CONFIRMED",
        "source": "USER"
    }
    response = client.put(f"/api/v1/documents/{doc_id}/fields/vendor", json=update_data)
    assert response.status_code == 200

    doc_data = response.json()
    assert doc_data["header"]["vendor"]["normalized_value"] == "XYZ Semiconductor"
    assert doc_data["header"]["vendor"]["validation_status"] == "CONFIRMED"

def test_update_item_field(client):
    # Upload first
    response = client.post("/api/v1/documents/upload", files={"file": ("test.jpg", b"mock", "image/jpeg")})
    doc_id = response.json()["document_id"]

    # Update quantity of first item
    update_data = {
        "normalized_value": "999",
        "validation_status": "CONFIRMED",
        "source": "USER"
    }
    response = client.put(f"/api/v1/documents/{doc_id}/items/0/quantity", json=update_data)
    assert response.status_code == 200

    doc_data = response.json()
    assert doc_data["items"][0]["quantity"]["normalized_value"] == "999"
    assert doc_data["items"][0]["quantity"]["validation_status"] == "CONFIRMED"
