from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    UniqueConstraint,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class CheckoutItem(Base):
    __tablename__ = "checkout_items"

    checkout_item_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(
        Integer, ForeignKey("checkout_transactions.transaction_id"), nullable=False
    )
    line_number = Column(
        Integer, nullable=False
    )  # Line number of the item in the transaction, unique within the scope of each transaction
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    quantity = Column(
        Integer, nullable=False
    )  # Quantity is whole number, no need for decimal, the partiality should be expressed in the unit of measure
    category_id = Column(
        Integer, ForeignKey("item_categories.category_id"), nullable=False
    )  # Category of the item at the time of transaction
    unit_of_measure = Column(
        Integer, ForeignKey("unit_of_measures.uom_id"), nullable=False
    )  # Unit of measure of the item at the time of transaction

    # Created at timestamp
    created_at = Column(DateTime, server_default=func.now())

    # Updated at timestamp
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    transaction = relationship("CheckoutTransaction", back_populates="checkout_items")
    item = relationship("Item", back_populates="checkout_items")
    category = relationship("ItemCategory", back_populates="checkout_items")
    uom = relationship("UnitOfMeasure", back_populates="checkout_items")
    inventory_adjustment_log = relationship(
        "InventoryAdjustmentLog", back_populates="checkout_item"
    )  # One-to-one relationship with InventoryAdjustmentLog

    # Unique constraint to ensure that the line number is unique within the scope of each transaction
    __table_args__ = (
        UniqueConstraint("transaction_id", "line_number", name="uq_transaction_line"),
    )

    def __repr__(self):
        return f"<Checkout Item(id={self.checkout_item_id}, Item='{self.item_id}', Quantity='{self.quantity}', UoM='{self.uom}')>"
