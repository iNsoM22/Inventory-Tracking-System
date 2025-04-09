from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from uuid import uuid4
from typing import List
from .product import Product
from .base import Base


class RestockItems(Base):
    __tablename__ = "restock_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate Identifier for Restock Items."
    )
    previous_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity of the Product before Restock."
    )
    restock_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity of the Product for Restock."
    )

    ###############
    # Foreign Keys
    ###############

    restock_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("restocks.id", ondelete="CASCADE"),
        primary_key=True,
        comment="(F.Key) Unique identifier for the Restock."
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("products.id"),
        primary_key=True,
        comment="(F.Key) Unique identifier for the Product."
    )

    ################
    # Relationships
    ################

    restock: Mapped["Restock"] = relationship(
        uselist=False,
        back_populates="items"
    )
    product: Mapped["Product"] = relationship(uselist=False)


class Restock(Base):
    __tablename__ = "restocks"

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Unique identifier for Restock Orders."
    )
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="Pending",
        comment="Restock Status. Can be Pending, Completed or Cancelled."
    )
    date_placed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Timestamp When the Restock Order is Placed."
    )
    date_received: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp When the Restock Order is Delivered."
    )

    ###############
    # Foreign Keys
    ###############

    store_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="(F.Key) Unique identifier for the Store."
    )

    ################
    # Relationships
    ################

    items: Mapped[List["RestockItems"]] = relationship(
        uselist=True,
        back_populates="restock",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


# Relationship: 1-to-Many
# Each Restock Order can have Multiple Items
# Each Item can only have a Single Restock Order Associated
# Each Restock Order can be made by a Store Only.
