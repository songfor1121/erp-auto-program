from app.services.company_identifier import CompanyIdentifier
from app.services.field_mapper import FieldMapper
from app.services.rule_engine import RuleEngine
from app.services.validator import Validator
from app.services.erp_adapter import ERPAdapter
from app.models import ExtractedItem

class Pipeline:
    @staticmethod
    def process_document(db, document_id: int, raw_text: str) -> None:
        # Step 1: Identify Company
        identity = CompanyIdentifier.identify(db, raw_text)
        company_id = identity.get("company_id")

        if not company_id:
            company_id = 1 # Fallback for mock test

        # Step 2: Map Fields (Standard Field Mapping)
        mapped_data = FieldMapper.map_fields(db, company_id, {})

        # Separate headers and line items
        header_keys = ["order_type", "vendor", "expected_receipt_date", "discount_rate"]
        header = {k: mapped_data.get(k) for k in header_keys}
        items = mapped_data.get("items", [])

        structured_data = {
            "header": header,
            "items": items
        }

        # Step 3: Normalize / Rule Engine
        normalized_data = RuleEngine.apply_rules(db, company_id, structured_data)

        # Step 4: Validate
        validated_data = Validator.validate(normalized_data)

        # Step 5: ERP Field Mapping
        final_data = ERPAdapter.map_to_erp(db, company_id, validated_data)

        # Step 6: Persist structured elements directly into the database
        header_data = final_data.get("header", {})
        for field_name, field_dict in header_data.items():
            if field_dict:
                raw_val = field_dict.get("raw_value")
                norm_val = field_dict.get("normalized_value")
                if norm_val is None:
                    norm_val = raw_val

                item = ExtractedItem(
                    document_id=document_id,
                    field_name=field_name,
                    raw_value=raw_val,
                    normalized_value=norm_val,
                    confidence=field_dict.get("confidence"),
                    validation_status=field_dict.get("validation_status", "PENDING"),
                    validation_message=field_dict.get("validation_message", ""),
                    source=field_dict.get("source", "AI")
                )
                db.add(item)

        line_items = final_data.get("items", [])
        for item_data in line_items:
            # Create parent line_item
            parent_item = ExtractedItem(
                document_id=document_id,
                field_name="line_item",
                validation_status="PENDING",
                source="SYSTEM"
            )
            db.add(parent_item)
            db.flush() # Get parent ID

            for field_name, field_dict in item_data.items():
                if field_dict:
                    raw_val = field_dict.get("raw_value")
                    norm_val = field_dict.get("normalized_value")
                    if norm_val is None:
                        norm_val = raw_val

                    child_item = ExtractedItem(
                        document_id=document_id,
                        field_name=field_name,
                        parent_id=parent_item.id,
                        raw_value=raw_val,
                        normalized_value=norm_val,
                        confidence=field_dict.get("confidence"),
                        validation_status=field_dict.get("validation_status", "PENDING"),
                        validation_message=field_dict.get("validation_message", ""),
                        source=field_dict.get("source", "AI")
                    )
                    db.add(child_item)

        db.commit()
