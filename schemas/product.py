from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, UUID, ForeignKey, Integer, Boolean
from typing import List
from uuid import uuid4
from .base import Base


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="Unique Identifier for the Category.")
    category: Mapped[str] = mapped_column(
        String, nullable=False, comment="Name of the Category.")

    products: Mapped[List["Product"]] = relationship(
        uselist=True, back_populates="category")


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
    price: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="Product price.")
    is_removed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Product Removal Indicator.")
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, comment="(F.K) Category of the Product.")
    category: Mapped["Category"] = relationship(
        uselist=False, back_populates="products")


# Relationship: 1-to-Many
# Each Product will have a Single Category.
# Each Category will have Multiple Products.
