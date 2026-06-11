from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_active_user, require_admin, require_admin_or_seller
from utils.events import notify

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


# ─────────────────────────────────────────────
# CREATE CATEGORY (Admin or Seller)
# ─────────────────────────────────────────────

@router.post("/", response_model=schemas.CategoryResponse, status_code=201)
def create_category(
    payload: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_seller),
):
    existing = db.query(models.Category).filter(models.Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = models.Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    notify("products_updated")
    return category


# ─────────────────────────────────────────────
# GET ALL CATEGORIES
# ─────────────────────────────────────────────

@router.get("/", response_model=list[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


# ─────────────────────────────────────────────
# GET SINGLE CATEGORY
# ─────────────────────────────────────────────

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# ─────────────────────────────────────────────
# UPDATE CATEGORY (Admin only)
# ─────────────────────────────────────────────

@router.patch("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    notify("products_updated")
    return category


# ─────────────────────────────────────────────
# DELETE CATEGORY (Admin only)
# ─────────────────────────────────────────────

@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    notify("products_updated")
