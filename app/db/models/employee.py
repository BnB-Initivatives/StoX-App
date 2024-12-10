from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_number = Column(
        String(8), unique=True, nullable=False
    )  # 8 digit employee number of the company in their HR system
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    department_id = Column(
        Integer, ForeignKey("departments.department_id"), nullable=False
    )

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees")
    checkout_transactions = relationship(
        "CheckoutTransaction", back_populates="employee"
    )
    scanned_invoices = relationship("ScannedInvoice", back_populates="employee")

    def __repr__(self):
        return f"<Employee(id={self.employee_id}, first_name={self.first_name}, last_name={self.last_name}, employee_num={self.employee_number}, department={self.department_id}>"
