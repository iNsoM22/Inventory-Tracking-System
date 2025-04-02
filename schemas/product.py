from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Float, UUID, ForeignKey, Integer, Boolean
from uuid import uuid4

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="Unique Identifier for the Category.")
    category: Mapped[str] = mapped_column(
        String, nullable=False, comment="Name of the Category.")


# Removal of a Product from the Database will not be allowed, due to dependencies.
# Incase of discontiunation of the Product, 'its is_removed' column will be
# marked as True.
class Product(Base):
    __tablename__ = 'products'

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, comment="Unique Identifier for the Product.")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Name of the Product.")
    description: Mapped[str] = mapped_column(
        String, nullable=False, comment="Description of the Product")
    category_id: Mapped[str] = mapped_column(
        ForeignKey("categories.id"), nullable=False, comment="Category ID of the Product.")
    price: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Product price.")
    is_removed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Product Removal Indicator")
