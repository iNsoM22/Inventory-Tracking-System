from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey
from datetime import datetime, timezone
from uuid import uuid4
from .base import Base
from .user import User


class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Unique Identifier for Employees."
    )
    first_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="First Name of the Employee."
    )
    last_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Last Name of the Employee."
    )
    hire_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Hire Date of the Employee."
    )
    leave_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Leave Date of the Employee."
    )
    phone_number: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        index=True,
        nullable=False,
        comment="Phone number of the Employee."
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
        comment="Email of the Employee."
    )
    address: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Address of the Employee."
    )
    position: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Position of the Employee."
    )

    ###############
    # Foreign Keys
    ###############

    store_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        comment="(F.Key) Identifier for Stores."
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=True,
        unique=True,
        comment="(F.Key) Identifier for Users."
    )

    ################
    # Relationships
    ################

    user: Mapped["User"] = relationship(
        uselist=False
    )
