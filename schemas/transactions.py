from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from uuid import uuid4

Base = declarative_base()


# Table to store each transaction made, a transaction could be defined as
# a Restock Order, a Sale Made, a Refund Made, or Product Removal.
# Considered this table for backwards compatibility as well for Audit reasons.
# This table will not be containing transactions related to new product addition in the Inventory.
# For that, Product Information should be inserted in the Products Table, followed by the
# Restock Order for that Product.
class Transation(Base):
    __tablename__ = 'transactions'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for Transactions.")
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Type of Transaction. Can be Restock, Sale, Refund or Product Removal.")
    order_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("orders.id"), nullable=True, comment="(F.Key) Unique identifier for the Orders.")
    refund_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("refunds.id"), nullable=True, comment="(F.Key) Unique identifier for the Refund.")
    restock_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("restocks.id"), nullable=True, comment="(F.Key) Unique identifier for the Stock-In.")
    removal_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stock_removals.id"), nullable=True, comment="(F.Key) Unique identifier for the Removed Items.")


class RemovalItems(Base):
    __tablename__ = "removal_items"

    id: Mapped[int] = mapped_column(Integer, nullable=False,
                                    unique=True, autoincrement=True, comment="Unique Surrogate ID.")
    removal_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stock_removals.id"), nullable=False, comment="(F.Key) Unique identifier for the Stocks Removal.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), nullable=False, comment="(F.Key) Unique identifier for the Product.")
    previous_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product before Removal.")
    removal_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Quantity of the Product for Removal.")


# Table for storing the Product Items that have been removed from the Inventory.
# This removal could be of complete inventory or of some specific quantity.
class StockRemoval(Base):
    __tablename__ = 'stock_removals'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for Stock Removal.")
    removal_reason: Mapped[str] = mapped_column(
        String, nullable=False, comment="Removal Resaon. Can be Expired, Damaged, Lost, Internal Use, Return to Supplier, or Adjustment.")
    removed_by: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("employees.id"), nullable=True, comment="(F.Key) Unique identifier for the Employee.")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(
        timezone.utc), comment="Timestamp When the Transaction is Made.")
