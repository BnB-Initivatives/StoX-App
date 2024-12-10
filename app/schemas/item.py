# Pydantic models for request/response validation, keep separate from database models

from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.vendor import VendorReadRequest
from app.schemas.department import DepartmentReadRequest
from app.schemas.unit_of_measure import UnitOfMeasureReadRequest
from app.schemas.item_category import ItemCategoryReadRequest


class ItemCreateRequest(BaseModel):
    item_code: str = Field(
        ..., min_length=1, max_length=20
    )  # external item code or product number e.g. value in the invoice
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    category: int = Field(..., gt=0)
    vendor_id: Optional[int] = Field(None, gt=0)
    owner_department: int = Field(..., gt=0)
    has_barcode: bool = False
    barcode: Optional[str] = Field(None, max_length=13)
    image_path: Optional[str] = Field(None, max_length=255)
    unit_of_measure: int = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=0, ge=0)


class ItemReadRequest(BaseModel):
    item_id: int
    item_code: str
    name: str
    description: Optional[str]
    item_category: ItemCategoryReadRequest
    vendor: Optional[VendorReadRequest]
    department: DepartmentReadRequest
    has_barcode: bool
    barcode: Optional[str]
    image_path: Optional[str]
    uom: UnitOfMeasureReadRequest  # must match the relationship name in the Item model
    quantity: int
    low_stock_threshold: int

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models


class ItemUpdateRequest(BaseModel):
    """
    Represents a request to update an existing item.
    All fields are optional and will only update the provided fields.
    This means that any field not provided in the update request will remain unchanged.
    """

    item_code: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    category: Optional[int] = Field(None, gt=0)
    vendor_id: Optional[int] = Field(None, gt=0)
    owner_department: Optional[int] = Field(None, gt=0)
    has_barcode: Optional[bool] = Field(None)
    barcode: Optional[str] = Field(None, max_length=13)
    image_path: Optional[str] = Field(None, max_length=255)
    unit_of_measure: Optional[int] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
