from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from typing import List
from uuid import uuid4
from .product import Product
from .customer import Customer
from .base import Base


# P.S: The Database will be normalized upto Boyce Codd's Form.
# These Items/Carts Tables are made to normalize the Database and to support
# efficient Queries.
class CartItems(Base):
    __tablename__ = "cart_items"

    order_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True, nullable=False, comment="(F.Key) Unique identifier for the Order.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), primary_key=True, nullable=False, comment="(F.Key) Unique identifier for the Product.")
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product in the Cart.")
    discount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Product Discount Rate (0-1).")
    order: Mapped["Order"] = relationship(uselist=False, back_populates="items")
    product: Mapped["Product"] = relationship(uselist=False)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique identifier for the Order.")
    order_amount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Price of the Order.")
    discount_amount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Discounted Amount of the Order.")
    tax: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Tax Amount applied to the order.")
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="Pending", comment="Order status. Can be Pending, Received, Cancelled, For Refund, or Refunded.")
    date_placed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(
        timezone.utc), comment="Timestamp When the Order is Placed.")
    date_received: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), comment="Timestamp When the Order is Delivered to the Customer.")
    order_mode: Mapped[str] = mapped_column(
        String, nullable=False, comment="Order mode, either Online or Offline.")
    order_delivery_address: Mapped[str] = mapped_column(String(200), 
                                                nullable=True, comment="Delivery Address for the Order.")
    customer_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("customers.id"), nullable=False, comment="(F.Key) Unique identifier for the Customer.")

    items: Mapped[List["CartItems"]] = relationship(
        uselist=True, back_populates="order", cascade="all, delete-orphan", passive_deletes=True)
    customer: Mapped["Customer"] = relationship(uselist=False)


# Relationship: 1-to-Many
# Each Order will have Multiple Cart Items.
# Each Cart Items is Associated with a particular Order
# Each Order will be Made by a Single Customer
