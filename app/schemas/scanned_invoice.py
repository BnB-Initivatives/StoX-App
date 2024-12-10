# Pydantic models for request/response validation, keep separate from database models

from pydantic import BaseModel, Field, field_validator

from typing import Optional
from datetime import datetime

from app.schemas.employee import EmployeeReadRequest
from app.schemas.vendor import VendorReadRequest
from app.schemas.scanned_invoice_item import (
    ScannedInvoiceItemCreateRequest,
    ScannedInvoiceItemReadRequest,
)


class ScannedInvoiceCreateRequest(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=100)
    vendor_name: str = Field(
        ..., min_length=1, max_length=100
    )  # as from the scanned invoice, the name is extracted
    scanned_by: int = Field(..., gt=0)
    image_file_path: str = Field(None, min_length=1, max_length=255)
    scanned_invoice_items: list[ScannedInvoiceItemCreateRequest]

    @field_validator("scanned_invoice_items")
    def check_list_items_not_empty(cls, v):
        if len(v) < 1:
            raise ValueError(
                "scanned_invoice_items list must contain at least one item"
            )
        return v

    @field_validator("image_file_path")
    def check_image_file_path(cls, v):
        # TODO: consider to add more validation for the image file path
        return v


class ScannedInvoiceReadRequest(BaseModel):
    scan_id: int
    invoice_number: str
    vendor: VendorReadRequest
    employee: EmployeeReadRequest  # match the relationship in the model
    image_file_path: Optional[str] = None
    total_items: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    scanned_invoice_items: list[ScannedInvoiceItemReadRequest] = []

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models
