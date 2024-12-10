from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="department")
    items = relationship("Item", back_populates="department")
    checkout_transactions = relationship(
        "CheckoutTransaction", back_populates="department"
    )

    def __repr__(self):
        return f"<Department(id={self.department_id}, name='{self.name}', description='{self.description}')>"
