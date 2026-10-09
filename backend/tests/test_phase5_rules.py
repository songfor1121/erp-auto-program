import pytest
from app.models import Company, ProductDictionary, NormalizationRule
from app.services.rule_engine import RuleEngine

def test_vendor_name_strict_mapping(db_session):
    c = Company(company_name="ABC", erp_vendor_name="에이비씨(주)", active=True)
    db_session.add(c)
    db_session.commit()

    data = {"header": {"vendor": {"raw_value": "ABC", "confidence": 0.99}}, "items": []}
    result = RuleEngine.apply_rules(db_session, c.id, data)
    assert result["header"]["vendor"]["normalized_value"] == "에이비씨(주)"

    # Unmapped case
    c2 = Company(company_name="DEF", erp_vendor_name=None, active=True)
    db_session.add(c2)
    db_session.commit()

    data2 = {"header": {"vendor": {"raw_value": "DEF", "confidence": 0.99}}, "items": []}
    result2 = RuleEngine.apply_rules(db_session, c2.id, data2)
    assert result2["header"]["vendor"]["validation_status"] == "NEEDS_REVIEW"

def test_order_number_prefix(db_session):
    c = Company(company_name="OrderCo", order_year_prefix="26-", active=True)
    db_session.add(c)
    db_session.commit()

    data = {"header": {}, "items": [{"order_number": {"raw_value": "923", "confidence": 0.99}}]}
    result = RuleEngine.apply_rules(db_session, c.id, data)
    assert result["items"][0]["order_number"]["normalized_value"] == "26-923"

    # Already has prefix
    data2 = {"header": {}, "items": [{"order_number": {"raw_value": "26-1008", "confidence": 0.99}}]}
    result2 = RuleEngine.apply_rules(db_session, c.id, data2)
    assert result2["items"][0]["order_number"]["normalized_value"] == "26-1008"

def test_product_dictionary(db_session):
    c = Company(company_name="ProdCo", active=True)
    db_session.add(c)
    db_session.commit()

    pd = ProductDictionary(company_id=c.id, raw_item_string="알루텍", erp_item_number="도금", is_confirmed=True)
    db_session.add(pd)
    db_session.commit()

    # Exact match
    data = {"header": {}, "items": [{"item_number": {"raw_value": "알루텍", "confidence": 0.99}}]}
    result = RuleEngine.apply_rules(db_session, c.id, data)
    assert result["items"][0]["item_number"]["normalized_value"] == "도금"

    # No match
    data2 = {"header": {}, "items": [{"item_number": {"raw_value": "알수없음", "confidence": 0.99}}]}
    result2 = RuleEngine.apply_rules(db_session, c.id, data2)
    assert result2["items"][0]["item_number"]["validation_status"] == "NEEDS_REVIEW"

def test_regex_specification(db_session):
    c = Company(company_name="SpecCo", active=True)
    db_session.add(c)
    db_session.commit()

    nr = NormalizationRule(company_id=c.id, field_name="specification", source_value="REGEX:x", target_value="*", active=True)
    db_session.add(nr)
    db_session.commit()

    data = {"header": {}, "items": [{"specification": {"raw_value": "10x200x23", "confidence": 0.99}}]}
    result = RuleEngine.apply_rules(db_session, c.id, data)
    assert result["items"][0]["specification"]["normalized_value"] == "10*200*23"
