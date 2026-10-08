from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    business_number = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    field_rules = relationship("FieldRule", back_populates="company")
    normalization_rules = relationship("NormalizationRule", back_populates="company")
    discount_rules = relationship("DiscountRule", back_populates="company")
    erp_mappings = relationship("ERPMapping", back_populates="company")
    documents = relationship("Document", back_populates="company")
    document_field_locations = relationship("DocumentFieldLocation", back_populates="company")
    field_aliases = relationship("FieldAlias", back_populates="company")
    document_samples = relationship("DocumentSample", back_populates="company")

class FieldRule(Base):
    __tablename__ = "field_rules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    field_name = Column(String, nullable=False)
    document_exists = Column(Boolean, default=True)
    erp_required = Column(Boolean, default=False)
    required = Column(Boolean, default=False)
    default_value = Column(String, nullable=True)

    company = relationship("Company", back_populates="field_rules")

class NormalizationRule(Base):
    __tablename__ = "normalization_rules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    field_name = Column(String, nullable=False)
    source_value = Column(String, nullable=False)
    target_value = Column(String, nullable=False)
    priority = Column(Integer, default=100)
    active = Column(Boolean, default=True)

    company = relationship("Company", back_populates="normalization_rules")

class DiscountRule(Base):
    __tablename__ = "discount_rules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    item_number = Column(String, default="ALL")
    discount_rate = Column(Float, nullable=False)
    priority = Column(Integer, default=100)
    source = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    company = relationship("Company", back_populates="discount_rules")

class ERPFieldSchema(Base):
    __tablename__ = "erp_field_schemas"

    id = Column(Integer, primary_key=True, index=True)
    erp_field_id = Column(String, nullable=False, unique=True) # e.g. 'order_number', 'vendor'
    display_name = Column(String, nullable=False) # e.g. '수주번호', '거래처'
    data_type = Column(String, nullable=False)
    is_required = Column(Boolean, default=False)
    source_type = Column(String, nullable=False) # document_extraction, company_rule, calculation, erp_master, user_input, future_api
    is_active = Column(Boolean, default=True)

    mappings = relationship("ERPMapping", back_populates="erp_field")

class StandardField(Base):
    __tablename__ = "standard_fields"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String, nullable=False, unique=True) # e.g. 'order_number', 'item_number'

    mappings = relationship("ERPMapping", back_populates="standard_field")

class ERPMapping(Base):
    __tablename__ = "erp_mappings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    standard_field_id = Column(Integer, ForeignKey("standard_fields.id"))
    erp_field_id = Column(Integer, ForeignKey("erp_field_schemas.id"))
    enabled = Column(Boolean, default=True)
    transform_rule = Column(String, nullable=True)

    company = relationship("Company", back_populates="erp_mappings")
    standard_field = relationship("StandardField", back_populates="mappings")
    erp_field = relationship("ERPFieldSchema", back_populates="mappings")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    image_url = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="documents")
    extracted_items = relationship("ExtractedItem", back_populates="document")

class ExtractedItem(Base):
    __tablename__ = "extracted_items"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    field_name = Column(String, nullable=False) # e.g., 'company_name', 'transaction_date', 'item_number'
    parent_id = Column(Integer, ForeignKey("extracted_items.id"), nullable=True) # For line items
    raw_value = Column(String, nullable=True)
    normalized_value = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    validation_status = Column(String, default="PENDING")
    validation_message = Column(String, nullable=True)
    source = Column(String, nullable=True) # e.g., 'OCR', 'AI', 'USER'

    document = relationship("Document", back_populates="extracted_items")
    parent = relationship("ExtractedItem", remote_side=[id])

class DocumentFieldLocation(Base):
    __tablename__ = "document_field_locations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    field_name = Column(String, nullable=False)
    document_label = Column(String, nullable=True)
    location_area = Column(String, nullable=True)
    location_detail = Column(String, nullable=True)
    anchor_text = Column(String, nullable=True)
    table_name = Column(String, nullable=True)
    column_header = Column(String, nullable=True)
    handwritten = Column(Boolean, default=False)
    printed = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    notes = Column(String, nullable=True)

    company = relationship("Company", back_populates="document_field_locations")

class FieldAlias(Base):
    __tablename__ = "field_aliases"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    field_name = Column(String, nullable=False)
    document_label = Column(String, nullable=True)
    alias = Column(String, nullable=False)
    example_value = Column(String, nullable=True)
    priority = Column(Integer, default=1)
    notes = Column(String, nullable=True)

    company = relationship("Company", back_populates="field_aliases")

class DocumentSample(Base):
    __tablename__ = "document_samples"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    sample_name = Column(String, nullable=False)
    document_type = Column(String, nullable=False) # e.g., PDF, IMAGE
    pdf_type = Column(String, nullable=True) # e.g., TEXT_PDF, IMAGE_PDF, MULTI_PAGE_PDF
    description = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    company = relationship("Company", back_populates="document_samples")