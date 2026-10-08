import pytest
from app.models import Company, Document, DiscountRule
from app.services.pipeline import Pipeline
from app.services.ocr_service import OCRService

@pytest.fixture
def mock_alutec_ocr(monkeypatch):
    def mock_process(filepath):
        return """
        발주구분: 일반
        거래처: 알루텍
        입고예정일: 2026-10-10
        DC:
        수주번호: SO-AL-202301
        품번: AL-998
        품명: 알루미늄
        규격: 1000x2000
        수량: 50
        단위수량: 1
        단가: 50000
        공급가액: 2500000
        """
    monkeypatch.setattr(OCRService, "process", mock_process)

def test_alutec_pipeline(db_session, mock_alutec_ocr, monkeypatch):
    # Setup company
    company = Company(company_name="알루텍", active=True)
    db_session.add(company)
    db_session.commit()

    # Setup discount rule
    dc_rule = DiscountRule(
        company_id=company.id,
        item_number="ALL",
        discount_rate=10.0,
        priority=50,
        active=True
    )
    db_session.add(dc_rule)
    db_session.commit()

    # Setup document
    doc = Document(image_url="IMG_3282.jpeg")
    db_session.add(doc)
    db_session.commit()

    # Override FieldMapper dynamically for this specific test to return Alutec data
    from app.services.field_mapper import FieldMapper
    def mock_map_fields(db, company_id, raw_document_data):
        return {
            "vendor": {"raw_value": "알루텍", "confidence": 0.99}, # Phase 4 structure uses vendor
            "discount_rate": {"raw_value": "", "confidence": 0.90}, # Now in header
            "items": [
                {
                    "order_number": {"raw_value": "SO-AL-202301", "confidence": 0.99}, # Now in line item
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

    # Process
    Pipeline.process_document(db_session, doc.id, OCRService.process("IMG_3282.jpeg"))

    # Validate DB
    from app.models import ExtractedItem
    items = db_session.query(ExtractedItem).filter(ExtractedItem.document_id == doc.id).all()

    # Assert Alutec company identification (using vendor instead of company_name for Phase 4 mock)
    vendor_item = next((i for i in items if i.field_name == "vendor" and i.parent_id is None), None)
    assert vendor_item.raw_value == "알루텍"

    # Assert DC Rate Rule Application (Rule engine puts it in normalized_value)
    # The rule engine must find the header discount_rate and apply the rule
    dc_item = next((i for i in items if i.field_name == "discount_rate" and i.parent_id is None), None)
    assert dc_item.normalized_value == "10.0"

    # Assert Math Validation Deferred (Supply amount remains intact)
    supply_item = next((i for i in items if i.field_name == "supply_amount" and i.parent_id is not None), None)
    assert supply_item.raw_value == "2500000"
    assert supply_item.validation_status == "CONFIRMED" # Because confidence > 0.90
