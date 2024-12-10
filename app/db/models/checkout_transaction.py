from sqlalchemy import Column, DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class CheckoutTransaction(Base):
    __tablename__ = "checkout_transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    department_id = Column(
        Integer, ForeignKey("departments.department_id"), nullable=False
    )  # department of the employee at the time of transaction
    total_items = Column(
        Integer, nullable=False
    )  # Total number of items in the transaction

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="checkout_transactions")
    department = relationship("Department", back_populates="checkout_transactions")
    checkout_items = relationship("CheckoutItem", back_populates="transaction")

    def __repr__(self):
        return f"<Checkout Transaction(id={self.transaction_id}, Employee='{self.employee_id}', Department='{self.department_id}')>"
