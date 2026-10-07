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

class ERPMapping(Base):
    __tablename__ = "erp_mappings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    source_field = Column(String, nullable=False)
    erp_field = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    transform_rule = Column(String, nullable=True)

    company = relationship("Company", back_populates="erp_mappings")

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
    raw_value = Column(String, nullable=True)
    normalized_value = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    validation_status = Column(String, default="PENDING")

    document = relationship("Document", back_populates="extracted_items")

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