from app.schemas.document import DocumentExtractionResponse, HeaderFields, FieldData, LineItem

class AIExtractor:
    @staticmethod
    def extract(document_id: int, text: str) -> DocumentExtractionResponse:
        # Phase 1/4: Mock structured extraction
        # This simulates generating structured JSON from the raw OCR text.
        # Updated to match the exactly 12 fields structure.

        return DocumentExtractionResponse(
            document_id=document_id,
            header=HeaderFields(
                order_type=FieldData(raw_value="일반", normalized_value="일반", confidence=0.99),
                vendor=FieldData(raw_value="ABC Semiconductor", normalized_value="ABC Semiconductor", confidence=0.99),
                expected_receipt_date=FieldData(raw_value="2026-10-07", normalized_value="2026-10-07", confidence=0.95),
                discount_rate=FieldData(raw_value="", normalized_value="", confidence=0.85, validation_status="NEEDS_REVIEW") # Usually empty or missing from header
            ),
            items=[
                LineItem(
                    order_number=FieldData(raw_value="SO-123456", normalized_value="SO-123456", confidence=0.97),
                    item_number=FieldData(raw_value="234b", normalized_value="234b", confidence=0.98),
                    item_name=FieldData(raw_value="Resistor", normalized_value="Resistor", confidence=0.99),
                    specification=FieldData(raw_value="10x20", normalized_value="10x20", confidence=0.99),
                    quantity=FieldData(raw_value="500", normalized_value="500", confidence=0.99),
                    unit_quantity=FieldData(raw_value="10", normalized_value="10", confidence=0.98),
                    unit_price=FieldData(raw_value="1200", normalized_value="1200", confidence=0.99),
                    supply_amount=FieldData(raw_value="570000", normalized_value="570000", confidence=0.96)
                ),
                LineItem(
                    order_number=FieldData(raw_value="SO-123456", normalized_value="SO-123456", confidence=0.97),
                    item_number=FieldData(raw_value="235b", normalized_value="235b", confidence=0.98),
                    item_name=FieldData(raw_value="Capacitor", normalized_value="Capacitor", confidence=0.99),
                    specification=FieldData(raw_value="20x30", normalized_value="20x30", confidence=0.99),
                    quantity=FieldData(raw_value="100", normalized_value="100", confidence=0.99),
                    unit_quantity=FieldData(raw_value="1", normalized_value="1", confidence=0.98),
                    unit_price=FieldData(raw_value="5000", normalized_value="5000", confidence=0.99),
                    supply_amount=FieldData(raw_value="500000", normalized_value="500000", confidence=0.99)
                )
            ]
        )
