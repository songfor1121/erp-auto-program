import os
import shutil

def setup_module(module):
    os.makedirs("uploads", exist_ok=True)

def teardown_module(module):
    if os.path.exists("uploads"):
        shutil.rmtree("uploads")

def test_invalid_file_type(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

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

    # Test low confidence "확인 필요" check mapping
    assert doc_data["items"][1]["discount_rate"]["validation_status"] == "NEEDS_REVIEW"

def test_update_field(client):
    # Make sure we have a doc to update
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", b"fake pdf", "application/pdf")}
    )
    doc_id = response.json()["document_id"]

    # Update a top level field
    response = client.put(
        f"/api/v1/documents/{doc_id}/fields/vendor",
        json={"normalized_value": "XYZ Corp", "validation_status": "CONFIRMED", "source": "USER"}
    )
    assert response.status_code == 200

    # Verify update
    doc_data = client.get(f"/api/v1/documents/{doc_id}").json()
    assert doc_data["header"]["vendor"]["normalized_value"] == "XYZ Corp"
    assert doc_data["header"]["vendor"]["source"] == "USER"

def test_update_item_field(client):
    # Make sure we have a doc to update
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.png", b"fake png", "image/png")}
    )
    doc_id = response.json()["document_id"]

    # Update an array item field
    response = client.put(
        f"/api/v1/documents/{doc_id}/items/0/quantity",
        json={"normalized_value": "999", "validation_status": "CONFIRMED", "source": "USER"}
    )
    assert response.status_code == 200

    # Verify update
    doc_data = client.get(f"/api/v1/documents/{doc_id}").json()
    assert doc_data["items"][0]["quantity"]["normalized_value"] == "999"
    assert doc_data["items"][0]["quantity"]["source"] == "USER"
