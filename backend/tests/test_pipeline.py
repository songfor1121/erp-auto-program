from fastapi.testclient import TestClient
from app.main import app
from app.services.field_mapper import FieldMapper
from app.models import Company, NormalizationRule, DiscountRule, ProductDictionary

client = TestClient(app)

def test_company_identification(db_session, monkeypatch):
    from app.services.company_identifier import CompanyIdentifier
    company = Company(company_name="ABC Semiconductor", active=True)
    db_session.add(company)
    db_session.commit()

    identity = CompanyIdentifier.identify(db_session, "ABC Semiconductor Invoice...")
    assert identity["company_id"] == company.id

def test_dc_rate_priority(db_session):
    c = Company(company_name="XYZ Corp", active=True)
    db_session.add(c)
    db_session.commit()

    dr_default = DiscountRule(company_id=c.id, item_number="ALL", discount_rate=10.0, priority=50, active=True)
    dr_specific = DiscountRule(company_id=c.id, item_number="235b", discount_rate=15.0, priority=100, active=True)
    db_session.add_all([dr_default, dr_specific])
    db_session.commit()

    structured_data = {
        "header": {
             "discount_rate": {"raw_value": "", "confidence": 0.50}
        },
        "items": [
             {"item_number": {"raw_value": "235b", "confidence": 0.99}},
             {"item_number": {"raw_value": "999", "confidence": 0.99}}
        ]
    }
    from app.services.rule_engine import RuleEngine
    normalized = RuleEngine.apply_rules(db_session, c.id, structured_data)

    assert normalized["header"]["discount_rate"]["normalized_value"] == "10.0"

def test_unit_conversion(db_session):
    c = Company(company_name="XYZ Corp", active=True)
    db_session.add(c)
    db_session.commit()

    # Needs a product dictionary rule now instead of normal rule for item number
    pd = ProductDictionary(company_id=c.id, raw_item_string="234b", erp_item_number="234(B)", is_confirmed=True)
    db_session.add(pd)
    db_session.commit()

    structured_data = {
        "header": {},
        "items": [{"item_number": {"raw_value": "234b", "confidence": 0.99}}]
    }

    from app.services.rule_engine import RuleEngine
    normalized = RuleEngine.apply_rules(db_session, c.id, structured_data)
    assert normalized["items"][0]["item_number"]["normalized_value"] == "234(B)"

def test_multiple_items_and_raw_preservation(db_session):
    c = Company(company_name="XYZ Corp", active=True)
    db_session.add(c)
    db_session.commit()

    structured_data = {
        "header": {},
        "items": [
            {"quantity": {"raw_value": "500", "confidence": 0.99}, "supply_amount": {"raw_value": "570000", "confidence": 0.99}},
            {"quantity": {"raw_value": "100", "confidence": 0.99}, "supply_amount": {"raw_value": "50000", "confidence": 0.99}}
        ]
    }
    from app.services.rule_engine import RuleEngine
    normalized = RuleEngine.apply_rules(db_session, c.id, structured_data)

    assert normalized["items"][0]["quantity"]["raw_value"] == "500"
    assert normalized["items"][0]["supply_amount"]["raw_value"] == "570000"

def test_full_pipeline_structure(db_session, monkeypatch):
    from app.services.ocr_service import OCRService
    monkeypatch.setattr(OCRService, "process", lambda x: "Mock text")

    with open("tests/mock.pdf", "wb") as f:
        f.write(b"%PDF-1.4 mock")

    response = client.post("/api/v1/documents/upload", files={"file": ("mock.pdf", open("tests/mock.pdf", "rb"), "application/pdf")})
    assert response.status_code == 200
    doc_id = response.json()["document_id"]

    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()

    assert "header" in data
    assert "items" in data
    assert len(data["items"]) == 2
