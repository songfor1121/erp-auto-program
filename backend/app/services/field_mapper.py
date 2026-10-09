from sqlalchemy.orm import Session
from app.services.ai_extractor import AIExtractor

class FieldMapper:
    @staticmethod
    def map_fields(db: Session, company_id: int, extracted_response):
        data = extracted_response.model_dump()

        return {
            "order_type": data["header"].get("order_type", {}),
            "vendor": data["header"].get("vendor", {}),
            "expected_receipt_date": data["header"].get("expected_receipt_date", {}),
            "discount_rate": data["header"].get("discount_rate", {}),
            "transaction_date": data["header"].get("transaction_date", {}),
            "items": data.get("items", [])
        }
