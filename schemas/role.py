from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from typing import List
from .base import Base
from .user import User


# This table will be used to define the Hierchy of the Organization.
# Also, the Higher Level allows the use of Complex and Important Functional APIs.
class Role(Base):
    __tablename__ = 'roles'

    level: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Role Level of the User."
    )
    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        comment="Role of the User."
    )

    ###############
    # Relationships
    ###############

    users: Mapped[List["User"]] = relationship(
        back_populates="role",
        uselist=True
    )
