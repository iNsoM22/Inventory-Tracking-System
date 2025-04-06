from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey, Integer, Boolean
from datetime import datetime, timezone
from uuid import uuid4
from typing import List
from .product import Product
from .base import Base


class RemovalItems(Base):
    __tablename__ = "removal_items"

    removal_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stock_removals.id", ondelete="CASCADE"), primary_key=True, nullable=False, comment="(F.Key) Unique identifier for the Stocks Removal.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), primary_key=True, nullable=False, comment="(F.Key) Unique identifier for the Product.")
    previous_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product before Removal.")
    removal_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product for Removal.")
    product: Mapped["Product"] = relationship(uselist=False)
    removal_order: Mapped["StockRemoval"] = relationship(
        uselist=False, back_populates="items")


# Table for storing the Product Items that have been removed from the Inventory.
# This removal could be of complete inventory or of some specific quantity.
class StockRemoval(Base):
    __tablename__ = 'stock_removals'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for Stock Removal.")
    removal_reason: Mapped[str] = mapped_column(
        String, nullable=False, comment="Removal Resaon. Can be Expired, Damaged, Lost, Internal Use, Return to Supplier, or Adjustment.")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(
        timezone.utc), comment="Timestamp When the Transaction is Made.")
    is_canceled: Mapped[bool] = mapped_column(Boolean, default=False, comment="Identifier to represent Cancellation of Removal Operation") 
    store_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False, index=True, comment="(F.Key) Unique identifier for the Store.")    
    
    items: Mapped[List["RemovalItems"]] = relationship(
        uselist=True, back_populates="removal_order", cascade="all, delete-orphan", passive_deletes=True)


# Relationship: 1-to-1
# Each Removal Item is associated to a Single Product
# Each Removal Order is Associated to a Specific Store

# Relationship: 1-to-Many
# Each Removal Item has a Single Removal Operation ID
# Each Removal Operation can have Multiple Removal Items
