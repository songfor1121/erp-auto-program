from pydantic import BaseModel
from typing import List, Optional

class FieldData(BaseModel):
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: Optional[float] = None
    validation_status: str = "PENDING"
    validation_message: Optional[str] = None
    source: str = "AI"

class LineItem(BaseModel):
    order_number: Optional[FieldData] = None
    item_number: Optional[FieldData] = None
    item_name: Optional[FieldData] = None
    specification: Optional[FieldData] = None
    quantity: Optional[FieldData] = None
    unit_quantity: Optional[FieldData] = None
    unit_price: Optional[FieldData] = None
    supply_amount: Optional[FieldData] = None

class HeaderFields(BaseModel):
    order_type: Optional[FieldData] = None
    vendor: Optional[FieldData] = None
    expected_receipt_date: Optional[FieldData] = None
    discount_rate: Optional[FieldData] = None
    transaction_date: Optional[FieldData] = None

class DocumentExtractionResponse(BaseModel):
    document_id: int
    header: HeaderFields
    items: List[LineItem]

class DocumentUploadResponse(BaseModel):
    document_id: int
    message: str

class UpdateFieldRequest(BaseModel):
    normalized_value: str
    validation_status: str = "CONFIRMED"
    source: str = "USER"
