from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import String, UUID
from uuid import uuid4


Base = declarative_base()


# Made the Email, and Physical Address Nullable, to provide support for
# Offline Customers, who don't want to Share their Information.
class Customers(Base):
    __tablename__ = 'customers'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for the Customers.")
    first_name: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="First Name of the Customer.")
    last_name: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="Last Name of the Customer.")
    phone_number: Mapped[str] = mapped_column(
        String(16), primary_key=True, comment="Phone number of the Customer.")
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=True, comment="Email of the Customer.")
    address: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="Address of the Customer.")
