import pandas as pd

def generate_template():
    # File path
    filepath = "company_rules_template.xlsx"

    # Define sheets and data
    sheets = {
        "Companies": pd.DataFrame({
            "company_id": ["A001", "B001", "C001", "Explanation: 회사 고유 ID"],
            "company_name": ["ABC Semiconductor", "XYZ Tech", "QWE Electronics", "Explanation: 회사명"],
            "business_number": ["123-45-67890", "987-65-43210", "", "Explanation: 사업자등록번호 (선택)"],
            "active": ["TRUE", "TRUE", "FALSE", "Explanation: 활성화 여부 (TRUE/FALSE)"]
        }),
        "FieldRules": pd.DataFrame({
            "company_id": ["A001", "A001", "B001", "Explanation: 회사 고유 ID"],
            "field_name": ["specification", "discount_rate", "specification", "Explanation: 필드명 (company_name, transaction_date, order_number, item_number, specification, quantity, unit_quantity, unit_price, supply_amount, discount_rate 등)"],
            "document_exists": ["TRUE", "TRUE", "FALSE", "Explanation: 해당 회사의 거래명세서에 이 필드가 존재하는지 (TRUE/FALSE)"],
            "erp_required": ["TRUE", "TRUE", "FALSE", "Explanation: ERP에 필수적으로 입력되어야 하는지 (TRUE/FALSE)"],
            "required": ["TRUE", "TRUE", "FALSE", "Explanation: 데이터 추출 시 필수 필드인지 (TRUE/FALSE)"],
            "default_value": ["", "10", "", "Explanation: 기본값 (필요 시)"]
        }),
        "NormalizationRules": pd.DataFrame({
            "company_id": ["A001", "A001", "B001", "Explanation: 회사 고유 ID"],
            "field_name": ["item_number", "item_number", "item_number", "Explanation: 정규화할 필드명"],
            "source_value": ["234b", "235b", "234b", "Explanation: 거래명세서 원본 값"],
            "target_value": ["234(B)", "235(B)", "234-B", "Explanation: ERP에 입력할 정규화된 값"],
            "priority": ["100", "100", "100", "Explanation: 우선순위 (숫자가 높을수록 우선)"],
            "active": ["TRUE", "TRUE", "TRUE", "Explanation: 활성화 여부 (TRUE/FALSE)"]
        }),
        "DiscountRules": pd.DataFrame({
            "company_id": ["A001", "B001", "C001", "Explanation: 회사 고유 ID"],
            "item_number": ["ALL", "234b", "ALL", "Explanation: 특정 품번 (전체는 ALL)"],
            "discount_rate": ["10", "5", "0", "Explanation: 할인율 (%)"],
            "priority": ["50", "100", "10", "Explanation: 우선순위"],
            "source": ["COMPANY_DEFAULT", "ITEM_SPECIFIC", "COMPANY_DEFAULT", "Explanation: 룰의 출처 구분 (설명용)"],
            "active": ["TRUE", "TRUE", "TRUE", "Explanation: 활성화 여부 (TRUE/FALSE)"]
        }),
        "ERPMapping": pd.DataFrame({
            "company_id": ["A001", "A001", "B001", "Explanation: 회사 고유 ID"],
            "source_field": ["order_number", "item_number", "specification", "Explanation: 원본 필드명"],
            "erp_field": ["수주번호", "품목코드", "규격", "Explanation: ERP 필드명"],
            "enabled": ["TRUE", "TRUE", "FALSE", "Explanation: 매핑 활성화 여부 (TRUE/FALSE)"],
            "transform_rule": ["", "ITEM_NORMALIZE", "", "Explanation: 적용할 변환 룰 (예: ITEM_NORMALIZE)"]
        })
    }

    # Write to Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Template successfully generated at {filepath}")

if __name__ == "__main__":
    generate_template()
