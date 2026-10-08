from sqlalchemy.orm import Session
from app.models import FieldAlias

class FieldMapper:
    @staticmethod
    def map_fields(db: Session, company_id: int, raw_document_data: dict):
        # Ideally, we query FieldAlias where company_id = company_id
        # aliases = db.query(FieldAlias).filter(FieldAlias.company_id == company_id).all()
        # and translate incoming raw field labels to Standard Field Names.
        # Returning mock structure for Phase 2 pipeline validation:

        return {
            "order_type": {"raw_value": "일반", "confidence": 0.99},
            "vendor": {"raw_value": "ABC Semiconductor", "confidence": 0.99},
            "expected_receipt_date": {"raw_value": "2026-10-10", "confidence": 0.99},
            "discount_rate": {"raw_value": "5", "confidence": 0.99},
            "order_number": {"raw_value": "SO-123456", "confidence": 0.99},
            "transaction_date": {"raw_value": "2026-10-07", "confidence": 0.95},
            "company_name": {"raw_value": "ABC Semiconductor", "confidence": 0.99},
            "items": [
                {
                    "item_number": {"raw_value": "234b", "confidence": 0.98},
                    "specification": {"raw_value": "10x20", "confidence": 0.99},
                    "quantity": {"raw_value": "500", "confidence": 0.99},
                    "unit_quantity": {"raw_value": "10", "confidence": 0.98},
                    "unit_price": {"raw_value": "1200", "confidence": 0.99},
                    "supply_amount": {"raw_value": "570000", "confidence": 0.96},
                    "discount_rate": {"raw_value": "5", "confidence": 0.99}
                },
                {
                    "item_number": {"raw_value": "235b", "confidence": 0.98},
                    "specification": {"raw_value": "20x30", "confidence": 0.99},
                    "quantity": {"raw_value": "100", "confidence": 0.99},
                    "unit_quantity": {"raw_value": "1", "confidence": 0.98},
                    "unit_price": {"raw_value": "5000", "confidence": 0.99},
                    "supply_amount": {"raw_value": "500000", "confidence": 0.99},
                    "discount_rate": {"raw_value": "", "confidence": 0.85}
                }
            ]
        }
