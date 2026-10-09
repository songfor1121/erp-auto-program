from sqlalchemy.orm import Session
from app.models import FieldAlias

class FieldMapper:
    @staticmethod
    def map_fields(db: Session, company_id: int, raw_document_data: dict):
        return {
            "order_type": {"raw_value": "일반", "confidence": 0.99},
            "vendor": {"raw_value": "알루텍", "confidence": 0.99},
            "expected_receipt_date": {"raw_value": "2026-10-10", "confidence": 0.99},
            "discount_rate": {"raw_value": "", "confidence": 0.99},
            "items": [
                {
                    "order_number": {"raw_value": "923", "confidence": 0.99},
                    "item_number": {"raw_value": "알루텍", "confidence": 0.98},
                    "item_name": {"raw_value": "도금", "confidence": 0.99},
                    "specification": {"raw_value": "10x200x23", "confidence": 0.99},
                    "quantity": {"raw_value": "500", "confidence": 0.99},
                    "unit_quantity": {"raw_value": "10", "confidence": 0.98},
                    "unit_price": {"raw_value": "1200", "confidence": 0.99},
                    "supply_amount": {"raw_value": "570000", "confidence": 0.96},
                },
                {
                    "order_number": {"raw_value": "26-1008", "confidence": 0.99},
                    "item_number": {"raw_value": "AL6061각재", "confidence": 0.98},
                    "item_name": {"raw_value": "알루미늄", "confidence": 0.99},
                    "specification": {"raw_value": "20x30", "confidence": 0.99},
                    "quantity": {"raw_value": "100", "confidence": 0.99},
                    "unit_quantity": {"raw_value": "1", "confidence": 0.98},
                    "unit_price": {"raw_value": "5000", "confidence": 0.99},
                    "supply_amount": {"raw_value": "500000", "confidence": 0.99},
                }
            ]
        }
