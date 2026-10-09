export interface FieldData {
  raw_value: string | null;
  normalized_value: string | null;
  confidence: number | null;
  validation_status: string;
  validation_message: string | null;
  source: string;
}

export interface LineItem {
  order_number?: FieldData;
  item_number?: FieldData;
  item_name?: FieldData;
  specification?: FieldData;
  quantity?: FieldData;
  unit_quantity?: FieldData;
  unit_price?: FieldData;
  supply_amount?: FieldData;
  discount_rate?: FieldData;
}

export interface HeaderData {
  order_type?: FieldData;
  vendor?: FieldData;
  expected_receipt_date?: FieldData;
  discount_rate?: FieldData;
  order_number?: FieldData;
  transaction_date?: FieldData;
  company_name?: FieldData;
}

export interface DocumentData {
  document_id: number;
  header: HeaderData;
  items: LineItem[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "문서 업로드에 실패했습니다.");
  }
  return res.json();
};

export const getDocument = async (id: string): Promise<DocumentData> => {
  const res = await fetch(`${API_BASE}/documents/${id}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "문서 정보를 불러오는 데 실패했습니다.");
  }
  return res.json();
};

export const updateField = async (
  docId: number,
  fieldName: string,
  normalizedValue: string,
  itemIndex?: number
) => {
  const url =
    itemIndex !== undefined
      ? `${API_BASE}/documents/${docId}/items/${itemIndex}/${fieldName}`
      : `${API_BASE}/documents/${docId}/fields/${fieldName}`;

  const res = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      normalized_value: normalizedValue,
      validation_status: "CONFIRMED",
      source: "USER",
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "필드 업데이트에 실패했습니다.");
  }
  return res.json();
};
