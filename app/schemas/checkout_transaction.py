# Pydantic models for request/response validation, keep separate from database models

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from app.schemas.department import DepartmentReadRequest
from app.schemas.employee import EmployeeReadRequest
from app.schemas.checkout_item import CheckoutItemCreateRequest, CheckoutItemReadRequest


class CheckoutTransactionCreateRequest(BaseModel):
    employee_id: int = Field(..., gt=0)
    department_id: int = Field(..., gt=0)
    total_items: int = Field(None, gt=0)
    checkout_items: list[CheckoutItemCreateRequest]

    @field_validator("checkout_items")
    def check_list_items_not_empty(cls, v):
        if len(v) < 1:
            raise ValueError("checkout_items list must contain at least one item")
        return v


class CheckoutTransactionReadRequest(BaseModel):
    transaction_id: int
    employee: EmployeeReadRequest
    department: DepartmentReadRequest
    total_items: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    checkout_items: list[CheckoutItemReadRequest] = []

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models
