from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, UUID
from typing import List
from .employee import Employee
from .inventory import Inventory
from .transaction import Transaction
from .base import Base
from .restock import Restock
from .removal import StockRemoval
from .order import Order
from .refund import Refund
from uuid import uuid4


class Location(Base):
    __tablename__ = 'locations'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="Primary Key for the Location.")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Name of the Location.")
    address: Mapped[str] = mapped_column(
        String, nullable=False, comment="Address of the Location.")
    stores: Mapped[List["Store"]] = relationship(
        uselist=True, back_populates="location", passive_deletes=True)


class Store(Base):
    __tablename__ = 'stores'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, comment="Primary Key for the Store.")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Name of the Store.")
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, comment="(F.K) Unique identifier for the Location.")

    location: Mapped["Location"] = relationship(
        uselist=False, back_populates="stores", passive_deletes=True)
    employees: Mapped[List["Employee"]] = relationship(
        uselist=True, back_populates="store", passive_deletes=True)
    inventory: Mapped[List["Inventory"]] = relationship(
        uselist=True, passive_deletes=True)
    transactions: Mapped[List["Transaction"]] = relationship(
        uselist=True, passive_deletes=True)
    restocks: Mapped[List["Restock"]] = relationship(uselist=True, passive_deletes=True)
    removals: Mapped[List["StockRemoval"]] = relationship(uselist=True, passive_deletes=True)
    orders: Mapped[List["Order"]] = relationship(uselist=True, passive_deletes=True)
    refunds: Mapped[List["Refund"]] = relationship(uselist=True, passive_deletes=True)


# Relationship: 1-to-Many
# Each Store will have Multiple Items in Inventory
# Each Store will have Multiple Employees
