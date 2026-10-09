import os
import json
from app.schemas.document import DocumentExtractionResponse, HeaderFields, FieldData, LineItem

class AIExtractor:
    @staticmethod
    def extract(document_id: int, file_path_or_text: str) -> DocumentExtractionResponse:

        use_mock = os.getenv("USE_MOCK_OCR", "True").lower() in ("true", "1", "yes")
        api_key = os.getenv("GEMINI_API_KEY")

        if use_mock or not api_key:
            return AIExtractor._mock_extract(document_id)

        # REAL AI EXTRACTION (Pseudocode until actual dependency and approval)
        # import google.generativeai as genai
        # genai.configure(api_key=api_key)
        # model = genai.GenerativeModel('gemini-1.5-flash')
        # ... read file ...
        # response = model.generate_content(...)
        # return AIExtractor._parse_ai_response(document_id, response.text)

        # Fallback if something goes wrong
        return AIExtractor._mock_extract(document_id)

    @staticmethod
    def _mock_extract(document_id: int) -> DocumentExtractionResponse:
        return DocumentExtractionResponse(
            document_id=document_id,
            header=HeaderFields(
                order_type=FieldData(raw_value="일반", normalized_value="일반", confidence=0.99),
                vendor=FieldData(raw_value="알루텍", normalized_value="알루텍", confidence=0.99),
                expected_receipt_date=FieldData(raw_value="2026-10-07", normalized_value="2026-10-07", confidence=0.95),
                discount_rate=FieldData(raw_value="", normalized_value="", confidence=0.85, validation_status="NEEDS_REVIEW")
            ),
            items=[
                LineItem(
                    order_number=FieldData(raw_value="923", normalized_value="923", confidence=0.97),
                    item_number=FieldData(raw_value="알루텍", normalized_value="알루텍", confidence=0.98),
                    item_name=FieldData(raw_value="도금", normalized_value="도금", confidence=0.99),
                    specification=FieldData(raw_value="10x200x23", normalized_value="10x200x23", confidence=0.99),
                    quantity=FieldData(raw_value="500", normalized_value="500", confidence=0.99),
                    unit_quantity=FieldData(raw_value="10", normalized_value="10", confidence=0.98),
                    unit_price=FieldData(raw_value="1200", normalized_value="1200", confidence=0.99),
                    supply_amount=FieldData(raw_value="570000", normalized_value="570000", confidence=0.96)
                ),
                LineItem(
                    order_number=FieldData(raw_value="26-1008", normalized_value="26-1008", confidence=0.97),
                    item_number=FieldData(raw_value="AL6061각재", normalized_value="AL6061각재", confidence=0.98),
                    item_name=FieldData(raw_value="알루미늄", normalized_value="알루미늄", confidence=0.99),
                    specification=FieldData(raw_value="20x30", normalized_value="20x30", confidence=0.99),
                    quantity=FieldData(raw_value="100", normalized_value="100", confidence=0.99),
                    unit_quantity=FieldData(raw_value="1", normalized_value="1", confidence=0.98),
                    unit_price=FieldData(raw_value="5000", normalized_value="5000", confidence=0.99),
                    supply_amount=FieldData(raw_value="500000", normalized_value="500000", confidence=0.99)
                )
            ]
        )
