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

const API_BASE = "http://localhost:8000/api/v1";

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Upload failed");
  return res.json();
};

export const getDocument = async (id: string): Promise<DocumentData> => {
  const res = await fetch(`${API_BASE}/documents/${id}`);
  if (!res.ok) throw new Error("Failed to fetch document");
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

  if (!res.ok) throw new Error("Failed to update field");
  return res.json();
};
