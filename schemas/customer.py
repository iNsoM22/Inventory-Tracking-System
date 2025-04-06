from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, UUID, ForeignKey
from uuid import uuid4
from .base import Base


# Made the Email, and Physical Address Nullable, to provide support for
# Offline Customers, who don't want to Share their Information.
class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for the Customers.")
    first_name: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="First Name of the Customer.")
    last_name: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="Last Name of the Customer.")
    phone_number: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, comment="Phone number of the Customer.")
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=True, comment="Email of the Customer.")
    address: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="Address of the Customer.")
    user_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=True, unique=True, comment="(F.Key) Identifier for Users.")
