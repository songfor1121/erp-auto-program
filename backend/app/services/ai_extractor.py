import os
import json
import logging
from app.schemas.document import DocumentExtractionResponse, HeaderFields, FieldData, LineItem

logger = logging.getLogger(__name__)

class AIExtractor:
    @staticmethod
    def extract(document_id: int, file_path_or_text: str) -> DocumentExtractionResponse:
        use_mock = os.getenv("USE_MOCK_OCR", "True").lower() in ("true", "1", "yes")

        if use_mock:
            return AIExtractor._mock_extract(document_id)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # We explicitly raise an error here if running in production mode without a key,
            # to avoid masking failures as mock successes.
            raise ValueError("GEMINI_API_KEY environment variable is missing in production mode.")

        try:
            import google.generativeai as genai
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

            genai.configure(api_key=api_key)

            # Using Gemini 1.5 Flash for fast multimodal extraction
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Upload file via File API
            uploaded_file = genai.upload_file(file_path_or_text)

            prompt = """
            다음 거래명세서 이미지 또는 PDF의 내용을 분석하여 정확히 구조화된 JSON으로 반환하시오.

            [추출 규칙]
            1. 수학적 계산을 임의로 하지 말고 문서에 보이는 글자 그대로 추출하시오.
            2. 단가, 수량, 공급가액, DC율 등은 숫자가 아닌 기호(예: %, 원, ,)를 제외한 숫자만 남기시오.
            3. 수주번호와 품번은 영문, 숫자, 하이픈, 괄호 등 기호를 텍스트와 분리하지 말고 원문 그대로 추출하시오.
            4. 각 필드별로 명확하게 보이고 확실하면 confidence를 0.99로, 흐리거나 불확실하면 0.5로 설정하시오.
            5. 값이 아예 없으면 raw_value를 빈 문자열 "" 로 하고 confidence를 0.0으로 하시오.

            [반환 JSON 스키마]
            반드시 아래 구조를 따르시오:
            {
              "header": {
                "order_type": {"raw_value": "...", "confidence": 0.99},
                "vendor": {"raw_value": "...", "confidence": 0.99},
                "expected_receipt_date": {"raw_value": "...", "confidence": 0.99},
                "discount_rate": {"raw_value": "...", "confidence": 0.99},
                "transaction_date": {"raw_value": "...", "confidence": 0.99}
              },
              "items": [
                {
                  "order_number": {"raw_value": "...", "confidence": 0.99},
                  "item_number": {"raw_value": "...", "confidence": 0.99},
                  "item_name": {"raw_value": "...", "confidence": 0.99},
                  "specification": {"raw_value": "...", "confidence": 0.99},
                  "quantity": {"raw_value": "...", "confidence": 0.99},
                  "unit_quantity": {"raw_value": "...", "confidence": 0.99},
                  "unit_price": {"raw_value": "...", "confidence": 0.99},
                  "supply_amount": {"raw_value": "...", "confidence": 0.99},
                  "discount_rate": {"raw_value": "...", "confidence": 0.99}
                }
              ]
            }
            """

            # Using response_mime_type to force JSON output (Supported in gemini-1.5)
            response = model.generate_content(
                [uploaded_file, prompt],
                generation_config={"response_mime_type": "application/json"},
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            # Clean up the file from Gemini storage
            uploaded_file.delete()

            json_text = response.text
            parsed_data = json.loads(json_text)

            return AIExtractor._parse_ai_dict(document_id, parsed_data)

        except Exception as e:
            logger.error(f"Gemini API Extraction failed: {str(e)}")
            raise RuntimeError(f"OCR 처리 중 오류가 발생했습니다: {str(e)}")

    @staticmethod
    def _parse_ai_dict(document_id: int, data: dict) -> DocumentExtractionResponse:
        # Helper to convert the raw JSON dict from Gemini into our Pydantic schema safely

        def safe_field(field_dict, default_status="PENDING"):
            if not field_dict:
                return FieldData(raw_value="", normalized_value="", confidence=0.0, validation_status="NEEDS_REVIEW")

            raw = str(field_dict.get("raw_value", ""))
            conf = float(field_dict.get("confidence", 0.0))

            status = default_status
            if conf < 0.90 or raw == "":
                status = "NEEDS_REVIEW"

            return FieldData(
                raw_value=raw,
                normalized_value=raw, # Initial normalization is just raw. Rule engine modifies this later.
                confidence=conf,
                validation_status=status
            )

        header_data = data.get("header", {})

        header = HeaderFields(
            order_type=safe_field(header_data.get("order_type")),
            vendor=safe_field(header_data.get("vendor")),
            expected_receipt_date=safe_field(header_data.get("expected_receipt_date")),
            discount_rate=safe_field(header_data.get("discount_rate")),
            transaction_date=safe_field(header_data.get("transaction_date"))
        )

        items = []
        for item in data.get("items", []):
            line_item = LineItem(
                order_number=safe_field(item.get("order_number")),
                item_number=safe_field(item.get("item_number")),
                item_name=safe_field(item.get("item_name")),
                specification=safe_field(item.get("specification")),
                quantity=safe_field(item.get("quantity")),
                unit_quantity=safe_field(item.get("unit_quantity")),
                unit_price=safe_field(item.get("unit_price")),
                supply_amount=safe_field(item.get("supply_amount")),
                discount_rate=safe_field(item.get("discount_rate"))
            )
            items.append(line_item)

        return DocumentExtractionResponse(
            document_id=document_id,
            header=header,
            items=items
        )

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
