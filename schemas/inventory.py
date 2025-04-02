from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Float, UUID, ForeignKey, Integer
from uuid import uuid4


Base = declarative_base()


class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="Unique Surrogate Identifier.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), nullable=False, comment="(F.Key) Unique identifier for the Product.")
    quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Quantity of the Product in the Inventory.")
    max_discount_amount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Max Discount Applicable on the Product (0-1).")
    restock_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("restocks.id"), nullable=False, comment="(F.Key) Unique identifier for the Restock.")
