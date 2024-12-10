from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class InventoryAdjustmentLog(Base):
    __tablename__ = "inventory_adjustment_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    old_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    quantity_changed = Column(Integer, nullable=False)
    adjustment_type = Column(
        String, nullable=False
    )  # e.g., 'checkout', 'received', 'manual'
    adjusted_at = Column(DateTime, default=func.now(), nullable=False)
    scanned_invoice_item_id = Column(
        Integer, ForeignKey("scanned_invoice_items.scanned_invoice_item_id")
    )
    checkout_item_id = Column(Integer, ForeignKey("checkout_items.checkout_item_id"))

    # Relationships
    item = relationship("Item", back_populates="inventory_adjustment_logs")
    checkout_item = relationship(
        "CheckoutItem", back_populates="inventory_adjustment_log"
    )
    scanned_invoice_item = relationship(
        "ScannedInvoiceItem", back_populates="inventory_adjustment_log"
    )
