from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, UUID, ForeignKey, Integer
from .product import Product
from .base import Base


class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate Unique Identifier."
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Quantity of the Product in the Inventory."
    )
    max_discount_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Max Discount Applicable on the Product (0-1)."
    )

    ###############
    # Foreign Keys
    ###############

    store_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        primary_key=True,
        comment="(F.Key) Unique identifier for the Store."
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("products.id", ondelete="RESTRICT"),
        primary_key=True,
        comment="(F.Key) Unique identifier for the Product."
    )

    ################
    # Relationships
    ################

    product: Mapped["Product"] = relationship(uselist=False)


# Relationship: 1-to-1
# Each Item in the Inventory is a Product.
