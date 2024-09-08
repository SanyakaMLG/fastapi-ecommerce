import enum
from typing import Annotated, Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, ForeignKey, Boolean, Column, Integer
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from json import JSONEncoder

from app.database import Base


intpk = Annotated[int, mapped_column(primary_key=True)]
str_255 = Annotated[str, 255]


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    phone: Mapped[str] = mapped_column(String(20), unique=True)
    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    middle_name: Mapped[str_255 | None]

    carts: Mapped[list["Cart"]] = relationship("Cart", back_populates="user")
    payment_methods: Mapped[list["PaymentMethod"]] = relationship("PaymentMethod", back_populates="user")
    shipping_addresses: Mapped[list["ShippingAddress"]] = relationship("ShippingAddress", back_populates="user")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")


class Product(Base):
    __tablename__ = "product"

    id: Mapped[intpk]
    title: Mapped[str_255]
    description: Mapped[str_255 | None]
    price: Mapped[float]
    discount: Mapped[float | None]
    quantity: Mapped[int]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", onupdate="CASCADE", ondelete="SET DEFAULT"),
        server_default=text("-1"),
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    carts: Mapped[Optional[list["Cart"]]] = relationship(
        back_populates="products", secondary="cart_item"
    )
    attributes: Mapped[Optional[list["AttributeValue"]]] = relationship(
        back_populates="products", secondary="product_attribute_value"
    )
    reviews: Mapped[Optional[list["Review"]]] = relationship(back_populates="product")


class Category(Base, JSONEncoder):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    title: Mapped[str_255]
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.id", onupdate="CASCADE", ondelete="SET NULL")
    )

    products: Mapped[Optional[list["Product"]]] = relationship(back_populates="category")
    parent: Mapped[Optional["Category"]] = relationship(backref="children", remote_side=[id])

    def default(self, o):
        return o.__dict__


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    is_active: Mapped[bool]

    user: Mapped["User"] = relationship(back_populates="carts")
    order: Mapped[Optional["Order"]] = relationship(back_populates="cart")
    products: Mapped[list["Product"]] = relationship(
        back_populates="carts", secondary="cart_item"
    )


class OrderStatus(enum.Enum):
    new = "new"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"


class DeliveryType(enum.Enum):
    pickup = "pickup"
    delivery = "delivery"


class Order(Base):
    __tablename__ = "order"

    id: Mapped[intpk]
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"))
    cart_cost: Mapped[float]
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.new)
    delivery_type: Mapped[DeliveryType]
    delivery_address: Mapped[int | None] = mapped_column(
        ForeignKey("shipping_address.id", onupdate="CASCADE", ondelete="SET NULL")
    )
    delivery_cost: Mapped[float]
    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_method.id", onupdate="CASCADE", ondelete="SET NULL")
    )

    cart: Mapped["Cart"] = relationship(back_populates="order")
    payment_method: Mapped["PaymentMethod"] = relationship(back_populates="orders")
    shipping_address: Mapped[Optional["ShippingAddress"]] = relationship(back_populates="orders")


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    card_number: Mapped[str_255]

    user: Mapped["User"] = relationship(back_populates="payment_methods")
    orders: Mapped[list["Order"]] = relationship(back_populates="payment_method")


class ShippingAddress(Base):
    __tablename__ = "shipping_address"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    address: Mapped[str_255]
    city: Mapped[str_255]
    state: Mapped[str_255]
    country: Mapped[str_255]
    postal_code: Mapped[str_255]

    user: Mapped["User"] = relationship(back_populates="shipping_addresses")
    orders: Mapped[list["Order"]] = relationship(back_populates="shipping_address")


class Review(Base):
    __tablename__ = "review"

    id: Mapped[intpk]
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int]
    comment: Mapped[str | None] = mapped_column(String(1000))

    product: Mapped["Product"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")


class Attribute(Base):
    __tablename__ = "attribute"

    id: Mapped[intpk]
    title: Mapped[str_255]
    in_filter: Mapped[bool]

    values: Mapped[list["AttributeValue"]] = relationship(back_populates="attribute")


class AttributeValue(Base):
    __tablename__ = "attribute_value"

    id: Mapped[intpk]
    attribute_id: Mapped[int] = mapped_column(ForeignKey("attribute.id"))
    value: Mapped[str_255]

    attribute: Mapped["Attribute"] = relationship(back_populates="values", lazy='selectin')
    products: Mapped[list["Product"]] = relationship(
        back_populates="attributes", secondary="product_attribute_value"
    )


class CartItem(Base):
    __tablename__ = "cart_item"

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("cart.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity: Mapped[int]
    history_price: Mapped[float | None]

    cart: Mapped["Cart"] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship(back_populates="carts")


class ProductAttributeValues(Base):
    __tablename__ = "product_attribute_value"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    attribute_value_id: Mapped[int] = mapped_column(
        ForeignKey("attribute_value.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
