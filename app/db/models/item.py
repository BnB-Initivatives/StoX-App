from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_code = Column(String(20), index=True, nullable=False)
    name = Column(String(100), index=True, nullable=False)
    description = Column(String(255), index=True)
    category = Column(
        Integer, ForeignKey("item_categories.category_id"), nullable=False
    )

    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    owner_department = Column(
        Integer, ForeignKey("departments.department_id"), nullable=False
    )

    has_barcode = Column(Boolean, default=False)
    barcode = Column(String(13))

    image_path = Column(String(255))

    # Unit of measure for the item (e.g., pieces, kilograms, liters)
    unit_of_measure = Column(
        Integer, ForeignKey("unit_of_measures.uom_id"), nullable=False
    )

    quantity = Column(Integer, default=0, nullable=False)

    # Threshold to trigger low stock alerts
    low_stock_threshold = Column(Integer, default=0)

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    item_category = relationship(
        "ItemCategory",
        back_populates="items",
        foreign_keys=[category],
        primaryjoin="Item.category == ItemCategory.category_id",
    )  # another way to define the relationship with primaryjoin when the foreign key is not the same as the column name
    vendor = relationship("Vendor", back_populates="items")
    department = relationship("Department", back_populates="items")
    uom = relationship("UnitOfMeasure", back_populates="items")
    checkout_items = relationship("CheckoutItem", back_populates="item")
    inventory_adjustment_logs = relationship(
        "InventoryAdjustmentLog", back_populates="item"
    )
    scanned_invoice_items = relationship("ScannedInvoiceItem", back_populates="item")
