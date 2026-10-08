from app.schemas.document import DocumentExtractionResponse, FieldData, LineItem

class AIExtractor:
    @staticmethod
    def extract(document_id: int, text: str) -> DocumentExtractionResponse:
        # Phase 1: Mock structured extraction
        # This simulates generating structured JSON from the raw OCR text.
        # Hardcoding the result for the mock pipeline. Notice that discount_rate has a low confidence to trigger the "확인 필요" state.

        return DocumentExtractionResponse(
            document_id=document_id,
            company_name=FieldData(raw_value="ABC Semiconductor", normalized_value="ABC Semiconductor", confidence=0.99),
            transaction_date=FieldData(raw_value="2026-10-07", normalized_value="2026-10-07", confidence=0.95),
            order_number=FieldData(raw_value="SO-123456", normalized_value="SO-123456", confidence=0.97),
            items=[
                LineItem(
                    item_number=FieldData(raw_value="234b", normalized_value="234b", confidence=0.98),
                    specification=FieldData(raw_value="10x20", normalized_value="10x20", confidence=0.99),
                    quantity=FieldData(raw_value="500", normalized_value="500", confidence=0.99),
                    unit_quantity=FieldData(raw_value="10", normalized_value="10", confidence=0.98),
                    unit_price=FieldData(raw_value="1200", normalized_value="1200", confidence=0.99),
                    supply_amount=FieldData(raw_value="570000", normalized_value="570000", confidence=0.96),
                    discount_rate=FieldData(raw_value="5", normalized_value="5", confidence=0.99)
                ),
                LineItem(
                    item_number=FieldData(raw_value="235b", normalized_value="235b", confidence=0.98),
                    specification=FieldData(raw_value="20x30", normalized_value="20x30", confidence=0.99),
                    quantity=FieldData(raw_value="100", normalized_value="100", confidence=0.99),
                    unit_quantity=FieldData(raw_value="1", normalized_value="1", confidence=0.98),
                    unit_price=FieldData(raw_value="5000", normalized_value="5000", confidence=0.99),
                    supply_amount=FieldData(raw_value="500000", normalized_value="500000", confidence=0.99),
                    discount_rate=FieldData(raw_value="", normalized_value="", confidence=0.85, validation_status="NEEDS_REVIEW") # Low confidence!
                )
            ]
        )
