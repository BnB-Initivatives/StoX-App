from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class ScannedInvoice(Base):
    __tablename__ = "scanned_invoices"

    scan_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(100), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    scanned_by = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)

    image_file_path = Column(String(255))  # Path to the scanned invoice file

    total_items = Column(
        Integer, nullable=False
    )  # Total number of items in the scanned invoice

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    vendor = relationship("Vendor", back_populates="scanned_invoices")
    employee = relationship("Employee", back_populates="scanned_invoices")
    scanned_invoice_items = relationship(
        "ScannedInvoiceItem", back_populates="scanned_invoice"
    )

    def __repr__(self):
        return f"<Scanned Invoice (id={self.scan_id}, scanned by='{self.scanned_by}', invoice number='{self.invoice_number}')>"
