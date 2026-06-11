from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_active_user, require_admin
import models, schemas

router = APIRouter(prefix="/api/v1/products", tags=["Reviews"])


# ─────────────────────────────────────────────
# SUBMIT REVIEW
# Customer must have a DELIVERED order containing this product.
# One review per customer per product (enforced by DB unique constraint).
# ─────────────────────────────────────────────

@router.post("/{product_id}/reviews", response_model=schemas.ReviewResponse, status_code=201)
def submit_review(
    product_id: int,
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not db.query(models.Product).filter(models.Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify the customer actually received this product
    purchased = (
        db.query(models.OrderItem)
        .join(models.Order, models.Order.id == models.OrderItem.order_id)
        .filter(
            models.OrderItem.product_id == product_id,
            models.Order.customer_id == current_user.id,
            models.Order.status == models.OrderStatus.delivered,
        )
        .first()
    )
    if not purchased:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review products from your delivered orders",
        )

    if db.query(models.Review).filter(
        models.Review.product_id == product_id,
        models.Review.customer_id == current_user.id,
    ).first():
        raise HTTPException(status_code=400, detail="You have already reviewed this product")

    review = models.Review(
        product_id=product_id,
        customer_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    review.customer_name = current_user.full_name
    return review


# ─────────────────────────────────────────────
# GET REVIEWS FOR A PRODUCT (Public)
# ─────────────────────────────────────────────

@router.get("/{product_id}/reviews", response_model=list[schemas.ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Product).filter(models.Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    reviews = (
        db.query(models.Review)
        .filter(models.Review.product_id == product_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )
    for r in reviews:
        r.customer_name = r.customer.full_name if r.customer else None
    return reviews


# ─────────────────────────────────────────────
# DELETE REVIEW (Admin only)
# ─────────────────────────────────────────────

@router.delete("/{product_id}/reviews/{review_id}", status_code=204)
def delete_review(
    product_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    review = db.query(models.Review).filter(
        models.Review.id == review_id,
        models.Review.product_id == product_id,
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
