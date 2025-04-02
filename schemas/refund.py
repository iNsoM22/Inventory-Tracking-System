from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Column, String, Float, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from uuid import uuid4


Base = declarative_base()


class RefundItems(Base):
    __tablename__ = "cart_items"
    id: Mapped[int] = Column(Integer, nullable=False,
                             unique=True, autoincrement=True, comment="Unique Surrogate ID.")
    refund_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("refunds.id"), nullable=False, comment="(F.Key) Unique identifier for the Order.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), nullable=False, comment="(F.Key) Unique identifier for the Product.")
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product to be Refunded.")


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique identifier for Refund Applications.")
    reason: Mapped[str] = mapped_column(
        String, nullable=False, comment="Reason for Refund.")
    amount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Amount to be refunded.")
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="Pending", comment="Application Status. Can be Pending, Approved, Rejected, or Refunded.")
    application_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(
        timezone.utc), comment="Timestamp When the Application for Refund is Submitted")
    date_refunded: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), nullable=True, comment="Timestamp When the Refund is Successful.")
    order_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("orders.id"), nullable=False, comment="(F.Key) Unique identifier for the Order.")
    proccessed_by: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("employees.id"), nullable=True, comment="(F.Key) Unique identifier for the Employee.")
