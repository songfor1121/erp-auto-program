from datetime import datetime

class Validator:
    @staticmethod
    def _validate_field(field_data: dict, field_name: str):
        if not field_data:
            return

        value = field_data.get("normalized_value")
        confidence = field_data.get("confidence")

        # 1. Check Confidence
        if confidence is not None and confidence < 0.90:
            field_data["validation_status"] = "NEEDS_REVIEW"
            field_data["validation_message"] = "신뢰도 낮음"
            return

        # 2. Check Numeric Formats
        numeric_fields = ["quantity", "unit_quantity", "unit_price", "supply_amount", "discount_rate"]
        if field_name in numeric_fields and value:
            try:
                float(value)
            except ValueError:
                field_data["validation_status"] = "NEEDS_REVIEW"
                field_data["validation_message"] = "숫자 형식이 아님"
                return

        # 3. Check Date Formats
        date_fields = ["transaction_date", "expected_receipt_date"]
        if field_name in date_fields and value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                field_data["validation_status"] = "NEEDS_REVIEW"
                field_data["validation_message"] = "올바른 날짜 형식(YYYY-MM-DD)이 아님"
                return

        # If it passes validation and wasn't already marked NEEDS_REVIEW manually (e.g. by missing rule):
        if field_data.get("validation_status") != "NEEDS_REVIEW":
            field_data["validation_status"] = "CONFIRMED"
            field_data["validation_message"] = None

    @staticmethod
    def validate(extracted_data: dict):
        # Applies data integrity and format validation.
        # Note: We do NOT calculate or alter amounts here. ERP handles calculations.

        if "header" in extracted_data:
            for field_name, field_data in extracted_data["header"].items():
                Validator._validate_field(field_data, field_name)

        if "items" in extracted_data:
            for item in extracted_data["items"]:
                for field_name, field_data in item.items():
                    Validator._validate_field(field_data, field_name)

        return extracted_data
