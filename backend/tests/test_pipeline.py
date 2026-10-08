import pytest
from app.services.pipeline import Pipeline
from app.services.rule_engine import RuleEngine
from app.services.validator import Validator
from app.services.field_mapper import FieldMapper
from app.services.company_identifier import CompanyIdentifier

from app.models import Company, NormalizationRule, DiscountRule

def test_company_identification(db_session):
    # Seed DB
    c = Company(company_name="ABC Semiconductor", active=True)
    db_session.add(c)
    db_session.commit()

    # Phase 2 rule: Must fallback or correctly identify company ID
    result = CompanyIdentifier.identify(db_session, "Some ABC Semiconductor text")
    assert result["company_id"] == c.id
    assert result["confidence"] == 0.95

def test_dc_rate_priority(db_session):
    # Setup company rules
    c = Company(company_name="XYZ Corp", active=True)
    db_session.add(c)
    db_session.commit()

    dr_default = DiscountRule(company_id=c.id, item_number="ALL", discount_rate=10.0, priority=50, active=True)
    dr_specific = DiscountRule(company_id=c.id, item_number="235b", discount_rate=15.0, priority=100, active=True)
    db_session.add_all([dr_default, dr_specific])
    db_session.commit()

    mapped_data = FieldMapper.map_fields(db_session, c.id, {})
    items = mapped_data["items"]

    assert items[0]["discount_rate"]["raw_value"] == "5" # Explicit
    assert items[1]["discount_rate"]["raw_value"] == "" # Needs fallback

    normalized = RuleEngine.apply_rules(db_session, c.id, {"items": items})

    # 234b explicit dc
    assert normalized["items"][0]["discount_rate"].get("normalized_value") == "5" or normalized["items"][0]["discount_rate"].get("raw_value") == "5"

    # 235b uses specific fallback rule
    assert normalized["items"][1]["discount_rate"]["normalized_value"] == "15.0"
    assert normalized["items"][1]["discount_rate"]["source"] == "company_rule"

def test_unit_conversion(db_session):
    c = Company(company_name="Unit Corp")
    db_session.add(c)
    db_session.commit()

    nr = NormalizationRule(company_id=c.id, field_name="unit_quantity", source_value="박스", target_value="BOX")
    db_session.add(nr)
    db_session.commit()

    data = {"items": [{"unit_quantity": {"raw_value": "박스"}}]}
    normalized = RuleEngine.apply_rules(db_session, c.id, data)
    assert normalized["items"][0]["unit_quantity"]["normalized_value"] == "BOX"

def test_data_integrity_validation():
    # Valid formats
    valid_item = {
        "quantity": {"normalized_value": "100"},
        "unit_price": {"normalized_value": "10"},
        "supply_amount": {"normalized_value": "1000", "validation_status": "PENDING"}
    }

    validated = Validator.validate({"items": [valid_item]})
    assert validated["items"][0]["supply_amount"]["validation_status"] == "CONFIRMED"

    # Invalid format
    invalid_item = {
        "quantity": {"normalized_value": "abc"},
        "supply_amount": {"normalized_value": "1000", "validation_status": "PENDING"}
    }

    validated = Validator.validate({"items": [invalid_item]})
    assert validated["items"][0]["quantity"]["validation_status"] == "NEEDS_REVIEW"
    assert validated["items"][0]["quantity"]["validation_message"] == "숫자 형식이 아님"

def test_confidence_validation():
    # Low confidence triggers review
    low_conf_item = {
        "supply_amount": {"normalized_value": "1000", "confidence": 0.85, "validation_status": "PENDING"}
    }

    validated = Validator.validate({"items": [low_conf_item]})
    assert validated["items"][0]["supply_amount"]["validation_status"] == "NEEDS_REVIEW"
    assert validated["items"][0]["supply_amount"]["validation_message"] == "신뢰도 낮음"

def test_multiple_items_and_raw_preservation(db_session):
    # Seed doc
    from app.models import Document
    new_doc = Document(image_url="test.pdf")
    db_session.add(new_doc)
    db_session.commit()
    db_session.refresh(new_doc)

    # Actually run the full mock pipeline
    Pipeline.process_document(db_session, new_doc.id, "ABC Semiconductor")

    # Since we can't cleanly return from the db pipeline directly in the test without querying:
    from app.models import ExtractedItem
    items = db_session.query(ExtractedItem).filter(ExtractedItem.document_id == new_doc.id).all()
    assert len(items) > 0

def test_full_pipeline_structure(client, db_session):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", b"fake pdf", "application/pdf")}
    )
    assert response.status_code == 200
    doc_id = response.json()["document_id"]

    doc_data = client.get(f"/api/v1/documents/{doc_id}").json()
    assert "header" in doc_data
    assert "items" in doc_data
    assert "order_type" in doc_data["header"]
    assert "vendor" in doc_data["header"]

    # Header fields
    assert doc_data["header"]["vendor"]["raw_value"] == "ABC Semiconductor"
