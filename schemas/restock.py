from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from uuid import uuid4
from typing import List
from .product import Product
from .base import Base


class RestockItems(Base):
    __tablename__ = "restock_items"

    restock_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("restocks.id"), primary_key=True, nullable=False, comment="(F.Key) Unique identifier for the Restock.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), primary_key=True, nullable=False, comment="(F.Key) Unique identifier for the Product.")
    previous_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product before Restock.")
    restock_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product for Restock.")

    product: Mapped["Product"] = relationship(uselist=False)
    restock: Mapped["Restock"] = relationship(
        uselist=False, back_populates="items")


class Restock(Base):
    __tablename__ = "restocks"

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique identifier for Restock Orders.")
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="Pending", comment="Restock Status. Can be Pending, Completed or Cancelled.")
    date_placed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(
        timezone.utc), comment="Timestamp When the Restock Order is Placed.")
    date_received: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), comment="Timestamp When the Restock Order is Delivered.")
    items: Mapped[List["RestockItems"]] = relationship(
        uselist=True, back_populates="restock")


# Relationship: 1-to-Many
# Each Restock Order can have Multiple Items
# Each Item can only have a Single Restock Order Associated
