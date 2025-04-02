from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import Float, UUID, ForeignKey, Integer
from product import Product

Base = declarative_base()


class Inventory(Base):
    __tablename__ = 'inventory'

    store_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("stores.id"), primary_key=True, comment="(F.Key) Unique identifier for the Store.")
    product_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("products.id"), primary_key=True, comment="(F.Key) Unique identifier for the Product.")
    quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Quantity of the Product in the Inventory.")
    max_discount_amount: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Max Discount Applicable on the Product (0-1).")
    product: Mapped["Product"] = relationship(uselist=False)


# Relationship: 1-to-1
# Each Item in the Inventory is a Product.
