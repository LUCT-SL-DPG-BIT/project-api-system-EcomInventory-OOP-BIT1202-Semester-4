from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class UserRole(str, enum.Enum):
    admin = "admin"
    customer = "customer"
    seller = "seller"


class DiscountType(str, enum.Enum):
    percentage = "percentage"
    flat = "flat"


# ─────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="customer")
    seller_profile = relationship("SellerProfile", back_populates="user", uselist=False)


# ─────────────────────────────────────────────
# SELLER PROFILE MODEL
# ─────────────────────────────────────────────

class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    shop_name    = Column(String(150), nullable=False)
    bio          = Column(Text, nullable=True)
    phone        = Column(String(50), nullable=True)
    location     = Column(String(200), nullable=True)
    what_you_sell = Column(String(200), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    user     = relationship("User", back_populates="seller_profile")
    products = relationship("Product", back_populates="seller")


# ─────────────────────────────────────────────
# CATEGORY MODEL
# ─────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="category")


# ─────────────────────────────────────────────
# PRODUCT MODEL
# ─────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    image_url = Column(String(500), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("seller_profiles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category    = relationship("Category", back_populates="products")
    seller      = relationship("SellerProfile", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews     = relationship("Review", back_populates="product")


# ─────────────────────────────────────────────
# ORDER MODEL
# ─────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0, server_default="0")
    voucher_code = Column(String(50), nullable=True)
    shipping_address = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# ORDER ITEM MODEL (junction between Order and Product)
# ─────────────────────────────────────────────

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ─────────────────────────────────────────────
# VOUCHER MODEL
# ─────────────────────────────────────────────

class Voucher(Base):
    __tablename__ = "vouchers"

    id             = Column(Integer, primary_key=True, index=True)
    code           = Column(String(50), unique=True, index=True, nullable=False)
    discount_type  = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=False)
    expiry_date    = Column(DateTime(timezone=True), nullable=True)
    usage_limit    = Column(Integer, nullable=True)   # None = unlimited
    times_used     = Column(Integer, default=0)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────────
# REVIEW MODEL
# One customer can review a product only once (UniqueConstraint).
# A review is only allowed after a delivered order (enforced in the router).
# ─────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("product_id", "customer_id"),)

    id          = Column(Integer, primary_key=True, index=True)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"),    nullable=False)
    rating      = Column(Integer, nullable=False)   # 1–5
    comment     = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    product  = relationship("Product", back_populates="reviews")
    customer = relationship("User")
