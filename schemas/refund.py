from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from typing import List
from uuid import uuid4
from .product import Product
from .order import Order
from .base import Base


class RefundItems(Base):
    __tablename__ = "refund_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate identifier for Refund Applications."
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity of the Product to be Refunded."
    )

    ###############
    # Foreign Keys
    ###############

    refund_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("refunds.id", ondelete="CASCADE"),
        primary_key=True,
        comment="(F.Key) Unique identifier for the Refund."
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

    product: Mapped["Product"] = relationship(
        uselist=False
    )
    refund: Mapped["Refund"] = relationship(
        uselist=False,
        back_populates="items"
    )


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Unique identifier for Refund Applications."
    )
    reason: Mapped[str] = mapped_column(
        String(400),
        nullable=False,
        comment="Reason for Refund."
    )
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Amount to be Refunded."
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="Pending",
        comment="Application Status. Can be Pending, Approved, Rejected, Cancelled or Refunded."
    )
    application_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Timestamp When the Application for Refund is Submitted."
    )
    date_refunded: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp When the Refund is Successful."
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
    order_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="(F.Key) Unique identifier for the Order."
    )

    ################
    # Relationships
    ################

    order: Mapped["Order"] = relationship(
        uselist=False,
        passive_deletes=True
    )
    items: Mapped[List["RefundItems"]] = relationship(
        uselist=True,
        back_populates="refund",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


# Relationship: 1-to-Many
# Each Refund Order can have Multiple Items
# Each Refund Order is associated with a Single Order
# Each Refund Item can have a Single Refund Order
# Each Refund Item is a Product
