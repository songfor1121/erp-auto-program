import pytest
from app.models import Company, Document, DiscountRule, ProductDictionary
from app.services.pipeline import Pipeline
from app.services.ocr_service import OCRService

@pytest.fixture
def mock_alutec_ocr(monkeypatch):
    def mock_process(filepath):
        return "mock text"
    monkeypatch.setattr(OCRService, "process", mock_process)

def test_alutec_pipeline(db_session, mock_alutec_ocr, monkeypatch):
    company = Company(company_name="알루텍", erp_vendor_name="알루텍", active=True)
    db_session.add(company)
    db_session.commit()

    dc_rule = DiscountRule(
        company_id=company.id,
        item_number="ALL",
        discount_rate=10.0,
        priority=50,
        active=True
    )
    db_session.add(dc_rule)

    pd = ProductDictionary(company_id=company.id, raw_item_string="AL-998", erp_item_number="도금", is_confirmed=True)
    db_session.add(pd)
    db_session.commit()

    doc = Document(image_url="IMG_3282.jpeg")
    db_session.add(doc)
    db_session.commit()

    from app.services.field_mapper import FieldMapper
    def mock_map_fields(db, company_id, raw_document_data):
        return {
            "vendor": {"raw_value": "알루텍", "confidence": 0.99},
            "discount_rate": {"raw_value": "", "confidence": 0.90},
            "items": [
                {
                    "order_number": {"raw_value": "SO-AL-202301", "confidence": 0.99},
                    "item_number": {"raw_value": "AL-998", "confidence": 0.99},
                    "specification": {"raw_value": "1000x2000", "confidence": 0.99},
                    "quantity": {"raw_value": "50", "confidence": 0.99},
                    "unit_quantity": {"raw_value": "1", "confidence": 0.99},
                    "unit_price": {"raw_value": "50000", "confidence": 0.99},
                    "supply_amount": {"raw_value": "2500000", "confidence": 0.99},
                }
            ]
        }
    monkeypatch.setattr(FieldMapper, "map_fields", mock_map_fields)

    Pipeline.process_document(db_session, doc.id, OCRService.process("IMG_3282.jpeg"))

    from app.models import ExtractedItem
    items = db_session.query(ExtractedItem).filter(ExtractedItem.document_id == doc.id).all()

    vendor_item = next((i for i in items if i.field_name == "vendor" and i.parent_id is None), None)
    assert vendor_item.raw_value == "알루텍"
    assert vendor_item.normalized_value == "알루텍"

    dc_item = next((i for i in items if i.field_name == "discount_rate" and i.parent_id is None), None)
    assert dc_item.normalized_value == "10.0"

    supply_item = next((i for i in items if i.field_name == "supply_amount" and i.parent_id is not None), None)
    assert supply_item.raw_value == "2500000"
    assert supply_item.validation_status == "CONFIRMED"

    item_number = next((i for i in items if i.field_name == "item_number" and i.parent_id is not None), None)
    assert item_number.normalized_value == "도금"
    assert item_number.source == "product_dictionary"
