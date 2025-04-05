from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey
from datetime import datetime
from uuid import uuid4
from .employee import Employee
from .base import Base


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
    handler_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("employees.id"), nullable=False, comment="(F.Key) Unique identifier for the Employee.")
    date: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), comment="Timestamp When the Transaction is Made.")
    store_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stores.id"), index=True, nullable=False, comment="(F.Key) Unique identifier for the Store.")

    handler: Mapped["Employee"] = relationship(uselist=False)

# Relationship: 1-to-1
# Each Operation would be Handled by a Single Employee
# Each Operation has to be Performed from a Particular Store