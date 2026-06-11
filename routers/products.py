from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional
import asyncio

from database import get_db
import models, schemas
from auth import get_current_active_user, require_admin, require_admin_or_seller
from utils.events import notify
from utils.email import send_new_product_email

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


# ─────────────────────────────────────────────
# HELPER: attach computed rating + seller fields
# ─────────────────────────────────────────────

def _attach_extras(product: models.Product, db: Session) -> models.Product:
    avg = (
        db.query(func.avg(models.Review.rating))
        .filter(models.Review.product_id == product.id)
        .scalar()
    )
    count = (
        db.query(func.count(models.Review.id))
        .filter(models.Review.product_id == product.id)
        .scalar() or 0
    )
    product.average_rating = round(float(avg), 1) if avg else None
    product.review_count   = count
    if product.seller:
        product.shop_name   = product.seller.shop_name
        product.seller_name = product.seller.user.full_name if product.seller.user else None
    else:
        product.shop_name   = None
        product.seller_name = None
    return product


# ─────────────────────────────────────────────
# ASYNC HELPER — Simulates async I/O (e.g. external price check)
# ─────────────────────────────────────────────

async def fetch_external_price_check(product_name: str) -> dict:
    await asyncio.sleep(0)
    return {"product": product_name, "price_verified": True}


# ─────────────────────────────────────────────
# CREATE PRODUCT (Admin or Seller)
# ─────────────────────────────────────────────

@router.post("/", response_model=schemas.ProductResponse, status_code=201)
async def create_product(
    payload: schemas.ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_seller),
):
    category = db.query(models.Category).filter(models.Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await fetch_external_price_check(payload.name)

    seller_id = None
    shop_name = None
    if current_user.role == models.UserRole.seller:
        profile = db.query(models.SellerProfile).filter(
            models.SellerProfile.user_id == current_user.id
        ).first()
        if not profile:
            raise HTTPException(status_code=400, detail="Seller profile not found")
        seller_id = profile.id
        shop_name = profile.shop_name

    product_data = payload.model_dump()
    product_data["seller_id"] = seller_id
    product = models.Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    notify("products_updated")

    # Email all customers about the new product (async, non-blocking)
    customers = db.query(models.User).filter(
        models.User.role == models.UserRole.customer,
        models.User.is_active == True,
    ).all()
    recipient_emails = [u.email for u in customers]
    if recipient_emails:
        background_tasks.add_task(
            send_new_product_email,
            product.name,
            shop_name or "EcomInventory Pro",
            product.id,
            recipient_emails,
        )

    return _attach_extras(product, db)


# ─────────────────────────────────────────────
# GET ALL PRODUCTS (with optional search & filter)
# ─────────────────────────────────────────────

@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    available_only: bool = Query(default=False),
    seller_id: Optional[int] = Query(default=None),
):
    query = db.query(models.Product)

    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    if available_only:
        query = query.filter(models.Product.is_available == True)
    if seller_id:
        query = query.filter(models.Product.seller_id == seller_id)

    return [_attach_extras(p, db) for p in query.all()]


# ─────────────────────────────────────────────
# GET MY PRODUCTS (Seller only)
# ─────────────────────────────────────────────

@router.get("/mine", response_model=list[schemas.ProductResponse])
def get_my_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != models.UserRole.seller:
        raise HTTPException(status_code=403, detail="Sellers only")
    profile = db.query(models.SellerProfile).filter(
        models.SellerProfile.user_id == current_user.id
    ).first()
    if not profile:
        return []
    products = db.query(models.Product).filter(
        models.Product.seller_id == profile.id
    ).all()
    return [_attach_extras(p, db) for p in products]


# ─────────────────────────────────────────────
# GET SINGLE PRODUCT
# ─────────────────────────────────────────────

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _attach_extras(product, db)


# ─────────────────────────────────────────────
# UPDATE PRODUCT (Admin or owning Seller)
# ─────────────────────────────────────────────

@router.patch("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_seller),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user.role == models.UserRole.seller:
        profile = db.query(models.SellerProfile).filter(
            models.SellerProfile.user_id == current_user.id
        ).first()
        if not profile or product.seller_id != profile.id:
            raise HTTPException(status_code=403, detail="You can only edit your own products")

    if payload.category_id:
        if not db.query(models.Category).filter(models.Category.id == payload.category_id).first():
            raise HTTPException(status_code=404, detail="Category not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    notify("products_updated")
    return _attach_extras(product, db)


# ─────────────────────────────────────────────
# DELETE PRODUCT (Admin or owning Seller)
# ─────────────────────────────────────────────

@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_seller),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user.role == models.UserRole.seller:
        profile = db.query(models.SellerProfile).filter(
            models.SellerProfile.user_id == current_user.id
        ).first()
        if not profile or product.seller_id != profile.id:
            raise HTTPException(status_code=403, detail="You can only delete your own products")

    db.delete(product)
    db.commit()
    notify("products_updated")
