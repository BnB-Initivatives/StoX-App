# Pydantic models for request/response validation, keep separate from database models

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.item import ItemReadRequest
from app.schemas.item_category import ItemCategoryReadRequest
from app.schemas.unit_of_measure import UnitOfMeasureReadRequest


class CheckoutItemCreateRequest(BaseModel):
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    # category_id: int = Field(None, gt=0)
    # unit_of_measure: int = Field(None, gt=0)


class CheckoutItemReadRequest(BaseModel):
    checkout_item_id: int
    transaction_id: int
    line_number: int
    item_id: int
    quantity: int
    category: ItemCategoryReadRequest
    uom: UnitOfMeasureReadRequest
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models
