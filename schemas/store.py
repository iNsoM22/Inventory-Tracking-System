from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, UUID, ForeignKey
from typing import List
from uuid import uuid4
from .employee import Employee
from .inventory import Inventory
from .transaction import Transaction
from .base import Base


class Location(Base):
    __tablename__ = 'locations'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique identifier for the Location.")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Name of the Location.")
    address: Mapped[str] = mapped_column(
        String, nullable=False, comment="Address of the Location.")
    stores: Mapped[List["Store"]] = relationship(
        uselist=True, back_populates="location")


class Store(Base):
    __tablename__ = 'stores'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique identifier for the Store.")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Name of the Store.")
    location_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("locations.id"), nullable=False, comment="(F.K) Unique identifier for the Location.")

    location: Mapped["Location"] = relationship(
        uselist=False, back_populates="stores")
    employees: Mapped[List["Employee"]] = relationship(
        uselist=True, back_populates="store")
    inventory: Mapped[List["Inventory"]] = relationship(
        uselist=True)
    transactions: Mapped[List["Transaction"]] = relationship(
        uselist=True, back_populates="store")


# Relationship: 1-to-Many
# Each Store will have Multiple Items in Inventory
# Each Store will have Multiple Employees
