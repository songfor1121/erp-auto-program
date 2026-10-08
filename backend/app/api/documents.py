import os
import shutil
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.document import DocumentUploadResponse, DocumentExtractionResponse, UpdateFieldRequest
from app.services.ocr_service import OCRService
from app.services.pipeline import Pipeline
from app.database import get_db
from app.models import Document, ExtractedItem

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images and PDFs are allowed.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save document record first to get ID
    new_doc = Document(image_url=file.filename)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    doc_id = new_doc.id
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        db.delete(new_doc)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    # Phase 2 Pipeline runs and writes directly to DB
    raw_text = OCRService.process(file_path)
    Pipeline.process_document(db, doc_id, raw_text)

    return DocumentUploadResponse(document_id=doc_id, message="File uploaded and processed successfully.")

@router.get("/{document_id}", response_model=DocumentExtractionResponse)
def get_document_data(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Reconstruct nested dictionary response from flat DB table
    header_fields = {}
    items = []

    extracted_items = db.query(ExtractedItem).filter(ExtractedItem.document_id == document_id).all()

    # Separate parent line items
    line_item_parents = [i for i in extracted_items if i.field_name == "line_item" and i.parent_id is None]

    for item in extracted_items:
        if item.parent_id is None and item.field_name != "line_item":
            header_fields[item.field_name] = {
                "raw_value": item.raw_value,
                "normalized_value": item.normalized_value,
                "confidence": item.confidence,
                "validation_status": item.validation_status,
                "validation_message": item.validation_message,
                "source": item.source
            }

    for parent in line_item_parents:
        children = [i for i in extracted_items if i.parent_id == parent.id]
        item_dict = {}
        for child in children:
            item_dict[child.field_name] = {
                "raw_value": child.raw_value,
                "normalized_value": child.normalized_value,
                "confidence": child.confidence,
                "validation_status": child.validation_status,
                "validation_message": child.validation_message,
                "source": child.source
            }
        items.append(item_dict)

    return {
        "document_id": document_id,
        "header": header_fields,
        "items": items
    }

from app.services.validator import Validator

@router.put("/{document_id}/fields/{field_name}")
def update_document_field(document_id: int, field_name: str, update: UpdateFieldRequest, db: Session = Depends(get_db)):
    doc_item = db.query(ExtractedItem).filter(
        ExtractedItem.document_id == document_id,
        ExtractedItem.field_name == field_name,
        ExtractedItem.parent_id == None
    ).first()

    if not doc_item:
        raise HTTPException(status_code=404, detail="Field not found")

    doc_item.normalized_value = update.normalized_value
    doc_item.source = update.source

    # Re-validate the single field dictionary logic
    field_dict = {
        "normalized_value": doc_item.normalized_value,
        "confidence": doc_item.confidence,
        "validation_status": update.validation_status,
    }
    Validator._validate_field(field_dict, field_name)

    doc_item.validation_status = field_dict.get("validation_status")
    doc_item.validation_message = field_dict.get("validation_message")

    db.commit()
    return get_document_data(document_id, db)

@router.put("/{document_id}/items/{item_index}/{field_name}")
def update_item_field(document_id: int, item_index: int, field_name: str, update: UpdateFieldRequest, db: Session = Depends(get_db)):
    # We must find the nth parent line item, then find its child field
    parents = db.query(ExtractedItem).filter(
        ExtractedItem.document_id == document_id,
        ExtractedItem.field_name == "line_item",
        ExtractedItem.parent_id == None
    ).order_by(ExtractedItem.id).all()

    if item_index >= len(parents):
        raise HTTPException(status_code=404, detail="Item not found")

    parent_id = parents[item_index].id

    doc_item = db.query(ExtractedItem).filter(
        ExtractedItem.parent_id == parent_id,
        ExtractedItem.field_name == field_name
    ).first()

    if not doc_item:
        raise HTTPException(status_code=404, detail="Field not found")

    doc_item.normalized_value = update.normalized_value
    doc_item.source = update.source

    # Re-validate the single field dictionary logic
    field_dict = {
        "normalized_value": doc_item.normalized_value,
        "confidence": doc_item.confidence,
        "validation_status": update.validation_status,
    }
    Validator._validate_field(field_dict, field_name)

    doc_item.validation_status = field_dict.get("validation_status")
    doc_item.validation_message = field_dict.get("validation_message")

    db.commit()
    return get_document_data(document_id, db)
