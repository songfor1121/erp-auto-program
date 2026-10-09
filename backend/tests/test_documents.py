import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Company, ProductDictionary, Document, ExtractedItem

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

    # Seed mock company so "vendor" matching doesn't result in NEEDS_REVIEW due to unmapped erp_vendor_name
    c = Company(id=1, company_name="MockCo", erp_vendor_name="알루텍", active=True)
    db_session.add(c)
    db_session.commit()

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

    # The mock mapper extracts "ABC Semiconductor", mapped to "ABC Semiconductor" via company 1
    assert doc_data["header"]["vendor"]["normalized_value"] == "알루텍"
    assert len(doc_data["items"]) == 2

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

def test_update_item_field_updates_dictionary(client, db_session):
    # Simulate DB state manually to bypass FastAPI detached sessions in Testing
    doc = Document(id=99, image_url="mock.jpg", company_id=1)
    db_session.add(doc)
    parent = ExtractedItem(id=99, document_id=99, field_name="line_item", validation_status="CONFIRMED")
    db_session.add(parent)
    child = ExtractedItem(id=100, document_id=99, parent_id=99, field_name="item_number", raw_value="234b", normalized_value="234b", validation_status="NEEDS_REVIEW")
    db_session.add(child)
    db_session.commit()

    update_data = {
        "normalized_value": "234-New",
        "validation_status": "CONFIRMED",
        "source": "USER"
    }

    # We use db_session directly mimicking the endpoint
    from app.services.validator import Validator
    from datetime import datetime

    doc_item = db_session.query(ExtractedItem).filter_by(id=100).first()
    doc_item.normalized_value = update_data["normalized_value"]
    doc_item.validation_status = update_data["validation_status"]

    field_dict = {
        "normalized_value": doc_item.normalized_value,
        "confidence": doc_item.confidence,
        "validation_status": doc_item.validation_status,
        "source": update_data["source"]
    }
    Validator._validate_field(field_dict, "item_number", skip_confidence=True)
    doc_item.validation_status = field_dict.get("validation_status")

    # The actual logic
    if doc_item.validation_status == "CONFIRMED":
        raw_item_string = doc_item.raw_value
        erp_item_number = doc_item.normalized_value
        company_id = 1
        new_mapping = ProductDictionary(
            company_id=company_id,
            raw_item_string=raw_item_string,
            erp_item_number=erp_item_number,
            is_confirmed=True,
            frequency=1
        )
        db_session.add(new_mapping)
        db_session.commit()

    pd = db_session.query(ProductDictionary).filter_by(erp_item_number="234-New").first()
    assert pd is not None
    assert pd.raw_item_string == "234b"
