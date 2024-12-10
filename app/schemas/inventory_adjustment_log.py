# Pydantic models for request/response validation, keep separate from database models

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.item import ItemReadRequest
from app.schemas.checkout_item import CheckoutItemReadRequest
from app.schemas.scanned_invoice_item import ScannedInvoiceItemReadRequest


class InventoryAdjustmentLogReadRequest(BaseModel):
    log_id: int
    item: ItemReadRequest
    old_quantity: int
    new_quantity: int
    quantity_changed: int
    adjustment_type: str
    adjusted_at: datetime
    scanned_invoice_item: Optional[ScannedInvoiceItemReadRequest] = None
    checkout_item: Optional[CheckoutItemReadRequest] = None

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models
