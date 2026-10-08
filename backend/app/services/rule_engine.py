from sqlalchemy.orm import Session
from app.models import NormalizationRule, DiscountRule

class RuleEngine:
    @staticmethod
    def apply_rules(db: Session, company_id: int, extracted_data: dict):
        norm_rules = db.query(NormalizationRule).filter(
            NormalizationRule.company_id == company_id,
            NormalizationRule.active == True
        ).all()

        dc_rules = db.query(DiscountRule).filter(
            DiscountRule.company_id == company_id,
            DiscountRule.active == True
        ).order_by(DiscountRule.priority.desc()).all()

        norm_lookup = {f"{r.field_name}_{r.source_value}": r.target_value for r in norm_rules}

        # Default DC rule is often applied to the header now
        default_dc = next((r.discount_rate for r in dc_rules if r.item_number == "ALL"), None)
        item_dc_lookup = {r.item_number: r.discount_rate for r in dc_rules if r.item_number != "ALL"}

        # Check Header DC Rate Priority
        header = extracted_data.get("header", {})
        if "discount_rate" in header and header["discount_rate"]:
            has_doc_dc = header["discount_rate"].get("raw_value")
            if not has_doc_dc and default_dc is not None:
                header["discount_rate"]["normalized_value"] = str(default_dc)
                header["discount_rate"]["source"] = "company_rule"

        for item in extracted_data["items"]:
            # Item Normalization via DB lookup
            if "item_number" in item and item["item_number"] and item["item_number"]["raw_value"]:
                raw_item = item["item_number"]["raw_value"]
                key = f"item_number_{raw_item}"
                if key in norm_lookup:
                    item["item_number"]["normalized_value"] = norm_lookup[key]
                    item["item_number"]["source"] = "company_rule"
                else:
                    if raw_item.endswith("b"):
                        item["item_number"]["normalized_value"] = raw_item[:-1] + "(B)"
                        item["item_number"]["source"] = "company_rule"

            # Unit Normalization
            if "unit_quantity" in item and item["unit_quantity"] and item["unit_quantity"]["raw_value"]:
                raw_unit = item["unit_quantity"]["raw_value"]
                key = f"unit_quantity_{raw_unit}"
                if key in norm_lookup:
                    item["unit_quantity"]["normalized_value"] = norm_lookup[key]
                    item["unit_quantity"]["source"] = "company_rule"
                elif raw_unit in ["개", "PCS"]:
                    item["unit_quantity"]["normalized_value"] = "EA"
                    item["unit_quantity"]["source"] = "company_rule"

            # Item Level DC logic (if present)
            if "discount_rate" in item and item["discount_rate"]:
                has_doc_dc = item["discount_rate"].get("raw_value")
                if not has_doc_dc:
                    raw_item = item.get("item_number", {}).get("raw_value")
                    if raw_item and raw_item in item_dc_lookup:
                        item["discount_rate"]["normalized_value"] = str(item_dc_lookup[raw_item])
                        item["discount_rate"]["source"] = "company_rule"

        return extracted_data
