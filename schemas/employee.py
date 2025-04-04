from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey, Integer
from datetime import datetime, timezone
from typing import List
from uuid import uuid4
from .base import Base


# This table will be used to define the Hierchy of the Organization.
# Also, the Higher Level allows the use of Complex and Important Functional APIs.
class Role(Base):
    __tablename__ = 'roles'
    
    level: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, comment="Role Level of the Employee.")
    role: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="Role Level of the Employee.")
    employees: Mapped[List["Employee"]] = relationship(back_populates="role")


class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for Employees.")
    first_name: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="First Name of the Employee.")
    last_name: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="Last Name of the Employee.")
    hire_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), comment="Hire Date of the Employee.")
    leave_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Leave Date of the Employee.")
    phone_number: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False, comment="Phone number of the Employee.")
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=True, comment="Email of the Employee.")
    address: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="Address of the Employee.")
    level: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("roles.level"), nullable=False, comment="(F.Key) Identifier for Role Level.")
    role = relationship("Role", back_populates="employees")
    store_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stores.id"), nullable=False, comment="(F.Key) Identifier for Stores.")
    store: Mapped["Store"] = relationship(
        uselist=False, back_populates="employees")


# Relationship: 1-to-Many
# Each Employee can have a Single Role
# Each Role can have Multiple Employees
# Each Employee can only work at a Single Store
