from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Column, String, Float, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from uuid import uuid4

Base = declarative_base()


class CartItems(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = Column(Integer, nullable=False,
                             unique=True, autoincrement=True)
    order_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("orders.id"), nullable=False, comment="(F.Key) Unique identifier for the Order.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), nullable=False, comment="(F.Key) Unique identifier for the Product.")
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product in the Cart.")
    discount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Product Discount Rate (0-1).")


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
        String, nullable=False, default="Pending", comment="Order status. Can be Pending, Received, Cancelled, or Refunded.")
    date_placed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(
        timezone.utc), comment="Timestamp When the Order is Placed.")
    date_received: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), comment="Timestamp When the Order is Delivered to the Customer.")
    order_mode: Mapped[str] = mapped_column(
        String, nullable=False, comment="Order mode, either Online or Offline.")
    proccessed_by: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("employees.id"), nullable=True, comment="(F.Key) Unique identifier for the Employee. Depends on the Mode of Order.")
