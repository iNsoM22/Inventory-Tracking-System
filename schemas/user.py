from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, Boolean, Integer, ForeignKey
from datetime import datetime, timezone
from uuid import uuid4
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Unique Identifier for User."
    )
    username: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
        comment="Username that will be used for Authentication."
    )
    password: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Hashed Password that will be used for Authentication"
    )
    is_internal_user: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Flag to indicate if the User is an internal/admin User."
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Timestamp of when the User is created."
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Timestamp of the last update to the user record."
    )

    ###############
    # Foreign Keys
    ###############

    level: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.level"),
        nullable=False,
        default=1,
        comment="Level of the User for RBAC."
    )
