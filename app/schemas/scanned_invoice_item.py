# Pydantic models for request/response validation, keep separate from database models
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.item import ItemReadRequest


class ScannedInvoiceItemCreateRequest(BaseModel):
    item_code: str = Field(
        ..., min_length=1, max_length=20
    )  # item_code of the item matches the item code or product number in the invoice
    quantity: int = Field(..., gt=0)
    item_id: int = Field(None, gt=0)


class ScannedInvoiceItemReadRequest(BaseModel):
    scanned_invoice_item_id: int
    scan_id: int
    line_number: int
    item: ItemReadRequest
    item_code: str
    quantity: int

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models
