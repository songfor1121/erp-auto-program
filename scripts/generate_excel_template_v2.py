import pandas as pd

def generate_template_v2():
    # File path
    filepath = "company_rules_template_v2.xlsx"

    # Define sheets and data
    sheets = {
        "Instructions": pd.DataFrame({
            "시트명": ["Companies", "FieldRules", "NormalizationRules", "DiscountRules", "ERPMapping", "DocumentFieldLocations", "FieldAliases", "DocumentSamples"],
            "작성 안내": [
                "자동입력을 적용할 회사의 기본 정보를 등록합니다.",
                "해당 회사의 거래명세서에 특정 데이터(수주번호, 규격 등)가 존재하는지, ERP 입력 시 필수값인지 정의합니다.",
                "AI가 읽어낸 원본 값(234b)을 ERP에 입력할 형식(234(B))으로 자동 변환하는 규칙을 작성합니다.",
                "회사의 기본 할인율(DC율) 또는 품번별 특정 할인율을 지정합니다. (예: 전체 10%, 특정품번 5%)",
                "추출된 데이터(source_field)를 실제 ERP의 어떤 입력칸(erp_field)에 넣을지 매핑합니다.",
                "동일한 항목이라도 회사별로 명세서 상 위치(상단, 표 안, 손글씨 등)가 다를 수 있습니다. 이를 명시합니다.",
                "회사별로 부르는 명칭(수주번호, 발주번호, 비고 등)의 차이를 정의합니다.",
                "PDF나 이미지 형태의 회사별 샘플 파일 목록과 형식을 기재하여 관리합니다."
            ]
        }),
        "Companies": pd.DataFrame({
            "company_id": ["A001", "B001", "C001"],
            "company_name": ["A회사", "B회사", "C회사"],
            "business_number": ["123-45-67890", "987-65-43210", ""],
            "active": ["TRUE", "TRUE", "FALSE"]
        }),
        "FieldRules": pd.DataFrame({
            "company_id": ["A001", "A001", "B001", "B001"],
            "field_name": ["specification", "order_number", "specification", "order_number"],
            "document_exists": ["FALSE", "TRUE", "TRUE", "TRUE"],
            "erp_required": ["FALSE", "TRUE", "TRUE", "TRUE"],
            "required": ["FALSE", "TRUE", "TRUE", "TRUE"],
            "default_value": ["", "", "", ""]
        }),
        "NormalizationRules": pd.DataFrame({
            "company_id": ["A001", "B001"],
            "field_name": ["item_number", "item_number"],
            "source_value": ["234b", "234b"],
            "target_value": ["234(B)", "234-B"],
            "priority": ["100", "100"],
            "active": ["TRUE", "TRUE"]
        }),
        "DiscountRules": pd.DataFrame({
            "company_id": ["A001", "A001", "B001"],
            "item_number": ["ALL", "234b", "ALL"],
            "discount_rate": ["10", "15", "5"],
            "priority": ["50", "100", "10"],
            "source": ["COMPANY_DEFAULT", "ITEM_SPECIFIC", "COMPANY_DEFAULT"],
            "active": ["TRUE", "TRUE", "TRUE"]
        }),
        "ERPMapping": pd.DataFrame({
            "company_id": ["A001", "A001", "B001", "B001", "A001", "A001"],
            "source_field": ["order_number", "item_number", "order_number", "item_number", "discount_rate", "supply_amount"],
            "erp_field": ["수주번호", "품번", "발주번호", "자재번호", "DC율", "공급가액"],
            "enabled": ["TRUE", "TRUE", "TRUE", "TRUE", "TRUE", "TRUE"],
            "transform_rule": ["", "ITEM_NORMALIZE", "", "ITEM_NORMALIZE", "", ""]
        }),
        "DocumentFieldLocations": pd.DataFrame({
            "company_id": ["A001", "B001", "C001", "A001"],
            "field_name": ["order_number", "order_number", "order_number", "order_number"],
            "document_label": ["비고", "없음", "없음", "비고"],
            "location_area": ["비고란", "품목 아래", "품목 아래", "상단 우측"],
            "location_detail": ["비고 칸에 있는 번호", "품명 바로 아래에 수주번호가 표시됨", "품목명 아래에 사람이 손글씨로 작성", "상단 문서번호 영역"],
            "anchor_text": ["비고", "", "", "문서번호"],
            "table_name": ["", "품목표", "품목표", ""],
            "column_header": ["", "", "", ""],
            "handwritten": ["FALSE", "FALSE", "TRUE", "FALSE"],
            "printed": ["TRUE", "TRUE", "FALSE", "TRUE"],
            "priority": ["1", "1", "1", "2"],
            "notes": ["기본 수주번호", "", "손글씨 인식 필요", "상단에도 수주번호가 있을 경우"]
        }),
        "FieldAliases": pd.DataFrame({
            "company_id": ["A001", "B001", "C001"],
            "field_name": ["order_number", "order_number", "order_number"],
            "document_label": ["수주번호", "비고", "발주번호"],
            "alias": ["수주번호", "비고", "발주번호"],
            "example_value": ["SO-12345", "비고란 기재", "PO-9999"],
            "priority": ["1", "1", "1"],
            "notes": ["", "B회사는 수주번호를 비고라고 부름", ""]
        }),
        "DocumentSamples": pd.DataFrame({
            "company_id": ["A001", "A001", "B001", "B001"],
            "sample_name": ["sample_01.pdf", "sample_02.jpg", "sample_01.pdf", "sample_03.pdf"],
            "document_type": ["PDF", "IMAGE", "PDF", "PDF"],
            "pdf_type": ["TEXT_PDF", "N/A", "IMAGE_PDF", "MULTI_PAGE_PDF"],
            "description": ["표준 거래명세서 원본", "스마트폰 촬영본", "스캔본 PDF", "3장짜리 다중 페이지 명세서"],
            "active": ["TRUE", "TRUE", "TRUE", "TRUE"]
        }),
        "ERPFieldList": pd.DataFrame({
            "ERP_필드명": [
                "수주번호", "거래명세서 첨부", "ST", "발주일자", "거래처",
                "납품현장", "납품주소", "특이사항", "발주구분", "담당자",
                "입고예정일", "도면 바코드", "품번", "품명", "규격",
                "수량", "단위수량", "단가", "공급가액", "DC율",
                "네고금액", "발주금액", "발주금액(DC적용)", "부가세액",
                "등록일자", "수정일자", "등록자", "수정자",
                "일괄등록", "복사", "삭제", "엑셀", "출력", "닫기"
            ],
            "필드_타입": [
                "데이터", "데이터", "데이터", "데이터", "데이터",
                "데이터", "데이터", "데이터", "데이터", "데이터",
                "데이터", "데이터", "데이터", "데이터", "데이터",
                "데이터", "데이터", "데이터", "데이터", "데이터",
                "데이터", "데이터", "데이터", "데이터",
                "자동입력", "자동입력", "자동입력", "자동입력",
                "UI버튼", "UI버튼", "UI버튼", "UI버튼", "UI버튼", "UI버튼"
            ],
            "설명": [
                "", "", "", "", "",
                "", "", "", "", "",
                "", "", "", "", "",
                "", "", "", "", "",
                "", "", "", "",
                "ERP 시스템 자체 생성값", "ERP 시스템 자체 생성값", "ERP 시스템 자체 생성값", "ERP 시스템 자체 생성값",
                "실제 값이 아닌 버튼", "실제 값이 아닌 버튼", "실제 값이 아닌 버튼", "실제 값이 아닌 버튼", "실제 값이 아닌 버튼", "실제 값이 아닌 버튼"
            ]
        })
    }

    # Write to Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Template successfully generated at {filepath}")

if __name__ == "__main__":
    generate_template_v2()
