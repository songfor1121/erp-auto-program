from sqlalchemy.orm import Session

class ERPAdapter:
    @staticmethod
    def map_to_erp(db: Session, company_id: int, validated_data: dict):
        # Mocks mapping standard fields to final ERP schema fields.
        return validated_data
