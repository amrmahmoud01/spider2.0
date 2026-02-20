from typing import List, Optional
from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import decimal


class Base(DeclarativeBase):
    pass


# ====================
# STORE TABLE
# ====================
class Store(Base):
    __tablename__ = 'store'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    storeName: Mapped[str] = mapped_column(String(90))
    storeLink: Mapped[str] = mapped_column(String(2083))
    logo: Mapped[Optional[str]] = mapped_column(String(2083))

    # One-to-many: Store → Product
    product: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="store",
        cascade="all, delete-orphan"
    )


# ====================
# PRODUCT TABLE
# ====================
class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        ForeignKeyConstraint(
            ["storeId"],
            ["store.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="product_ibfk_1",
        ),
        Index("storeId", "storeId"),
    )

    productId: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2))
    type: Mapped[Optional[str]] = mapped_column(String(90))
    color: Mapped[Optional[str]] = mapped_column(String(90))
    productLink: Mapped[Optional[str]] = mapped_column(String(2083))
    name: Mapped[Optional[str]] = mapped_column(String(90))
    storeId: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(90))
    salePrice: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2))

    # Many-to-one: Product → Store
    store: Mapped["Store"] = relationship(
        "Store",
        back_populates="product"
    )

    # One-to-many: Product → Productimages
    productimages: Mapped[List["Productimages"]] = relationship(
        "Productimages",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    # One-to-many: Product → Productcolors
    productcolors: Mapped[List["Productcolors"]] = relationship(
        "Productcolors",
        back_populates="product",
        cascade="all, delete-orphan"
    )


# ====================
# PRODUCT IMAGES TABLE
# ====================
class Productimages(Base):
    __tablename__ = "productimages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["productId"],
            ["product.productId"],
            name="productimages_ibfk_1",
        ),
        Index("productId", "productId"),
    )

    imageId: Mapped[int] = mapped_column(Integer, primary_key=True)
    URL: Mapped[str] = mapped_column(String(2083))
    productId: Mapped[int] = mapped_column(Integer)

    # Many-to-one: Productimages → Product
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="productimages"
    )


# ====================
# PRODUCT COLORS TABLE
# ====================
class Productcolors(Base):
    __tablename__ = "productcolors"
    __table_args__ = (
        ForeignKeyConstraint(
            ["productId"],
            ["product.productId"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="productcolors_ibfk_1",
        ),
    )

    # Composite Primary Key
    productId: Mapped[int] = mapped_column(Integer, primary_key=True)
    color: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Many-to-one: Productcolors → Product
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="productcolors"
    )
