from sqlalchemy.orm import Session
import re
from app.models import NormalizationRule, DiscountRule, Company, ProductDictionary

class RuleEngine:
    @staticmethod
    def apply_rules(db: Session, company_id: int, extracted_data: dict):
        company = db.query(Company).filter(Company.id == company_id).first()
        erp_vendor_name = company.erp_vendor_name if company else None
        order_year_prefix = company.order_year_prefix if company else None

        norm_rules = db.query(NormalizationRule).filter(
            NormalizationRule.company_id == company_id,
            NormalizationRule.active == True
        ).all()

        dc_rules = db.query(DiscountRule).filter(
            DiscountRule.company_id == company_id,
            DiscountRule.active == True
        ).order_by(DiscountRule.priority.desc()).all()

        product_dict = db.query(ProductDictionary).filter(
            ProductDictionary.company_id == company_id,
            ProductDictionary.active == True
        ).all()

        norm_lookup = {f"{r.field_name}_{r.source_value}": r.target_value for r in norm_rules}
        regex_norm_rules = [r for r in norm_rules if r.source_value.startswith("REGEX:")]

        pd_lookup = {}
        for pd in product_dict:
            if pd.is_confirmed:
                if pd.raw_item_string not in pd_lookup:
                    pd_lookup[pd.raw_item_string] = []
                # Don't add duplicates
                if pd.erp_item_number not in pd_lookup[pd.raw_item_string]:
                    pd_lookup[pd.raw_item_string].append(pd.erp_item_number)

        default_dc = next((r.discount_rate for r in dc_rules if r.item_number == "ALL"), None)
        item_dc_lookup = {r.item_number: r.discount_rate for r in dc_rules if r.item_number != "ALL"}

        header = extracted_data.get("header", {})

        if "vendor" in header and header["vendor"]:
            if erp_vendor_name:
                header["vendor"]["normalized_value"] = erp_vendor_name
                header["vendor"]["source"] = "company_rule"
            else:
                header["vendor"]["normalized_value"] = header["vendor"]["raw_value"]
                header["vendor"]["validation_status"] = "NEEDS_REVIEW"
                header["vendor"]["validation_message"] = "ERP 거래처명이 설정되지 않았습니다."
                header["vendor"]["confidence"] = 0.0

        if "discount_rate" in header and header["discount_rate"]:
            has_doc_dc = header["discount_rate"].get("raw_value")
            if not has_doc_dc and default_dc is not None:
                header["discount_rate"]["normalized_value"] = str(default_dc)
                header["discount_rate"]["source"] = "company_rule"

        for item in extracted_data["items"]:
            if "order_number" in item and item["order_number"] and item["order_number"].get("raw_value"):
                raw_order = item["order_number"]["raw_value"]
                if order_year_prefix:
                    if not raw_order.startswith(order_year_prefix):
                        if raw_order.replace("-", "").isdigit():
                            item["order_number"]["normalized_value"] = f"{order_year_prefix}{raw_order}"
                            item["order_number"]["source"] = "company_rule"
                        else:
                            item["order_number"]["normalized_value"] = raw_order
                            item["order_number"]["validation_status"] = "NEEDS_REVIEW"
                            item["order_number"]["validation_message"] = "수주번호 형식이 불분명합니다."
                            item["order_number"]["confidence"] = 0.0
                    else:
                        item["order_number"]["normalized_value"] = raw_order
                else:
                    item["order_number"]["normalized_value"] = raw_order

            if "item_number" in item and item["item_number"] and item["item_number"].get("raw_value"):
                raw_item = item["item_number"]["raw_value"]
                candidates = pd_lookup.get(raw_item, [])
                if len(candidates) == 1:
                    item["item_number"]["normalized_value"] = candidates[0]
                    item["item_number"]["source"] = "product_dictionary"
                elif len(candidates) > 1:
                    item["item_number"]["normalized_value"] = raw_item
                    item["item_number"]["validation_status"] = "NEEDS_REVIEW"
                    item["item_number"]["validation_message"] = "다수의 품번 후보가 존재합니다."
                    item["item_number"]["confidence"] = 0.0
                else:
                    item["item_number"]["normalized_value"] = raw_item
                    item["item_number"]["validation_status"] = "NEEDS_REVIEW"
                    item["item_number"]["validation_message"] = "품번 사전에 등록되지 않았습니다."
                    item["item_number"]["confidence"] = 0.0

            if "item_name" in item and item["item_name"]:
                pass

            if "specification" in item and item["specification"] and item["specification"].get("raw_value"):
                raw_spec = item["specification"]["raw_value"]
                matched = False
                for rule in regex_norm_rules:
                    if rule.field_name == "specification":
                        pattern = rule.source_value.replace("REGEX:", "")
                        if re.search(pattern, raw_spec):
                            try:
                                item["specification"]["normalized_value"] = re.sub(pattern, rule.target_value, raw_spec)
                                item["specification"]["source"] = "company_rule"
                                matched = True
                                break
                            except:
                                pass
                if not matched:
                    item["specification"]["normalized_value"] = raw_spec

            if "unit_quantity" in item and item["unit_quantity"] and item["unit_quantity"].get("raw_value"):
                raw_unit = item["unit_quantity"]["raw_value"]
                key = f"unit_quantity_{raw_unit}"
                if key in norm_lookup:
                    item["unit_quantity"]["normalized_value"] = norm_lookup[key]
                    item["unit_quantity"]["source"] = "company_rule"
                else:
                    item["unit_quantity"]["normalized_value"] = raw_unit

            for qty_field in ["quantity", "unit_price", "supply_amount"]:
                if qty_field in item and item[qty_field] and item[qty_field].get("raw_value"):
                     item[qty_field]["normalized_value"] = item[qty_field]["raw_value"]

            if "discount_rate" in item and item["discount_rate"]:
                has_doc_dc = item["discount_rate"].get("raw_value")
                if not has_doc_dc:
                    raw_item = item.get("item_number", {}).get("raw_value")
                    if raw_item and raw_item in item_dc_lookup:
                        item["discount_rate"]["normalized_value"] = str(item_dc_lookup[raw_item])
                        item["discount_rate"]["source"] = "company_rule"

        return extracted_data
