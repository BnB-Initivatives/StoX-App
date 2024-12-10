from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class ScannedInvoiceItem(Base):
    __tablename__ = "scanned_invoice_items"

    scanned_invoice_item_id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scanned_invoices.scan_id"), nullable=False)
    line_number = Column(
        Integer, nullable=False
    )  # Line number of the item in the scan, unique within the scope of each scan
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    item_code = Column(String(20), nullable=False)
    quantity = Column(
        Integer, nullable=False
    )  # Quantity is whole number, no need for decimal, the partiality should be expressed in the unit of measure
    # TODO: IMPORTANT!!! need to check business again, how to break down the received quantity into the quantity and uom when checking out.

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    scanned_invoice = relationship(
        "ScannedInvoice", back_populates="scanned_invoice_items"
    )
    item = relationship("Item", back_populates="scanned_invoice_items")

    inventory_adjustment_log = relationship(
        "InventoryAdjustmentLog", back_populates="scanned_invoice_item"
    )  # One-to-one relationship with InventoryAdjustmentLog

    # Unique constraint to ensure that the line number is unique within the scope of each scan
    __table_args__ = (UniqueConstraint("scan_id", "line_number", name="uq_scan_line"),)
