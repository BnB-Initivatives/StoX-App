# Pydantic models for request/response validation, keep separate from database models

from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.department import DepartmentReadRequest


class EmployeeCreateRequest(BaseModel):
    employee_number: str = Field(..., min_length=8, max_length=8)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    department_id: int = Field(..., gt=0)


class EmployeeReadRequest(BaseModel):
    employee_id: int
    employee_number: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    department: DepartmentReadRequest  # Nested DepartmentReadRequest model to include department details and department key must match the relationship key in the Employee model

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models


class EmployeeUpdateRequest(BaseModel):
    employee_number: Optional[str] = Field(None, min_length=1, max_length=8)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    department_id: Optional[int] = Field(None, gt=0)
