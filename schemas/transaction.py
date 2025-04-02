from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from uuid import uuid4
from product import Product
from typing import List
from employee import Employee
from store import Store


Base = declarative_base()


# Table to store each transaction made, a transaction could be defined as
# a Restock Order, a Sale Made, a Refund Made, or Product Removal.
# Considered this table for backwards compatibility as well for Audit reasons.
# This table will not be containing transactions related to new product addition in the Inventory.
# For that, Product Information should be inserted in the Products Table, followed by the
# Restock Order for that Product.
# Also, the Transaction Join will be based on the Transaction Type and ID with the Associated Tables.
class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for Transactions.")
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Type of Transaction. Can be Restock, Sale, Refund or Product Removal.")
    operation_id: Mapped[UUID] = mapped_column(
        UUID, nullable=False, comment="(F.Key) Unique identifier for the Associated record.")
    handled_by: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("employees.id"), nullable=False, comment="(F.Key) Unique identifier for the Employee.")
    date: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), comment="Timestamp When the Transaction is Made.")
    store_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stores.id"), index=True, nullable=False, comment="(F.Key) Unique identifier for the Store.")

    processed_by: Mapped["Employee"] = relationship(uselist=False)
    store: Mapped["Store"] = relationship(
        uselist=False, back_populates="transactions")

# Relationship: 1-to-1
# Each Operation would be Handled by a Single Employee
# Each Operation has to be Performed from a Particular Store


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
    items: Mapped[List["RemovalItems"]] = relationship(
        uselist=True, back_populates="removal_order")


# Relationship: 1-to-1
# Each Removal Item is associated to a Single Product

# Relationship: 1-to-Many
# Each Removal Item has a Single Removal Operation ID
# Each Removal Operation can have Multiple Removal Items
