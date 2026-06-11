from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import OrderStatus, UserRole, DiscountType


# ─────────────────────────────────────────────
# USER SCHEMAS
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.customer


class SellerRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    shop_name: str = Field(..., min_length=2, max_length=150)
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    what_you_sell: Optional[str] = None


class SellerProfileResponse(BaseModel):
    id: int
    user_id: int
    shop_name: str
    bio: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    what_you_sell: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


# ─────────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ─────────────────────────────────────────────
# CATEGORY SCHEMAS
# ─────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None


# ─────────────────────────────────────────────
# PRODUCT SCHEMAS
# ─────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    is_available: Optional[bool] = True
    image_url: Optional[str] = None
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    is_available: bool
    image_url: Optional[str]
    category_id: int
    seller_id: Optional[int] = None
    shop_name: Optional[str] = None
    seller_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    average_rating: Optional[float] = None
    review_count: int = 0

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None


# ─────────────────────────────────────────────
# ORDER SCHEMAS
# ─────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=5)
    items: List[OrderItemCreate]
    voucher_code: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    status: OrderStatus
    total_amount: float
    discount_amount: float = 0.0
    voucher_code: Optional[str] = None
    shipping_address: str
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ─────────────────────────────────────────────
# ANALYTICS SCHEMAS
# ─────────────────────────────────────────────

class TopProduct(BaseModel):
    product_id: int
    product_name: str
    total_sold: int


class CategoryRevenue(BaseModel):
    category_name: str
    revenue: float


class AnalyticsSummary(BaseModel):
    delivered_revenue: float
    orders_by_status: dict
    top_5_products: List[TopProduct]
    revenue_by_category: List[CategoryRevenue]


# ─────────────────────────────────────────────
# VOUCHER SCHEMAS
# ─────────────────────────────────────────────

class VoucherCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(default=None, gt=0)
    is_active: bool = True


class VoucherResponse(BaseModel):
    id: int
    code: str
    discount_type: DiscountType
    discount_value: float
    expiry_date: Optional[datetime]
    usage_limit: Optional[int]
    times_used: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# REVIEW SCHEMAS
# ─────────────────────────────────────────────

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    customer_id: int
    customer_name: Optional[str] = None
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# VOUCHER BROADCAST SCHEMA
# ─────────────────────────────────────────────

class VoucherBroadcast(BaseModel):
    user_ids: Optional[List[int]] = None  # None = send to all customers
